"""Run arena between two checkpoints by loading models and using SelfPlayWorker.
Requires torch.
"""
from __future__ import annotations
from training.selfplay import SelfPlayWorker
from training.model import make_model
from core.board.board import Board
from .device import get_device


def net_predict_factory_from_model(model):
    from training.net import make_net_predictor
    return make_net_predictor(model)


def play_match(ckptA, ckptB, games=20, sims=50):
    import torch
    cfg = {'channels':64,'blocks':6,'in_planes':13,'action_size':20480}
    device = get_device()
    A = make_model(device=device, **cfg)
    B = make_model(device=device, **cfg)
    A.load_state_dict(torch.load(ckptA, map_location=device))
    B.load_state_dict(torch.load(ckptB, map_location=device))
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
