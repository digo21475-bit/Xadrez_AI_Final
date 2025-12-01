"""Iterative deepening search driver.

Performs depth-iterating loop with time management, probing TT for best moves
and collecting PV line from transposition table.
"""
from typing import Any, Dict, List, Optional
from .alphabeta import alpha_beta, SearchState
from .time_manager import TimeManager
from .pv import PVTable
from engine.utils.constants import MATE_SCORE


def search_root(board: Any, max_time_ms: Optional[int] = None, max_depth: Optional[int] = 3) -> Dict:
    """Iterative deepening search from root position.
    
    Args:
        board: Chess position to search
        max_time_ms: Time limit in milliseconds (None = unlimited)
        max_depth: Maximum depth to search (None = 1)
    
    Returns:
        Dict with keys:
            - best_move: Best move found (or None)
            - score: Evaluation of best_move
            - depth: Depth reached
            - nodes: Total nodes visited
            - pv: Principal variation line (list of moves)
    """
    tm = TimeManager()
    tm.start(max_time_ms)
    state = SearchState()
    pv = PVTable()

    best_move = None
    best_score = 0
    nodes = 0
    depth_reached = 0

    # Iterate through increasing depths
    for depth in range(1, (max_depth or 1) + 1):
        # Check time before starting next iteration
        if tm.expired():
            break
        
        # Run search at this depth
        score = alpha_beta(board, depth, -MATE_SCORE, MATE_SCORE, state, ply=0)
        nodes = state.nodes
        depth_reached = depth
        best_score = score
        
        # Try to get best move from TT
        try:
            entry = state.tt.probe(getattr(board, 'zobrist_key', 0))
            if entry is not None and entry.best_move is not None:
                best_move = entry.best_move
        except Exception:
            pass

        # Check time after search
        if tm.expired():
            break

    result = {
        'best_move': best_move,
        'score': best_score,
        'depth': depth_reached,
        'nodes': nodes,
        'pv': pv.get_root(),
    }
    return result
