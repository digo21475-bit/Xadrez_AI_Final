import pytest
import torch

from training.mcts import MCTS, MCTSNode
from training.net import make_net_predictor
from training.encoder import index_to_move


class DummyBoard:
    def __init__(self, max_sq=64):
        self.mailbox = [(0, 'P') for _ in range(max_sq)]

    def copy(self):
        return self

    def make_move(self, mv):
        # accept any move
        return

    def is_game_over(self):
        return False

    def game_result(self):
        return 0


class SimpleNet:
    def __init__(self, action_size, value=0.5):
        self.action_size = action_size
        self._value = value

    def __call__(self, board):
        logits = torch.ones(self.action_size, dtype=torch.float32)
        v = torch.tensor(self._value, dtype=torch.float32)
        return logits, v


def test_mcts_simulate_backprop_updates_counts(monkeypatch):
    action_size = 16
    net = SimpleNet(action_size)
    m = MCTS(net, action_size=action_size, sims=1)

    root = MCTSNode()
    # create one child so descent will add to path
    child = MCTSNode()
    child.P = 1.0
    root.children[0] = child

    # replace frozen Move with a mutable stand-in so tests can set piece
    class MutableMove:
        def __init__(self, from_sq, to_sq, piece=None, is_capture=False, promotion=None):
            self.from_sq = from_sq
            self.to_sq = to_sq
            self.piece = piece
            self.is_capture = is_capture
            self.promotion = promotion

    monkeypatch.setattr('training.mcts.Move', MutableMove, raising=False)
    board = DummyBoard()
    # call private simulate to trigger selection->expansion->backup
    m._simulate(root, board)

    # after simulation there should be at least one visit counted
    assert root.N >= 1
    assert child.N >= 1
    assert child.W >= 0
    assert child.Q == pytest.approx(child.W / child.N)


def test_mcts_run_uses_batch_predict():
    import training.mcts as mcts_mod
    from types import SimpleNamespace
    
    # ensure Move is mutable for move application during descent
    class MutableMove:
        def __init__(self, from_sq, to_sq, piece=None, is_capture=False, promotion=None):
            self.from_sq = from_sq
            self.to_sq = to_sq
            self.piece = piece
            self.is_capture = is_capture
            self.promotion = promotion

    # monkeypatch Move in mcts module
    setattr(mcts_mod, 'Move', MutableMove)

    action_size = 8

    class FakeModel:
        def __init__(self):
            pass

        def __call__(self, t):
            b = t.shape[0]
            pi = torch.ones((b, action_size), dtype=torch.float32)
            v = torch.zeros((b,), dtype=torch.float32)
            return pi, v

    class FakeNet:
        def __init__(self, model):
            self.model = model
            self.batch_called = False

        def __call__(self, board):
            # return logits and value tensor
            logits = torch.ones(action_size, dtype=torch.float32)
            v = torch.tensor(0.0)
            return logits, v

        def batch_predict(self, boards):
            self.batch_called = True
            # return per-board tensors
            pi = torch.ones((len(boards), action_size), dtype=torch.float32)
            v = torch.zeros((len(boards),), dtype=torch.float32)
            return [pi[i] for i in range(len(boards))], [v[i] for i in range(len(boards))]

    fake = FakeNet(FakeModel())
    m = MCTS(fake, action_size=action_size, sims=4)
    board = DummyBoard()

    pi = m.run(board)
    assert isinstance(pi, list)
    # ensure batch path was used
    assert fake.batch_called is True
