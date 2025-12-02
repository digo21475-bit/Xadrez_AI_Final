"""Unit tests for training/replay_buffer.py persistence and sampling."""
import os
import torch

from training.replay_buffer import ReplayBuffer


def test_replay_buffer_add_save_load(tmp_path):
    p = tmp_path / "rb" / "replay.pt"
    path = str(p)
    rb = ReplayBuffer(path, capacity=10)
    assert len(rb) == 0

    # add items
    for i in range(5):
        rb.add((i, i * 2, 1, 0))
    assert len(rb) == 5

    # sample less than size
    s = rb.sample(3)
    assert isinstance(s, list)
    assert len(s) == 3

    # save and reload
    rb.save()
    rb2 = ReplayBuffer(path, capacity=10)
    assert len(rb2) == 5
import os
import tempfile
import importlib


def test_replay_buffer_add_save_load(tmp_path):
    ReplayBuffer = importlib.import_module('training.replay_buffer').ReplayBuffer
    p = tmp_path / 'replay.pt'
    buf = ReplayBuffer(str(p), capacity=10)
    item = (b'board', b'pi', 0, 1)
    buf.add(item)
    assert len(buf) == 1
    buf.save()
    # load new instance
    buf2 = ReplayBuffer(str(p), capacity=10)
    assert len(buf2) == 1

