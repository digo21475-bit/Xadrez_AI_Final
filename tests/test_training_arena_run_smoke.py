"""Tests for training/arena_runner.py and training/run_smoke.py"""
import importlib
import tempfile
import torch


def test_arena_runner_imports():
    """Test arena_runner module imports."""
    arena = importlib.import_module('training.arena_runner')
    assert arena is not None
    assert hasattr(arena, 'play_match')


def test_arena_net_predict_factory():
    """Test net_predict_factory_from_model."""
    arena = importlib.import_module('training.arena_runner')
    model_mod = importlib.import_module('training.model')
    
    device = torch.device('cpu')
    model = model_mod.make_model(device=device, channels=8, blocks=1)
    
    net_predict = arena.net_predict_factory_from_model(model)
    assert net_predict is not None
    assert callable(net_predict)


def test_run_smoke_imports():
    """Test run_smoke module imports."""
    run_smoke = importlib.import_module('training.run_smoke')
    assert run_smoke is not None
    # Should have some functions or config
    assert len(dir(run_smoke)) > 2


def test_run_smoke_config():
    """Test run_smoke configuration."""
    run_smoke = importlib.import_module('training.run_smoke')
    config = importlib.import_module('training.config')
    
    # Create config
    cfg = config.TrainConfig(device='cpu')
    assert cfg.device == 'cpu'
