import pytest
from engine.tt.transposition import TranspositionTable, TTEntry, EXACT


def test_tt_store_and_probe():
    tt = TranspositionTable()
    key = 12345
    tt.store(key, depth=3, score=100, flag=EXACT, best_move='e2e4')
    e = tt.probe(key)
    assert e is not None
    assert e.score == 100
    assert e.best_move == 'e2e4'
