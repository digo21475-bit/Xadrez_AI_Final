"""Unit test to ensure MCTS uses the batched prediction path when available.

This creates a small fake network object that implements both `__call__`
and `batch_predict`. The test asserts that `batch_predict` was invoked during
`MCTS.run()`.
"""
import pytest
import torch

from training.mcts import MCTS
from training.encoder import index_to_move


class DummyBoard:
    """Minimal board-like object for MCTS testing that accepts any move."""
    def __init__(self, action_size: int):
        # make mailbox large enough for any from-square returned by index_to_move
        max_f = max(index_to_move(i)[0] for i in range(action_size))
        self.mailbox = [(0, 'P') for _ in range(max_f + 1)]

    def copy(self):
        return self

    def make_move(self, mv):
        # accept the move but do nothing
        return

    def is_game_over(self):
        return False

    def game_result(self):
        return 0


class FakeNet:
    def __init__(self, action_size: int, preferred: int = 0):
        self.action_size = action_size
        self.batch_called = False
        self.preferred = preferred

    def __call__(self, board):
        # return logits tensor and scalar value tensor
        logits = torch.zeros(self.action_size, dtype=torch.float32)
        logits[self.preferred % self.action_size] = 1.0
        value = torch.tensor(0.0, dtype=torch.float32)
        return logits, value

    def batch_predict(self, boards):
        # mark that batched path was used
        self.batch_called = True
        logits = torch.zeros(self.action_size, dtype=torch.float32)
        logits[self.preferred % self.action_size] = 1.0
        value = torch.tensor(0.0, dtype=torch.float32)
        return [logits for _ in boards], [value for _ in boards]


def test_mcts_invokes_batch_predict():
    action_size = 32
    # Use a dummy board implementation that accepts any move
    board = DummyBoard(action_size)

    fake = FakeNet(action_size, preferred=0)
    mcts = MCTS(fake, action_size=action_size, sims=8)

    # run should trigger the batched simulation path
    # monkeypatch _descend_to_leaf to avoid dependence on move generation
    from training.mcts import MCTSNode
    def _fake_descend(root, bd):
        return MCTSNode(), [], bd
    mcts._descend_to_leaf = _fake_descend
    pi = mcts.run(board)

    assert fake.batch_called is True, "Expected MCTS to call `batch_predict`"
    assert isinstance(pi, list)
    assert len(pi) == action_size
