import os
import json
import torch
import numpy as np

from types import SimpleNamespace

from training.train_optimized import train_loop_with_grad_accum


class DummyConfig:
    def __init__(self, base_dir):
        self.device = 'cpu'
        self.lr = 1e-3
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.weight_decay = 1e-4
        self.use_amp = False
        self.amp_dtype = 'float16'
        self.ckpt_dir = os.path.join(base_dir, 'ckpts')
        self.keep_last_n_ckpts = 2
        self.batch_size = 2
        self.max_tokens_per_batch = 65536
        self.log_dir = os.path.join(base_dir, 'logs')
        self.num_epochs = 1
        self.iters_per_epoch = 2
        self.grad_accum_steps = 1
        self.ckpt_every_steps = 1
        self.verbose = False


class TinyModel(torch.nn.Module):
    def __init__(self, action_size=4):
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


class RB:
    def __init__(self, items):
        self.items = items
    def sample(self, n):
        # return a batch of tuples (state, pi, player, outcome)
        return self.items[:n]


def test_train_loop_with_grad_accum_saves_ckpt(tmp_path):
    base = str(tmp_path)
    cfg = DummyConfig(base)
    model = TinyModel(action_size=4)

    # create one small batch item
    state = np.zeros((13,8,8), dtype=np.float32)
    pi = np.array([1,0,0,0], dtype=np.float32)
    item = (state, pi, 1, 0)
    buf = RB([item, item])

    step, path = train_loop_with_grad_accum(model, buf, cfg)
    # final checkpoint path exists
    assert os.path.exists(path)
    assert isinstance(step, int)
