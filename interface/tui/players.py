"""Player adapters for TUI autoplay.

Provides a `choose_move(name, board, max_time_ms, max_depth)` helper that
returns a Move-like object compatible with `core.board.Board.make_move()`.

If `name` is 'engine' or 'search', it calls the engine search implementation.
If `name` refers to a Python module with `choose_move(board)` it will import
and call it. Otherwise returns None.
"""
from typing import Optional
import asyncio


async def choose_move(name: str, board, max_time_ms: int = 1000, max_depth: int = 1) -> Optional[object]:
    """Asynchronous helper to choose a move by name.

    This offloads CPU-heavy or synchronous implementations to a thread using
    ``asyncio.to_thread`` and passes a copy of the board to avoid concurrent
    mutation issues with the UI.
    """
    name = (name or '').lower()
    # direct engine integration
    if name in ("engine", "search", "search_engine"):
        try:
            from engine import search_root

            def _run_search(b, t, d):
                return search_root(b, max_time_ms=t, max_depth=d)

            # Use a board copy to avoid races with the UI thread
            bcopy = board.copy() if hasattr(board, 'copy') else board
            res = await asyncio.to_thread(_run_search, bcopy, max_time_ms, max_depth)
            return res.get('best_move') if isinstance(res, dict) else None
        except Exception:
            return None

    # try to import module by name and call choose_move(board) in thread
    try:
        mod = __import__(name)
        if hasattr(mod, 'choose_move'):
            try:
                func = getattr(mod, 'choose_move')

                # run possibly-sync choose_move in thread
                bcopy = board.copy() if hasattr(board, 'copy') else board
                return await asyncio.to_thread(func, bcopy)
            except Exception:
                return None
    except Exception:
        return None

    return None
