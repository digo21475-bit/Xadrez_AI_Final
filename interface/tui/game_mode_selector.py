"""TUI widgets for game mode selection and game info display."""
from textual.widgets import Static, Button, Container
from textual.containers import Grid
from rich.panel import Panel
from rich.text import Text
from game_manager import GameMode


class GameModeSelector(Container):
    """Widget to select game mode before starting a game."""

    DEFAULT_CSS = """
    GameModeSelector {
        border: solid $accent;
        height: auto;
    }

    GameModeSelector Button {
        margin: 0 1;
    }

    #game_mode_grid {
        grid-size: 2 3;
        width: 100%;
    }
    """

    def __init__(self):
        super().__init__()
        self.selected_mode: GameMode | None = None
        self.modes = [
            GameMode.HUMAN_VS_HUMAN,
            GameMode.HUMAN_VS_RANDOM,
            GameMode.HUMAN_VS_ENGINE,
            GameMode.RANDOM_VS_RANDOM,
            GameMode.RANDOM_VS_ENGINE,
            GameMode.ENGINE_VS_ENGINE,
        ]

    def compose(self):
        """Compose the mode selector grid."""
        yield Static("Select Game Mode:", id="mode_title")
        with Grid(id="game_mode_grid"):
            for mode in self.modes:
                label = mode.value.replace("_", " ").title()
                btn = Button(label, id=f"mode_{mode.value}")
                btn.data = mode
                yield btn

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle mode selection."""
        if event.button.id and event.button.id.startswith("mode_"):
            self.selected_mode = event.button.data
            self.post_message(self.ModeSelected(self.selected_mode))

    class ModeSelected(Container.ScreenResume):
        """Message sent when mode is selected."""
        def __init__(self, mode: GameMode):
            super().__init__()
            self.mode = mode


class GameInfoDisplay(Static):
    """Widget showing current game info: mode, agents, board state."""

    DEFAULT_CSS = """
    GameInfoDisplay {
        border: solid $accent;
        height: auto;
        padding: 1;
    }
    """

    def __init__(self, game_manager=None):
        super().__init__()
        self.game_manager = game_manager

    def render(self) -> str:
        """Render game info."""
        if not self.game_manager:
            return "[dim]No game in progress[/]"

        white_name = self.game_manager.white_agent.name()
        black_name = self.game_manager.black_agent.name()
        is_white_turn = self.game_manager.board.side_to_move.name == "WHITE"
        turn_indicator = "● White" if is_white_turn else "● Black"

        info = f"""
[bold]Game Info[/]
White: {white_name}
Black: {black_name}
Turn: {turn_indicator}
Fullmove: {self.game_manager.board.fullmove_number}
Status: {"Game Over - " + (self.game_manager.termination_reason or "Unknown") if self.game_manager.game_over else "In Progress"}
"""
        return info
