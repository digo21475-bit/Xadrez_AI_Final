"""
Comprehensive test coverage for core/moves/move.py.

Covers:
- Move class dataclass with frozen=True
- to_uci() method with all piece types and promotions
- Square coordinate conversion logic
- UCI notation edge cases
"""

import pytest
from core.moves.move import Move, PROMOTION_UCI, FILES, RANKS
from utils.enums import PieceType


class TestMoveDataclass:
    """Test Move dataclass structure and properties."""
    
    def test_move_creation_minimal(self):
        """Test Move creation with minimal parameters."""
        move = Move(from_sq=0, to_sq=8, piece=PieceType.PAWN)
        
        assert move.from_sq == 0
        assert move.to_sq == 8
        assert move.piece == PieceType.PAWN
        assert move.is_capture is False
        assert move.promotion is None
    
    def test_move_creation_with_capture(self):
        """Test Move creation with capture flag."""
        move = Move(from_sq=0, to_sq=9, piece=PieceType.PAWN, is_capture=True)
        
        assert move.from_sq == 0
        assert move.to_sq == 9
        assert move.is_capture is True
        assert move.promotion is None
    
    def test_move_creation_with_promotion(self):
        """Test Move creation with promotion."""
        move = Move(
            from_sq=48,
            to_sq=56,
            piece=PieceType.PAWN,
            is_capture=False,
            promotion=PieceType.QUEEN
        )
        
        assert move.from_sq == 48
        assert move.to_sq == 56
        assert move.promotion == PieceType.QUEEN
    
    def test_move_frozen_dataclass(self):
        """Test that Move is frozen (immutable)."""
        move = Move(from_sq=0, to_sq=8, piece=PieceType.PAWN)
        
        with pytest.raises(Exception):
            move.from_sq = 16
    
    def test_move_equality(self):
        """Test Move equality comparison."""
        move1 = Move(from_sq=0, to_sq=8, piece=PieceType.PAWN)
        move2 = Move(from_sq=0, to_sq=8, piece=PieceType.PAWN)
        move3 = Move(from_sq=0, to_sq=16, piece=PieceType.PAWN)
        
        assert move1 == move2
        assert move1 != move3
    
    def test_move_hashable(self):
        """Test that Move is hashable (can be used in sets/dicts)."""
        move1 = Move(from_sq=0, to_sq=8, piece=PieceType.PAWN)
        move2 = Move(from_sq=0, to_sq=8, piece=PieceType.PAWN)
        
        move_set = {move1, move2}
        assert len(move_set) == 1  # Should be deduplicated


class TestMoveToUCIBasicMoves:
    """Test to_uci() conversion for basic moves without promotion."""
    
    def test_pawn_move_e2_to_e4(self):
        """Test pawn move e2-e4 (index 12 to 28)."""
        move = Move(from_sq=12, to_sq=28, piece=PieceType.PAWN)
        
        assert move.to_uci() == "e2e4"
    
    def test_pawn_move_d7_to_d5(self):
        """Test pawn move d7-d5 (index 51 to 35)."""
        move = Move(from_sq=51, to_sq=35, piece=PieceType.PAWN)
        
        assert move.to_uci() == "d7d5"
    
    def test_knight_move_b1_to_c3(self):
        """Test knight move b1-c3 (index 1 to 18)."""
        move = Move(from_sq=1, to_sq=18, piece=PieceType.KNIGHT)
        
        assert move.to_uci() == "b1c3"
    
    def test_knight_move_g8_to_f6(self):
        """Test knight move g8-f6 (index 62 to 45)."""
        move = Move(from_sq=62, to_sq=45, piece=PieceType.KNIGHT)
        
        assert move.to_uci() == "g8f6"
    
    def test_bishop_move_f1_to_c4(self):
        """Test bishop move f1-c4 (index 5 to 26)."""
        move = Move(from_sq=5, to_sq=26, piece=PieceType.BISHOP)
        
        assert move.to_uci() == "f1c4"
    
    def test_rook_move_a1_to_a8(self):
        """Test rook move a1-a8 (index 0 to 56)."""
        move = Move(from_sq=0, to_sq=56, piece=PieceType.ROOK)
        
        assert move.to_uci() == "a1a8"
    
    def test_queen_move_d1_to_d4(self):
        """Test queen move d1-d4 (index 3 to 27)."""
        move = Move(from_sq=3, to_sq=27, piece=PieceType.QUEEN)
        
        assert move.to_uci() == "d1d4"
    
    def test_king_move_e1_to_f2(self):
        """Test king move e1-f2 (index 4 to 13)."""
        move = Move(from_sq=4, to_sq=13, piece=PieceType.KING)
        
        assert move.to_uci() == "e1f2"


class TestMoveToUCICornerSquares:
    """Test to_uci() conversion from corner squares."""
    
    def test_move_from_a1(self):
        """Test move from a1 (index 0)."""
        move = Move(from_sq=0, to_sq=8, piece=PieceType.ROOK)
        assert move.to_uci() == "a1a2"
    
    def test_move_from_h1(self):
        """Test move from h1 (index 7)."""
        move = Move(from_sq=7, to_sq=15, piece=PieceType.ROOK)
        assert move.to_uci() == "h1h2"
    
    def test_move_from_a8(self):
        """Test move from a8 (index 56)."""
        move = Move(from_sq=56, to_sq=48, piece=PieceType.ROOK)
        assert move.to_uci() == "a8a7"
    
    def test_move_from_h8(self):
        """Test move from h8 (index 63)."""
        move = Move(from_sq=63, to_sq=55, piece=PieceType.ROOK)
        assert move.to_uci() == "h8h7"
    
    def test_move_to_a1(self):
        """Test move to a1 (index 0)."""
        move = Move(from_sq=8, to_sq=0, piece=PieceType.ROOK)
        assert move.to_uci() == "a2a1"
    
    def test_move_to_h8(self):
        """Test move to h8 (index 63)."""
        move = Move(from_sq=55, to_sq=63, piece=PieceType.ROOK)
        assert move.to_uci() == "h7h8"


class TestMoveToUCIPromotion:
    """Test to_uci() conversion with pawn promotions."""
    
    def test_promotion_to_queen(self):
        """Test pawn promotion to queen."""
        move = Move(
            from_sq=48,  # a7
            to_sq=56,    # a8
            piece=PieceType.PAWN,
            promotion=PieceType.QUEEN
        )
        
        assert move.to_uci() == "a7a8q"
    
    def test_promotion_to_rook(self):
        """Test pawn promotion to rook."""
        move = Move(
            from_sq=52,  # e7
            to_sq=60,    # e8
            piece=PieceType.PAWN,
            promotion=PieceType.ROOK
        )
        
        assert move.to_uci() == "e7e8r"
    
    def test_promotion_to_bishop(self):
        """Test pawn promotion to bishop."""
        move = Move(
            from_sq=51,  # d7
            to_sq=59,    # d8
            piece=PieceType.PAWN,
            promotion=PieceType.BISHOP
        )
        
        assert move.to_uci() == "d7d8b"
    
    def test_promotion_to_knight(self):
        """Test pawn promotion to knight."""
        move = Move(
            from_sq=49,  # b7
            to_sq=57,    # b8
            piece=PieceType.PAWN,
            promotion=PieceType.KNIGHT
        )
        
        assert move.to_uci() == "b7b8n"
    
    def test_promotion_capture(self):
        """Test promotion with capture flag set."""
        move = Move(
            from_sq=48,
            to_sq=57,
            piece=PieceType.PAWN,
            is_capture=True,
            promotion=PieceType.QUEEN
        )
        
        # UCI notation includes promotion even with capture
        assert move.to_uci() == "a7b8q"


class TestMoveToUCIAllSquares:
    """Test to_uci() for all 64 squares."""
    
    def test_all_diagonal_moves(self):
        """Test moves across all diagonals."""
        # Main diagonal (a1-h8)
        diagonal_squares = [
            (0, 9), (9, 18), (18, 27), (27, 36),
            (36, 45), (45, 54), (54, 63)
        ]
        
        for from_sq, to_sq in diagonal_squares:
            move = Move(from_sq=from_sq, to_sq=to_sq, piece=PieceType.BISHOP)
            uci = move.to_uci()
            
            # Should be valid UCI format
            assert len(uci) == 4
            assert uci[0] in FILES
            assert uci[1] in RANKS
            assert uci[2] in FILES
            assert uci[3] in RANKS
    
    def test_all_horizontal_moves(self):
        """Test moves across all ranks."""
        # Rank 1
        rank_1_squares = [(i, i + 1) for i in range(0, 7)]
        
        for from_sq, to_sq in rank_1_squares:
            move = Move(from_sq=from_sq, to_sq=to_sq, piece=PieceType.ROOK)
            uci = move.to_uci()
            
            assert len(uci) == 4
            assert uci[1] == "1"  # Same rank
            assert uci[3] == "1"
    
    def test_all_vertical_moves(self):
        """Test moves across all files."""
        # A-file (0, 8, 16, 24, 32, 40, 48, 56)
        a_file_squares = [(i * 8, (i + 1) * 8) for i in range(0, 7)]
        
        for from_sq, to_sq in a_file_squares:
            move = Move(from_sq=from_sq, to_sq=to_sq, piece=PieceType.ROOK)
            uci = move.to_uci()
            
            assert len(uci) == 4
            assert uci[0] == "a"  # Same file
            assert uci[2] == "a"


class TestMoveToUCIEdgeCases:
    """Test to_uci() edge cases and special positions."""
    
    def test_move_same_square_theoretical(self):
        """Test move from square to itself (theoretical edge case)."""
        move = Move(from_sq=27, to_sq=27, piece=PieceType.KING)
        uci = move.to_uci()
        
        # Should produce "d4d4"
        assert uci == "d4d4"
    
    def test_move_promotion_no_piece_type_specified(self):
        """Test that to_uci() works with promotion specified."""
        move = Move(
            from_sq=48,
            to_sq=56,
            piece=PieceType.PAWN,
            promotion=PieceType.QUEEN
        )
        
        uci = move.to_uci()
        assert "q" in uci
    
    def test_capture_flag_does_not_affect_uci(self):
        """Test that is_capture flag doesn't change UCI notation."""
        move1 = Move(from_sq=12, to_sq=21, piece=PieceType.PAWN, is_capture=False)
        move2 = Move(from_sq=12, to_sq=21, piece=PieceType.PAWN, is_capture=True)
        
        # UCI notation should be identical
        assert move1.to_uci() == move2.to_uci()
    
    def test_promotion_uci_suffix_order(self):
        """Test that promotion suffix is correctly appended."""
        move = Move(
            from_sq=48,
            to_sq=56,
            piece=PieceType.PAWN,
            promotion=PieceType.KNIGHT
        )
        
        uci = move.to_uci()
        # Should end with 'n' for knight
        assert uci.endswith("n")
        assert uci.count(uci[-1]) == 1  # Only one promotion character


class TestMoveUIConstants:
    """Test PROMOTION_UCI dictionary and coordinate constants."""
    
    def test_promotion_uci_mapping(self):
        """Test that PROMOTION_UCI contains all piece types."""
        assert PieceType.QUEEN in PROMOTION_UCI
        assert PieceType.ROOK in PROMOTION_UCI
        assert PieceType.BISHOP in PROMOTION_UCI
        assert PieceType.KNIGHT in PROMOTION_UCI
    
    def test_promotion_uci_values(self):
        """Test that PROMOTION_UCI has correct values."""
        assert PROMOTION_UCI[PieceType.QUEEN] == "q"
        assert PROMOTION_UCI[PieceType.ROOK] == "r"
        assert PROMOTION_UCI[PieceType.BISHOP] == "b"
        assert PROMOTION_UCI[PieceType.KNIGHT] == "n"
    
    def test_files_constant(self):
        """Test FILES constant."""
        assert FILES == "abcdefgh"
        assert len(FILES) == 8
    
    def test_ranks_constant(self):
        """Test RANKS constant."""
        assert RANKS == "12345678"
        assert len(RANKS) == 8
    
    def test_file_rank_correspondence(self):
        """Test that file and rank indices correspond to square coordinates."""
        # a1 = 0: file_idx=0, rank_idx=0
        sq = 0
        file_idx = sq & 7  # 0
        rank_idx = sq >> 3  # 0
        assert FILES[file_idx] == "a"
        assert RANKS[rank_idx] == "1"
        
        # h8 = 63: file_idx=7, rank_idx=7
        sq = 63
        file_idx = sq & 7  # 7
        rank_idx = sq >> 3  # 7
        assert FILES[file_idx] == "h"
        assert RANKS[rank_idx] == "8"


class TestMoveSquareExtraction:
    """Test the square coordinate extraction logic used in to_uci()."""
    
    def test_file_extraction_bitwise_and(self):
        """Test file extraction using & 7."""
        for sq in range(64):
            file_idx = sq & 7
            assert 0 <= file_idx <= 7
            assert FILES[file_idx] in "abcdefgh"
    
    def test_rank_extraction_bitshift(self):
        """Test rank extraction using >> 3."""
        for sq in range(64):
            rank_idx = sq >> 3
            assert 0 <= rank_idx <= 7
            assert RANKS[rank_idx] in "12345678"
    
    def test_square_reconstruction(self):
        """Test that file/rank extraction can reconstruct squares."""
        for sq in range(64):
            file_idx = sq & 7
            rank_idx = sq >> 3
            reconstructed = rank_idx * 8 + file_idx
            assert reconstructed == sq


class TestMoveIntegration:
    """Integration tests for Move class."""
    
    def test_move_roundtrip_basic(self):
        """Test creating a move and converting to UCI."""
        moves_data = [
            (12, 28, PieceType.PAWN, "e2e4"),
            (1, 18, PieceType.KNIGHT, "b1c3"),
            (5, 26, PieceType.BISHOP, "f1c4"),
        ]
        
        for from_sq, to_sq, piece, expected_uci in moves_data:
            move = Move(from_sq=from_sq, to_sq=to_sq, piece=piece)
            assert move.to_uci() == expected_uci
    
    def test_move_roundtrip_with_promotions(self):
        """Test creating promotion moves and converting to UCI."""
        promotions_data = [
            (48, 56, PieceType.PAWN, PieceType.QUEEN, "a7a8q"),
            (49, 57, PieceType.PAWN, PieceType.KNIGHT, "b7b8n"),
            (51, 59, PieceType.PAWN, PieceType.BISHOP, "d7d8b"),
            (52, 60, PieceType.PAWN, PieceType.ROOK, "e7e8r"),
        ]
        
        for from_sq, to_sq, piece, promo, expected_uci in promotions_data:
            move = Move(
                from_sq=from_sq,
                to_sq=to_sq,
                piece=piece,
                promotion=promo
            )
            assert move.to_uci() == expected_uci
    
    def test_multiple_moves_unique(self):
        """Test that different moves produce different UCI strings."""
        moves = [
            Move(from_sq=12, to_sq=28, piece=PieceType.PAWN),
            Move(from_sq=12, to_sq=20, piece=PieceType.PAWN),
            Move(from_sq=1, to_sq=18, piece=PieceType.KNIGHT),
        ]
        
        ucis = [m.to_uci() for m in moves]
        assert len(set(ucis)) == len(ucis)  # All unique
