"""Move ordering helpers: MVV-LVA, history heuristic, simple scoring."""
from typing import Dict

PIECE_VALUE = {
    'PAWN': 100,
    'KNIGHT': 320,
    'BISHOP': 330,
    'ROOK': 500,
    'QUEEN': 900,
    'KING': 20000,
}


def mvv_lva_score(move) -> int:
    """Score a capture by Most Valuable Victim - Least Valuable Attacker.
    
    Higher score = more favorable capture.
    Score = victim_value * 1000 - attacker_value
    
    Args:
        move: Move object with 'captured' and 'piece' attributes
    
    Returns:
        MVV-LVA score (0 if not a capture or missing attributes)
    """
    try:
        victim = getattr(move, 'captured', None)
        attacker = getattr(move, 'piece', None)
        v = PIECE_VALUE.get(str(victim).upper(), 0) if victim is not None else 0
        a = PIECE_VALUE.get(str(attacker).upper(), 0) if attacker is not None else 0
        return v * 1000 - a
    except Exception:
        return 0


class HistoryTable:
    """Tracks history of moves that caused cutoffs (history heuristic)."""
    def __init__(self):
        """Initialize empty history table."""
        self.table: Dict[str, int] = {}

    def add(self, move: object, depth: int) -> None:
        """Record a move causing cutoff with bonus scaled by depth.
        
        Args:
            move: Move that caused beta cutoff
            depth: Depth at which cutoff occurred (deeper = more bonus)
        """
        key = getattr(move, 'uci', None) or repr(move)
        self.table[key] = self.table.get(key, 0) + (1 << depth)

    def score(self, move: object) -> int:
        """Get accumulated history score for a move.
        
        Args:
            move: Move to score
        
        Returns:
            Accumulated score (0 if not in table)
        """
        key = getattr(move, 'uci', None) or repr(move)
        return self.table.get(key, 0)
