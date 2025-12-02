"""Simple MCTS with neural network prior (PUCT).
Not heavily optimized; suitable for self-play workers.
"""
from __future__ import annotations
import math
import random
from collections import defaultdict
from typing import Any, Dict, List
from training.encoder import index_to_move, move_to_index, ACTION_SIZE
try:
    from core.moves.move import Move
except Exception:
    Move = None

try:
    # prefer bound method when available, otherwise import core generator
    from core.moves.legal_movegen import generate_legal_moves as _core_generate_legal_moves
except Exception:
    _core_generate_legal_moves = None


class MCTSNode:
    def __init__(self):
        self.N = 0
        self.W = 0.0
        self.Q = 0.0
        self.P = 0.0
        self.children: Dict[int, 'MCTSNode'] = {}


class MCTS:
    def __init__(self, net_predict, action_size: int, c_puct=1.0, sims=50):
        self.net = net_predict
        self.action_size = action_size
        self.c_puct = c_puct
        self.sims = sims

    def run(self, board):
        root = MCTSNode()
        # get priors from net
        # net expects a board-like object; net wrapper should accept board
        state = board
        pi_logits, _ = self.net(state)
        # expect pi_logits as numpy or torch
        if hasattr(pi_logits, 'detach'):
            import torch
            pi = torch.softmax(pi_logits, dim=-1).cpu().numpy()
        else:
            import numpy as np
            pi = np.exp(pi_logits - pi_logits.max())
            pi = pi / pi.sum()

        # Only create root children for legal moves (mask illegal actions)
        # obtain legal moves from board if it exposes the method,
        # otherwise fall back to core.moves.legal_movegen.generate_legal_moves
        legal_moves = []
        try:
            if hasattr(board, 'generate_legal_moves'):
                legal_moves = list(board.generate_legal_moves())
            elif _core_generate_legal_moves is not None:
                legal_moves = list(_core_generate_legal_moves(board))
        except Exception:
            legal_moves = []

        if legal_moves:
            for m in legal_moves:
                try:
                    a = move_to_index(m)
                except Exception:
                    continue
                if a is None or a < 0 or a >= min(len(pi), self.action_size):
                    continue
                node = MCTSNode()
                node.P = float(pi[a])
                root.children[a] = node
        else:
            # fallback: if we cannot enumerate legal moves, include all actions
            for a in range(min(len(pi), self.action_size)):
                node = MCTSNode()
                node.P = float(pi[a])
                root.children[a] = node

        # If the net supports batched prediction, use a batched simulation path
        if hasattr(self.net, 'batch_predict'):
            # collect leaves first, then evaluate in batch
            leaves = []  # list of (node, path, board)
            for _ in range(self.sims):
                try:
                    node, path, leaf_board = self._descend_to_leaf(root, board.copy())
                    if node is None:
                        continue
                    leaves.append((node, path, leaf_board))
                except Exception:
                    continue

            if leaves:
                boards = [leaf[2] for leaf in leaves]
                # net.batch_predict should return (pi_logits_list, values_list)
                try:
                    pi_list, v_list = self.net.batch_predict(boards)
                except Exception:
                    # fallback to sequential
                    pi_list, v_list = [], []
                    for b in boards:
                        p, vv = self.net(b)
                        pi_list.append(p)
                        v_list.append(vv)

                # process each leaf result
                for (node, path, _), pi_logits, value in zip(leaves, pi_list, v_list):
                    # normalise and expand
                    if hasattr(pi_logits, 'detach'):
                        import torch
                        pi = torch.softmax(pi_logits, dim=-1).cpu().numpy()
                        v = float(value.detach().cpu().item())
                    else:
                        import numpy as np
                        pi = np.exp(pi_logits - pi_logits.max())
                        pi = pi / pi.sum()
                        v = float(value)

                    # restrict expansion at the leaf to legal moves when possible
                    leaf_board = _  # renamed for clarity
                    legal_at_leaf = []
                    try:
                        if hasattr(leaf_board, 'generate_legal_moves'):
                            legal_at_leaf = list(leaf_board.generate_legal_moves())
                        elif _core_generate_legal_moves is not None:
                            legal_at_leaf = list(_core_generate_legal_moves(leaf_board))
                    except Exception:
                        legal_at_leaf = []

                    if legal_at_leaf:
                        for m2 in legal_at_leaf:
                            try:
                                a = move_to_index(m2)
                            except Exception:
                                continue
                            if a is None or a < 0 or a >= min(self.action_size, len(pi)):
                                continue
                            if a not in node.children:
                                cn = MCTSNode()
                                cn.P = float(pi[a])
                                node.children[a] = cn
                    else:
                        for a in range(min(self.action_size, len(pi))):
                            if a not in node.children:
                                cn = MCTSNode()
                                cn.P = float(pi[a])
                                node.children[a] = cn

                    # backup
                    for parent, a in reversed(path):
                        child = parent.children.get(a)
                        if child is None:
                            continue
                        child.N += 1
                        child.W += v
                        child.Q = child.W / child.N
                        parent.N += 1
        else:
            for _ in range(self.sims):
                self._simulate(root, board.copy())

        # return visit distribution
        visits = [root.children[a].N if a in root.children else 0 for a in range(self.action_size)]
        s = sum(visits)
        if s == 0:
            return [1.0 / self.action_size] * self.action_size
        return [v / s for v in visits]

    def _simulate(self, root: MCTSNode, board):
        path = []
        node = root
        b = board
        # descent
        while True:
            if not node.children:
                break
            # select
            best_a, best_ucb, best_child = None, -1e9, None
            for a, child in node.children.items():
                u = child.Q + self.c_puct * child.P * math.sqrt(node.N + 1) / (1 + child.N)
                if u > best_ucb:
                    best_ucb = u
                    best_a = a
                    best_child = child
            if best_child is None:
                break
            path.append((node, best_a))
            # apply move
            # translate action index to Move and apply using core Board.make_move
            try:
                f, t, promo = index_to_move(best_a)
                if Move is None:
                    return
                mv = Move(from_sq=f, to_sq=t, piece=None, is_capture=False, promotion=promo)
                # core Board.make_move expects piece filled; try to fill from mailbox
                cell = b.mailbox[f]
                if cell is None:
                    return
                color, ptype = cell
                mv.piece = ptype
                b.make_move(mv)
            except Exception:
                return
            node = best_child

        # expand and evaluate
        pi_logits, value = self.net(b)
        if hasattr(pi_logits, 'detach'):
            import torch
            pi = torch.softmax(pi_logits, dim=-1).cpu().numpy()
            v = float(value.detach().cpu().item())
        else:
            import numpy as np
            pi = np.exp(pi_logits - pi_logits.max())
            pi = pi / pi.sum()
            v = float(value)

        # add children - restrict to legal moves when possible
        # same fallback for expansion: prefer board.generate_legal_moves,
        # otherwise use core generator if available
        legal_here = []
        try:
            if hasattr(b, 'generate_legal_moves'):
                legal_here = list(b.generate_legal_moves())
            elif _core_generate_legal_moves is not None:
                legal_here = list(_core_generate_legal_moves(b))
        except Exception:
            legal_here = []

        if legal_here:
            for m2 in legal_here:
                try:
                    a = move_to_index(m2)
                except Exception:
                    continue
                if a is None or a < 0 or a >= min(self.action_size, len(pi)):
                    continue
                if a not in node.children:
                    cn = MCTSNode()
                    cn.P = float(pi[a])
                    node.children[a] = cn
        else:
            for a in range(min(self.action_size, len(pi))):
                if a not in node.children:
                    cn = MCTSNode()
                    cn.P = float(pi[a])
                    node.children[a] = cn

        # backup
        for parent, a in reversed(path):
            child = parent.children.get(a)
            if child is None:
                continue
            child.N += 1
            child.W += v
            child.Q = child.W / child.N
            parent.N += 1

    def _descend_to_leaf(self, root: MCTSNode, board):
        """Descend the tree from root to a leaf without evaluating the leaf.
        Returns (node, path, board) where node is the leaf node (may have no children yet),
        path is the list of (parent, action) pairs, and board is the board at leaf.
        """
        path = []
        node = root
        b = board
        # descent
        while True:
            if not node.children:
                break
            # select
            best_a, best_ucb, best_child = None, -1e9, None
            for a, child in node.children.items():
                u = child.Q + self.c_puct * child.P * math.sqrt(node.N + 1) / (1 + child.N)
                if u > best_ucb:
                    best_ucb = u
                    best_a = a
                    best_child = child
            if best_child is None:
                break
            path.append((node, best_a))
            # apply move
            try:
                f, t, promo = index_to_move(best_a)
                if Move is None:
                    return None, None, None
                mv = Move(from_sq=f, to_sq=t, piece=None, is_capture=False, promotion=promo)
                cell = b.mailbox[f]
                if cell is None:
                    return None, None, None
                color, ptype = cell
                mv.piece = ptype
                b.make_move(mv)
            except Exception:
                return None, None, None
            node = best_child

        return node, path, b
