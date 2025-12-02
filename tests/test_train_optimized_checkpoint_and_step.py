import os
import torch
import tempfile
import json
import numpy as np
import types
import pytest

from training.train_optimized import CheckpointManager, train_step


class TinyModel(torch.nn.Module):
    def __init__(self, action_size=8):
        super().__init__()
        self.action_size = action_size
        self.linear = torch.nn.Linear(13*8*8, action_size)
        self.vhead = torch.nn.Linear(action_size, 1)

    def forward(self, x):
        b = x.shape[0]
        flat = x.view(b, -1).float()
        pi = self.linear(flat)
        v = self.vhead(pi)
        return pi, v


def test_checkpoint_manager_save_load_cleanup(tmp_path):
    ckpt_dir = str(tmp_path / 'ckpts')
    mgr = CheckpointManager(ckpt_dir, keep_last_n=2)

    model = TinyModel()
    optim = torch.optim.Adam(model.parameters())

    # fake scaler with state_dict
    class Scaler:
        def state_dict(self):
            return {'s': 1}
        def load_state_dict(self, d):
            self.d = d

    scaler = Scaler()

    # save multiple checkpoints
    p1 = mgr.save(1, model, optim, scaler, metrics={'m':1})
    p2 = mgr.save(2, model, optim, scaler, metrics={'m':2})
    p3 = mgr.save(3, model, optim, scaler, metrics={'m':3})

    # only last 2 should remain
    files = sorted([f for f in os.listdir(ckpt_dir) if f.startswith('ckpt_')])
    assert len(files) == 2

    # load latest
    step = mgr.load_latest(model, optim, scaler, device=torch.device('cpu'))
    assert step == 3


def test_train_step_empty_and_error_and_useamp(monkeypatch):
    device = torch.device('cpu')
    model = TinyModel(action_size=4)

    loss_pi = torch.nn.CrossEntropyLoss()
    loss_v = torch.nn.MSELoss()

    # empty batch
    out = train_step(model, [], device, loss_pi, loss_v, use_amp=False)
    assert isinstance(out, torch.Tensor)

    # simulate batch loading error by monkeypatching numpy.array to raise
    import numpy as _np
    _orig_array = _np.array
    monkeypatch.setattr('numpy.array', lambda *a, **k: (_ for _ in ()).throw(Exception('npfail')))
    bad = [({'bad': True}, [0,1,2,3], 1, 0)]
    out2 = train_step(model, bad, device, loss_pi, loss_v, use_amp=False)
    assert out2.item() == 0.0

    # restore numpy.array without reloading the whole module (avoids reload warning)
    monkeypatch.setattr('numpy.array', _orig_array)

    # test use_amp true on cpu with float32 -> should avoid autocast path
    batch = [(np.zeros((13,8,8)), np.array([1,0,0,0]), 1, 0)]
    out3 = train_step(model, batch, device, loss_pi, loss_v, use_amp=True, dtype=torch.float32)
    assert isinstance(out3, torch.Tensor)
