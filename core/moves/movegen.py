# core/moves/movegen.py
from __future__ import annotations

from typing import List, Iterable
from utils.constants import bit, pop_lsb, SQUARE_BB
from core.moves.tables.attack_tables import knight_attacks, king_attacks
from core.moves.magic.magic_bitboards import rook_attacks, bishop_attacks
from utils.enums import Color, PieceType
from core.moves.move import Move
from core.moves.castling import _gen_castling_moves



# -------------------------
# Small utilities
# -------------------------

def _bb_to_moves(board, from_sq: int, target_bb: int, piece: PieceType, occ_enemy: int) -> List[Move]:
    """Convert target bitboard into Move objects for a given from_sq / piece."""
    moves: List[Move] = []
    while target_bb:
        target_bb, to_sq = pop_lsb(target_bb)
        is_capture = bool(bit(to_sq) & occ_enemy)
        moves.append(Move(
            from_sq=from_sq,
            to_sq=to_sq,
            piece=piece,
            is_capture=is_capture
        ))
    return moves

# -------------------------
# Generators
# -------------------------
def _gen_pawn_moves(board, stm: Color, occ_all: int, occ_enemy: int) -> List[Move]:
    moves: List[Move] = []

    pawns = board.bitboards[int(stm)][int(PieceType.PAWN)]
    direction = 8 if stm == Color.WHITE else -8
    start_rank = 1 if stm == Color.WHITE else 6
    promo_rank = 7 if stm == Color.WHITE else 0
    ep_sq = board.en_passant_square

    while pawns:
        pawns, from_sq = pop_lsb(pawns)
        file = from_sq & 7
        rank = from_sq >> 3

        # single forward
        forward = from_sq + direction
        if 0 <= forward < 64 and not (occ_all & SQUARE_BB[forward]):
            if (forward >> 3) == promo_rank:
                for promo in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
                    moves.append(Move(from_sq, forward, PieceType.PAWN, False, promo))
            else:
                moves.append(Move(from_sq, forward, PieceType.PAWN))

            # double push
            if rank == start_rank:
                double_forward = from_sq + 2 * direction
                if 0 <= double_forward < 64 and not (occ_all & SQUARE_BB[double_forward]):
                    moves.append(Move(from_sq, double_forward, PieceType.PAWN))

        # captures (including promotions on capture and en-passant)
        for df in (-1, 1):
            nf = file + df
            if nf < 0 or nf > 7:
                continue

            target = from_sq + direction + df
            if not (0 <= target < 64):
                continue

            # normal capture (may be promotion)
            if occ_enemy & SQUARE_BB[target]:
                if (target >> 3) == promo_rank:
                    for promo in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
                        moves.append(Move(from_sq, target, PieceType.PAWN, True, promo))
                else:
                    moves.append(Move(from_sq, target, PieceType.PAWN, True))

            # en passant capture
            elif ep_sq is not None and target == ep_sq:
                victim_sq = target - 8 if stm == Color.WHITE else target + 8
                if 0 <= victim_sq < 64:
                    victim = board.mailbox[victim_sq]
                    if victim is not None:
                        v_color, v_piece = victim
                        if v_piece == PieceType.PAWN and v_color != stm:
                            moves.append(Move(from_sq, target, PieceType.PAWN, True))

    return moves

def _gen_knight_moves(board, stm: Color, occ_own: int, occ_enemy: int) -> List[Move]:
    moves: List[Move] = []
    knights = board.bitboards[int(stm)][int(PieceType.KNIGHT)]
    while knights:
        knights, from_sq = pop_lsb(knights)
        attacks = knight_attacks(from_sq) & ~occ_own
        moves.extend(_bb_to_moves(board, from_sq, attacks, PieceType.KNIGHT, occ_enemy))
    return moves

def _gen_slider_moves(board, stm: Color, occ_all: int, occ_own: int, occ_enemy: int) -> List[Move]:
    moves: List[Move] = []

    # bishops
    bishops = board.bitboards[int(stm)][int(PieceType.BISHOP)]
    while bishops:
        bishops, from_sq = pop_lsb(bishops)
        attacks = bishop_attacks(from_sq, occ_all) & ~occ_own
        moves.extend(_bb_to_moves(board, from_sq, attacks, PieceType.BISHOP, occ_enemy))

    # rooks
    rooks = board.bitboards[int(stm)][int(PieceType.ROOK)]
    while rooks:
        rooks, from_sq = pop_lsb(rooks)
        attacks = rook_attacks(from_sq, occ_all) & ~occ_own
        moves.extend(_bb_to_moves(board, from_sq, attacks, PieceType.ROOK, occ_enemy))

    # queens (rook + bishop)
    queens = board.bitboards[int(stm)][int(PieceType.QUEEN)]
    while queens:
        queens, from_sq = pop_lsb(queens)
        attacks = (rook_attacks(from_sq, occ_all) | bishop_attacks(from_sq, occ_all)) & ~occ_own
        moves.extend(_bb_to_moves(board, from_sq, attacks, PieceType.QUEEN, occ_enemy))

    return moves

def _gen_king_moves(board, stm: Color, occ_own: int, occ_enemy: int) -> List[Move]:
    moves: List[Move] = []
    king_bb = board.bitboards[int(stm)][int(PieceType.KING)]
    if king_bb:
        _, from_sq = pop_lsb(king_bb)
        attacks = king_attacks(from_sq) & ~occ_own
        moves.extend(_bb_to_moves(board, from_sq, attacks, PieceType.KING, occ_enemy))
    return moves

# -------------------------
# Public pipeline
# -------------------------

def generate_pseudo_legal_moves(board) -> List[Move]:
    """
    Main entry: returns list[Move] of all pseudo-legal moves (excluding castling here).
    Castling moves are appended from a separate generator for clarity.
    """
    stm = board.side_to_move
    enemy = Color.BLACK if stm == Color.WHITE else Color.WHITE

    occ_all = board.all_occupancy
    occ_own = board.occupancy[int(stm)]
    occ_enemy = board.occupancy[int(enemy)]

    moves: List[Move] = []

    # pipeline: pawns, knights, sliders, king, castling
    moves.extend(_gen_pawn_moves(board, stm, occ_all, occ_enemy))
    moves.extend(_gen_knight_moves(board, stm, occ_own, occ_enemy))
    moves.extend(_gen_slider_moves(board, stm, occ_all, occ_own, occ_enemy))
    moves.extend(_gen_king_moves(board, stm, occ_own, occ_enemy))

    # castling kept as separate call (explicitly appended)
    moves.extend(_gen_castling_moves(board))

    return moves
