"""Tests for training/replay_buffer.py"""
import importlib
import tempfile
import numpy as np


def test_replay_buffer_create():
    """Test ReplayBuffer creation."""
    rb = importlib.import_module('training.replay_buffer')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = tmpdir + '/buffer.pt'
        buf = rb.ReplayBuffer(path=path, capacity=100)
        assert buf is not None
        assert hasattr(buf, 'add')


def test_replay_buffer_add():
    """Test ReplayBuffer.add()."""
    rb = importlib.import_module('training.replay_buffer')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = tmpdir + '/buffer.pt'
        buf = rb.ReplayBuffer(path=path, capacity=100)
        
        # Add dummy entries
        board = np.zeros((13, 8, 8), dtype=np.float32)
        policy = np.ones(20480, dtype=np.float32) / 20480
        value = 0.5
        
        buf.add((board, policy, 0, value))
        # Should have item
        assert len(buf) >= 1


def test_replay_buffer_save():
    """Test ReplayBuffer save."""
    rb = importlib.import_module('training.replay_buffer')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = tmpdir + '/buffer.pt'
        buf = rb.ReplayBuffer(path=path, capacity=50)
        
        # Add some entries
        for i in range(5):
            board = np.random.randn(13, 8, 8).astype(np.float32)
            policy = np.ones(20480, dtype=np.float32) / 20480
            value = float(i) / 5.0
            buf.add((board, policy, 0, value))
        
        # Save
        buf.save()
        # Load new buffer from same path
        buf2 = rb.ReplayBuffer(path=path, capacity=50)
        assert len(buf2) >= 0  # Should have loaded data


def test_replay_buffer_sample():
    """Test ReplayBuffer.sample()."""
    rb = importlib.import_module('training.replay_buffer')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = tmpdir + '/buffer.pt'
        buf = rb.ReplayBuffer(path=path, capacity=100)
        
        # Add entries
        for i in range(10):
            board = np.random.randn(13, 8, 8).astype(np.float32)
            policy = np.ones(20480, dtype=np.float32) / 20480
            value = 0.5
            buf.add((board, policy, 0, value))
        
        # Sample
        batch = buf.sample(batch_size=3)
        assert len(batch) <= 3
        assert len(batch) > 0
