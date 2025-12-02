import numpy as np
import importlib


def test_small_model_forward():
    """Create a tiny model and ensure forward pass returns expected shapes."""
    torch = importlib.import_module('torch')
    make_model = importlib.import_module('training.model').make_model

    device = torch.device('cpu')
    m = make_model(device=device, in_planes=13, channels=8, blocks=1, action_size=10)
    x = np.random.randn(1, 13, 8, 8).astype('float32')
    t = torch.tensor(x, device=device)
    pi, v = m(t)
    assert pi.shape[0] == 1
    assert v.shape[0] == 1

