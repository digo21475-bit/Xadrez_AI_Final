# castling.py (optimized)
from __future__ import annotations

from typing import List
from utils.constants import SQUARE_BB
from utils.enums import Color, PieceType
from core.moves.move import Move
from utils.constants import (
    CASTLE_WHITE_K, CASTLE_WHITE_Q,
    CASTLE_BLACK_K, CASTLE_BLACK_Q,
)


# Pré-cálculo das casas envolvidas no roque (evita repetir literais)
_WS_K_EMPTY = SQUARE_BB[5] | SQUARE_BB[6]
_WS_Q_EMPTY = SQUARE_BB[1] | SQUARE_BB[2] | SQUARE_BB[3]
_BS_K_EMPTY = SQUARE_BB[61] | SQUARE_BB[62]
_BS_Q_EMPTY = SQUARE_BB[57] | SQUARE_BB[58] | SQUARE_BB[59]

# Listas de verificação de ataque (minimiza chamadas e loops)
_WS_K_CHECK = (4, 5, 6)
_WS_Q_CHECK = (4, 3, 2)
_BS_K_CHECK = (60, 61, 62)
_BS_Q_CHECK = (60, 59, 58)


def _all_safe(board, sq_list, enemy) -> bool:
    """Retorna True se todas as casas sq_list NÃO são atacadas."""
    # Inline loop otimizado: mais rápido que all() com generator
    for sq in sq_list:
        if board.is_square_attacked(sq, enemy):
            return False
    return True


def _gen_castling_moves(board) -> List[Move]:
    stm = board.side_to_move
    enemy = Color.BLACK if stm == Color.WHITE else Color.WHITE

    king_bb = board.bitboards[int(stm)][int(PieceType.KING)]
    if not king_bb:
        return []

    occ = board.all_occupancy
    rights = board.castling_rights

    moves = []

    if stm == Color.WHITE:
        # --------------------------------------------------
        # WHITE KING SIDE (O-O)
        # --------------------------------------------------
        if rights & CASTLE_WHITE_K:
            if not (occ & _WS_K_EMPTY):
                if _all_safe(board, _WS_K_CHECK, enemy):
                    moves.append(Move(4, 6, PieceType.KING))

        # --------------------------------------------------
        # WHITE QUEEN SIDE (O-O-O)
        # --------------------------------------------------
        if rights & CASTLE_WHITE_Q:
            if not (occ & _WS_Q_EMPTY):
                if _all_safe(board, _WS_Q_CHECK, enemy):
                    moves.append(Move(4, 2, PieceType.KING))

    else:
        # --------------------------------------------------
        # BLACK KING SIDE (O-O)
        # --------------------------------------------------
        if rights & CASTLE_BLACK_K:
            if not (occ & _BS_K_EMPTY):
                if _all_safe(board, _BS_K_CHECK, enemy):
                    moves.append(Move(60, 62, PieceType.KING))

        # --------------------------------------------------
        # BLACK QUEEN SIDE (O-O-O)
        # --------------------------------------------------
        if rights & CASTLE_BLACK_Q:
            if not (occ & _BS_Q_EMPTY):
                if _all_safe(board, _BS_Q_CHECK, enemy):
                    moves.append(Move(60, 58, PieceType.KING))

    return moves
