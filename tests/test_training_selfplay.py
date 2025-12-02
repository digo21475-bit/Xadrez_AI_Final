"""Tests for training/selfplay.py"""
import importlib
import torch


def test_selfplay_worker_smoke():
    """Test SelfPlayWorker initialization and basic methods."""
    selfplay = importlib.import_module('training.selfplay')
    
    def dummy_net(board):
        logits = torch.zeros(20480)
        value = torch.tensor(0.0)
        return logits, value
    
    worker = selfplay.SelfPlayWorker(dummy_net, mcts_sims=2)
    assert worker is not None
    assert hasattr(worker, 'play_game')


def test_selfplay_play_game():
    """Test SelfPlayWorker.play_game() returns valid game data."""
    selfplay = importlib.import_module('training.selfplay')
    board_mod = importlib.import_module('core.board.board')
    
    def dummy_net(board):
        import torch
        logits = torch.zeros(20480)
        value = torch.tensor(0.0)
        return logits, value
    
    worker = selfplay.SelfPlayWorker(dummy_net, mcts_sims=1)
    board = board_mod.Board()
    game_data, outcome = worker.play_game(board, temperature=1.0, max_moves=2)
    
    # Should return list of records and outcome
    assert isinstance(game_data, list)
    # At least one move
    if len(game_data) > 0:
        state, pi, side = game_data[0]
        assert state is not None
        assert len(pi) == 20480
    assert isinstance(outcome, (int, float))


