from dataclasses import dataclass
from typing import Optional, Dict


EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


@dataclass
class TTEntry:
    key: int
    depth: int
    score: int
    flag: int
    best_move: Optional[object]


class TranspositionTable:
    """Simple transposition table using a dict keyed by zobrist key."""

    def __init__(self, size_mb: int = 16):
        self.table: Dict[int, TTEntry] = {}

    def probe(self, key: int) -> Optional[TTEntry]:
        return self.table.get(key)

    def store(self, key: int, depth: int, score: int, flag: int, best_move: Optional[object]):
        entry = self.table.get(key)
        # Replace if deeper or not present
        if entry is None or depth >= entry.depth:
            self.table[key] = TTEntry(key=key, depth=depth, score=score, flag=flag, best_move=best_move)

    def clear(self):
        self.table.clear()
