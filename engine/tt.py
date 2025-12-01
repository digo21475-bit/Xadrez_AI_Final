"""Transposition table wrapper (top-level).

Provides simple TT with probe/store and flags.
"""
from dataclasses import dataclass
from typing import Optional, Dict

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


@dataclass
class TTEntry:
    """Entry in transposition table: stores evaluation and best move for a position."""
    key: int
    depth: int
    score: int
    flag: int
    best_move: Optional[object]


class TranspositionTable:
    """Simple transposition table using dict-backed storage."""
    def __init__(self, size_mb: int = 16):
        """Initialize transposition table.
        
        Args:
            size_mb: Hint for size (ignored with dict backend)
        """
        # simple dict-backed TT
        self.table: Dict[int, TTEntry] = {}

    def probe(self, key: int) -> Optional[TTEntry]:
        """Look up position in transposition table.
        
        Args:
            key: Zobrist hash of position
        
        Returns:
            TTEntry if found, None otherwise
        """
        return self.table.get(key)

    def store(self, key: int, depth: int, score: int, flag: int, best_move: Optional[object]):
        """Store position evaluation in transposition table.
        
        Replaces existing entry if new depth >= old depth.
        
        Args:
            key: Zobrist hash of position
            depth: Depth searched
            score: Evaluation score
            flag: EXACT, LOWERBOUND, or UPPERBOUND
            best_move: Best move found for this position
        """
        entry = self.table.get(key)
        # prefer deeper or replace
        if entry is None or depth >= entry.depth:
            self.table[key] = TTEntry(key=key, depth=depth, score=score, flag=flag, best_move=best_move)

    def clear(self):
        """Clear all entries from transposition table."""
        self.table.clear()
