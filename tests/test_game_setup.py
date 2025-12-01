#!/usr/bin/env python3
"""
Test script for the new game setup screen
Run with: /path/to/venv/bin/python test_game_setup.py
"""

from interface.tui.game_setup import GameSetupScreen
from textual.app import App, ComposeResult


class TestSetupApp(App):
    """Simple test app for the game setup screen"""
    
    def compose(self) -> ComposeResult:
        yield GameSetupScreen()
    
    def on_game_setup_screen_game_setup_complete(self, event) -> None:
        """Handle setup completion"""
        print(f"\nGame setup complete!")
        print(f"White: {event.white_player}")
        print(f"Black: {event.black_player}")
        self.exit()
    
    def on_game_setup_screen_game_setup_cancelled(self, event) -> None:
        """Handle setup cancellation"""
        print("\nGame setup cancelled")
        self.exit()


if __name__ == "__main__":
    app = TestSetupApp()
    app.run()
