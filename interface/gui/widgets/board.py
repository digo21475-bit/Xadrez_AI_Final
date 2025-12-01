"""Renderização do tabuleiro em pygame."""
import pygame
import os
from pathlib import Path
from interface.gui.config import TILE_SIZE, LIGHT_SQ, DARK_SQ, SELECTED_SQ, TEXT_COLOR

try:
    from utils.enums import Color, PieceType
    PIECE_UNICODE = {
        PieceType.PAWN: ('♙', '♟'),
        PieceType.KNIGHT: ('♘', '♞'),
        PieceType.BISHOP: ('♗', '♝'),
        PieceType.ROOK: ('♖', '♜'),
        PieceType.QUEEN: ('♕', '♛'),
        PieceType.KING: ('♔', '♚'),
    }
    PIECE_NAMES = {
        PieceType.PAWN: 'pawn',
        PieceType.KNIGHT: 'knight',
        PieceType.BISHOP: 'bishop',
        PieceType.ROOK: 'rook',
        PieceType.QUEEN: 'queen',
        PieceType.KING: 'king',
    }
except:
    Color = type('Color', (), {'WHITE': 0, 'BLACK': 1})
    PieceType = type('PieceType', (), {
        'PAWN': 0, 'KNIGHT': 1, 'BISHOP': 2, 'ROOK': 3, 'QUEEN': 4, 'KING': 5
    })
    PIECE_UNICODE = {
        0: ('♙', '♟'),
        1: ('♘', '♞'),
        2: ('♗', '♝'),
        3: ('♖', '♜'),
        4: ('♕', '♛'),
        5: ('♔', '♚'),
    }
    PIECE_NAMES = {
        0: 'pawn', 1: 'knight', 2: 'bishop', 3: 'rook', 4: 'queen', 5: 'king'
    }


class BoardWidget:
    def __init__(self, board, x=0, y=0):
        self.board = board
        self.x = x
        self.y = y
        self.selected_sq = None
        self.font = pygame.font.Font(None, int(TILE_SIZE * 0.8))
        self.piece_images = {}
        self._load_piece_images()

    def _load_piece_images(self):
        """Carrega PNGs das peças de assets/."""
        base_path = Path(__file__).parent.parent.parent.parent / "assets"
        
        for color_name, color_code in [('w', Color.WHITE), ('b', Color.BLACK)]:
            for piece_type, piece_name in PIECE_NAMES.items():
                fname = base_path / f"{color_name}_{piece_name}.png"
                if fname.exists():
                    try:
                        img = pygame.image.load(str(fname))
                        img = pygame.transform.scale(img, (TILE_SIZE - 4, TILE_SIZE - 4))
                        self.piece_images[(color_code, piece_type)] = img
                    except Exception as e:
                        print(f"Erro ao carregar {fname}: {e}")

    def draw(self, surf):
        for rank in range(8):
            for file in range(8):
                sq = rank * 8 + file
                rect = pygame.Rect(
                    self.x + file * TILE_SIZE,
                    self.y + (7 - rank) * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                
                # cor do quadrado
                is_light = (rank + file) % 2 == 0
                color = LIGHT_SQ if is_light else DARK_SQ
                if sq == self.selected_sq:
                    color = SELECTED_SQ
                pygame.draw.rect(surf, color, rect)
                pygame.draw.rect(surf, (100, 100, 100), rect, 1)
                
                # peça
                cell = self.board.mailbox[sq]
                if cell:
                    color_idx, ptype = cell
                    
                    # Tentar usar PNG
                    img = self.piece_images.get((color_idx, ptype))
                    if img:
                        img_rect = img.get_rect(center=rect.center)
                        surf.blit(img, img_rect)
                    else:
                        # Fallback: Unicode
                        if isinstance(ptype, int):
                            pair = PIECE_UNICODE.get(ptype, ('?', '?'))
                        else:
                            pair = PIECE_UNICODE.get(ptype, ('?', '?'))
                        ch = pair[0] if color_idx == Color.WHITE else pair[1]
                        
                        txt = self.font.render(ch, True, (0, 0, 0) if is_light else (255, 255, 255))
                        txt_rect = txt.get_rect(center=rect.center)
                        surf.blit(txt, txt_rect)

    def on_click(self, x, y):
        """Retorna o índice do quadrado clicado, ou -1."""
        if not (self.x <= x < self.x + 8 * TILE_SIZE and
                self.y <= y < self.y + 8 * TILE_SIZE):
            return -1
        file = (x - self.x) // TILE_SIZE
        rank = 7 - (y - self.y) // TILE_SIZE
        return rank * 8 + file


