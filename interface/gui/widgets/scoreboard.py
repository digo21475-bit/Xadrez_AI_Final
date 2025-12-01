"""Placar persistente."""
import pygame
from interface.gui.config import BUTTON_BG, TEXT_COLOR, FONT_SIZE_NORMAL


class Scoreboard:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.white_wins = 0
        self.black_wins = 0
        self.draws = 0
        self.font_title = pygame.font.Font(None, 20)
        self.font_normal = pygame.font.Font(None, 16)

    def draw(self, surf):
        # painel
        pygame.draw.rect(surf, BUTTON_BG, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surf, TEXT_COLOR, (self.x, self.y, self.width, self.height), 2)
        
        y_off = self.y + 10
        x_off = self.x + 10
        
        # título
        txt = self.font_title.render("SCOREBOARD", True, TEXT_COLOR)
        surf.blit(txt, (x_off, y_off))
        y_off += 30
        
        # stats
        stats = [
            f"White Wins: {self.white_wins}",
            f"Black Wins: {self.black_wins}",
            f"Draws: {self.draws}",
        ]
        for stat in stats:
            txt = self.font_normal.render(stat, True, TEXT_COLOR)
            surf.blit(txt, (x_off, y_off))
            y_off += 25

    def record_win(self, side):
        if side == 0:  # White
            self.white_wins += 1
        else:  # Black
            self.black_wins += 1

    def record_draw(self):
        self.draws += 1
