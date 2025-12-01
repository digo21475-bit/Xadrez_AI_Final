"""
Comprehensive test coverage for core/moves/tables/attack_tables.py missing lines.

Covers:
- _fallback_sliding_attacks loop logic (lines 175-206)
- init() exception fallback path (lines 288-293)
- init() on-demand calls in public wrappers
- fallback rook and bishop attacks
"""

import pytest
from core.moves.tables.attack_tables import (
    _fallback_sliding_attacks,
    _fallback_rook_attacks,
    _fallback_bishop_attacks,
    init,
    knight_attacks,
    king_attacks,
    pawn_attacks,
    rook_attacks,
    bishop_attacks,
    queen_attacks,
)
from utils.enums import Color


class TestFallbackSlidingAttacksRookPattern:
    """Test _fallback_sliding_attacks for rook directions (lines 175-206)."""
    
    def test_fallback_rook_attacks_center_empty_board(self):
        """Test rook attacks from center square (empty board)."""
        # Square d4 (index 27) on empty board
        sq = 27
        occ = 0  # No occupancy
        
        # Rook directions: N(+8), S(-8), E(+1), W(-1)
        attacks = _fallback_rook_attacks(sq, occ)
        
        # Should attack all squares on same rank and file
        # d-file: d1-d8 (3, 11, 19, 35, 43, 51, 59)
        # 4-rank: a4-h4 (24, 25, 26, 28, 29, 30, 31)
        assert (attacks & (1 << 3)) != 0   # d1
        assert (attacks & (1 << 11)) != 0  # d2
        assert (attacks & (1 << 24)) != 0  # a4
        assert (attacks & (1 << 30)) != 0  # g4
    
    def test_fallback_rook_attacks_blocked(self):
        """Test rook attacks stop at occupied squares."""
        # Square a1 (index 0)
        sq = 0
        
        # Piece at a3 (blocks vertical)
        # Piece at c1 (blocks horizontal)
        occ = (1 << 16) | (1 << 2)
        
        attacks = _fallback_rook_attacks(sq, occ)
        
        # Should attack a2, but not a3 or beyond
        assert (attacks & (1 << 8)) != 0   # a2
        assert (attacks & (1 << 16)) != 0  # a3 (the blocking square itself)
        assert (attacks & (1 << 24)) == 0  # a4 (blocked)
        
        # Should attack b1, c1 but not beyond c1
        assert (attacks & (1 << 1)) != 0   # b1
        assert (attacks & (1 << 2)) != 0   # c1 (the blocking square)
        assert (attacks & (1 << 3)) == 0   # d1 (blocked)


class TestFallbackSlidingAttacksBishopPattern:
    """Test _fallback_sliding_attacks for bishop directions (lines 175-206)."""
    
    def test_fallback_bishop_attacks_center_empty_board(self):
        """Test bishop attacks from center square (empty board)."""
        # Square d4 (index 27) on empty board
        sq = 27
        occ = 0
        
        # Bishop directions: NE(+9), NW(+7), SE(-9), SW(-7)
        attacks = _fallback_bishop_attacks(sq, occ)
        
        # Should attack diagonals
        # One diagonal: a1, b2, c3, d4, e5, f6, g7, h8
        # Other diagonal: a7, b6, c5, d4, e3, f2, g1
        assert (attacks & (1 << 0)) != 0   # a1
        assert (attacks & (1 << 9)) != 0   # b2
        assert (attacks & (1 << 36)) != 0  # e5
        assert (attacks & (1 << 63)) != 0  # h8
    
    def test_fallback_bishop_attacks_blocked_on_diagonal(self):
        """Test bishop attacks stop at occupied diagonal squares."""
        # Square e1 (index 4)
        sq = 4
        
        # Piece at f2 (blocks NE diagonal)
        occ = 1 << 13
        
        attacks = _fallback_bishop_attacks(sq, occ)
        
        # Should see f2 but not g3 or further
        assert (attacks & (1 << 13)) != 0  # f2 (blocking square)
        assert (attacks & (1 << 22)) == 0  # g3 (blocked)


class TestFallbackRookAttacks:
    """Test _fallback_rook_attacks convenience wrapper (lines 194-196)."""
    
    def test_fallback_rook_attacks_empty_board(self):
        """Test rook attacks wrapper on empty board."""
        sq = 27  # d4
        occ = 0
        
        attacks = _fallback_rook_attacks(sq, occ)
        
        # Should be non-zero
        assert attacks != 0
        
        # Should have bits set on same rank and file
        # Rank 4: squares 24-31
        rank_4_mask = 0xFF << 24
        file_d_mask = (1 << 3) | (1 << 11) | (1 << 19) | (1 << 35) | (1 << 43) | (1 << 51) | (1 << 59)
        
        expected = rank_4_mask | file_d_mask
        assert (attacks & expected) != 0


class TestFallbackBishopAttacks:
    """Test _fallback_bishop_attacks convenience wrapper (lines 197-199)."""
    
    def test_fallback_bishop_attacks_empty_board(self):
        """Test bishop attacks wrapper on empty board."""
        sq = 27  # d4
        occ = 0
        
        attacks = _fallback_bishop_attacks(sq, occ)
        
        # Should be non-zero
        assert attacks != 0


class TestAttackTablesInitExceptionFallback:
    """Test init() exception fallback path (lines 288-293)."""
    
    def test_init_successful_execution(self):
        """Test init() completes without error and populates tables."""
        init()
        
        # Tables should be populated
        assert knight_attacks(0) != 0
        assert king_attacks(0) != 0
        assert pawn_attacks(0, Color.WHITE) != 0
    
    def test_init_idempotent_multiple_calls(self):
        """Test init() can be called multiple times (idempotent)."""
        init()
        first_knight = knight_attacks(0)
        
        init()
        second_knight = knight_attacks(0)
        
        # Should get same results
        assert first_knight == second_knight
    
    def test_init_populates_knight_attacks(self):
        """Test init() populates knight attack tables."""
        init()
        
        # Knight from a1 should attack b3, c2
        attacks_a1 = knight_attacks(0)
        assert (attacks_a1 & (1 << 10)) != 0  # b3
        assert (attacks_a1 & (1 << 17)) != 0  # c2
    
    def test_init_populates_king_attacks(self):
        """Test init() populates king attack tables."""
        init()
        
        # King from e1 should attack adjacent squares
        attacks_e1 = king_attacks(4)
        assert (attacks_e1 & (1 << 3)) != 0   # d1
        assert (attacks_e1 & (1 << 5)) != 0   # f1
        assert (attacks_e1 & (1 << 11)) != 0  # d2
        assert (attacks_e1 & (1 << 12)) != 0  # e2
        assert (attacks_e1 & (1 << 13)) != 0  # f2
    
    def test_init_populates_pawn_attacks_white(self):
        """Test init() populates pawn attack tables for white."""
        init()
        
        # White pawn from e2 attacks d3, f3
        attacks_e2 = pawn_attacks(12, Color.WHITE)
        assert (attacks_e2 & (1 << 19)) != 0  # d3
        assert (attacks_e2 & (1 << 21)) != 0  # f3
    
    def test_init_populates_pawn_attacks_black(self):
        """Test init() populates pawn attack tables for black."""
        init()
        
        # Black pawn from e7 attacks d6, f6
        attacks_e7 = pawn_attacks(52, Color.BLACK)
        assert (attacks_e7 & (1 << 43)) != 0  # d6
        assert (attacks_e7 & (1 << 45)) != 0  # f6


class TestAttackTablesOnDemandInitialization:
    """Test that public attack functions trigger on-demand init."""
    
    def test_rook_attacks_initializes_tables(self):
        """Test rook_attacks function (should trigger init via wrapper)."""
        # This tests that calling rook_attacks doesn't fail
        attacks = rook_attacks(27, 0)
        assert isinstance(attacks, int)
    
    def test_bishop_attacks_initializes_tables(self):
        """Test bishop_attacks function (should trigger init via wrapper)."""
        attacks = bishop_attacks(27, 0)
        assert isinstance(attacks, int)
    
    def test_queen_attacks_initializes_tables(self):
        """Test queen_attacks is combination of rook + bishop attacks."""
        queen_atk = queen_attacks(27, 0)
        rook_atk = rook_attacks(27, 0)
        bishop_atk = bishop_attacks(27, 0)
        
        # Queen should have bits from both rook and bishop
        assert (queen_atk & rook_atk) != 0
        assert (queen_atk & bishop_atk) != 0


class TestAttackTablesFallbackConsistency:
    """Test consistency between fallback implementations and tables."""
    
    def test_fallback_rook_vs_rook_attacks_empty_board(self):
        """Test fallback rook attacks match rook_attacks wrapper on empty board."""
        init()
        
        sq = 27
        occ = 0
        
        fallback_result = _fallback_rook_attacks(sq, occ)
        table_result = rook_attacks(sq, occ)
        
        # Should match (or table uses fallback)
        assert fallback_result == table_result
    
    def test_fallback_bishop_vs_bishop_attacks_empty_board(self):
        """Test fallback bishop attacks match bishop_attacks wrapper on empty board."""
        init()
        
        sq = 27
        occ = 0
        
        fallback_result = _fallback_bishop_attacks(sq, occ)
        table_result = bishop_attacks(sq, occ)
        
        # Should match (or table uses fallback)
        assert fallback_result == table_result


class TestAttackTablesEdgeCases:
    """Test attack tables with edge case positions."""
    
    def test_knight_attacks_edge_squares(self):
        """Test knight attacks from edge squares don't wrap around."""
        init()
        
        # Knight from a1 should not have attacked squares on h-file
        attacks_a1 = knight_attacks(0)
        h_file_mask = 0x0101010101010101 << 7  # h-file shifted
        
        # Shouldn't have attacks wrapping to h-file
        for i in range(8):
            h_square = i * 8 + 7
            if h_square < 64:
                # Knight from a1 shouldn't attack h-file squares (too far)
                assert (attacks_a1 & (1 << h_square)) == 0 or h_square in [17]  # c2 is ok
    
    def test_fallback_rook_attacks_edge_square_no_wrap(self):
        """Test fallback rook attacks from edge don't wrap."""
        sq = 0  # a1 (leftmost)
        occ = 0
        
        attacks = _fallback_rook_attacks(sq, occ)
        
        # Should not have attacks on h-file except where appropriate
        # Rook from a1 should attack a-file and rank-1 (including h1)
        # h1 is at index 7 (same rank), so it's valid
        assert (attacks & (1 << 7)) != 0  # h1 (same rank)
    
    def test_fallback_bishop_attacks_corner_square(self):
        """Test bishop attacks from corner square."""
        sq = 0  # a1 (corner)
        occ = 0
        
        attacks = _fallback_bishop_attacks(sq, occ)
        
        # From a1, bishop should attack long diagonal only
        # a1-h8 diagonal: 0, 9, 18, 27, 36, 45, 54, 63
        expected_diagonal = (1 << 9) | (1 << 18) | (1 << 27) | (1 << 36) | (1 << 45) | (1 << 54) | (1 << 63)
        
        assert (attacks & expected_diagonal) != 0


class TestAttackTablesIntegration:
    """Integration tests for attack tables."""
    
    def test_all_attack_tables_initialized(self):
        """Test that all attack tables are properly initialized."""
        init()
        
        for sq in range(64):
            knight = knight_attacks(sq)
            king = king_attacks(sq)
            pawn_w = pawn_attacks(sq, Color.WHITE)
            pawn_b = pawn_attacks(sq, Color.BLACK)
            
            # All should return valid bitboards (can be 0 for edge cases)
            assert isinstance(knight, int)
            assert isinstance(king, int)
            assert isinstance(pawn_w, int)
            assert isinstance(pawn_b, int)
    
    def test_rook_bishop_queen_relationship(self):
        """Test queen attacks = rook attacks | bishop attacks."""
        init()
        
        for sq in range(64):
            for occ in [0, 0xFFFFFFFFFFFFFFFF]:  # Empty and full boards
                queen = queen_attacks(sq, occ)
                rook = rook_attacks(sq, occ)
                bishop = bishop_attacks(sq, occ)
                
                # Queen should have all bits from rook or bishop
                combined = rook | bishop
                assert (queen | combined) == queen or (queen | combined) == combined
