import os
import sys
import json
from types import SimpleNamespace

import pytest

from training import run_smoke


def test_run_smoke_integration_minimal(tmp_path, monkeypatch):
    # run in tmp cwd
    monkeypatch.chdir(tmp_path)

    # patch run_prechecks to succeed
    monkeypatch.setattr('training.run_smoke.run_prechecks', lambda: True)

    # create tiny model factory
    class TinyModel:
        def parameters(self):
            return []

    monkeypatch.setitem(sys.modules, 'training.model', SimpleNamespace(make_model=lambda **kw: TinyModel()))

    # stub SelfPlayWorker to produce one small record
    class FakeWorker:
        def __init__(self, net_predict, mcts_sims=0):
            pass
        def play_game(self, b, temperature=1.0, max_moves=60):
            # return one record: (state, pi, player), outcome
            return ([(None, [1.0], 1)], 0)

    monkeypatch.setitem(sys.modules, 'training.selfplay', SimpleNamespace(SelfPlayWorker=FakeWorker))

    # stub ReplayBuffer to write a file on save
    class RB:
        def __init__(self, path, capacity=0):
            self.path = path
            self.items = []
            os.makedirs(os.path.dirname(path), exist_ok=True)
        def add(self, item):
            self.items.append(item)
        def save(self):
            with open(self.path, 'w') as f:
                json.dump({'n': len(self.items)}, f)
        def __len__(self):
            return len(self.items)

    monkeypatch.setitem(sys.modules, 'training.replay_buffer', SimpleNamespace(ReplayBuffer=RB))

    # run main which should create models/AgentA/checkpoints/replay.pt
    run_smoke.main()
    replay_path = os.path.join('models', 'AgentA', 'checkpoints', 'replay.pt')
    assert os.path.exists(replay_path)
    data = json.loads(open(replay_path).read())
    assert data.get('n', 0) >= 1
