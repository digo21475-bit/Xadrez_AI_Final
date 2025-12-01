"""
Módulo de renderização para a TUI.

Contém as funções e widgets responsáveis por desenhar o tabuleiro
e os painéis (BoardPanel, StatusPanel, LogPanel). Estes eram
implementados dentro de `main.py` — foram extraídos para aqui para
separar responsabilidades.
"""
from __future__ import annotations

from textual.widgets import Static
from textual.reactive import reactive

from rich.table import Table
from rich.panel import Panel
from rich.text import Text
try:
    from rich.image import Image as RichImage
except Exception:
    RichImage = None

# Try to import Pillow for image-based board rendering
try:
    from PIL import Image as PILImage, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Tentar importar enums do projeto; caso falhe, definir substitutos
try:
    from utils.enums import PieceType, Color
    # Use Unicode chess symbols: (white, black)
    PIECE_UNICODE = {
        PieceType.PAWN:   ('♙', '♟'),
        PieceType.KNIGHT: ('♘', '♞'),
        PieceType.BISHOP: ('♗', '♝'),
        PieceType.ROOK:   ('♖', '♜'),
        PieceType.QUEEN:  ('♕', '♛'),
        PieceType.KING:   ('♔', '♚'),
    }
except Exception:
    class Color:
        WHITE = 0
        BLACK = 1

    class PieceType:
        PAWN = 0
        KNIGHT = 1
        BISHOP = 2
        ROOK = 3
        QUEEN = 4
        KING = 5

    PIECE_UNICODE = {
        PieceType.PAWN:   ('P', 'p'),
        PieceType.KNIGHT: ('N', 'n'),
        PieceType.BISHOP: ('B', 'b'),
        PieceType.ROOK:   ('R', 'r'),
        PieceType.QUEEN:  ('Q', 'q'),
        PieceType.KING:   ('K', 'k'),
    }


def render_board_ascii(board) -> Table:
    """
    Constrói um Rich.Table para exibir o tabuleiro ASCII (8x8).
    Necessita board.mailbox com 64 itens: None ou (color, pieceType).
    """
    # vertical padding is larger than horizontal to visually stretch rows
    tbl = Table.grid(padding=(1, 0))
    tbl.expand = True

    for rank in range(7, -1, -1):
        row = []
        for file in range(8):
            sq = rank * 8 + file
            cell = board.mailbox[sq]
            if cell is None:
                # use single-char cell for narrower horizontal footprint
                row.append(".")
            else:
                colr, ptype = cell
                # pick unicode symbol depending on color
                pair = PIECE_UNICODE.get(ptype, ('?', '?'))
                ch = pair[0] if colr == Color.WHITE else pair[1]
                if colr == Color.WHITE:
                    row.append(f"[bold]{ch}[/]")
                else:
                    row.append(f"[dim]{ch}[/]")
        tbl.add_row(*row)

    return tbl


def build_board_image(board, tile_size: int = 48):
    """Build a PIL image of the board using piece PNGs from assets.

    Returns a PIL Image or None if PIL or assets are missing.
    """
    if not PIL_AVAILABLE:
        return None

    import os
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    # adjust path if assets live at workspace root
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))

    # Create base image
    board_px = tile_size * 8
    img = PILImage.new('RGBA', (board_px, board_px), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Colors for light/dark squares
    light = (240, 217, 181, 255)
    dark = (181, 136, 99, 255)

    # Draw squares
    for rank in range(8):
        for file in range(8):
            x0 = file * tile_size
            y0 = (7 - rank) * tile_size
            rect = [x0, y0, x0 + tile_size, y0 + tile_size]
            sq_color = light if (rank + file) % 2 == 0 else dark
            draw.rectangle(rect, fill=sq_color)

    # Piece image mapping (expects assets w_*.png and b_*.png)
    piece_map = {
        'PAWN': 'pawn', 'KNIGHT': 'knight', 'BISHOP': 'bishop',
        'ROOK': 'rook', 'QUEEN': 'queen', 'KING': 'king'
    }

    # Try to load a DejaVu TTF from bundled assets to render Unicode piece glyphs
    font = None
    try:
        font_candidates = [
            os.path.join(assets_dir, 'dejavu-fonts-ttf-2.37', 'ttf', 'DejaVuSans.ttf'),
            os.path.join(assets_dir, 'dejavu-fonts-ttf-2.37', 'ttf', 'DejaVuSansMono.ttf'),
            os.path.join(assets_dir, 'dejavu-fonts-ttf-2.37', 'ttf', 'DejaVuSerif.ttf'),
        ]
        for fp in font_candidates:
            if os.path.exists(fp):
                try:
                    # font size chosen proportionally to tile size
                    font = ImageFont.truetype(fp, int(tile_size * 0.7))
                    break
                except Exception:
                    font = None
    except Exception:
        font = None

    # Iterate squares and paste piece images
    for sq in range(64):
        cell = board.mailbox[sq]
        if cell is None:
            continue
        colr, ptype = cell
        # get piece name from PieceType
        try:
            name = ptype.name if hasattr(ptype, 'name') else str(ptype)
        except Exception:
            name = str(ptype)
        # normalize name
        name_key = name.upper()
        pname = piece_map.get(name_key)
        if not pname:
            continue
        # If a DejaVu TTF was loaded, render the Unicode chess glyph instead
        if font is not None:
            try:
                pair = PIECE_UNICODE.get(ptype, ('?', '?'))
                ch = pair[0] if colr == Color.WHITE else pair[1]

                # measure text and center it in the tile
                bbox = draw.textbbox((0, 0), ch, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]

                file = sq % 8
                rank = sq // 8
                x = file * tile_size + (tile_size - w) // 2
                y = (7 - rank) * tile_size + (tile_size - h) // 2

                # choose contrasting fill colors for white/black pieces
                fill_white = (240, 240, 240, 255)
                fill_black = (15, 15, 15, 255)
                fill = fill_white if colr == Color.WHITE else fill_black

                draw.text((x, y), ch, font=font, fill=fill)
                continue
            except Exception:
                # fall back to PNG approach below
                pass

        # fallback to image-based pieces when font not available or drawing failed
        color_prefix = 'w' if colr == Color.WHITE else 'b'
        fname = os.path.join(assets_dir, f"{color_prefix}_{pname}.png")
        if not os.path.exists(fname):
            continue

        try:
            pimg = PILImage.open(fname).convert('RGBA')
            # resize to fit tile
            pimg = pimg.resize((tile_size, tile_size), PILImage.LANCZOS)
            file = sq % 8
            rank = sq // 8
            x = file * tile_size
            y = (7 - rank) * tile_size
            img.paste(pimg, (x, y), pimg)
        except Exception:
            continue

    return img


class BoardPanel(Static):
    board = reactive(None)

    def on_mount(self):
        """Configura o painel para ocupar mais espaço."""
        # Prefer vertical expansion; keep width constrained to match CSS
        self.styles.height = "1fr"
        self.styles.width = "40"
        # add more vertical padding and less horizontal padding
        self.styles.padding = (2, 1)

    def render(self) -> Panel:
        if self.board is None:
            return Panel(Text("No board loaded"), title="Board")

        # Prefer image-based rendering if available
        try:
            pil_img = None
            if PIL_AVAILABLE:
                pil_img = build_board_image(self.board, tile_size=48)
            if pil_img is not None and RichImage is not None:
                # Use Rich's Image renderable
                rimg = RichImage.from_pil(pil_img)
                return Panel(rimg, title="Board", expand=True)
        except Exception:
            # fallback to ascii table
            pass

        tbl = render_board_ascii(self.board)
        # Aumentar padding do painel
        panel = Panel(tbl, title="Board", expand=True)
        return panel


class StatusPanel(Static):
    status_text = reactive("")

    def update_status(self, text: str):
        self.status_text = text
        self.refresh()

    def render(self) -> Panel:
        return Panel(Text(self.status_text), title="Status")


class LogPanel(Static):
    """
    Painel de log compatível com Textual moderno.
    """
    log_text: Text = reactive(Text(""))

    def on_mount(self):
        self.styles.border = ("round", "white")
        self.styles.height = "1fr"

    def render(self):
        return Panel(self.log_text, title="Log")

    def log(self, line: str):
        self.log_text.append(line + "\n")
        self.refresh()

    def clear(self):
        self.log_text = Text("")
        self.refresh()


class HistoryPanel(Static):
    """
    Painel para exibir histórico de movimentos ao lado do tabuleiro.
    """
    history_text: Text = reactive(Text(""))

    def on_mount(self):
        self.styles.border = ("round", "white")
        self.styles.height = "1fr"

    def render(self):
        return Panel(self.history_text, title="Movimentos")

    def update_history(self, moves_text: str):
        """Atualiza o painel com histórico formatado."""
        self.history_text = Text(moves_text)
        self.refresh()

    def clear(self):
        self.history_text = Text("")
        self.refresh()


class PlayerStatsHeader(Static):
    """
    Header exibindo estatísticas dos jogadores e razão de empate.
    """
    white_wins = reactive(0)
    white_losses = reactive(0)
    black_wins = reactive(0)
    black_losses = reactive(0)
    # Unified draw counter (global, not per-color)
    draws = reactive(0)
    draw_reason = reactive("")

    def render(self) -> Panel:
        """Renderiza header com estatísticas."""
        # Line with win/loss for each side
        stats_line = (
            f"[bold cyan]♔ White[/] "
            f"[green]W:{self.white_wins}[/] "
            f"[red]L:{self.white_losses}[/] "
            f"     "
            f"[bold yellow]♚ Black[/] "
            f"[green]W:{self.black_wins}[/] "
            f"[red]L:{self.black_losses}[/]"
        )

        # Unified draws line
        draw_line = f"\n[bold]Draws:[/] [yellow]{self.draws}[/]"

        # Draw reason, if present
        reason_line = ""
        if self.draw_reason:
            reason_line = f"\n[dim]Reason: {self.draw_reason}[/]"

        content = Text.from_markup(stats_line + draw_line + reason_line)
        return Panel(content, expand=False)

    def update_stats(self, white_wins=None, white_losses=None, draws=None,
                     black_wins=None, black_losses=None):
        """Atualiza estatísticas."""
        if white_wins is not None:
            self.white_wins = white_wins
        if white_losses is not None:
            self.white_losses = white_losses
        if black_wins is not None:
            self.black_wins = black_wins
        if black_losses is not None:
            self.black_losses = black_losses
        if draws is not None:
            self.draws = draws
        self.refresh()

    def set_draw_reason(self, reason: str):
        """Define a razão do empate."""
        self.draw_reason = reason
        self.refresh()

    def clear_draw_reason(self):
        """Limpa a razão do empate."""
        self.draw_reason = ""
        self.refresh()


class HelpBar(Static):
    """
    Pequena barra de ajuda exibindo comandos disponíveis.
    """
    help_text: Text = reactive(Text(""))

    def on_mount(self):
        # minimal styling
        self.styles.height = "auto"
        self.styles.padding = (0, 1)

        # default help summary
        default = (
            "Comandos: show | history | move <lan> | undo | play <p1> <p2> | "
            "stop | perft <n> | set <fen> | help | quit"
        )
        self.help_text = Text.from_markup(f"[dim]{default}[/]")

    def render(self) -> Panel:
        return Panel(self.help_text, expand=True)

    def update_help(self, text: str):
        self.help_text = Text.from_markup(text)
        self.refresh()
