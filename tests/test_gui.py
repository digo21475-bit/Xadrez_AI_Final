"""Testes da GUI pygame."""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock pygame
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()
sys.modules['pygame.display'] = MagicMock()

from interface.gui.config import MODES, TILE_SIZE
from interface.gui.screens.gameover import GameOverScreen


class TestModes:
    def test_six_modes(self):
        assert len(MODES) == 6

    def test_mode_random_vs_random(self):
        assert MODES["Random vs Random"] == ("random", "random")


class TestGameOverCountdown:
    def test_countdown_3s(self):
        screen = GameOverScreen()
        screen.set_result("white_win", "Checkmate")
        assert screen.countdown == 3
        
        screen.tick(1500)  # 1.5s
        assert 1.4 < screen.countdown < 1.6
        
        # total 3.5s deve resetar
        done = screen.tick(2100)
        assert done is True
        assert screen.result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

