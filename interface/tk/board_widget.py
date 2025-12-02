"""Canvas-based chess board widget for Tk.

Provides a simple drawing of an 8x8 board and click handling.
"""
from __future__ import annotations
import os
try:
    import tkinter as tk
except Exception:  # pragma: no cover
    tk = None
try:
    # Prefer Pillow for robust PNG handling in Tk
    from PIL import Image as PILImage, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


class BoardWidget(tk.Canvas if tk is not None else object):
    """Simple board widget implemented as a `tk.Canvas`.

    Public methods:
    - draw_board(): draw squares
    - set_position(position): update internal position and redraw pieces (placeholder)
    - coord_to_square(x, y): canvas coords -> (file, rank)
    """

    LIGHT = '#F0D9B5'
    DARK = '#B58863'

    def __init__(self, parent, square_size: int = 48, rows: int = 8, cols: int = 8, **kwargs):
        if tk is None:
            raise RuntimeError('tkinter not available')

        width = cols * square_size
        height = rows * square_size
        super().__init__(parent, width=width, height=height, **kwargs)
        self.square_size = square_size
        self.rows = rows
        self.cols = cols
        self.position = None
        self._drawn = False
        self.bind('<Button-1>', self._on_click)
        self.draw_board()
        # prepare image cache for piece PNGs
        self._image_cache: dict[str, 'tk.PhotoImage'] = {}
        # preload piece images (may be lazy-loaded on first draw)
        self._pieces_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'pieces'))
        # optional external click callback: receives square index 0..63
        self._click_callback = None
        # selection state for simple human move entry
        self._selected_from: int | None = None


    def draw_board(self):
        """Draw the 8x8 chessboard squares."""
        self.delete('square')
        s = self.square_size
        for r in range(self.rows):
            for c in range(self.cols):
                x0 = c * s
                y0 = r * s
                x1 = x0 + s
                y1 = y0 + s
                color = self.LIGHT if (r + c) % 2 == 0 else self.DARK
                self.create_rectangle(x0, y0, x1, y1, fill=color, outline='', tags='square')
        self._drawn = True

    def set_position(self, position):
        """Set the internal `position` and redraw pieces (placeholder).

        `position` may be any representation. For now this is a placeholder.
        """
        self.position = position
        # clear previous piece drawings
        self.delete('piece')
        try:
            # if position is None, create a fresh board
            if position is None:
                try:
                    from core.board.board import Board
                    board = Board()
                except Exception:
                    board = None
            else:
                board = position

            if board is None:
                return

            # draw pieces from board.mailbox (A1=0..H8=63). We map to canvas coords: file 0..7 col, rank 0..7 row (A1 bottom-left)
            # Our canvas origin is top-left; rank 0 (A1) maps to bottom row. We'll render with rank inverted.
            piece_map = {
                # PieceType -> (white_symbol, black_symbol)
                0: ('♙', '♟'),  # PAWN
                1: ('♘', '♞'),  # KNIGHT
                2: ('♗', '♝'),  # BISHOP
                3: ('♖', '♜'),  # ROOK
                4: ('♕', '♛'),  # QUEEN
                5: ('♔', '♚'),  # KING
            }

            for sq in range(64):
                cell = board.get_piece_at(sq)
                if cell is None:
                    continue
                color, piece_type = cell
                # piece_type is PieceType enum; convert to int/name
                try:
                    pt = int(piece_type)
                except Exception:
                    pt = int(piece_type)

                # map integer piece types to names used in assets
                type_map = {
                    0: 'pawn',
                    1: 'knight',
                    2: 'bishop',
                    3: 'rook',
                    4: 'queen',
                    5: 'king',
                }
                pname = type_map.get(pt)
                if pname is None:
                    continue

                # determine color name: NOTE: keep explicit 'white'/'black' to avoid ambiguity
                color_name = 'white' if int(color) == 0 else 'black'

                file = sq % 8
                rank = sq // 8
                # invert rank for canvas (rank 0 -> bottom)
                canvas_row = 7 - rank
                cx = int(file * self.square_size + self.square_size / 2)
                cy = int(canvas_row * self.square_size + self.square_size / 2)

                # load image for this piece (cached)
                img = self._get_piece_image(color_name, pname)
                if img is None:
                    # fallback: draw a text marker
                    glyph = '?' if color_name == 'white' else 'x'
                    self.create_text(cx, cy, text=glyph, tags='piece', fill='black')
                else:
                    self.create_image(cx, cy, image=img, tags=('piece',), anchor='center')
        except Exception as e:
            # on any error, print and fallback to placeholder
            print('[BoardWidget] error drawing pieces:', e)

    def _get_piece_image(self, color_name: str, pname: str):
        """Return a Tk image object for the given piece name, scaled to square_size.

        Caches results in `self._image_cache` to avoid reloading.
        """
        key = f"{color_name}_{pname}_{self.square_size}"
        if key in self._image_cache:
            return self._image_cache[key]

        # candidate file: assets/pieces/white_pawn.png etc.
        fname = os.path.join(self._pieces_dir, f"{color_name}_{pname}.png")
        if not os.path.exists(fname):
            return None

        try:
            if PIL_AVAILABLE:
                pil = PILImage.open(fname).convert('RGBA')
                pil = pil.resize((self.square_size, self.square_size), PILImage.LANCZOS)
                # Recolor using alpha mask: fill silhouette with target color to guarantee
                # white pieces appear light regardless of source artwork.
                alpha = pil.split()[-1]
                if color_name == 'white':
                    base = PILImage.new('RGBA', pil.size, (240, 240, 240, 255))
                else:
                    base = PILImage.new('RGBA', pil.size, (10, 10, 10, 255))
                base.putalpha(alpha)
                tkimg = ImageTk.PhotoImage(base)
            else:
                # rely on Tk's PhotoImage (may or may not support PNG in all builds)
                tkimg = tk.PhotoImage(file=fname)
            # store strong reference
            self._image_cache[key] = tkimg
            return tkimg
        except Exception:
            return None

    def coord_to_square(self, x: int, y: int) -> tuple[int, int]:
        """Convert canvas coordinates to (file, rank) 0-based."""
        c = int(x // self.square_size)
        r = int(y // self.square_size)
        return c, r

    def _on_click(self, event):
        file, rank = self.coord_to_square(event.x, event.y)
        # convert file,rank (0..7) to square index A1=0..H8=63 (rank 0 = A1)
        sq = rank * 8 + file
        # notify callback if present
        try:
            if self._click_callback:
                self._click_callback(sq)
        except Exception:
            pass

        # debug print
        print(f'[BoardWidget] click at canvas ({event.x},{event.y}) -> square {file,rank} -> idx {sq}')

    def set_click_callback(self, cb):
        """Set a callback to receive square index (0..63) on user clicks.

        Callback signature: cb(square_index: int)
        """
        self._click_callback = cb
