"""Unit tests for MCTS core behaviors (visit distribution, sims edge cases)."""
import pytest
import torch

from training.mcts import MCTS


class DummyBoard:
    def __init__(self, action_size: int):
        # mailbox large enough
        self.mailbox = [(0, 'P') for _ in range(64)]

    def copy(self):
        return self

    def make_move(self, mv):
        return

    def is_game_over(self):
        return False

    def game_result(self):
        return 0


class SimpleNet:
    def __init__(self, action_size):
        self.action_size = action_size

    def __call__(self, board):
        logits = torch.zeros(self.action_size, dtype=torch.float32)
        logits += 1.0
        value = torch.tensor(0.0, dtype=torch.float32)
        return logits, value


@pytest.mark.parametrize("sims", [0, 1, 8])
def test_mcts_visits_distribution_basic(sims):
    action_size = 16
    net = SimpleNet(action_size=action_size)
    m = MCTS(net, action_size=action_size, sims=sims)
    board = DummyBoard(action_size)
    pi = m.run(board)
    assert isinstance(pi, list)
    assert len(pi) == action_size
    if sims == 0:
        assert all(abs(p - 1/action_size) < 1e-6 for p in pi)