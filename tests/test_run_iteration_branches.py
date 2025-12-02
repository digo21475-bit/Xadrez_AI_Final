import os
import sys
import pytest

from training import run_iteration as ri


def test_run_iteration_training_failure(monkeypatch, tmp_path):
    agent_dir = str(tmp_path / 'agent')
    os.makedirs(os.path.join(agent_dir, 'checkpoints'), exist_ok=True)

    # prechecks OK
    monkeypatch.setattr('training.run_iteration.run_prechecks', lambda: True)

    # stub SelfPlayWorker produce empty
    class FakeWorker:
        def __init__(self, *a, **k):
            pass
        def play_game(self, b, temperature, max_moves):
            return ([], 0)
    monkeypatch.setitem(sys.modules, 'training.selfplay', __import__('types').SimpleNamespace(SelfPlayWorker=FakeWorker))
    monkeypatch.setitem(sys.modules, 'training.model', __import__('types').SimpleNamespace(make_model=lambda **kw: object()))
    monkeypatch.setitem(sys.modules, 'training.replay_buffer', __import__('types').SimpleNamespace(ReplayBuffer=lambda p, capacity=0: type('RB',(),{'add':lambda s,x:None,'save':lambda s:None,'__len__':lambda s:0})()))

    # trainer raises
    def bad_train(model, buf, cfg, device=None):
        raise Exception('train fail')
    monkeypatch.setitem(sys.modules, 'training.trainer', __import__('types').SimpleNamespace(train_loop=bad_train))

    ok = ri.run_iteration(agent_dir, num_selfplay=1, trainer_iters=1)
    assert ok is False


def test_run_iteration_eval_failure(monkeypatch, tmp_path):
    agent_dir = str(tmp_path / 'agent')
    os.makedirs(os.path.join(agent_dir, 'checkpoints'), exist_ok=True)

    monkeypatch.setattr('training.run_iteration.run_prechecks', lambda: True)
    # stubs for selfplay/trainer
    class FakeWorker:
        def __init__(self, *a, **k):
            pass
        def play_game(self, b, temperature, max_moves):
            return ([], 0)
    monkeypatch.setitem(sys.modules, 'training.selfplay', __import__('types').SimpleNamespace(SelfPlayWorker=FakeWorker))
    monkeypatch.setitem(sys.modules, 'training.model', __import__('types').SimpleNamespace(make_model=lambda **kw: object()))
    monkeypatch.setitem(sys.modules, 'training.replay_buffer', __import__('types').SimpleNamespace(ReplayBuffer=lambda p, capacity=0: type('RB',(),{'add':lambda s,x:None,'save':lambda s:None,'__len__':lambda s:0})()))
    monkeypatch.setitem(sys.modules, 'training.trainer', __import__('types').SimpleNamespace(train_loop=lambda m,b,c,device=None: 'ckpt'))

    # eval loop raises
    monkeypatch.setitem(sys.modules, 'training.eval_loop', __import__('types').SimpleNamespace(promote_if_better=lambda *a, **k: (_ for _ in ()).throw(Exception('eval fail'))))

    ok = ri.run_iteration(agent_dir, num_selfplay=1, trainer_iters=1)
    assert ok is False
