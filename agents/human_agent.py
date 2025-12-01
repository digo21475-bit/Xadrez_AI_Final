"""Human agent: awaits user input to decide moves."""
from typing import Optional, Any
from .agent_base import Agent


class HumanAgent(Agent):
    """Agent controlled by a human player.
    
    Awaits LAN/UCI input from stdin or external input mechanism.
    """

    def __init__(self, input_handler=None):
        """Initialize HumanAgent.
        
        Args:
            input_handler: optional callable that returns a move (for testing/mocking).
        """
        self.input_handler = input_handler

    async def get_move(self, board: Any) -> Optional[object]:
        """Wait for human input and return the move.
        
        In a real TUI, this would be handled by the event loop
        and the move would be injected via set_pending_move() or similar.
        
        Args:
            board: current board state (used for validation if needed).
        
        Returns:
            Move object or None.
        """
        # In the TUI integration, the human agent will be handled specially:
        # - TUI waits for input in a separate event handler
        # - When move is ready, the game loop continues
        # For now, this is a placeholder that can be overridden or handled
        # via a pending_move mechanism in the game manager.
        if self.input_handler:
            return await self.input_handler(board)
        return None

    def name(self) -> str:
        return "Human"
