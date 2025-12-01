"""Random agent: selects random legal moves."""
import random
import asyncio
import threading
from typing import Optional, Any
from .agent_base import Agent


class RandomAgent(Agent):
    """Agent that selects uniformly random legal moves."""

    async def get_move(self, board: Any) -> Optional[object]:
        """Select a random legal move.
        
        Args:
            board: current board state.
        
        Returns:
            Randomly selected Move object or None if no legal moves.
        """
        try:
            def _collect_moves(b):
                # Method 1: board.generate_legal_moves() (if it exists)
                try:
                    return list(b.generate_legal_moves())
                except (AttributeError, Exception):
                    pass
                
                # Method 2: core.moves.legal_movegen.generate_legal_moves(b)
                try:
                    from core.moves.legal_movegen import generate_legal_moves
                    return list(generate_legal_moves(b))
                except Exception:
                    pass
                
                return []

            # Python 3.8 compatible: use run_in_executor instead of to_thread
            loop = asyncio.get_event_loop()
            moves = await loop.run_in_executor(None, _collect_moves, board)
            return random.choice(moves) if moves else None
        except Exception:
            return None

    def name(self) -> str:
        return "Random"
