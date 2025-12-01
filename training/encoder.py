"""Encoder: board <-> tensor and action <-> index mapping.

Uses `core.moves.Move`/UCI for mapping. Action space: 4096 normal moves
plus 4x for promotions -> total 20480.
"""
from __future__ import annotations
from typing import Tuple, Optional
try:
    from core.moves.move import Move
    from utils.enums import PieceType
except Exception:
    Move = None
    PieceType = None


BOARD_SHAPE = (13, 8, 8)  # 12 piece planes + side-to-move
ACTION_SIZE = 4096 * 5  # 4096 normal + 4x promotions


def board_to_tensor(board):
    """Convert a `board` (core board) to numpy tensor (C,H,W).

    Expects `board.mailbox` and `board.side_to_move`.
    """
    import numpy as np
    planes = np.zeros(BOARD_SHAPE, dtype=np.int8)
    # piece planes: order WHITE PAWN..KING, BLACK PAWN..KING
    if hasattr(board, 'mailbox') and board.mailbox is not None:
        for sq, entry in enumerate(board.mailbox):
            if entry is None:
                continue
            color, ptype = entry
            try:
                idx = int(ptype) - 1
            except Exception:
                continue
            plane = idx + (0 if int(color) == 0 else 6)
            r = sq >> 3
            f = sq & 7
            planes[plane, r, f] = 1

    # side to move
    stm = 1 if getattr(board, 'side_to_move', 0) else 0
    planes[12, :, :] = stm
    return planes.astype(np.float32)


def move_to_index(move: 'Move') -> int:
    """Map a Move -> int index. Uses from*64 + to for base; promotions offset.
    If Move.promotion is None use base slot.
    """
    base = move.from_sq * 64 + move.to_sq
    if getattr(move, 'promotion', None) is None:
        return base
    promo_map = {
        PieceType.QUEEN: 0,
        PieceType.ROOK: 1,
        PieceType.BISHOP: 2,
        PieceType.KNIGHT: 3,
    }
    p = promo_map.get(move.promotion, 0)
    return 4096 + base * 4 + p


def index_to_move(idx: int) -> Tuple[int, int, Optional['PieceType']]:
    """Inverse of `move_to_index`: returns (from_sq,to_sq,promotion_or_None).
    """
    if idx < 4096:
        f = idx // 64
        t = idx % 64
        return f, t, None
    rem = idx - 4096
    base = rem // 4
    p = rem % 4
    f = base // 64
    t = base % 64
    rev = {0: PieceType.QUEEN, 1: PieceType.ROOK, 2: PieceType.BISHOP, 3: PieceType.KNIGHT}
    return f, t, rev[p]


def validate_mapping_roundtrip():
    # quick sanity
    for f in (0, 10, 63):
        for t in (0, 7, 63):
            class M: pass
            m = M()
            m.from_sq = f
            m.to_sq = t
            m.promotion = None
            i = move_to_index(m)
            assert index_to_move(i)[0] == f
