"""Controles (botões)."""
import pygame
from interface.gui.config import BUTTON_BG, BUTTON_HOVER, TEXT_COLOR, FONT_SIZE_NORMAL


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.hovered = False

    def draw(self, surf):
        color = BUTTON_HOVER if self.hovered else BUTTON_BG
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, TEXT_COLOR, self.rect, 2)
        
        txt = self.font.render(self.text, True, TEXT_COLOR)
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

    def on_click(self, x, y):
        return self.rect.collidepoint(x, y)

    def on_motion(self, x, y):
        self.hovered = self.rect.collidepoint(x, y)


class ControlPanel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.buttons = {
            'start': Button(x, y, 100, 40, 'Start'),
            'pause': Button(x + 110, y, 100, 40, 'Pause'),
            'undo': Button(x + 220, y, 100, 40, 'Undo'),
            'new': Button(x + 330, y, 100, 40, 'New Game'),
        }

    def draw(self, surf):
        for btn in self.buttons.values():
            btn.draw(surf)

    def on_click(self, x, y):
        for name, btn in self.buttons.items():
            if btn.on_click(x, y):
                return name
        return None

    def on_motion(self, x, y):
        for btn in self.buttons.values():
            btn.on_motion(x, y)
