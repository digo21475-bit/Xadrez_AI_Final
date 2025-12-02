"""Heavy training runner for building a robust model.

This script configures a larger network and a high number of MCTS simulations
for self-play. The default configuration is aggressive and intended for
multi-GPU / long-running runs. For local smoke tests, import `run_heavy`
and call it with small values for `num_selfplay` and `trainer_iters`.
"""
from __future__ import annotations
import os
import time
from typing import Dict, Any


def run_heavy(num_selfplay: int = 256,
              selfplay_sims: int = 800,
              trainer_iters: int = 20000,
              batch_size: int = 512,
              model_kwargs: Dict[str, Any] | None = None,
              agent_dir: str = 'models/AgentA_heavy',
              preferred_device: str | None = None,
              use_reward_shaping: bool = True) -> int:
    """Run a heavy training job.
    
    Args:
        num_selfplay: number of self-play games
        selfplay_sims: MCTS simulations per move
        trainer_iters: training iterations
        batch_size: batch size for training
        model_kwargs: model configuration
        agent_dir: directory to save model
        preferred_device: 'cuda', 'cpu', or None (auto-select)
        use_reward_shaping: if True, use incremental reward shaping
    
    Returns 0 on success, 1 on failure.
    """
    if model_kwargs is None:
        # large model suitable for GPU(s)
        model_kwargs = dict(channels=192, blocks=20, action_size=20480)

    os.makedirs(agent_dir, exist_ok=True)
    ckpt_dir = os.path.join(agent_dir, 'checkpoints')
    os.makedirs(ckpt_dir, exist_ok=True)

    print(f"[run_heavy] Starting heavy run: selfplay={num_selfplay}, sims={selfplay_sims}, iters={trainer_iters}")

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

        device = get_device(preferred_device)
        print('[run_heavy] device =', device)

        model = make_model(device=device, **model_kwargs)
        net = make_net_predictor(model)
        worker = SelfPlayWorker(net, mcts_sims=selfplay_sims, use_reward_shaping=use_reward_shaping)

        buf_path = os.path.join(ckpt_dir, 'replay.pt')
        buf = ReplayBuffer(buf_path, capacity=2_000_000)

        total_moves = 0
        for g in range(num_selfplay):
            b = None
            try:
                from core.board.board import Board
                b = Board()
            except Exception:
                b = None
            recs, outcome = worker.play_game(b, temperature=1.0, max_moves=800)
            for record in recs:
                buf.add(record)
            total_moves += len(recs)
            print(f"  Game {g+1}/{num_selfplay}: {len(recs)} moves, outcome={outcome}")

        buf.save()
        print(f"[run_heavy] Self-play complete, total moves={total_moves}, buffer size={len(buf)}")
        print(f"[run_heavy] Reward shaping: {use_reward_shaping}")

        cfg = {
            'ckpt_dir': ckpt_dir,
            'batch_size': batch_size,
            'lr': 1e-3,
            'wd': 1e-4,
            'iters': trainer_iters,
            'weight_step_reward': 0.3,
            'weight_final_reward': 0.7,
        }

        start = time.time()
        latest = train_loop(model, buf, cfg, device=device)
        print(f"[run_heavy] Training complete, saved: {latest} (took {time.time()-start:.1f}s)")

    except Exception as e:
        print('Run failed:', e)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    # Do not run heavy defaults when executed directly without care.
    print('This is a heavy training runner. Import and call run_heavy(...) programmatically.')
    raise SystemExit(0)
