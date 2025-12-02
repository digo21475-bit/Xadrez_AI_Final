import sys
import importlib
from types import SimpleNamespace

import training.evaluate_and_promote as ep


def test_evaluate_and_promote_main_monkeypatch(monkeypatch, capsys):
    # patch promote_if_better to return a dict
    def fake_promote(agent_dir, iteration, games, threshold, sims):
        return {'promoted': False, 'winrate': 0.0}

    # ensure the evaluate_and_promote module imports the patched function
    monkeypatch.setattr('training.eval_loop.promote_if_better', fake_promote)
    import sys
    monkeypatch.setattr(sys, 'argv', ['prog', 'models/A', '--games', '1'])
    # reload module main to ensure it uses patched sys
    importlib.reload(ep)
    # call main should print arena result
    ep.main()
    captured = capsys.readouterr()
    assert 'arena result' in captured.out
