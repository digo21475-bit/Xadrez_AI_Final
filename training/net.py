"""Network prediction wrappers: provide single-call and batched prediction helpers.
The MCTS implementation checks for a `batch_predict` attribute on the net
callable; this module exposes `make_net_predictor(model)` which returns an
object that can be called with a board and also supports `batch_predict(boards)`.
"""
from __future__ import annotations
from typing import Iterable, List, Tuple

import torch


class NetPredictor:
    def __init__(self, model):
        self.model = model
        # infer device from model parameters
        try:
            self.device = next(model.parameters()).device
        except Exception:
            self.device = torch.device('cpu')

    def __call__(self, board):
        # lazy import to avoid circulars
        from training.encoder import board_to_tensor

        x = board_to_tensor(board)
        t = torch.tensor(x[None], dtype=torch.float32, device=self.device)
        pi, v = self.model(t)
        return pi[0].detach(), v[0].detach()

    def batch_predict(self, boards: Iterable) -> Tuple[List, List]:
        """Predict priors and values for a list of board objects in a single
        batched model call. Returns two lists: pi_logits_list and values_list.
        """
        from training.encoder import board_to_tensor

        xs = [board_to_tensor(b) for b in boards]
        if len(xs) == 0:
            return [], []
        import numpy as np
        arr = np.stack(xs, axis=0)
        t = torch.tensor(arr, dtype=torch.float32, device=self.device)
        pi_batch, v_batch = self.model(t)
        # return lists of detached tensors (MCTS handles torch tensors)
        pi_list = [p.detach() for p in pi_batch]
        v_list = [vv.detach() for vv in v_batch]
        return pi_list, v_list


def make_net_predictor(model):
    return NetPredictor(model)
