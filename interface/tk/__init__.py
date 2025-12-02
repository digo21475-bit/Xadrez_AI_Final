"""Simple Tkinter-based GUI package for Xadrez_AI_Final.

This module exposes a minimal Tk-based application, board widget and control panel.
"""
from .app import TkChessApp
from .board_widget import BoardWidget
from .control_panel import ControlPanel
from .start_screen import StartScreen

__all__ = ["TkChessApp", "BoardWidget", "ControlPanel", "StartScreen"]
