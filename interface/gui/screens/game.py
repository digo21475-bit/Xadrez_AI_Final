"""Tela de jogo (tabuleiro + controles)."""
import pygame
from interface.gui.config import (
    BG_COLOR, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, SCOREBOARD_WIDTH,
    TEXT_COLOR, FONT_SIZE_NORMAL
)
from interface.gui.widgets.board import BoardWidget
from interface.gui.widgets.scoreboard import Scoreboard
from interface.gui.widgets.controls import ControlPanel


class GameScreen:
    def __init__(self, board, white_type, black_type):
        self.board = board
        self.white_type = white_type
        self.black_type = black_type
        
        self.board_widget = BoardWidget(board, 10, 10)
        self.scoreboard = Scoreboard(
            SCREEN_WIDTH - SCOREBOARD_WIDTH - 10, 10,
            SCOREBOARD_WIDTH - 20, 200
        )
        self.controls = ControlPanel(10, SCREEN_HEIGHT - 60)
        
        self.font_normal = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.move_history = []
        self.paused = False

    def draw(self, surf):
        surf.fill(BG_COLOR)
        
        # tabuleiro
        self.board_widget.draw(surf)
        
        # scoreboard
        self.scoreboard.draw(surf)
        
        # info
        y = 10 + 8 * TILE_SIZE + 20
        txt = self.font_normal.render(
            f"White: {self.white_type} | Black: {self.black_type}",
            True, TEXT_COLOR
        )
        surf.blit(txt, (10, y))
        
        # histórico de movimentos (últimas linhas)
        if self.move_history:
            moves_text = " ".join(self.move_history[-10:])
            txt = self.font_normal.render(f"Moves: {moves_text}", True, TEXT_COLOR)
            surf.blit(txt, (10, y + 30))
        
        # status paused
        if self.paused:
            txt = self.font_normal.render("PAUSED", True, (255, 0, 0))
            surf.blit(txt, (SCREEN_WIDTH // 2 - 40, 20))
        
        # controles
        self.controls.draw(surf)

    def add_move(self, move_uci):
        self.move_history.append(move_uci)

    def on_control_click(self, x, y):
        """Retorna o nome do controle clicado."""
        return self.controls.on_click(x, y)

    def on_board_click(self, x, y):
        """Retorna o índice do quadrado."""
        return self.board_widget.on_click(x, y)

    def on_motion(self, x, y):
        self.controls.on_motion(x, y)
