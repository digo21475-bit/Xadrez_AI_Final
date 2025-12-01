"""Utilities to update and manage agent metadata.json."""
from __future__ import annotations
import os, json, time
from datetime import datetime


def update_metadata(agent_dir: str, **updates):
    """Update metadata.json with new fields (iteration, promotion_time, arena_stats, etc.)."""
    meta_path = os.path.join(agent_dir, 'metadata.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            data = json.load(f)
    else:
        data = {'name': os.path.basename(agent_dir), 'created': datetime.now().isoformat()}

    data.update(updates)
    data['last_updated'] = datetime.now().isoformat()

    with open(meta_path, 'w') as f:
        json.dump(data, f, indent=2)


def log_promotion(agent_dir: str, iteration: int, arena_stats: dict):
    """Log a promotion event to metadata."""
    update_metadata(
        agent_dir,
        iteration=iteration,
        promotion_time=time.time(),
        last_arena_stats=arena_stats
    )
