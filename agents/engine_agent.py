"""Engine agent: uses chess engine (alpha-beta + iterative deepening)."""
import asyncio
from typing import Optional, Any
from .agent_base import Agent


class EngineAgent(Agent):
    """Agent using the Xadrez_AI_Final chess engine.
    
    Calls engine.search_root() with configurable time and depth limits.
    """

    def __init__(self, max_time_ms: int = 1000, max_depth: int = 3):
        """Initialize EngineAgent.
        
        Args:
            max_time_ms: time budget in milliseconds.
            max_depth: maximum search depth.
        """
        self.max_time_ms = max_time_ms
        self.max_depth = max_depth

    async def get_move(self, board: Any) -> Optional[object]:
        """Use engine to decide move.
        
        Args:
            board: current board state.
        
        Returns:
            Best move found by engine or None if search failed.
        """
        try:
            from engine import search_root
            from core.moves.legal_movegen import generate_legal_moves

            def _run_search(b, t, d):
                return search_root(b, max_time_ms=t, max_depth=d)

            bcopy = board.copy() if hasattr(board, 'copy') else board
            # Python 3.8 compatible: use run_in_executor instead of to_thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _run_search, bcopy, self.max_time_ms, self.max_depth)
            
            if isinstance(result, dict):
                best_move = result.get('best_move')
                if best_move:
                    return best_move
                
                # Fallback: se engine nao retornar move, usar primeiro legal move
                try:
                    moves = list(generate_legal_moves(bcopy))
                    if moves:
                        return moves[0]
                except:
                    pass
            
            return None
        except Exception:
            return None

    def name(self) -> str:
        return f"Engine (d={self.max_depth}, t={self.max_time_ms}ms)"
