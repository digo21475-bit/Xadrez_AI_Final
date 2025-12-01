from typing import List, Optional
from engine.ordering.mvv_lva import score_capture


class MovePicker:
    def __init__(self, board, moves: List[object], ply: int = 0, tt_move: Optional[object] = None,
                 killers=None, history=None):
        self.board = board
        self.moves = list(moves)
        self.ply = ply
        self.tt_move = tt_move
        self.killers = killers
        self.history = history
        self._sorted = False

    def _score(self, move):
        # highest priority to TT move
        if self.tt_move is not None and move == self.tt_move:
            return 10_000_000
        # captures
        sc = score_capture(move)
        if sc:
            return 1_000_000 + sc
        # killers
        if self.killers is not None:
            k0, k1 = self.killers.get(self.ply)
            if move == k0:
                return 900_000
            if move == k1:
                return 800_000
        # history
        if self.history is not None:
            return 1000 + self.history.score(move)
        return 0

    def _sort(self):
        if not self._sorted:
            self.moves.sort(key=self._score, reverse=True)
            self._sorted = True

    def next(self):
        self._sort()
        if not self.moves:
            return None
        return self.moves.pop(0)
