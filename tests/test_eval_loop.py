import os
import json
import time
import pytest

import training.eval_loop as eval_loop


def test_promote_if_better_latest_missing(tmp_path):
    agent = tmp_path / "agent"
    agent.mkdir()
    with pytest.raises(FileNotFoundError):
        eval_loop.promote_if_better(str(agent))


def test_promote_if_better_no_champion(tmp_path, monkeypatch):
    agent = tmp_path / "agent"
    ckpt = agent / "checkpoints"
    ckpt.mkdir(parents=True)
    latest = ckpt / "latest.pt"
    latest.write_text("dummy")

    # ensure no best exists; call promote_if_better
    stats = eval_loop.promote_if_better(str(agent), iteration=1, games=0)
    assert stats['promoted'] is True
    # check arena record files
    exp_dir = agent / 'experiments'
    assert (exp_dir / 'last_arena.json').exists()
    js = json.loads((exp_dir / 'last_arena.json').read_text())
    assert js.get('promoted') is True


def test_promote_if_better_compares_and_writes(tmp_path, monkeypatch):
    agent = tmp_path / "agent"
    ckpt = agent / "checkpoints"
    ckpt.mkdir(parents=True)
    (ckpt / 'latest.pt').write_text('latest')
    (ckpt / 'best.pt').write_text('best')

    # stub play_match to return A wins enough to promote
    def fake_play(a, b, games, sims):
        return {'A': games, 'B': 0, 'draws': 0}

    monkeypatch.setattr('training.eval_loop.play_match', fake_play)
    # monkeypatch log_promotion to avoid side effects
    monkeypatch.setattr('training.eval_loop.log_promotion', lambda *a, **k: None)

    stats = eval_loop.promote_if_better(str(agent), iteration=2, games=5, threshold=0.5, sims=1)
    assert stats['promoted'] is True
    assert 'winrate' in stats
    # CSV should exist
    assert (agent / 'experiments' / 'arena.csv').exists()
