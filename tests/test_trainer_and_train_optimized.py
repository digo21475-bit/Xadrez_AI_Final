import importlib
import numpy as np


def make_sample_batch(action_size=20, n=4):
    batch = []
    for _ in range(n):
        state = np.zeros((13, 8, 8), dtype=np.float32)
        pi = np.ones((action_size,), dtype=np.float32) / action_size
        player = 0
        outcome = 0.0
        batch.append((state, pi, player, outcome))
    return batch


def test_trainer_saves_checkpoint(tmp_path, monkeypatch):
    trainer = importlib.import_module('training.trainer')
    model_mod = importlib.import_module('training.model')
    ReplayBuffer = importlib.import_module('training.replay_buffer').ReplayBuffer
    torch = importlib.import_module('torch')

    # small model
    device = torch.device('cpu')
    m = model_mod.make_model(device=device, channels=8, blocks=1, in_planes=13, action_size=20)

    # buffer with some samples
    p = tmp_path / 'replay.pt'
    buf = ReplayBuffer(str(p), capacity=100)
    for item in make_sample_batch(action_size=20, n=4):
        buf.add(item)

    cfg = {
        'ckpt_dir': str(tmp_path / 'checkpoints'),
        'batch_size': 2,
        'iters': 2,
        'lr': 1e-3,
        'wd': 1e-4,
    }

    latest = trainer.train_loop(m, buf, cfg, device=device)
    # check file exists
    import os
    assert os.path.exists(latest)


def test_train_optimized_small_loop(tmp_path):
    train_mod = importlib.import_module('training.train_optimized')
    model_mod = importlib.import_module('training.model')
    ReplayBuffer = importlib.import_module('training.replay_buffer').ReplayBuffer
    cfg_mod = importlib.import_module('training.config')
    torch = importlib.import_module('torch')

    device = torch.device('cpu')
    m = model_mod.make_model(device=device, channels=8, blocks=1, in_planes=13, action_size=20)

    buf = ReplayBuffer(str(tmp_path / 'replay.pt'), capacity=100)
    for item in make_sample_batch(action_size=20, n=8):
        buf.add(item)

    cfg = cfg_mod.TrainConfig.from_device(device='cpu', agent_dir=str(tmp_path))
    cfg.num_epochs = 1
    cfg.iters_per_epoch = 4
    cfg.batch_size = 2
    cfg.ckpt_every_steps = 2
    cfg.ckpt_dir = str(tmp_path / 'ckpts')
    cfg.log_dir = str(tmp_path / 'logs')
    cfg.replay_path = str(tmp_path / 'replay.pt')

    step, path = train_mod.train_loop_with_grad_accum(m, buf, cfg)
    assert step >= 0
    import os
    assert os.path.exists(path)
