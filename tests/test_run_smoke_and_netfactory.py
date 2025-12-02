import os
import json
import pytest

from training import run_smoke


def test_net_predict_factory_has_batch():
    # create a tiny model-like object with parameters() attribute
    class Tiny:
        def parameters(self):
            return []
    net = run_smoke.net_predict_factory(Tiny())
    assert hasattr(net, '__call__')
    assert hasattr(net, 'batch_predict')


def test_run_smoke_prechecks_failure(tmp_path, monkeypatch):
    # run in a temp cwd so relative paths go into tmp_path
    monkeypatch.chdir(tmp_path)
    out_dir = tmp_path / 'models' / 'AgentA' / 'experiments'

    # make run_prechecks raise
    monkeypatch.setattr('training.run_smoke.run_prechecks', lambda: (_ for _ in ()).throw(Exception('fail')))
    # call main which should write prechecks.json with ok False
    run_smoke.main()
    pj = out_dir / 'prechecks.json'
    assert pj.exists()
    js = json.loads(pj.read_text())
    assert js['ok'] is False
