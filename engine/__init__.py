"""Chess engine: iterative deepening alpha-beta search with transposition table.

Main entry point is search_root(board, max_time_ms, max_depth) which returns
a dictionary with best_move, score, depth, nodes, and pv.

Example:
	from engine import search_root
	result = search_root(board, max_time_ms=1000, max_depth=8)
	best_move = result['best_move']
"""
from . import search
from .iterdeep import search_root

__all__ = ["search_root", "search"]

