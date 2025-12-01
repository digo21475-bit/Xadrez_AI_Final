"""Base agent interface for Xadrez_AI_Final."""
from abc import ABC, abstractmethod
from typing import Optional, Any


class Agent(ABC):
    """Abstract base class for game agents.
    
    An agent decides what move to make from a given board state.
    """

    @abstractmethod
    async def get_move(self, board: Any) -> Optional[object]:
        """Decide and return a move for the given board state.
        
        Args:
            board: core.board.Board instance representing current position.
        
        Returns:
            Move object (core.moves.move.Move) or None if no legal move.
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """Return a human-readable name for this agent."""
        pass
