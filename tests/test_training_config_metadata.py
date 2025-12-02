"""Tests for training/train.py and training/run_smoke.py"""
import importlib
import tempfile
import os


def test_train_config_from_device():
    """Test TrainConfig initialization."""
    config = importlib.import_module('training.config')
    
    cfg = config.TrainConfig(device='cpu')
    assert cfg is not None
    assert cfg.device == 'cpu'
    assert cfg.model_channels == 64


def test_train_config_default_values():
    """Test TrainConfig default values."""
    config = importlib.import_module('training.config')
    
    cfg = config.TrainConfig()
    assert cfg.device == 'cpu'
    assert cfg.batch_size == 128
    assert cfg.model_blocks == 6


def test_metadata_utils_read():
    """Test metadata_utils functions."""
    metadata = importlib.import_module('training.metadata_utils')
    
    # Check module exists and has functions
    assert hasattr(metadata, 'update_metadata') or hasattr(metadata, 'get_metadata')

