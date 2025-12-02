import importlib
import numpy as np


def make_sample_batch(action_size=10, n=2):
    # state shape (13,8,8), pi length action_size, player, outcome
    batch = []
    for _ in range(n):
        state = np.zeros((13, 8, 8), dtype=np.float32)
        pi = np.ones((action_size,), dtype=np.float32) / action_size
        player = 0
        outcome = 0.0
        batch.append((state, pi, player, outcome))
    return batch


def test_train_step_returns_tensor():
    torch = importlib.import_module('torch')
    model_mod = importlib.import_module('training.model')
    train_mod = importlib.import_module('training.train_optimized')

    device = torch.device('cpu')
    model = model_mod.make_model(device=device, channels=8, blocks=1, in_planes=13, action_size=10)
    loss_fn_pi = torch.nn.CrossEntropyLoss()
    loss_fn_v = torch.nn.MSELoss()
    batch = make_sample_batch(action_size=10, n=2)

    loss = train_mod.train_step(model, batch, device, loss_fn_pi, loss_fn_v, use_amp=False)
    assert hasattr(loss, 'item')
    assert float(loss.item()) >= 0.0


def test_train_step_with_amp():
    """Test train_step with AMP enabled (autocast path)."""
    torch = importlib.import_module('torch')
    model_mod = importlib.import_module('training.model')
    train_mod = importlib.import_module('training.train_optimized')

    device = torch.device('cpu')
    model = model_mod.make_model(device=device, channels=8, blocks=1, in_planes=13, action_size=10)
    loss_fn_pi = torch.nn.CrossEntropyLoss()
    loss_fn_v = torch.nn.MSELoss()
    batch = make_sample_batch(action_size=10, n=2)

    loss = train_mod.train_step(model, batch, device, loss_fn_pi, loss_fn_v, use_amp=True, dtype=torch.float32)
    assert hasattr(loss, 'item')
    assert float(loss.item()) >= 0.0

