"""Tela de configuração (seleção de modos)."""
import pygame
from interface.gui.config import (
    BG_COLOR, BUTTON_BG, BUTTON_HOVER, TEXT_COLOR, FONT_SIZE_TITLE,
    SCREEN_WIDTH, SCREEN_HEIGHT, MODES
)


class SetupScreen:
    def __init__(self):
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        self.font_normal = pygame.font.Font(None, 18)
        self.selected_mode = None
        self.buttons = {}
        
        # criar botões para cada modo
        y = 100
        for mode_name in MODES.keys():
            self.buttons[mode_name] = {
                'rect': pygame.Rect(150, y, 700, 50),
                'name': mode_name,
            }
            y += 70

    def draw(self, surf):
        surf.fill(BG_COLOR)
        
        # título
        txt = self.font_title.render("SELECT GAME MODE", True, TEXT_COLOR)
        surf.blit(txt, (150, 30))
        
        # botões
        for mode_name, btn in self.buttons.items():
            color = BUTTON_HOVER if mode_name == self.selected_mode else BUTTON_BG
            pygame.draw.rect(surf, color, btn['rect'])
            pygame.draw.rect(surf, TEXT_COLOR, btn['rect'], 2)
            
            txt = self.font_normal.render(mode_name, True, TEXT_COLOR)
            txt_rect = txt.get_rect(center=btn['rect'].center)
            surf.blit(txt, txt_rect)

    def on_click(self, x, y):
        """Retorna o modo selecionado, ou None."""
        for mode_name, btn in self.buttons.items():
            if btn['rect'].collidepoint(x, y):
                return mode_name
        return None

    def on_motion(self, x, y):
        """Atualiza hover."""
        for mode_name, btn in self.buttons.items():
            if btn['rect'].collidepoint(x, y):
                self.selected_mode = mode_name
                return
        self.selected_mode = None
