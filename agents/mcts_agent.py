"""MCTS agent using a policy+value neural network (PUCT).

This is a compact, self-contained implementation intended for integration
and testing. It performs a fixed number of simulations and selects the
most-visited root child as the chosen move.

Not a highly-optimized production search, but good for experiments and
as a stronger replacement for raw policy-only play.
"""
from __future__ import annotations
from typing import Any, Optional, Dict, Tuple
import math
import time
import os

try:
    import torch
except Exception:
    torch = None

from .agent_base import Agent

try:
    from training.model import make_model
    from training.encoder import board_to_tensor, move_to_index, ACTION_SIZE
except Exception:
    make_model = None
    board_to_tensor = None
    move_to_index = None
    ACTION_SIZE = None


class MCTSAgent(Agent):
    """PUCT MCTS agent.

    Parameters:
    - model_path: optional checkpoint path to load weights (if None, will
      attempt to construct an uninitialized model via `make_model`).
    - sims: number of MCTS simulations per move.
    - cpuct: exploration constant.
    """

    def __init__(self, model_path: Optional[str] = None, sims: int = 128, cpuct: float = 1.0, device: Optional[str] = None):
        if device is None and torch is not None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = device
        self.sims = int(sims)
        self.cpuct = float(cpuct)
        self.model = None
        self.model_path = model_path
        if make_model is not None and torch is not None:
            try:
                kwargs = {}
                if ACTION_SIZE is not None:
                    kwargs['action_size'] = ACTION_SIZE
                self.model = make_model(device=self.device, **kwargs)
                if model_path and os.path.exists(model_path):
                    ckpt = torch.load(model_path, map_location=self.device)
                    sd = ckpt.get('state_dict', ckpt) if isinstance(ckpt, dict) else ckpt
                    try:
                        self.model.load_state_dict(sd)
                    except Exception:
                        try:
                            self.model.load_state_dict(sd, strict=False)
                        except Exception:
                            pass
                if self.model is not None:
                    self.model.eval()
            except Exception:
                self.model = None

    async def get_move(self, board: Any) -> Optional[object]:
        # collect legal moves
        try:
            moves = list(board.generate_legal_moves())
        except Exception:
            try:
                from core.moves.legal_movegen import generate_legal_moves as core_gen
                moves = list(core_gen(board))
            except Exception:
                moves = []

        if not moves:
            return None

        # if no model, fallback to first legal move
        if self.model is None or board_to_tensor is None or move_to_index is None:
            return moves[0]

        # node structure keyed by zobrist (or id) -> node dict
        class Node(dict):
            pass

        def make_node(prior: float = 0.0) -> Node:
            return Node(N=0, W=0.0, P=float(prior), children={}, expanded=False)

        # root node
        root = make_node(0.0)

        # helper: evaluate network on a board and return priors dict(move->p) and value (float)
        def evaluate_network(b):
            try:
                import numpy as np
                arr = board_to_tensor(b)
                t = torch.from_numpy(arr).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    pi, v = self.model(t)
                logits = pi.squeeze(0).cpu().numpy()
                val = float(v.squeeze().cpu().numpy())
                return logits, val
            except Exception:
                return None, 0.0

        # expand root with network priors
        logits, v = evaluate_network(board)
        if logits is None:
            return moves[0]

        # map legal moves to priors using logits softmax over legal indices
        idxs = []
        for m in moves:
            try:
                idxs.append(move_to_index(m))
            except Exception:
                idxs.append(None)

        legal_logits = []
        for idx in idxs:
            if idx is None:
                legal_logits.append(-1e9)
            else:
                try:
                    legal_logits.append(float(logits[idx]))
                except Exception:
                    legal_logits.append(-1e9)

        # softmax
        maxl = max(legal_logits)
        exps = [math.exp(x - maxl) for x in legal_logits]
        s = sum(exps)
        if s <= 0:
            priors = [1.0 / len(moves)] * len(moves)
        else:
            priors = [e / s for e in exps]

        # attach children to root
        total_N = 0
        for m, p in zip(moves, priors):
            root['children'][m] = make_node(p)

        # run simulations
        for sim in range(self.sims):
            b_sim = board.copy() if hasattr(board, 'copy') else board
            node = root
            path = []  # list of (parent_node, move, child_node)

            # selection
            while node.get('expanded', False) and node['children']:
                # select child maximizing U = Q + cpuct * P * sqrt(sum_N)/(1+N)
                sum_N = sum(child['N'] for child in node['children'].values())
                best_u = None
                best_move = None
                best_child = None
                for mv, child in node['children'].items():
                    N = child['N']
                    Q = 0.0 if N == 0 else child['W'] / N
                    U = Q + self.cpuct * child['P'] * (math.sqrt(sum_N) / (1 + N))
                    if best_u is None or U > best_u:
                        best_u = U
                        best_move = mv
                        best_child = child
                if best_move is None:
                    break
                # play the move on b_sim
                try:
                    b_sim.make_move(best_move)
                except Exception:
                    # if we cannot play this move, mark child visited to avoid reuse
                    best_child['N'] += 1
                    best_child['W'] += 0.0
                    path.append((node, best_move, best_child))
                    break
                path.append((node, best_move, best_child))
                node = best_child

            # expansion
            if not node.get('expanded', False):
                # evaluate network at this leaf
                logits_l, val_l = evaluate_network(b_sim)
                if logits_l is None:
                    leaf_val = 0.0
                    node['expanded'] = True
                else:
                    # build priors for this node
                    try:
                        legal_here = list(b_sim.generate_legal_moves())
                    except Exception:
                        from core.moves.legal_movegen import generate_legal_moves as core_gen
                        legal_here = list(core_gen(b_sim))

                    idxs_here = []
                    for m in legal_here:
                        try:
                            idxs_here.append(move_to_index(m))
                        except Exception:
                            idxs_here.append(None)

                    legal_logits_here = []
                    for idx in idxs_here:
                        if idx is None:
                            legal_logits_here.append(-1e9)
                        else:
                            try:
                                legal_logits_here.append(float(logits_l[idx]))
                            except Exception:
                                legal_logits_here.append(-1e9)

                    maxlh = max(legal_logits_here) if legal_logits_here else 0.0
                    exps_h = [math.exp(x - maxlh) for x in legal_logits_here]
                    s_h = sum(exps_h)
                    if s_h <= 0:
                        pri_h = [1.0 / len(legal_here)] * len(legal_here) if legal_here else []
                    else:
                        pri_h = [e / s_h for e in exps_h]

                    # attach children
                    for m2, p2 in zip(legal_here, pri_h):
                        if m2 not in node['children']:
                            node['children'][m2] = make_node(p2)
                    leaf_val = float(val_l)
                    node['expanded'] = True

            # backpropagate
            v_back = leaf_val
            for parent, mv, child in reversed(path):
                child['N'] += 1
                child['W'] += v_back
                v_back = -v_back

        # choose move with highest visit count
        best_mv = None
        best_N = -1
        for mv, child in root['children'].items():
            if child['N'] > best_N:
                best_N = child['N']
                best_mv = mv

        return best_mv

    def name(self) -> str:
        base = f"MCTS(sims={self.sims},cpuct={self.cpuct})"
        if self.model_path:
            return f"{base} [{os.path.basename(self.model_path)}]"
        return base
