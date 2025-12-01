from engine.ordering.mvv_lva import score_capture


class DummyMove:
    def __init__(self, piece=None, captured=None):
        self.piece = piece
        self.captured = captured


def test_mvv_lva_orders():
    m1 = DummyMove(piece='PAWN', captured='QUEEN')
    m2 = DummyMove(piece='QUEEN', captured='PAWN')
    s1 = score_capture(m1)
    s2 = score_capture(m2)
    assert s1 > s2
