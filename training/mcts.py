"""Simple MCTS with neural network prior (PUCT).
Not heavily optimized; suitable for self-play workers.
"""
from __future__ import annotations
import math
import random
from collections import defaultdict
from typing import Any, Dict, List
from training.encoder import index_to_move, ACTION_SIZE
try:
    from core.moves.move import Move
except Exception:
    Move = None


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

        for a in range(min(len(pi), self.action_size)):
            node = MCTSNode()
            node.P = float(pi[a])
            root.children[a] = node

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

        # add children
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
