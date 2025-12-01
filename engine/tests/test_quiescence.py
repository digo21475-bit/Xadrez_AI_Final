from engine.search.alphabeta import quiescence, SearchState


class CaptureMove:
    def __init__(self, piece='PAWN', captured='QUEEN'):
        self.piece = piece
        self.captured = captured


class StubBoard:
    def __init__(self):
        # one capture available
        self.mailbox = [None] * 64
        self.zobrist_key = 2
        self.side_to_move = 0
        self._moves = [CaptureMove()]

    def generate_legal_moves(self, captures_only=False):
        if captures_only:
            return list(self._moves)
        return list(self._moves)

    def make_move(self, m):
        pass

    def unmake_move(self):
        pass


def test_quiescence_handles_capture():
    b = StubBoard()
    state = SearchState()
    val = quiescence(b, -10000, 10000, state, ply=0)
    assert isinstance(val, int)
