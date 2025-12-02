import importlib


def test_get_device_cpu_monkeypatch(monkeypatch):
    """When CUDA is not available, get_device should return cpu."""
    torch = importlib.import_module('torch')

    monkeypatch.setattr(torch.cuda, 'is_available', lambda: False)
    mod = importlib.import_module('training.device')
    dev = mod.get_device()
    assert str(dev).startswith('cpu')

