"""
Enums fundamentais do Xadrez_AI_Final.

Invariantes:
    - A1 = 0 .. H8 = 63 (coerente com todo o projeto)
    - Valores numéricos dos enums são parte da ABI interna e NÃO devem mudar
    - PieceIndex = índice 0..11 (6 peças * 2 cores), usado por bitboards

Objetivo:
    Manter enums pequenos, claros e estáveis. Eles são usados em todo o motor
    e servem como base para movegen, board, zobrist e perft.
"""

from __future__ import annotations
from enum import IntEnum
from typing import Tuple
try:
    from typing import TypeAlias
except ImportError:
    # Python 3.8 compatibility: TypeAlias não existe
    TypeAlias = type(None)

# ---------------------------------------------------------
# Tipos semânticos
# ---------------------------------------------------------

PieceIndex = int   # usado em bitboards e arrays indexados (int compatível com Python 3.8)

__all__ = [
    "Color",
    "PieceType",
    "MoveType",
    "GameResult",
    "PieceIndex",
    "piece_index",
]

# ---------------------------------------------------------
# Bases internas fixas para peça+cor → índice
# WHITE = 0..5   BLACK = 6..11
# ---------------------------------------------------------

_PIECE_INDEX_BASE: Tuple[int, int] = (0, 6)


# ---------------------------------------------------------
# Enums principais
# ---------------------------------------------------------

class Color(IntEnum):
    WHITE = 0
    BLACK = 1


class PieceType(IntEnum):
    PAWN   = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK   = 3
    QUEEN  = 4
    KING   = 5


class MoveType(IntEnum):
    QUIET      = 0
    CAPTURE    = 1
    PROMOTION  = 2
    PROMO_CAP  = 3
    EN_PASSANT = 4
    CASTLE     = 5


class GameResult(IntEnum):
    ONGOING                     = 0
    WHITE_WIN                   = 1
    BLACK_WIN                   = 2

    DRAW_STALEMATE              = 3
    DRAW_REPETITION             = 4
    DRAW_FIFTY_MOVE             = 5
    DRAW_INSUFFICIENT_MATERIAL  = 6


# ---------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------

def piece_index(piece_type: PieceType, color: Color) -> PieceIndex:
    """
    Retorna índice [0..11] para tabelas de bitboards:

        White: 0..5   (P, N, B, R, Q, K)
        Black: 6..11  (P, N, B, R, Q, K)

    Esta função é O(1) e alinhada com o layout das tabelas internas.
    """
    if not isinstance(piece_type, PieceType):
        raise TypeError(f"piece_type inválido: {type(piece_type).__name__}")
    if not isinstance(color, Color):
        raise TypeError(f"color inválido: {type(color).__name__}")

    return _PIECE_INDEX_BASE[int(color)] + int(piece_type)
