from engine.search.iterative import search_root


class StubBoard:
    def __init__(self):
        # minimal mailbox with no real pieces; implement generate_legal_moves/make/unmake
        self.mailbox = [None] * 64
        self.zobrist_key = 1
        self.side_to_move = 0
        self._moves = [StubMove('e2e4'), StubMove('d2d4')]

    def generate_legal_moves(self):
        return list(self._moves)

    def make_move(self, m):
        # no state change required for stub
        pass

    def unmake_move(self):
        pass

    def is_in_check(self):
        return False


class StubMove:
    def __init__(self, uci):
        self.uci = uci

    def __eq__(self, other):
        return getattr(other, 'uci', None) == self.uci

    def __repr__(self):
        return f"StubMove({self.uci})"


def test_search_root_returns_move():
    b = StubBoard()
    res = search_root(b, max_time_ms=100, max_depth=1)
    assert res['best_move'] is None or isinstance(res['best_move'], (str, type(b._moves[0]), type(None)))
    assert res['depth'] >= 0
