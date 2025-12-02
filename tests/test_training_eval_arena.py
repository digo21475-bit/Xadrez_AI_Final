"""Tests for training/eval_arena.py"""
import importlib
import tempfile
import os


def test_run_arena_basic():
    """Test run_arena() with dummy agents."""
    eval_arena = importlib.import_module('training.eval_arena')
    
    # Create dummy agents
    def agentA_play(as_white):
        return 0  # draw
    
    def agentB_play(as_white):
        return 0  # draw
    
    stats = eval_arena.run_arena(agentA_play, agentB_play, games=2)
    
    assert isinstance(stats, dict)
    assert stats['games'] == 2
    assert stats['wins'] + stats['draws'] + stats['losses'] == 2


def test_run_arena_with_csv_output(tmp_path):
    """Test run_arena() writes CSV output."""
    eval_arena = importlib.import_module('training.eval_arena')
    
    def agentA_play(as_white):
        return 1  # A wins
    
    def agentB_play(as_white):
        return -1  # A wins (from B's perspective)
    
    csv_path = str(tmp_path / 'results.csv')
    stats = eval_arena.run_arena(agentA_play, agentB_play, games=2, out_csv=csv_path)
    
    assert os.path.exists(csv_path)
    with open(csv_path, 'r') as f:
        lines = f.readlines()
        # Header + 2 results
        assert len(lines) >= 3
