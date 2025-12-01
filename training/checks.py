"""Integrity checks: perft, encoder round-trip, action mapping.
"""
from __future__ import annotations
from core.perft.perft import perft
from core.board.board import Board
from training.encoder import index_to_move, move_to_index
from core.moves.legal_movegen import generate_legal_moves


def check_perft(depth=3):
    b = Board()
    nodes = perft(b, depth)
    print('perft', depth, nodes)
    return nodes


def check_mapping_roundtrip(n=50):
    b = Board()
    moves = list(generate_legal_moves(b))
    for mv in moves[:n]:
        idx = move_to_index(mv)
        f,t,p = index_to_move(idx)
        if f != mv.from_sq or t != mv.to_sq:
            print('mismatch', mv, idx, (f,t,p))
            return False
    print('mapping roundtrip ok')
    return True


def run_all():
    ok1 = check_perft(3)
    ok2 = check_mapping_roundtrip()
    return ok1, ok2


if __name__ == '__main__':
    run_all()
