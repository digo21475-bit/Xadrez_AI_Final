"""Game manager: orchestrates a chess match with two agents."""
from typing import Optional, Dict, Any, Callable
from enum import Enum
from agents import Agent, HumanAgent, RandomAgent, EngineAgent
from core.board.board import Board
from utils.enums import Color


class GameMode(Enum):
    """Predefined game modes."""
    HUMAN_VS_HUMAN = "human_vs_human"
    HUMAN_VS_RANDOM = "human_vs_random"
    HUMAN_VS_ENGINE = "human_vs_engine"
    RANDOM_VS_RANDOM = "random_vs_random"
    RANDOM_VS_ENGINE = "random_vs_engine"
    ENGINE_VS_ENGINE = "engine_vs_engine"


class GameManager:
    """Manages a single chess game with two agents."""

    def __init__(
        self,
        white_agent: Agent,
        black_agent: Agent,
        board: Optional[Board] = None,
        on_move_callback: Optional[Callable] = None
    ):
        """Initialize game manager.
        
        Args:
            white_agent: Agent controlling White.
            black_agent: Agent controlling Black.
            board: Board instance (default: starting position).
            on_move_callback: optional async callback called after each move.
                callback(move, board, is_white_move).
        """
        self.white_agent = white_agent
        self.black_agent = black_agent
        self.board = board or Board()
        self.on_move_callback = on_move_callback
        self.game_over = False
        self.termination_reason = None
        self.pending_move: Optional[object] = None  # for human input

    def set_pending_move(self, move: object) -> None:
        """Set move for human player (called by TUI event handler)."""
        self.pending_move = move

    @classmethod
    def from_mode(
        cls,
        mode: GameMode,
        engine_depth: int = 3,
        engine_time_ms: int = 1000,
        board: Optional[Board] = None
    ) -> "GameManager":
        """Create a GameManager from a predefined mode.
        
        Args:
            mode: GameMode enum value.
            engine_depth: depth for engine agents.
            engine_time_ms: time budget for engine agents.
            board: Board instance (default: starting position).
        
        Returns:
            GameManager instance with appropriate agents.
        """
        agents_map = {
            GameMode.HUMAN_VS_HUMAN: (HumanAgent(), HumanAgent()),
            GameMode.HUMAN_VS_RANDOM: (HumanAgent(), RandomAgent()),
            GameMode.HUMAN_VS_ENGINE: (HumanAgent(), EngineAgent(engine_time_ms, engine_depth)),
            GameMode.RANDOM_VS_RANDOM: (RandomAgent(), RandomAgent()),
            GameMode.RANDOM_VS_ENGINE: (RandomAgent(), EngineAgent(engine_time_ms, engine_depth)),
            GameMode.ENGINE_VS_ENGINE: (EngineAgent(engine_time_ms, engine_depth), EngineAgent(engine_time_ms, engine_depth)),
        }
        white, black = agents_map.get(mode, (HumanAgent(), HumanAgent()))
        return cls(white, black, board=board)

    def get_agent_for_side(self, color: Color) -> Agent:
        """Get the agent for the given color."""
        return self.white_agent if color == Color.WHITE else self.black_agent

    async def play_move(self, move: object) -> None:
        """Execute a move on the board.
        
        Args:
            move: Move object to play.
        """
        if move is None:
            self.game_over = True
            self.termination_reason = "Invalid move (None)"
            return

        try:
            self.board.make_move(move)
            is_white = self.board.side_to_move == Color.BLACK  # moved to opposite
            if self.on_move_callback:
                await self.on_move_callback(move, self.board, is_white)
        except Exception as e:
            self.game_over = True
            self.termination_reason = f"Move error: {e}"

    async def get_next_move(self) -> Optional[object]:
        """Get the next move from the current side's agent.
        
        Returns:
            Move object or None if agent cannot produce move.
        """
        color = self.board.side_to_move
        agent = self.get_agent_for_side(color)

        if isinstance(agent, HumanAgent):
            # For human, return pending move (set by TUI)
            # The game loop should check this before calling get_next_move
            return self.pending_move
        else:
            # For AI agents, call get_move
            return await agent.get_move(self.board)

    def check_game_over(self) -> bool:
        """Check if game is over (mate, stalemate, draw).
        
        Returns:
            True if game is over, False otherwise.
        """
        try:
            from core.moves.legal_movegen import generate_legal_moves
            from core.rules.game_status import get_game_status

            moves = list(generate_legal_moves(self.board))
            if not moves:
                status = get_game_status(self.board)
                if status.is_checkmate:
                    self.termination_reason = "Checkmate"
                    self.game_over = True
                    return True
                if status.is_stalemate:
                    self.termination_reason = "Stalemate"
                    self.game_over = True
                    return True
                self.termination_reason = "No legal moves"
                self.game_over = True
                return True

            if status.is_draw_by_fifty_move:
                self.termination_reason = "50-move rule"
                self.game_over = True
                return True

            if status.is_draw_by_repetition:
                self.termination_reason = "Repetition"
                self.game_over = True
                return True

            if status.is_insufficient_material:
                self.termination_reason = "Insufficient material"
                self.game_over = True
                return True

        except Exception:
            pass

        return False

    def get_result(self) -> Dict[str, Any]:
        """Get game result summary.
        
        Returns:
            Dict with keys: mode, white_agent, black_agent, result, reason, fullmove.
        """
        return {
            "white_agent": self.white_agent.name(),
            "black_agent": self.black_agent.name(),
            "result": "?" if not self.game_over else "Draw" if "draw" in (self.termination_reason or "").lower() else "?",
            "reason": self.termination_reason,
            "fullmove": self.board.fullmove_number,
        }
