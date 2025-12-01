"""Iterative deepening driver that exposes `search_root`.

Implements depth-increasing loop, time controller, PV extraction and stop support.
"""
from typing import Any, Dict, List, Optional
from .search.impl import alpha_beta, SearchState, build_pv_from_tt, SearchController
import time


def search_root(board: Any, max_time_ms: Optional[int] = None, max_depth: Optional[int] = 4) -> Dict:
    ctrl = SearchController()
    state = SearchState()
    start = time.time()
    deadline = None if max_time_ms is None else start + max_time_ms / 1000.0

    best_move = None
    best_score = 0
    nodes = 0
    depth_reached = 0
    pv_line: List[object] = []

    # root iterative loop
    for depth in range(1, (max_depth or 1) + 1):
        if deadline is not None and time.time() >= deadline:
            break
        try:
            # run search at this depth
            state.controller = ctrl
            score = alpha_beta(board, depth, -32000, 32000, state, ply=0)
        except TimeoutError:
            break
        except Exception:
            # other errors shouldn't stop whole loop
            break

        nodes = state.nodes
        depth_reached = depth
        best_score = score

        # probe TT at root for best move
        try:
            entry = state.tt.probe(getattr(board, 'zobrist_key', 0))
            if entry is not None:
                best_move = entry.best_move
        except Exception:
            best_move = best_move

        # reconstruct PV from TT
        pv_line = build_pv_from_tt(board, state.tt, max_depth=depth)

        # time check
        if deadline is not None and time.time() >= deadline:
            break

    return {
        'best_move': best_move,
        'score': best_score,
        'depth': depth_reached,
        'nodes': nodes,
        'pv': pv_line,
    }
