"""
Comprehensive test coverage for core/rules/game_status.py missing lines.

Covers:
- GameOverReason enum values
- GameStatus dataclass properties and equality
- GameStatus convenience properties (is_checkmate, is_stalemate, etc.)
- get_game_status edge cases and all result types
"""

import pytest
from core.board.board import Board
from core.rules.game_status import (
    GameStatus,
    GameOverReason,
    get_game_status,
)
from core.rules.draw_repetition import RepetitionTable
from core.moves.legal_movegen import generate_legal_moves
from utils.enums import GameResult, Color


class TestGameOverReasonEnum:
    """Test GameOverReason enum values."""
    
    def test_game_over_reason_checkmate(self):
        """Test GameOverReason.CHECKMATE exists."""
        assert GameOverReason.CHECKMATE is not None
    
    def test_game_over_reason_stalemate(self):
        """Test GameOverReason.STALEMATE exists."""
        assert GameOverReason.STALEMATE is not None
    
    def test_game_over_reason_repetition(self):
        """Test GameOverReason.REPETITION exists."""
        assert GameOverReason.REPETITION is not None
    
    def test_game_over_reason_fifty_move(self):
        """Test GameOverReason.FIFTY_MOVE exists."""
        assert GameOverReason.FIFTY_MOVE is not None
    
    def test_game_over_reason_insufficient_material(self):
        """Test GameOverReason.INSUFFICIENT_MATERIAL exists."""
        assert GameOverReason.INSUFFICIENT_MATERIAL is not None
    
    def test_game_over_reason_all_different(self):
        """Test that all reasons are distinct."""
        reasons = [
            GameOverReason.CHECKMATE,
            GameOverReason.STALEMATE,
            GameOverReason.REPETITION,
            GameOverReason.FIFTY_MOVE,
            GameOverReason.INSUFFICIENT_MATERIAL,
        ]
        # All should be unique (enum auto())
        assert len(set(reasons)) == 5


class TestGameStatusDataclass:
    """Test GameStatus dataclass structure and frozen property."""
    
    def test_game_status_creation_minimal(self):
        """Test GameStatus creation with minimal parameters."""
        status = GameStatus(
            is_game_over=False,
            result=GameResult.ONGOING
        )
        
        assert status.is_game_over is False
        assert status.result == GameResult.ONGOING
        assert status.reason is None
    
    def test_game_status_creation_with_reason(self):
        """Test GameStatus creation with reason."""
        status = GameStatus(
            is_game_over=True,
            result=GameResult.WHITE_WIN,
            reason=GameOverReason.CHECKMATE
        )
        
        assert status.is_game_over is True
        assert status.result == GameResult.WHITE_WIN
        assert status.reason == GameOverReason.CHECKMATE
    
    def test_game_status_frozen(self):
        """Test that GameStatus is frozen (immutable)."""
        status = GameStatus(
            is_game_over=False,
            result=GameResult.ONGOING
        )
        
        with pytest.raises(Exception):
            status.is_game_over = True


class TestGameStatusEquality:
    """Test GameStatus equality with GameResult and other GameStatus."""
    
    def test_game_status_equality_with_game_result(self):
        """Test GameStatus == GameResult comparison (line 38)."""
        status = GameStatus(
            is_game_over=False,
            result=GameResult.ONGOING
        )
        
        # Should be equal to the GameResult
        assert status == GameResult.ONGOING
    
    def test_game_status_equality_with_game_result_mismatch(self):
        """Test GameStatus != GameResult when results differ."""
        status = GameStatus(
            is_game_over=True,
            result=GameResult.WHITE_WIN,
            reason=GameOverReason.CHECKMATE
        )
        
        assert status != GameResult.DRAW_STALEMATE
        assert status != GameResult.ONGOING
    
    def test_game_status_equality_with_same_status(self):
        """Test GameStatus == GameStatus with same values (line 45-48)."""
        status1 = GameStatus(
            is_game_over=True,
            result=GameResult.WHITE_WIN,
            reason=GameOverReason.CHECKMATE
        )
        
        status2 = GameStatus(
            is_game_over=True,
            result=GameResult.WHITE_WIN,
            reason=GameOverReason.CHECKMATE
        )
        
        assert status1 == status2
    
    def test_game_status_equality_with_different_status(self):
        """Test GameStatus != GameStatus with different values."""
        status1 = GameStatus(
            is_game_over=True,
            result=GameResult.WHITE_WIN,
            reason=GameOverReason.CHECKMATE
        )
        
        status2 = GameStatus(
            is_game_over=True,
            result=GameResult.BLACK_WIN,
            reason=GameOverReason.CHECKMATE
        )
        
        assert status1 != status2
    
    def test_game_status_equality_different_reason(self):
        """Test GameStatus != GameStatus with different reason."""
        status1 = GameStatus(
            is_game_over=True,
            result=GameResult.DRAW_STALEMATE,
            reason=GameOverReason.STALEMATE
        )
        
        status2 = GameStatus(
            is_game_over=True,
            result=GameResult.DRAW_STALEMATE,
            reason=GameOverReason.FIFTY_MOVE
        )
        
        assert status1 != status2
    
    def test_game_status_equality_with_non_game_status_object(self):
        """Test GameStatus != non-GameStatus object (line 42)."""
        status = GameStatus(
            is_game_over=False,
            result=GameResult.ONGOING
        )
        
        assert status != "not a status"
        assert status != 42
        assert status != None


class TestGameStatusProperties:
    """Test GameStatus convenience properties."""
    
    def test_is_checkmate_property(self):
        """Test is_checkmate property (line 51-52)."""
        status_checkmate = GameStatus(
            is_game_over=True,
            result=GameResult.WHITE_WIN,
            reason=GameOverReason.CHECKMATE
        )
        
        assert status_checkmate.is_checkmate is True
    
    def test_is_checkmate_property_false(self):
        """Test is_checkmate property returns False for other reasons."""
        status_stalemate = GameStatus(
            is_game_over=True,
            result=GameResult.DRAW_STALEMATE,
            reason=GameOverReason.STALEMATE
        )
        
        assert status_stalemate.is_checkmate is False
    
    def test_is_stalemate_property(self):
        """Test is_stalemate property (line 54-55)."""
        status_stalemate = GameStatus(
            is_game_over=True,
            result=GameResult.DRAW_STALEMATE,
            reason=GameOverReason.STALEMATE
        )
        
        assert status_stalemate.is_stalemate is True
    
    def test_is_stalemate_property_false(self):
        """Test is_stalemate property returns False for other reasons."""
        status_checkmate = GameStatus(
            is_game_over=True,
            result=GameResult.WHITE_WIN,
            reason=GameOverReason.CHECKMATE
        )
        
        assert status_checkmate.is_stalemate is False
    
    def test_is_draw_by_repetition_property(self):
        """Test is_draw_by_repetition property (line 57-58)."""
        status_repetition = GameStatus(
            is_game_over=True,
            result=GameResult.DRAW_REPETITION,
            reason=GameOverReason.REPETITION
        )
        
        assert status_repetition.is_draw_by_repetition is True
    
    def test_is_draw_by_repetition_property_false_not_game_over(self):
        """Test is_draw_by_repetition returns False when game not over (line 57)."""
        status = GameStatus(
            is_game_over=False,
            result=GameResult.ONGOING,
            reason=None
        )
        
        assert status.is_draw_by_repetition is False
    
    def test_is_draw_by_repetition_property_false_wrong_reason(self):
        """Test is_draw_by_repetition returns False for other reasons."""
        status_fifty = GameStatus(
            is_game_over=True,
            result=GameResult.DRAW_FIFTY_MOVE,
            reason=GameOverReason.FIFTY_MOVE
        )
        
        assert status_fifty.is_draw_by_repetition is False
    
    def test_is_draw_by_fifty_move_property(self):
        """Test is_draw_by_fifty_move property (line 60-61)."""
        status_fifty = GameStatus(
            is_game_over=True,
            result=GameResult.DRAW_FIFTY_MOVE,
            reason=GameOverReason.FIFTY_MOVE
        )
        
        assert status_fifty.is_draw_by_fifty_move is True
    
    def test_is_draw_by_fifty_move_property_false_not_game_over(self):
        """Test is_draw_by_fifty_move returns False when game not over (line 60)."""
        status = GameStatus(
            is_game_over=False,
            result=GameResult.ONGOING,
            reason=None
        )
        
        assert status.is_draw_by_fifty_move is False
    
    def test_is_insufficient_material_property(self):
        """Test is_insufficient_material property (line 63-64)."""
        status_insufficient = GameStatus(
            is_game_over=True,
            result=GameResult.DRAW_INSUFFICIENT_MATERIAL,
            reason=GameOverReason.INSUFFICIENT_MATERIAL
        )
        
        assert status_insufficient.is_insufficient_material is True
    
    def test_is_insufficient_material_property_false_not_game_over(self):
        """Test is_insufficient_material returns False when game not over (line 63)."""
        status = GameStatus(
            is_game_over=False,
            result=GameResult.ONGOING,
            reason=None
        )
        
        assert status.is_insufficient_material is False


class TestGetGameStatusCheckmate:
    """Test get_game_status for checkmate positions."""
    
    def test_get_game_status_checkmate_white_delivers(self):
        """Test checkmate with white delivering mate."""
        # White queen on g7, black king on h8, white king on h6
        board = Board.from_fen("7k/6Q1/7K/8/8/8/8/8 b - - 0 1")
        
        status = get_game_status(board)
        
        assert status.is_game_over is True
        assert status.result == GameResult.WHITE_WIN
        assert status.reason == GameOverReason.CHECKMATE
        assert status.is_checkmate is True


class TestGetGameStatusStalemate:
    """Test get_game_status for stalemate positions."""
    
    def test_get_game_status_stalemate_classic(self):
        """Test classic stalemate position."""
        # King on h8, queen on f6, white king on f5
        board = Board.from_fen("7k/5Q2/5K2/8/8/8/8/8 b - - 0 1")
        
        status = get_game_status(board)
        
        assert status.is_game_over is True
        assert status.result == GameResult.DRAW_STALEMATE
        assert status.reason == GameOverReason.STALEMATE
        assert status.is_stalemate is True


class TestGetGameStatusRepetition:
    """Test get_game_status for threefold repetition."""
    
    def test_get_game_status_repetition_threefold(self):
        """Test threefold repetition detection."""
        board = Board.from_fen("8/8/8/8/8/6N1/5K2/6k1 w - - 0 1")
        
        repetition_table = RepetitionTable()
        repetition_table.push(board.zobrist_key)
        
        # Simulate moves that repeat position
        for _ in range(2):
            white_move = list(generate_legal_moves(board))[0]
            board.make_move(white_move)
            repetition_table.push(board.zobrist_key)
            
            black_move = list(generate_legal_moves(board))[0]
            board.make_move(black_move)
            repetition_table.push(board.zobrist_key)
            
            board.unmake_move()
            repetition_table.push(board.zobrist_key)
            
            board.unmake_move()
            repetition_table.push(board.zobrist_key)
        
        status = get_game_status(board, repetition_table)
        
        assert status.is_game_over is True
        assert status.result == GameResult.DRAW_REPETITION
        assert status.reason == GameOverReason.REPETITION
        assert status.is_draw_by_repetition is True
    
    def test_get_game_status_no_repetition_without_table(self):
        """Test no repetition when repetition_table is None."""
        board = Board.from_fen("8/8/8/8/8/6N1/5K2/6k1 w - - 0 1")
        
        # No repetition_table passed
        status = get_game_status(board, repetition_table=None)
        
        assert status.is_draw_by_repetition is False


class TestGetGameStatusFiftyMoveRule:
    """Test get_game_status for fifty move rule."""
    
    def test_get_game_status_fifty_move_rule_triggered(self):
        """Test fifty move rule when halfmove_clock >= 100."""
        board = Board.from_fen("8/8/8/8/8/8/5K2/6k1 w - - 100 75")
        
        status = get_game_status(board)
        
        assert status.is_game_over is True
        assert status.result == GameResult.DRAW_FIFTY_MOVE
        assert status.reason == GameOverReason.FIFTY_MOVE
        assert status.is_draw_by_fifty_move is True
    
    def test_get_game_status_fifty_move_rule_not_triggered(self):
        """Test fifty move rule not triggered before 100 plies."""
        board = Board.from_fen("8/8/8/8/8/8/5K2/6k1 w - - 50 75")
        
        status = get_game_status(board)
        
        # Should be ongoing (not checkmate, not stalemate, etc.)
        assert status.is_draw_by_fifty_move is False


class TestGetGameStatusInsufficientMaterial:
    """Test get_game_status for insufficient material."""
    
    def test_get_game_status_insufficient_material_k_vs_k(self):
        """Test insufficient material for K vs K."""
        board = Board.from_fen("8/8/8/8/8/8/5K2/6k1 w - - 0 1")
        
        status = get_game_status(board)
        
        assert status.is_game_over is True
        assert status.result == GameResult.DRAW_INSUFFICIENT_MATERIAL
        assert status.reason == GameOverReason.INSUFFICIENT_MATERIAL
        assert status.is_insufficient_material is True
    
    def test_get_game_status_insufficient_material_k_b_vs_k(self):
        """Test insufficient material for K+B vs K."""
        board = Board.from_fen("8/8/8/8/8/8/5K2/6kB w - - 0 1")
        
        status = get_game_status(board)
        
        assert status.is_game_over is True
        assert status.result == GameResult.DRAW_INSUFFICIENT_MATERIAL
        assert status.reason == GameOverReason.INSUFFICIENT_MATERIAL


class TestGetGameStatusOngoing:
    """Test get_game_status for ongoing games."""
    
    def test_get_game_status_ongoing_startpos(self):
        """Test ongoing game at startpos."""
        board = Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        
        status = get_game_status(board)
        
        assert status.is_game_over is False
        assert status.result == GameResult.ONGOING
        assert status.reason is None
    
    def test_get_game_status_ongoing_after_moves(self):
        """Test ongoing game after some moves."""
        board = Board.from_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
        
        status = get_game_status(board)
        
        assert status.is_game_over is False
        assert status.result == GameResult.ONGOING


class TestGetGameStatusCheckPriority:
    """Test priority of game status detection."""
    
    def test_checkmate_detected_before_other_checks(self):
        """Test that checkmate is detected even without repetition table."""
        board = Board.from_fen("7k/6Q1/7K/8/8/8/8/8 b - - 0 1")
        
        # Don't pass repetition table
        status = get_game_status(board)
        
        assert status.reason == GameOverReason.CHECKMATE
    
    def test_stalemate_detected_before_other_checks(self):
        """Test that stalemate is detected even without repetition table."""
        board = Board.from_fen("7k/5Q2/5K2/8/8/8/8/8 b - - 0 1")
        
        status = get_game_status(board)
        
        assert status.reason == GameOverReason.STALEMATE
    
    def test_repetition_checked_before_fifty_move(self):
        """Test repetition is checked before fifty move rule."""
        board = Board.from_fen("8/8/8/8/8/6N1/5K2/6k1 w - - 100 75")
        
        repetition_table = RepetitionTable()
        # Force threefold
        zobrist = board.zobrist_key
        repetition_table.push(zobrist)
        repetition_table.push(zobrist)
        repetition_table.push(zobrist)
        
        status = get_game_status(board, repetition_table)
        
        # Should be repetition, not fifty move
        assert status.reason == GameOverReason.REPETITION


class TestGameStatusIntegration:
    """Integration tests for game status functionality."""
    
    def test_game_status_all_draw_types(self):
        """Test all draw types can be represented."""
        draws = [
            (GameResult.DRAW_STALEMATE, GameOverReason.STALEMATE),
            (GameResult.DRAW_REPETITION, GameOverReason.REPETITION),
            (GameResult.DRAW_FIFTY_MOVE, GameOverReason.FIFTY_MOVE),
            (GameResult.DRAW_INSUFFICIENT_MATERIAL, GameOverReason.INSUFFICIENT_MATERIAL),
        ]
        
        for draw_result, draw_reason in draws:
            status = GameStatus(
                is_game_over=True,
                result=draw_result,
                reason=draw_reason
            )
            
            assert status.is_game_over is True
            assert status.result == draw_result
            assert status.reason == draw_reason
    
    def test_game_status_all_win_types(self):
        """Test both win types can be represented."""
        wins = [
            (GameResult.WHITE_WIN, GameOverReason.CHECKMATE),
            (GameResult.BLACK_WIN, GameOverReason.CHECKMATE),
        ]
        
        for win_result, win_reason in wins:
            status = GameStatus(
                is_game_over=True,
                result=win_result,
                reason=win_reason
            )
            
            assert status.is_game_over is True
            assert status.result == win_result
            assert status.reason == win_reason
