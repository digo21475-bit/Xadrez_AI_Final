"""Search package exports.

Exports some convenience symbols used by other modules/tests.
"""
from .iterative import search_root
# prefer the existing alphabeta implementation for alpha_beta/SearchState
from .alphabeta import alpha_beta, SearchState
# helper utilities implemented in impl (if present)
try:
    from .impl import build_pv_from_tt, SearchController
except Exception:
    # impl may not exist in some states; fall back to minimal stubs
    def build_pv_from_tt(board, tt, max_depth=64):
        return []

    class SearchController:
        def __init__(self):
            self.stop = False

__all__ = ["search_root", "alpha_beta", "SearchState", "build_pv_from_tt", "SearchController"]
