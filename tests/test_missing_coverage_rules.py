"""
Comprehensive test coverage for core/rules/draw.py and repetition.py missing lines.

Covers draw.py missing lines (19-46):
- is_insufficient_material for all piece combinations
- is_fifty_move_rule threshold check

Covers repetition.py missing lines (20-25):
- RepetitionTable.push/pop operations
- is_threefold detection
"""

import pytest
from core.board.board import Board
from core.rules.draw_repetition import is_insufficient_material, is_fifty_move_rule
from core.rules.draw_repetition import RepetitionTable
from utils.enums import Color, PieceType


class TestInsufficientMaterialKings:
    """Test is_insufficient_material for King vs King (lines 19-20)."""
    
    def test_king_vs_king_insufficient(self):
        """Test K vs K returns True (insufficient material)."""
        board = Board()
        board.clear()
        board.set_piece_at(0, Color.WHITE, PieceType.KING)
        board.set_piece_at(63, Color.BLACK, PieceType.KING)
        
        assert is_insufficient_material(board) is True


class TestInsufficientMaterialKingVsMinor:
    """Test is_insufficient_material for K vs K+Minor (lines 21-25)."""
    
    def test_king_vs_king_bishop_insufficient(self):
        """Test K vs K+B returns True (insufficient material, lines 21-22)."""
        board = Board()
        board.clear()
        board.set_piece_at(0, Color.WHITE, PieceType.KING)
        board.set_piece_at(7, Color.BLACK, PieceType.KING)
        board.set_piece_at(27, Color.BLACK, PieceType.BISHOP)
        
        assert is_insufficient_material(board) is True
    
    def test_king_vs_king_knight_insufficient(self):
        """Test K vs K+N returns True (insufficient material, lines 23-24)."""
        board = Board()
        board.clear()
        board.set_piece_at(0, Color.WHITE, PieceType.KING)
        board.set_piece_at(7, Color.BLACK, PieceType.KING)
        board.set_piece_at(27, Color.BLACK, PieceType.KNIGHT)
        
        assert is_insufficient_material(board) is True
    
    def test_king_bishop_vs_king_insufficient(self):
        """Test K+B vs K returns True (insufficient material, lines 26-27)."""
        board = Board()
        board.clear()
        board.set_piece_at(0, Color.WHITE, PieceType.KING)
        board.set_piece_at(27, Color.WHITE, PieceType.BISHOP)
        board.set_piece_at(63, Color.BLACK, PieceType.KING)
        
        assert is_insufficient_material(board) is True
    
    def test_king_knight_vs_king_insufficient(self):
        """Test K+N vs K returns True (insufficient material, lines 28-29)."""
        board = Board()
        board.clear()
        board.set_piece_at(0, Color.WHITE, PieceType.KING)
        board.set_piece_at(27, Color.WHITE, PieceType.KNIGHT)
        board.set_piece_at(63, Color.BLACK, PieceType.KING)
        
        assert is_insufficient_material(board) is True


class TestInsufficientMaterialKingBishopVsKingBishop:
    """Test is_insufficient_material for K+B vs K+B (lines 32-41)."""
    
    def test_king_bishop_vs_king_bishop_same_color_insufficient(self):
        """Test K+B vs K+B same color returns True (insufficient, lines 35-40)."""
        board = Board()
        board.clear()
        
        # Both bishops on same color (white square = a1, c1)
        board.set_piece_at(0, Color.WHITE, PieceType.KING)   # a1
        board.set_piece_at(2, Color.WHITE, PieceType.BISHOP)  # c1 (light square)

        board.set_piece_at(63, Color.BLACK, PieceType.KING)   # h8
        board.set_piece_at(61, Color.BLACK, PieceType.BISHOP) # f8 (light square)
        
        assert is_insufficient_material(board) is True
    
    def test_king_bishop_vs_king_bishop_opposite_colors_sufficient(self):
        """Test K+B vs K+B opposite colors returns False (sufficient, lines 35-40)."""
        board = Board()
        board.clear()
        
        # Bishops on different colors
        board.set_piece_at(0, Color.WHITE, PieceType.KING)   # a1
        board.set_piece_at(2, Color.WHITE, PieceType.BISHOP)  # c1 (light square)

        board.set_piece_at(63, Color.BLACK, PieceType.KING)   # h8
        board.set_piece_at(60, Color.BLACK, PieceType.BISHOP) # e8 (dark square)
        
        assert is_insufficient_material(board) is False


class TestInsufficientMaterialKingKnightVsKingKnight:
    """Test is_insufficient_material for K+N vs K+N (lines 42-44)."""
    
    def test_king_knight_vs_king_knight_insufficient(self):
        """Test K+N vs K+N returns True (insufficient, lines 42-44)."""
        board = Board()
        board.clear()
        
        board.set_piece_at(0, Color.WHITE, PieceType.KING)
        board.set_piece_at(1, Color.WHITE, PieceType.KNIGHT)

        board.set_piece_at(63, Color.BLACK, PieceType.KING)
        board.set_piece_at(62, Color.BLACK, PieceType.KNIGHT)
        
        assert is_insufficient_material(board) is True


class TestInsufficientMaterialWithPawns:
    """Test is_insufficient_material with pawns (sufficient material)."""
    
    def test_king_pawn_vs_king_sufficient(self):
        """Test K+P vs K returns False (sufficient because of pawn)."""
        board = Board()
        board.clear()
        
        board.set_piece_at(0, Color.WHITE, PieceType.KING)
        board.set_piece_at(8, Color.WHITE, PieceType.PAWN)

        board.set_piece_at(63, Color.BLACK, PieceType.KING)
        
        assert is_insufficient_material(board) is False
    
    def test_king_bishop_rook_vs_king_sufficient(self):
        """Test K+B+R vs K returns False (sufficient because of rook)."""
        board = Board()
        board.clear()
        
        board.set_piece_at(0, Color.WHITE, PieceType.KING)
        board.set_piece_at(1, Color.WHITE, PieceType.BISHOP)
        board.set_piece_at(2, Color.WHITE, PieceType.ROOK)

        board.set_piece_at(63, Color.BLACK, PieceType.KING)
        
        assert is_insufficient_material(board) is False


class TestFiftyMoveRule:
    """Test is_fifty_move_rule (line 45-46)."""
    
    def test_fifty_move_rule_not_reached(self):
        """Test fifty_move_rule returns False when halfmove_clock < 100."""
        board = Board()
        board.halfmove_clock = 50
        
        assert is_fifty_move_rule(board) is False
    
    def test_fifty_move_rule_exactly_100(self):
        """Test fifty_move_rule returns True when halfmove_clock == 100."""
        board = Board()
        board.halfmove_clock = 100
        
        assert is_fifty_move_rule(board) is True
    
    def test_fifty_move_rule_exceeded(self):
        """Test fifty_move_rule returns True when halfmove_clock > 100."""
        board = Board()
        board.halfmove_clock = 150
        
        assert is_fifty_move_rule(board) is True


class TestRepetitionTablePush:
    """Test RepetitionTable.push (line 20-21)."""
    
    def test_repetition_push_single_key(self):
        """Test push adds key to table."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        
        assert table._count[zobrist_key] == 1
        assert zobrist_key in table._stack
    
    def test_repetition_push_same_key_twice(self):
        """Test push increments count for repeated key."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        table.push(zobrist_key)
        
        assert table._count[zobrist_key] == 2
        assert len(table._stack) == 2
    
    def test_repetition_push_different_keys(self):
        """Test push adds different keys independently."""
        table = RepetitionTable()
        key1 = 0x1111111111111111
        key2 = 0x2222222222222222
        
        table.push(key1)
        table.push(key2)
        
        assert table._count[key1] == 1
        assert table._count[key2] == 1
        assert len(table._stack) == 2


class TestRepetitionTablePop:
    """Test RepetitionTable.pop (line 22-26)."""
    
    def test_repetition_pop_single_key(self):
        """Test pop removes key from table."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        table.pop()
        
        assert zobrist_key not in table._count
        assert len(table._stack) == 0
    
    def test_repetition_pop_repeated_key(self):
        """Test pop decrements count for repeated keys."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        table.push(zobrist_key)
        table.pop()
        
        assert table._count[zobrist_key] == 1
        assert len(table._stack) == 1
    
    def test_repetition_pop_removes_entry_when_zero(self):
        """Test pop removes entry when count reaches zero."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        table.push(zobrist_key)
        table.pop()
        table.pop()
        
        assert zobrist_key not in table._count


class TestRepetitionTableIsThreefold:
    """Test RepetitionTable.is_threefold (line 25)."""
    
    def test_is_threefold_not_reached(self):
        """Test is_threefold returns False when count < 3."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        table.push(zobrist_key)
        
        assert table.is_threefold(zobrist_key) is False
    
    def test_is_threefold_exactly_three(self):
        """Test is_threefold returns True when count == 3 (line 25)."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        table.push(zobrist_key)
        table.push(zobrist_key)
        
        assert table.is_threefold(zobrist_key) is True
    
    def test_is_threefold_exceeded(self):
        """Test is_threefold returns True when count > 3."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        table.push(zobrist_key)
        table.push(zobrist_key)
        table.push(zobrist_key)
        
        assert table.is_threefold(zobrist_key) is True
    
    def test_is_threefold_unknown_key(self):
        """Test is_threefold returns False for unknown key."""
        table = RepetitionTable()
        unknown_key = 0x9999999999999999
        
        assert table.is_threefold(unknown_key) is False
    
    def test_is_threefold_after_pop(self):
        """Test is_threefold correctly reflects count after pop."""
        table = RepetitionTable()
        zobrist_key = 0x1234567890ABCDEF
        
        table.push(zobrist_key)
        table.push(zobrist_key)
        table.push(zobrist_key)
        assert table.is_threefold(zobrist_key) is True
        
        table.pop()
        assert table.is_threefold(zobrist_key) is False


class TestRepetitionTableIntegration:
    """Integration tests for RepetitionTable workflow."""
    
    def test_repetition_game_sequence(self):
        """Test typical game sequence with position repetitions."""
        table = RepetitionTable()
        
        # Simulate a back-and-forth that leads to a threefold repetition
        pos1 = 0x1111111111111111
        pos2 = 0x2222222222222222

        # Sequence: pos1, pos2, pos1, pos2, pos1 -> pos1 occurs 3 times
        table.push(pos1)
        table.push(pos2)
        table.push(pos1)
        table.push(pos2)
        table.push(pos1)

        assert table.is_threefold(pos1) is True
