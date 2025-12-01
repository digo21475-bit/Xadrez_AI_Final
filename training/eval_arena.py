"""Run matches between two agents (models) and report winrate.
"""
from __future__ import annotations
import csv
import os


def run_arena(agentA_play, agentB_play, games=20, out_csv=None):
    # agentX_play(board, as_white:bool) -> outcome from perspective of white
    results = []
    for i in range(games):
        as_white = (i % 2 == 0)
        outcome = agentA_play(as_white) if as_white else agentB_play(not as_white)
        results.append(outcome)

    wins = sum(1 for r in results if r == 1)
    draws = sum(1 for r in results if r == 0)
    losses = sum(1 for r in results if r == -1)

    if out_csv:
        os.makedirs(os.path.dirname(out_csv), exist_ok=True)
        with open(out_csv, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['result'])
            for r in results:
                w.writerow([r])

    return {'wins': wins, 'draws': draws, 'losses': losses, 'games': games}
