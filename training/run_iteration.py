"""Full training iteration: selfplay → replay buffer → trainer → evaluate_and_promote.
Usage:
  python3 -m training.run_iteration models/AgentA --iteration 0 --num-selfplay 5
"""
from __future__ import annotations
import argparse, os, json, time, sys
import torch
from .prechecks import run_prechecks
from .metadata_utils import update_metadata
from .device import get_device


def run_iteration(
    agent_dir: str,
    iteration: int = 0,
    num_selfplay: int = 10,
    selfplay_sims: int = 50,
    trainer_iters: int = 100,
    batch_size: int = 128,
    eval_games: int = 200,
    eval_sims: int = 80,
    eval_threshold: float = 0.55,
):
    """Run one complete training iteration."""
    print(f"\n{'='*70}")
    print(f"Iteration {iteration} for {agent_dir}")
    print(f"{'='*70}\n")

    # Step 1: Prechecks
    print("[1/4] Running prechecks...")
    try:
        run_prechecks()
        print("✓ Prechecks passed\n")
    except Exception as e:
        print(f"✗ Prechecks failed: {e}")
        return False

    # Step 2: Self-play (generate replay buffer data)
    print(f"[2/4] Running {num_selfplay} self-play games...")
    try:
        from .selfplay import SelfPlayWorker
        from .model import make_model
        from .replay_buffer import ReplayBuffer
        from core.board.board import Board

        # pick device once for this run
        device = get_device()

        model = make_model(device=device, channels=64, blocks=6)
        from .net import make_net_predictor
        net = make_net_predictor(model)
        worker = SelfPlayWorker(net, mcts_sims=selfplay_sims)
        buf = ReplayBuffer(
            os.path.join(agent_dir, 'checkpoints/replay.pt'),
            capacity=200_000
        )

        total_moves = 0
        for g in range(num_selfplay):
            b = Board()
            recs, outcome = worker.play_game(b, temperature=1.0, max_moves=200)
            for s, pi, player in recs:
                buf.add((s, pi, player, outcome))
            total_moves += len(recs)
            print(f"  Game {g+1}/{num_selfplay}: {len(recs)} moves")

        buf.save()
        print(f"✓ Self-play complete: {total_moves} total moves, buffer size={len(buf)}\n")
    except Exception as e:
        print(f"✗ Self-play failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Train
    print(f"[3/4] Training for {trainer_iters} iterations...")
    try:
        from .trainer import train_loop

        cfg = {
            'ckpt_dir': os.path.join(agent_dir, 'checkpoints'),
            'batch_size': batch_size,
            'lr': 1e-3,
            'wd': 1e-4,
            'iters': trainer_iters,
        }
        # pass the chosen device to the trainer so tensors and model stay on same device
        latest_ckpt = train_loop(model, buf, cfg, device=device)
        print(f"✓ Training complete, checkpoint saved: {latest_ckpt}\n")
    except Exception as e:
        print(f"✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Evaluate and promote
    print(f"[4/4] Evaluating and promoting...")
    try:
        from .eval_loop import promote_if_better

        stats = promote_if_better(
            agent_dir,
            iteration=iteration,
            games=eval_games,
            threshold=eval_threshold,
            sims=eval_sims,
        )
        promoted = stats.get('promoted', False)
        print(f"✓ Arena complete: winrate={stats.get('winrate', 0):.2%}, promoted={promoted}\n")
    except Exception as e:
        print(f"✗ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Update metadata
    update_metadata(agent_dir, iteration=iteration, last_run=time.time())
    print(f"{'='*70}")
    print(f"✓ Iteration {iteration} complete")
    print(f"{'='*70}\n")
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument('agent_dir')
    p.add_argument('--iteration', type=int, default=0)
    p.add_argument('--num-selfplay', type=int, default=5)
    p.add_argument('--selfplay-sims', type=int, default=50)
    p.add_argument('--trainer-iters', type=int, default=100)
    p.add_argument('--batch-size', type=int, default=128)
    p.add_argument('--eval-games', type=int, default=20)
    p.add_argument('--eval-sims', type=int, default=50)
    p.add_argument('--eval-threshold', type=float, default=0.55)
    args = p.parse_args()

    ok = run_iteration(
        args.agent_dir,
        iteration=args.iteration,
        num_selfplay=args.num_selfplay,
        selfplay_sims=args.selfplay_sims,
        trainer_iters=args.trainer_iters,
        batch_size=args.batch_size,
        eval_games=args.eval_games,
        eval_sims=args.eval_sims,
        eval_threshold=args.eval_threshold,
    )
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
