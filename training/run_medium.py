"""Medium training runner (CPU-friendly default).

This script performs:
- a small number of self-play games (to populate replay buffer)
- a short training loop using `training.trainer.train_loop`

Designed for local experimentation on CPU. Adjust parameters below.
"""
from __future__ import annotations
import os
import time

from core.board.board import Board


def main():
    # parameters (tweak for longer/shorter runs)
    agent_dir = 'models/AgentA_medium'
    num_selfplay = 6
    selfplay_sims = 20
    trainer_iters = 200
    batch_size = 64
    model_kwargs = dict(channels=32, blocks=3, action_size=20480)

    os.makedirs(agent_dir, exist_ok=True)
    ckpt_dir = os.path.join(agent_dir, 'checkpoints')
    os.makedirs(ckpt_dir, exist_ok=True)

    print(f"[run_medium] Starting medium run: selfplay={num_selfplay}, sims={selfplay_sims}, iters={trainer_iters}")

    try:
        from .prechecks import run_prechecks
        run_prechecks()
    except Exception as e:
        print('Prechecks failed, aborting:', e)
        return 1

    try:
        from .model import make_model
        from .net import make_net_predictor
        from .selfplay import SelfPlayWorker
        from .replay_buffer import ReplayBuffer
        from .trainer import train_loop
        from .device import get_device

        device = get_device()
        print('[run_medium] device =', device)

        # smaller model for CPU
        model = make_model(device=device, **model_kwargs)
        net = make_net_predictor(model)
        worker = SelfPlayWorker(net, mcts_sims=selfplay_sims)

        buf_path = os.path.join(ckpt_dir, 'replay.pt')
        buf = ReplayBuffer(buf_path, capacity=100_000)

        total_moves = 0
        for g in range(num_selfplay):
            b = Board()
            recs, outcome = worker.play_game(b, temperature=1.0, max_moves=200)
            for s, pi, player in recs:
                buf.add((s, pi, player, outcome))
            total_moves += len(recs)
            print(f"  Game {g+1}/{num_selfplay}: {len(recs)} moves")

        buf.save()
        print(f"[run_medium] Self-play complete, total moves={total_moves}, buffer size={len(buf)}")

        # Training
        cfg = {
            'ckpt_dir': ckpt_dir,
            'batch_size': batch_size,
            'lr': 1e-3,
            'wd': 1e-4,
            'iters': trainer_iters,
        }

        start = time.time()
        latest = train_loop(model, buf, cfg, device=device)
        print(f"[run_medium] Training complete, saved: {latest} (took {time.time()-start:.1f}s)")

    except Exception as e:
        print('Run failed:', e)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
