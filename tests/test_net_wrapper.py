"""Tests for `training.net` wrapper behavior (single and batched predict)."""
import torch

from training.net import make_net_predictor


class TinyModel(torch.nn.Module):
    def __init__(self, action_size):
        super().__init__()
        self.action_size = action_size

    def forward(self, x):
        # x: batch x features (we ignore features)
        b = x.shape[0]
        pi = torch.zeros((b, self.action_size), dtype=torch.float32)
        # set a small preference for action 0
        pi[:, 0] = 1.0
        v = torch.zeros((b,), dtype=torch.float32)
        return pi, v


def test_net_predictor_single_and_batch():
    action_size = 8
    model = TinyModel(action_size)
    net = make_net_predictor(model)

    # single call should return tensors
    class FakeBoard:
        pass

    b = FakeBoard()
    p, v = net(b)
    assert hasattr(p, 'detach')
    assert hasattr(v, 'detach')

    # batch_predict should accept a list of boards and return lists
    boards = [FakeBoard() for _ in range(3)]
    pis, vs = net.batch_predict(boards)
    assert isinstance(pis, list) and isinstance(vs, list)
    assert len(pis) == 3 and len(vs) == 3