"""Move ordering: selects and orders moves for alpha-beta search.

Uses multiple heuristics:
1. Transposition table moves (best from previous iterations)
2. MVV-LVA scoring for captures
3. Killer moves (quiet moves that cause cutoffs)
4. History heuristic (moves that worked well before)
"""
from typing import List, Optional
from .move_ordering import mvv_lva_score, HistoryTable


class Killers:
    """Stores killer moves (quiet moves causing beta cutoff) by ply."""
    def __init__(self, max_ply: int = 512):
        """Initialize killer moves table.
        
        Args:
            max_ply: Maximum search depth to track killers
        """
        self.killers = [[None, None] for _ in range(max_ply)]

    def add(self, ply: int, move: object) -> None:
        """Add a killer move at given ply.
        
        Args:
            ply: Search depth
            move: Quiet move that caused beta cutoff
        """
        if ply >= len(self.killers):
            return
        if move == self.killers[ply][0]:
            return
        self.killers[ply][1] = self.killers[ply][0]
        self.killers[ply][0] = move

    def get(self, ply: int) -> tuple:
        """Get killer moves at given ply.
        
        Args:
            ply: Search depth
            
        Returns:
            Tuple of (primary_killer, secondary_killer) or (None, None)
        """
        if ply >= len(self.killers):
            return (None, None)
        return tuple(self.killers[ply])


class MovePicker:
    """Orders and returns moves in priority order for search."""
    def __init__(self, board: object, moves: List[object], ply: int = 0, 
                 tt_move: Optional[object] = None,
                 killers: Optional[Killers] = None, 
                 history: Optional[HistoryTable] = None):
        """Initialize move picker.
        
        Args:
            board: Chess position
            moves: List of legal moves to order
            ply: Current search depth (for killers)
            tt_move: Best move from transposition table
            killers: Killer moves table
            history: History heuristic table
        """
        self.board = board
        self.moves = list(moves)
        self.ply = ply
        self.tt_move = tt_move
        self.killers = killers or Killers()
        self.history = history or HistoryTable()
        self._sorted = False

    def _score(self, move: object) -> int:
        """Score a move for ordering (higher = better).
        
        Priority:
        1. Transposition table move (10M)
        2. Captures by MVV-LVA (1M + score)
        3. Killer moves (900k, 800k)
        4. History heuristic (1k + score)
        """
        # TT move highest priority
        if self.tt_move is not None and move == self.tt_move:
            return 10_000_000
        
        # Captures scored by MVV-LVA
        sc = mvv_lva_score(move)
        if sc:
            return 1_000_000 + sc
        
        # Killer moves
        k0, k1 = self.killers.get(self.ply)
        if move == k0:
            return 900_000
        if move == k1:
            return 800_000
        
        # History heuristic
        return 1000 + self.history.score(move)

    def _sort(self) -> None:
        """Sort moves by priority once (lazy sort)."""
        if not self._sorted:
            self.moves.sort(key=self._score, reverse=True)
            self._sorted = True

    def next(self) -> Optional[object]:
        """Get next best move, sorting on first call.
        
        Returns:
            Next move or None if no moves left
        """
        self._sort()
        if not self.moves:
            return None
        return self.moves.pop(0)
