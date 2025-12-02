import sys
import builtins
import importlib
import pytest

from training import run_smoke


def test_run_smoke_no_torch(monkeypatch, tmp_path, capsys):
    # run in tmp cwd
    monkeypatch.chdir(tmp_path)

    # make run_prechecks pass
    monkeypatch.setattr('training.run_smoke.run_prechecks', lambda: True)

    # simulate ImportError for torch by temporarily replacing builtins.__import__
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == 'torch':
            raise ImportError('no torch')
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, '__import__', fake_import)

    try:
        run_smoke.main()
    finally:
        monkeypatch.setattr(builtins, '__import__', real_import)

    captured = capsys.readouterr()
    assert 'smoke-run skipped' in captured.out or 'Torch or model not available' in captured.out
