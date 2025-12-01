"""Run arena between two checkpoints by loading models and using SelfPlayWorker.
Requires torch.
"""
from __future__ import annotations
from training.selfplay import SelfPlayWorker
from training.model import make_model
from core.board.board import Board


def net_predict_factory_from_model(model):
    def predict(board):
        from training.encoder import board_to_tensor
        import torch
        x = board_to_tensor(board)
        t = torch.tensor(x[None], dtype=torch.float32)
        pi, v = model(t)
        return pi[0].detach().cpu(), v[0].detach().cpu()
    return predict


def play_match(ckptA, ckptB, games=20, sims=50):
    import torch
    cfg = {'channels':64,'blocks':6,'in_planes':13,'action_size':20480}
    A = make_model(device='cpu', **cfg)
    B = make_model(device='cpu', **cfg)
    A.load_state_dict(torch.load(ckptA, map_location='cpu'))
    B.load_state_dict(torch.load(ckptB, map_location='cpu'))
    netA = net_predict_factory_from_model(A)
    netB = net_predict_factory_from_model(B)

    stats = {'A':0,'B':0,'draws':0}
    for i in range(games):
        b = Board()
        # alternate who uses which model (white/black)
        if i % 2 == 0:
            wnet, bnet = netA, netB
        else:
            wnet, bnet = netB, netA
        # simple loop: each side selects best from its MCTS (single-threaded)
        workerW = SelfPlayWorker(wnet, mcts_sims=sims)
        recs, outcome = workerW.play_game(b, temperature=0.0, max_moves=200)
        if outcome == 1:
            stats['A' if i%2==0 else 'B'] += 1
        elif outcome == -1:
            stats['B' if i%2==0 else 'A'] += 1
        else:
            stats['draws'] += 1

    return stats
