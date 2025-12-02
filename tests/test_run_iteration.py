import os
import sys
import types
import pytest

from training import run_iteration as ri


def test_run_iteration_prechecks_fail(monkeypatch, tmp_path):
    # make agent dir
    agent_dir = str(tmp_path / 'agent')
    os.makedirs(agent_dir, exist_ok=True)

    # make run_prechecks raise
    monkeypatch.setattr('training.run_iteration.run_prechecks', lambda: (_ for _ in ()).throw(Exception('fail')))

    ok = ri.run_iteration(agent_dir, num_selfplay=0, trainer_iters=0)
    assert ok is False


def test_run_iteration_full_flow_monkeypatch(monkeypatch, tmp_path):
    agent_dir = str(tmp_path / 'agent')
    os.makedirs(os.path.join(agent_dir, 'checkpoints'), exist_ok=True)

    # prechecks OK
    monkeypatch.setattr('training.run_iteration.run_prechecks', lambda: True)

    # stub SelfPlayWorker to produce no moves
    class FakeWorker:
        def __init__(self, *a, **k):
            pass
        def play_game(self, b, temperature, max_moves):
            return ([], 0)

    monkeypatch.setitem(sys.modules, 'training.selfplay', __import__('types').SimpleNamespace(SelfPlayWorker=FakeWorker))

    # stub make_model
    monkeypatch.setitem(sys.modules, 'training.model', __import__('types').SimpleNamespace(make_model=lambda **kw: object()))

    # stub ReplayBuffer
    class RB:
        def __init__(self, p, capacity=0):
            pass
        def __len__(self):
            return 0
        def add(self, x):
            pass
        def save(self):
            pass
    monkeypatch.setitem(sys.modules, 'training.replay_buffer', __import__('types').SimpleNamespace(ReplayBuffer=RB))

    # stub trainer.train_loop
    monkeypatch.setitem(sys.modules, 'training.trainer', __import__('types').SimpleNamespace(train_loop=lambda m,b,c,device=None: 'ckpt'))

    # stub eval_loop.promote_if_better
    monkeypatch.setitem(sys.modules, 'training.eval_loop', __import__('types').SimpleNamespace(promote_if_better=lambda *a, **k: {'promoted': False, 'winrate':0}))

    # call run_iteration (should return True)
    ok = ri.run_iteration(agent_dir, num_selfplay=1, trainer_iters=1)
    assert ok is True
