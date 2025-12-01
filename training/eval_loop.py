"""Evaluation loop: run arena between current latest and champion; promote best if winrate>55%.
"""
from __future__ import annotations
import os, json, time
from training.arena_runner import play_match
from training.metadata_utils import log_promotion


def promote_if_better(agent_dir: str, iteration: int = 0, games: int = 200, threshold: float = 0.55, sims: int = 80):
    """Run arena: challenger (`latest.pt`) vs champion (`best.pt`) and promote if challenger winrate > threshold.

    Returns stats dict and promoted flag.
    """
    ckpt_dir = os.path.join(agent_dir, 'checkpoints')
    latest = os.path.join(ckpt_dir, 'latest.pt')
    best = os.path.join(ckpt_dir, 'best.pt')

    if not os.path.exists(latest):
        raise FileNotFoundError(f"latest checkpoint not found: {latest}")

    # if no champion exists, promote latest immediately
    if not os.path.exists(best):
        os.replace(latest, best)
        stats = {'promoted': True, 'reason': 'no_champion', 'games': 0}
        _write_arena_record(agent_dir, stats)
        return stats

    # run arena: challenger as A, champion as B
    stats = play_match(latest, best, games=games, sims=sims)

    # compute challenger winrate (wins/games)
    challenger_wins = stats.get('A', 0)
    winrate = challenger_wins / max(1, games)
    promoted = False
    if winrate > threshold:
        # promote: overwrite best.pt with latest.pt
        os.replace(latest, best)
        promoted = True

    stats.update({'promoted': promoted, 'winrate': winrate, 'games': games, 'timestamp': time.time()})
    _write_arena_record(agent_dir, stats)
    if promoted:
        log_promotion(agent_dir, iteration, stats)
    return stats


def _write_arena_record(agent_dir: str, stats: dict):
    exp_dir = os.path.join(agent_dir, 'experiments')
    os.makedirs(exp_dir, exist_ok=True)
    csvp = os.path.join(exp_dir, 'arena.csv')
    jsn = os.path.join(exp_dir, 'last_arena.json')
    # append CSV simple row
    header = 'timestamp,wins_A,wins_B,draws,games,winrate,promoted\n'
    line = f"{stats.get('timestamp', time.time())},{stats.get('A',0)},{stats.get('B',0)},{stats.get('draws',0)},{stats.get('games',0)},{stats.get('winrate',0):.4f},{stats.get('promoted')}\n"
    if not os.path.exists(csvp):
        with open(csvp, 'w') as f:
            f.write(header)
            f.write(line)
    else:
        with open(csvp, 'a') as f:
            f.write(line)

    with open(jsn, 'w') as f:
        json.dump(stats, f, indent=2)
