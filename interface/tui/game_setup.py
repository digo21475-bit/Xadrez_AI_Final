"""
Game setup screen for selecting player types (Human, Random, Engine)
"""

from textual.app import ComposeResult
from textual.widgets import Static, RadioButton, RadioSet, Button
from textual.containers import Container, Vertical
from textual.message import Message
from rich.panel import Panel
from rich.text import Text


class GameSetupScreen(Static):
    """Screen for configuring player types for White and Black"""
    
    DEFAULT_CSS = """
    GameSetupScreen {
        width: 1fr;
        height: 1fr;
        align: center middle;
        background: $surface;
    }
    
    .setup_container {
        width: 60;
        height: auto;
        border: thick $accent;
        padding: 1 2;
    }
    
    .player_section {
        width: 1fr;
        height: auto;
        margin: 1 0;
    }
    
    .section_title {
        width: 1fr;
        height: auto;
        margin: 1 0 0 0;
    }
    
    .button_group {
        width: 1fr;
        height: auto;
        margin: 2 0 0 0;
        layout: horizontal;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.white_player = "human"
        self.black_player = "human"
        self.setup_done = False
    
    def compose(self) -> ComposeResult:
        with Container(classes="setup_container"):
            # Title
            yield Static(
                Text("===== Configuração da Partida =====", style="bold cyan"),
                classes="section_title"
            )
            
            # White Player Section
            yield Static(
                Text("\nSelecione o tipo de jogador das BRANCAS:", style="bold yellow"),
                classes="section_title"
            )
            
            with RadioSet(id="white_player"):
                yield RadioButton("Humano", id="white_human", value=True)
                yield RadioButton("Random", id="white_random")
                yield RadioButton("Engine", id="white_engine")
            
            # Black Player Section
            yield Static(
                Text("\nSelecione o tipo de jogador das PRETAS:", style="bold yellow"),
                classes="section_title"
            )
            
            with RadioSet(id="black_player"):
                yield RadioButton("Humano", id="black_human", value=True)
                yield RadioButton("Random", id="black_random")
                yield RadioButton("Engine", id="black_engine")
            
            # Buttons
            with Container(classes="button_group"):
                yield Button("Iniciar", id="btn_start", variant="primary")
                yield Button("Cancelar", id="btn_cancel")
    
    def on_mount(self) -> None:
        """Set initial selection to Human vs Human"""
        # The RadioButtons are set to value=True in compose, so they're already selected
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Track radio button changes"""
        # Get the pressed button from the radio set
        radio_set = event.control
        
        if radio_set.id == "white_player":
            # Check which radio button is pressed
            for i, button in enumerate(radio_set.query("RadioButton")):
                if button.value:
                    if i == 0:
                        self.white_player = "human"
                    elif i == 1:
                        self.white_player = "random"
                    elif i == 2:
                        self.white_player = "engine"
                    break
        
        elif radio_set.id == "black_player":
            for i, button in enumerate(radio_set.query("RadioButton")):
                if button.value:
                    if i == 0:
                        self.black_player = "human"
                    elif i == 1:
                        self.black_player = "random"
                    elif i == 2:
                        self.black_player = "engine"
                    break
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "btn_start":
            self.setup_done = True
            self.post_message(self.GameSetupComplete(self.white_player, self.black_player))
        elif event.button.id == "btn_cancel":
            # Reset to default
            self.setup_done = False
            self.post_message(self.GameSetupCancelled())
    
    class GameSetupComplete(Message):
        """Message sent when game setup is complete"""
        def __init__(self, white_player: str, black_player: str):
            super().__init__()
            self.white_player = white_player
            self.black_player = black_player
    
    class GameSetupCancelled(Message):
        """Message sent when setup is cancelled"""
        pass
