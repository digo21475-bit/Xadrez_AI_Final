"""
Comprehensive test coverage for core/perft/perft.py missing lines.

Covers:
- _move_to_key fast path with bytes and string fallbacks
- perft_divide error handling (depth < 1)
- perft_iterative core loops and stack operations
"""

import pytest
from core.board.board import Board
from core.perft.perft import _move_to_key, perft, perft_divide, perft_iterative
from core.moves.move import Move
from utils.enums import PieceType, Color


class MockMove:
    """Mock move object for testing _move_to_key paths."""
    
    def __init__(self, uci_returns=None, uci_returns_bytes=False, has_no_uci=False):
        self.uci_returns = uci_returns
        self.uci_returns_bytes = uci_returns_bytes
        self.has_no_uci = has_no_uci
    
    def uci(self):
        if self.uci_returns_bytes:
            return b"e2e4"
        return self.uci_returns
    
    def __getattr__(self, name):
        if name == "uci" and self.has_no_uci:
            raise AttributeError("No uci method")
        raise AttributeError(f"Mock has no attribute {name}")
    
    def __str__(self):
        return "e2e4"


class TestMoveToKeyFastPaths:
    """Test _move_to_key with different return types (lines 19-22)."""
    
    def test_move_to_key_with_uci_string(self):
        """Test when move.uci() returns a string."""
        move = MockMove(uci_returns="e2e4")
        result = _move_to_key(move)
        assert result == "e2e4"
    
    def test_move_to_key_with_uci_bytes(self):
        """Test when move.uci() returns bytes (line 20)."""
        move = MockMove(uci_returns_bytes=True)
        result = _move_to_key(move)
        assert result == "e2e4"
    
    def test_move_to_key_without_uci_method(self):
        """Test fallback when move has no uci method (lines 21-22)."""
        move = MockMove(has_no_uci=True)
        move.__dict__['uci'] = None  # simulate no uci attribute
        
        class FallbackMove:
            def __str__(self):
                return "e2e4_str"
        
        fallback_move = FallbackMove()
        result = _move_to_key(fallback_move)
        assert result == "e2e4_str"


class TestPerftDivideErrorHandling:
    """Test perft_divide error conditions (line 58)."""
    
    def test_perft_divide_depth_zero_raises_error(self):
        """Test that perft_divide with depth < 1 raises ValueError (line 58)."""
        board = Board()
        with pytest.raises(ValueError, match="perft_divide requer depth >= 1"):
            perft_divide(board, 0)
    
    def test_perft_divide_negative_depth_raises_error(self):
        """Test that perft_divide with negative depth raises ValueError."""
        board = Board()
        with pytest.raises(ValueError, match="perft_divide requer depth >= 1"):
            perft_divide(board, -1)


class TestPerftIterativeLogic:
    """Test perft_iterative implementation (lines 95-128)."""
    
    def test_perft_iterative_depth_zero(self):
        """Test iterative perft with depth 0 returns 1."""
        board = Board()
        result = perft_iterative(board, 0)
        assert result == 1
    
    def test_perft_iterative_startpos_depth_1(self):
        """Test iterative perft on starting position, depth 1 (20 moves)."""
        board = Board()
        result = perft_iterative(board, 1)
        assert result == 20
    
    def test_perft_iterative_vs_recursive_depth_2(self):
        """Compare iterative vs recursive at depth 2 (should match)."""
        board = Board()
        iterative_result = perft_iterative(board, 2)
        
        board2 = Board()
        recursive_result = perft(board2, 2)
        
        assert iterative_result == recursive_result
    
    def test_perft_iterative_stack_operations(self):
        """Test that iterative perft correctly manages the stack during traversal."""
        # Starting position has specific move counts
        board = Board()
        result = perft_iterative(board, 1)
        assert result == 20  # 20 legal moves from start
    
    def test_perft_iterative_deep_position(self):
        """Test iterative perft on a standard deep position."""
        # Position after 1.e4 e5
        board = Board()
        board.set_fen("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2")
        
        # Compare both implementations
        iter_result = perft_iterative(board, 1)
        
        board2 = Board()
        board2.set_fen("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2")
        rec_result = perft(board2, 1)
        
        assert iter_result == rec_result


class TestPerftDivideOutput:
    """Test perft_divide outputs and sorting (lines 95-128)."""
    
    def test_perft_divide_returns_total(self, capsys):
        """Test that perft_divide returns correct total and prints sorted output."""
        board = Board()
        result = perft_divide(board, 1)
        
        # Starting position has 20 legal moves
        assert result == 20
        
        # Verify output was printed
        captured = capsys.readouterr()
        assert "PERFT DIVIDE" in captured.out
        assert "TOTAL: 20" in captured.out
    
    def test_perft_divide_depth_2(self, capsys):
        """Test perft_divide at depth 2."""
        board = Board()
        result = perft_divide(board, 2)
        
        # Verify reasonable result
        assert result >= 400  # Expected around 400 nodes


class TestIntegrationPerftConsistency:
    """Integration tests ensuring all perft variants are consistent."""
    
    def test_recursive_vs_iterative_consistency_depth_3(self):
        """Ensure recursive and iterative perft give same results at depth 3."""
        board = Board()
        rec_result = perft(board, 3)
        
        board2 = Board()
        iter_result = perft_iterative(board2, 3)
        
        assert rec_result == iter_result
    
    def test_perft_divide_vs_perft_consistency(self, capsys):
        """Ensure perft_divide total matches perft result."""
        board1 = Board()
        divide_total = perft_divide(board1, 1)
        
        board2 = Board()
        perft_total = perft(board2, 1)
        
        assert divide_total == perft_total
