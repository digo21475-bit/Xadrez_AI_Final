import importlib
import torch


def test_mcts_numpy_path():
    """Test MCTS numpy conversion path (.cpu().numpy())."""
    torch = importlib.import_module('torch')
    mcts_mod = importlib.import_module('training.mcts')

    # Create numpy-returning net (non-torch tensors)
    def net_predict_numpy(board):
        import numpy as np
        logits = np.zeros(20, dtype=np.float32)
        value = np.float32(0.0)
        return logits, value

    mcts = mcts_mod.MCTS(net_predict_numpy, action_size=20, c_puct=1.0, sims=2)

    class FakeBoard:
        def copy(self):
            return self

    dist = mcts.run(FakeBoard())
    assert isinstance(dist, list)
    assert len(dist) == 20


def test_mcts_returns_distribution(monkeypatch):
    mcts_mod = importlib.import_module('training.mcts')

    # Force Move to None so simulate returns early and we get a fallback distribution
    monkeypatch.setattr(mcts_mod, 'Move', None)

    # dummy net returning torch tensors on CPU
    def net_predict(board):
        logits = torch.zeros(20)
        value = torch.tensor(0.0)
        return logits, value

    mcts = mcts_mod.MCTS(net_predict, action_size=20, c_puct=1.0, sims=2)

    class FakeBoard:
        def copy(self):
            return self

    dist = mcts.run(FakeBoard())
    assert isinstance(dist, list)
    assert len(dist) == 20
    assert abs(sum(dist) - 1.0) < 1e-6


def test_arena_play_match_smoke(tmp_path):
    arena = importlib.import_module('training.arena_runner')
    model_mod = importlib.import_module('training.model')
    torch = importlib.import_module('torch')

    device = torch.device('cpu')
    # Use same config as arena_runner.play_match()
    cfg = {'channels': 64, 'blocks': 6, 'in_planes': 13, 'action_size': 20480}
    A = model_mod.make_model(device=device, **cfg)
    B = model_mod.make_model(device=device, **cfg)

    ckptA = tmp_path / 'A.pt'
    ckptB = tmp_path / 'B.pt'
    torch.save(A.state_dict(), str(ckptA))
    torch.save(B.state_dict(), str(ckptB))

    stats = arena.play_match(str(ckptA), str(ckptB), games=1, sims=2)
    assert isinstance(stats, dict)
    assert set(stats.keys()) >= {'A', 'B', 'draws'}
