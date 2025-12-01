"""
Constantes e utilitários bitboard do Xadrez_AI_Final.

Invariantes:
    - Bitboards são inteiros 64-bit (A1 = bit 0, H8 = bit 63)
    - Todas as máscaras são pré-computadas e imutáveis
    - Funções auxiliares são O(1) e puras
"""

from __future__ import annotations
from typing import Final, Tuple

# =========================================================
# Mascara 64-bit
# =========================================================
U64: Final[int] = 0xFFFFFFFFFFFFFFFF


# =========================================================
# Funções auxiliares básicas
# =========================================================

def bit(square: int) -> int:
    """Retorna um bitboard com apenas o bit `square` ligado."""
    if not (0 <= square < 64):
        raise ValueError(f"square fora do intervalo [0..63]: {square}")
    return (1 << square) & U64


def sq(file_idx: int, rank_idx: int) -> int:
    """Converte (file_idx, rank_idx) para índice de 0..63."""
    if not (0 <= file_idx < 8 and 0 <= rank_idx < 8):
        raise ValueError(f"file_idx/rank_idx inválidos: {(file_idx, rank_idx)}")
    return (rank_idx << 3) | file_idx


# =========================================================
# FILE masks
# =========================================================

_FILE_A: Final[int] = 0x0101010101010101
FILES_MASKS: Final[Tuple[int, ...]] = tuple((_FILE_A << i) & U64 for i in range(8))

FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H = FILES_MASKS


# =========================================================
# RANK masks
# =========================================================

_RANK_1: Final[int] = 0x00000000000000FF
RANKS_MASKS: Final[Tuple[int, ...]] = tuple((_RANK_1 << (8 * i)) & U64 for i in range(8))

RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8 = RANKS_MASKS


# =========================================================
# Center masks
# =========================================================

CENTER_4_MASK: Final[int] = (
    bit(sq(3, 3)) | bit(sq(4, 3)) |
    bit(sq(3, 4)) | bit(sq(4, 4))
) & U64

FILES_CDEF: Final[int] = FILE_C | FILE_D | FILE_E | FILE_F
CLASSIC_CENTER: Final[int] = FILES_CDEF & (RANK_3 | RANK_4 | RANK_5 | RANK_6)


# =========================================================
# Diagonais principais
# =========================================================

DIAGONAL_A1H8: Final[int] = 0x8040201008040201
ANTI_DIAGONAL_H1A8: Final[int] = 0x0102040810204080


# =========================================================
# Direções (offsets no índice 0..63)
# =========================================================

NORTH: Final[int] = 8
SOUTH: Final[int] = -8
EAST:  Final[int] = 1
WEST:  Final[int] = -1

NORTH_EAST: Final[int] = NORTH + EAST
NORTH_WEST: Final[int] = NORTH + WEST
SOUTH_EAST: Final[int] = SOUTH + EAST
SOUTH_WEST: Final[int] = SOUTH + WEST


# =========================================================
# Dimensões internas
# =========================================================

PIECE_TYPES: Final[int] = 6
COLOR_COUNT: Final[int] = 2
PIECE_COUNT: Final[int] = 12
MOVE_TYPE_COUNT: Final[int] = 6


# =========================================================
# Tabelas por square (pré-computadas)
# =========================================================

SQUARE_TO_FILE: Final[Tuple[int, ...]] = tuple(i & 7 for i in range(64))
SQUARE_TO_RANK: Final[Tuple[int, ...]] = tuple(i >> 3 for i in range(64))
SQUARE_BB:      Final[Tuple[int, ...]] = tuple((1 << i) & U64 for i in range(64))


# =========================================================
# Borda e exclusões
# =========================================================

NOT_FILE_A:  Final[int] = (~FILE_A) & U64
NOT_FILE_H:  Final[int] = (~FILE_H) & U64
NOT_FILE_AB: Final[int] = (~(FILE_A | FILE_B)) & U64
NOT_FILE_GH: Final[int] = (~(FILE_G | FILE_H)) & U64


# =========================================================
# Pawn helpers
# =========================================================

PAWN_FORWARD: Final[dict[int, int]] = {
    0: NORTH,  # WHITE
    1: SOUTH,  # BLACK
}

PAWN_DOUBLE_RANK: Final[dict[int, int]] = {
    0: 1,  # RANK 2 (white)
    1: 6,  # RANK 7 (black)
}


# =========================================================
# Ferramentas de debug
# =========================================================

def bitboard_to_str(bb: int) -> str:
    """Renderiza bitboard como matriz textual (rank 8 → rank 1)."""
    bb &= U64
    rows = []
    for rank_idx in range(7, -1, -1):
        base = rank_idx << 3
        row = "".join(
            "1" if ((bb >> (base + file)) & 1) else "."
            for file in range(8)
        )
        rows.append(row)
    return "\n".join(rows)


def square_index(coord: str) -> int:
    """Converte string como 'e4' para índice 0..63."""
    if not isinstance(coord, str) or len(coord) != 2:
        raise ValueError(f"coord inválido: {coord}")
    file_ch, rank_ch = coord[0].lower(), coord[1]
    if not ('a' <= file_ch <= 'h'):
        raise ValueError(f"file inválido: {coord}")
    if not ('1' <= rank_ch <= '8'):
        raise ValueError(f"rank inválido: {coord}")
    return ((int(rank_ch) - 1) << 3) | (ord(file_ch) - ord('a'))


def pop_lsb(bb: int) -> tuple[int, int]:
    """
    Remove e retorna o bit menos significativo:
        (novo_bb, square)
    """
    if bb == 0:
        raise ValueError("pop_lsb chamado com bb == 0")
    lsb = bb & -bb
    sq = lsb.bit_length() - 1
    return bb & (bb - 1), sq


# =========================================================
# Castling flags
# =========================================================

CASTLE_WHITE_K: Final[int] = 1 << 0
CASTLE_WHITE_Q: Final[int] = 1 << 1
CASTLE_BLACK_K: Final[int] = 1 << 2
CASTLE_BLACK_Q: Final[int] = 1 << 3

CASTLING_ALL: Final[int] = (
    CASTLE_WHITE_K | CASTLE_WHITE_Q |
    CASTLE_BLACK_K | CASTLE_BLACK_Q
)


# =========================================================
# API pública
# =========================================================

__all__ = [
    "U64",
    "bit",
    "sq",
    "FILES_MASKS",
    "RANKS_MASKS",
    "FILE_A", "FILE_H",
    "RANK_1", "RANK_8",
    "CENTER_4_MASK", "CLASSIC_CENTER",
    "DIAGONAL_A1H8", "ANTI_DIAGONAL_H1A8",
    "NORTH", "SOUTH", "EAST", "WEST",
    "NORTH_EAST", "NORTH_WEST", "SOUTH_EAST", "SOUTH_WEST",
    "PIECE_TYPES", "COLOR_COUNT", "PIECE_COUNT", "MOVE_TYPE_COUNT",
    "SQUARE_TO_FILE", "SQUARE_TO_RANK", "SQUARE_BB",
    "NOT_FILE_A", "NOT_FILE_H", "NOT_FILE_AB", "NOT_FILE_GH",
    "PAWN_FORWARD", "PAWN_DOUBLE_RANK",
    "bitboard_to_str", "square_index", "pop_lsb",
    "CASTLE_WHITE_K", "CASTLE_WHITE_Q",
    "CASTLE_BLACK_K", "CASTLE_BLACK_Q",
    "CASTLING_ALL",
]
