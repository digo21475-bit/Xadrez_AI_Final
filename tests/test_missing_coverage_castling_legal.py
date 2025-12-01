"""
Tests to increase coverage for `core.moves.castling` and `core.moves.legal_movegen`.

Covers:
- `_gen_castling_moves` behavior in positions with castling rights
- Integration with `generate_legal_moves` to ensure castling moves appear
- Basic sanity checks for legal move generation (startpos)
"""

from core.moves.castling import _gen_castling_moves
from core.moves.legal_movegen import generate_legal_moves
from core.board.board import Board
from core.moves.move import Move
from utils.enums import PieceType


def _has_move(moves, from_sq, to_sq, piece=PieceType.KING):
    for m in moves:
        if m.from_sq == from_sq and m.to_sq == to_sq and m.piece == piece:
            return True
    return False


class TestCastlingGen:
    def test_gen_castling_moves_startpos_none(self):
        """In starting position there should be no immediate castling from _gen_castling_moves (blocked)."""
        board = Board()  # starting position has pieces between king and rook
        moves = _gen_castling_moves(board)
        assert isinstance(moves, list)
        assert moves == []

    def test_gen_castling_moves_both_sides_available(self):
        """Position where both white castlings are legal (empty between, rights present)."""
        # FEN: both sides rooks and kings in corner, empty between
        fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
        board = Board.from_fen(fen)

        moves = _gen_castling_moves(board)

        # White castlings should be present: e1->g1 (4->6), e1->c1 (4->2)
        assert _has_move(moves, 4, 6)
        assert _has_move(moves, 4, 2)

    def test_gen_castling_moves_blocked_by_occupancy(self):
        """When squares between king and rook are occupied, castling should not be generated."""
        # place pieces between the king and rook (example): f1 (5) occupied
        fen = "r3k2r/8/8/8/8/8/8/R4K1R w KQkq - 0 1"
        board = Board.from_fen(fen)

        moves = _gen_castling_moves(board)
        # Queen side may still be possible, king side blocked
        assert not _has_move(moves, 4, 6)


class TestLegalMovegenIntegration:
    def test_generate_legal_moves_startpos_count(self):
        """Starting position should have 20 legal moves for white."""
        board = Board()
        mvlist = list(generate_legal_moves(board))
        assert len(mvlist) == 20

    def test_generate_legal_moves_includes_castling_when_available(self):
        """Integration: generate_legal_moves should include castling moves when valid."""
        fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
        board = Board.from_fen(fen)

        all_moves = list(generate_legal_moves(board))

        # Ensure both castling moves are included among legal moves
        assert _has_move(all_moves, 4, 6)
        assert _has_move(all_moves, 4, 2)
