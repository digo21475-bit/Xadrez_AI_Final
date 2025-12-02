"""Smoke-run: create model, run one short self-play game, save to replay buffer.
"""
from __future__ import annotations
import json, time, os
from core.board.board import Board
from training.prechecks import run_prechecks
import json, os, time


def net_predict_factory(model):
    from training.net import make_net_predictor
    return make_net_predictor(model)


def main():
    # run prechecks first
    start = time.time()
    try:
        run_prechecks()
        pre_status = {'ok': True, 'time': time.time() - start}
    except Exception as e:
        pre_status = {'ok': False, 'error': str(e), 'time': time.time() - start}

    # persist prechecks
    out_dir = 'models/AgentA/experiments'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'prechecks.json'), 'w') as f:
        json.dump(pre_status, f)

    if not pre_status['ok']:
        print('Prechecks failed; aborting smoke-run. See', os.path.join(out_dir, 'prechecks.json'))
        return

    # proceed only if torch available
    try:
        import torch
        from training.model import make_model
        from training.replay_buffer import ReplayBuffer
        from training.selfplay import SelfPlayWorker
        from training.device import get_device
    except Exception as e:
        print('Torch or model not available:', e)
        print('Prechecks passed; smoke-run skipped (no torch).')
        return

    # small model
    device = get_device()
    model = make_model(device=device, channels=32, blocks=2, action_size=20480)
    net = net_predict_factory(model)
    worker = SelfPlayWorker(net_predict=net, mcts_sims=10)
    b = Board()
    buf = ReplayBuffer('models/AgentA/checkpoints/replay.pt', capacity=1000)
    recs, outcome = worker.play_game(b, temperature=1.0, max_moves=60)
    for s, pi, player in recs:
        buf.add((s, pi, player, 0))
    buf.save()
    print('smoke done, len', len(buf))


if __name__ == '__main__':
    main()
