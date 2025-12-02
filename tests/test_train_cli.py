import os
import json
import tempfile
import pytest

import training.train as train_mod


class DummyConfig:
    def __init__(self, device, agent_dir):
        self.device = device
        self.agent_dir = agent_dir
        self.model_channels = 8
        self.model_blocks = 1
        self.model_in_planes = 13
        self.action_size = 32
        self.replay_path = os.path.join(agent_dir, 'checkpoints', 'replay.pt')
        self.replay_capacity = 100

    def to_dict(self):
        return {'device': self.device}

    @classmethod
    def from_device(cls, device, agent_dir):
        return cls(device, agent_dir)


def test_train_main_flow_monkeypatch(monkeypatch, tmp_path):
    agent_dir = str(tmp_path / 'models' / 'AgentA')
    os.makedirs(os.path.join(agent_dir, 'checkpoints'), exist_ok=True)

    # monkeypatch TrainConfig
    monkeypatch.setattr('training.train.TrainConfig', DummyConfig)

    # monkeypatch make_model to return a tiny nn.Module
    class Tiny:
        pass
    monkeypatch.setattr('training.train.make_model', lambda **kw: Tiny())

    # monkeypatch ReplayBuffer to be empty
    class RB:
        def __init__(self, path, capacity=0):
            self._len = 0
        def __len__(self):
            return 0
    monkeypatch.setattr('training.train.ReplayBuffer', RB)

    # monkeypatch train_loop_with_grad_accum to return (steps, ckpt)
    monkeypatch.setattr('training.train.train_loop_with_grad_accum', lambda m,b,c: (123, 'ckpt.pt'))

    # monkeypatch update_metadata to write nothing
    monkeypatch.setattr('training.train.update_metadata', lambda *a, **k: None)

    # call main with custom argv
    import sys
    monkeypatch.setattr(sys, 'argv', ['prog'])
    # run main (should not raise)
    train_mod.main()
