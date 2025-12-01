"""Tela de fim de jogo com auto-reset."""
import pygame
from interface.gui.config import BG_COLOR, TEXT_COLOR, FONT_SIZE_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT


class GameOverScreen:
    def __init__(self):
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        self.font_normal = pygame.font.Font(None, 20)
        self.result = None
        self.reason = None
        self.countdown = 0  # segundos até auto-reset

    def set_result(self, result, reason=""):
        """result: 'white_win' | 'black_win' | 'draw'"""
        self.result = result
        self.reason = reason
        self.countdown = 3  # 3 segundos

    def draw(self, surf):
        if not self.result:
            return False  # não exibir
        
        surf.fill((0, 0, 0))
        
        # resultado
        result_text = {
            'white_win': 'WHITE WINS!',
            'black_win': 'BLACK WINS!',
            'draw': 'DRAW',
        }.get(self.result, '?')
        
        txt = self.font_title.render(result_text, True, TEXT_COLOR)
        surf.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 150))
        
        # motivo
        if self.reason:
            txt = self.font_normal.render(f"Reason: {self.reason}", True, TEXT_COLOR)
            surf.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 250))
        
        # countdown
        txt = self.font_normal.render(f"Restarting in {self.countdown}s...", True, TEXT_COLOR)
        surf.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 350))
        
        return True

    def tick(self, dt):
        """Decrementa o countdown. Retorna True se deve reiniciar."""
        if not self.result:
            return False
        self.countdown -= dt / 1000  # dt em ms
        if self.countdown <= 0:
            self.result = None
            return True
        return False

    def clear(self):
        self.result = None
        self.reason = None
        self.countdown = 0
