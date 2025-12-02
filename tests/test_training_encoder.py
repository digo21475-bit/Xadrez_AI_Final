"""Tests for training/encoder.py"""
import importlib
import numpy as np


def test_board_to_tensor_shape():
    """Test board_to_tensor() output shape."""
    encoder = importlib.import_module('training.encoder')
    board_mod = importlib.import_module('core.board.board')
    
    board = board_mod.Board()
    tensor = encoder.board_to_tensor(board)
    
    # Should be 13 planes x 8 x 8
    assert isinstance(tensor, np.ndarray)
    assert tensor.shape == (13, 8, 8)
    assert tensor.dtype == np.float32


def test_board_to_tensor_initial_position():
    """Test board_to_tensor() with initial board."""
    encoder = importlib.import_module('training.encoder')
    board_mod = importlib.import_module('core.board.board')
    
    board = board_mod.Board()
    tensor = encoder.board_to_tensor(board)
    
    # Initial position should have non-zero values
    assert np.any(tensor > 0)
    # All values should be 0 or 1 (one-hot encoding)
    assert np.all((tensor == 0) | (tensor == 1))


def test_encoder_has_action_size():
    """Test encoder has ACTION_SIZE."""
    encoder = importlib.import_module('training.encoder')
    
    assert hasattr(encoder, 'ACTION_SIZE')
    assert encoder.ACTION_SIZE == 20480

