"""CLI: evaluate latest vs best for an agent and promote if challenger is better.

Usage:
  python3 training/evaluate_and_promote.py models/AgentA --games 200 --threshold 0.55
"""
from __future__ import annotations
import argparse, os, json
from training.eval_loop import promote_if_better


def main():
    p = argparse.ArgumentParser()
    p.add_argument('agent_dir')
    p.add_argument('--iteration', type=int, default=0)
    p.add_argument('--games', type=int, default=200)
    p.add_argument('--threshold', type=float, default=0.55)
    p.add_argument('--sims', type=int, default=80)
    args = p.parse_args()

    stats = promote_if_better(args.agent_dir, iteration=args.iteration, games=args.games, threshold=args.threshold, sims=args.sims)
    print('arena result:', json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
