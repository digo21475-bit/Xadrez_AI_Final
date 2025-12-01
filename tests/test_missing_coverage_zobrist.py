"""
Comprehensive test coverage for core/hash/zobrist.py missing lines.

Covers:
- xor_enpassant with None/invalid input (line 136)
- verify_entropy error path and computation (lines 153-162)
- signature empty table path (line 173)
- Module-level convenience wrappers (lines 190, 194, 198, 202, 206, 210, 214, 218, 222)
"""

import pytest
from core.hash.zobrist import (
    Zobrist,
    init,
    reset,
    ensure_initialized,
    xor_piece,
    xor_castling,
    xor_enpassant,
    xor_side,
    verify_entropy,
    signature,
)
from utils.enums import PieceType, Color, piece_index


class TestZobristXorEnpassantEdgeCases:
    """Test xor_enpassant with None and -1 inputs (line 136)."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure Zobrist is initialized."""
        Zobrist.init(seed=0xDEADBEEF)
        yield
        Zobrist.reset()
    
    def test_xor_enpassant_with_none(self):
        """Test xor_enpassant returns hash unchanged when passed None (line 136)."""
        h = 0x123456789ABCDEF0
        result = Zobrist.xor_enpassant(h, None)
        assert result == h  # Should return unchanged
    
    def test_xor_enpassant_with_minus_one(self):
        """Test xor_enpassant returns hash unchanged when passed -1."""
        h = 0x123456789ABCDEF0
        result = Zobrist.xor_enpassant(h, -1)
        assert result == h  # Should return unchanged
    
    def test_xor_enpassant_with_valid_square(self):
        """Test xor_enpassant with valid square changes the hash."""
        h = 0x123456789ABCDEF0
        result = Zobrist.xor_enpassant(h, 16)  # valid en passant square
        assert result != h  # Should change the hash
        assert isinstance(result, int)


class TestZobristVerifyEntropyPaths:
    """Test verify_entropy error handling and computation (lines 153-162)."""
    
    def test_verify_entropy_not_initialized_raises(self):
        """Test verify_entropy raises RuntimeError when Zobrist not initialized (line 153-154)."""
        Zobrist.reset()
        with pytest.raises(RuntimeError, match="Zobrist not initialized"):
            Zobrist.verify_entropy()
    
    def test_verify_entropy_after_init(self):
        """Test verify_entropy returns valid fraction after init (lines 156-162)."""
        Zobrist.init(seed=0x12345678)
        entropy = Zobrist.verify_entropy()
        
        # Entropy should be between 0.0 and 1.0
        assert 0.0 <= entropy <= 1.0
        
        # With 12 pieces * 64 squares = 768 keys, expect high uniqueness
        # (likely all unique or very close)
        assert entropy > 0.95
        
        Zobrist.reset()
    
    def test_verify_entropy_deterministic_seed(self):
        """Test verify_entropy is deterministic for same seed."""
        Zobrist.init(seed=0xCAFEBABE)
        entropy1 = Zobrist.verify_entropy()
        
        Zobrist.reset()
        Zobrist.init(seed=0xCAFEBABE)
        entropy2 = Zobrist.verify_entropy()
        
        assert entropy1 == entropy2
        Zobrist.reset()


class TestZobristSignatureEmpty:
    """Test signature with uninitialized Zobrist (line 173)."""
    
    def test_signature_uninitialized_returns_empty_bytes(self):
        """Test signature returns empty bytes when Zobrist not initialized (line 173)."""
        Zobrist.reset()
        sig = Zobrist.signature()
        assert sig == b""
    
    def test_signature_after_init(self):
        """Test signature returns non-empty bytes after init."""
        Zobrist.init(seed=0xDEADBEEF)
        sig = Zobrist.signature()
        assert len(sig) > 0
        assert isinstance(sig, bytes)
        Zobrist.reset()
    
    def test_signature_deterministic(self):
        """Test signature is deterministic for same seed."""
        Zobrist.init(seed=0x12345678)
        sig1 = Zobrist.signature()
        
        Zobrist.reset()
        Zobrist.init(seed=0x12345678)
        sig2 = Zobrist.signature()
        
        assert sig1 == sig2
        Zobrist.reset()


class TestModuleLevelWrappersFunctions:
    """Test module-level convenience wrapper functions (lines 190, 194, 198, 202, 206, 210, 214, 218, 222)."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset and initialize Zobrist for each test."""
        Zobrist.reset()
        Zobrist.init(seed=0xC0FFEE)
        yield
        Zobrist.reset()
    
    def test_module_init_wrapper_line_190(self):
        """Test module-level init() wrapper (line 190)."""
        # Reset first
        Zobrist.reset()
        
        # Call module-level init
        init(seed=0x11111111)
        
        # Verify it's initialized
        assert len(Zobrist.piece_square) > 0
        
        Zobrist.reset()
    
    def test_module_reset_wrapper_line_194(self):
        """Test module-level reset() wrapper (line 194)."""
        # Ensure initialized
        Zobrist.init()
        assert len(Zobrist.piece_square) > 0
        
        # Call module-level reset
        reset()
        
        # Verify it's reset
        assert len(Zobrist.piece_square) == 0
    
    def test_module_ensure_initialized_wrapper_line_198(self):
        """Test module-level ensure_initialized() wrapper (line 198)."""
        Zobrist.reset()
        
        # Call module-level ensure_initialized
        ensure_initialized(seed=0x99999999)
        
        # Verify it's initialized
        assert len(Zobrist.piece_square) > 0
        
        Zobrist.reset()
    
    def test_module_xor_piece_wrapper_line_202(self):
        """Test module-level xor_piece() wrapper (line 202)."""
        h = 0x123456789ABCDEF0
        result = xor_piece(h, piece_index(PieceType.PAWN, Color.WHITE), 16)
        
        assert isinstance(result, int)
        assert result != h  # Should change
    
    def test_module_xor_castling_wrapper_line_206(self):
        """Test module-level xor_castling() wrapper (line 206)."""
        h = 0x123456789ABCDEF0
        result = xor_castling(h, 0b1111)  # All castling rights
        
        assert isinstance(result, int)
        assert result != h  # Should change
    
    def test_module_xor_enpassant_wrapper_line_210(self):
        """Test module-level xor_enpassant() wrapper (line 210)."""
        h = 0x123456789ABCDEF0
        result = xor_enpassant(h, 24)  # Valid en passant square
        
        assert isinstance(result, int)
        assert result != h  # Should change
    
    def test_module_xor_side_wrapper_line_214(self):
        """Test module-level xor_side() wrapper (line 214)."""
        h = 0x123456789ABCDEF0
        result = xor_side(h)
        
        assert isinstance(result, int)
        assert result != h  # Should change
    
    def test_module_verify_entropy_wrapper_line_218(self):
        """Test module-level verify_entropy() wrapper (line 218)."""
        entropy = verify_entropy()
        
        assert 0.0 <= entropy <= 1.0
        assert entropy > 0.9  # Should be high for good random distribution
    
    def test_module_signature_wrapper_line_222(self):
        """Test module-level signature() wrapper (line 222)."""
        sig = signature()
        
        assert isinstance(sig, bytes)
        assert len(sig) > 0


class TestZobristIntegration:
    """Integration tests for Zobrist hashing workflow."""
    
    def test_zobrist_deterministic_hash_sequence(self):
        """Test that hash computation is deterministic."""
        Zobrist.init(seed=0xDEADBEEF)
        
        # Compute hash sequence
        h = 0
        h = Zobrist.xor_piece(h, piece_index(PieceType.PAWN, Color.WHITE), 8)
        h = Zobrist.xor_side(h)
        h = Zobrist.xor_castling(h, 0xF)
        h = Zobrist.xor_enpassant(h, 16)
        
        # Reset and recompute
        Zobrist.reset()
        Zobrist.init(seed=0xDEADBEEF)
        
        h2 = 0
        h2 = Zobrist.xor_piece(h2, piece_index(PieceType.PAWN, Color.WHITE), 8)
        h2 = Zobrist.xor_side(h2)
        h2 = Zobrist.xor_castling(h2, 0xF)
        h2 = Zobrist.xor_enpassant(h2, 16)
        
        assert h == h2
        Zobrist.reset()
    
    def test_zobrist_xor_properties(self):
        """Test XOR properties: xor with same value twice cancels out."""
        Zobrist.init(seed=0x11111111)
        
        h = 0x1234567890ABCDEF
        
        # XOR piece twice (toggle on, toggle off)
        h1 = Zobrist.xor_piece(h, piece_index(PieceType.KNIGHT, Color.WHITE), 5)
        h2 = Zobrist.xor_piece(h1, piece_index(PieceType.KNIGHT, Color.WHITE), 5)
        
        assert h == h2  # Should cancel out
        Zobrist.reset()
