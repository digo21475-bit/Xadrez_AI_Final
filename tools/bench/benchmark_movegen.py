"""
Simple benchmark harness for move generation and perft sampling.
Run this locally to get a rough performance measure.
"""

import time
from core.board.board import Board
from core.perft.perft import perft
from core.moves.legal_movegen import generate_legal_moves


def bench_movegen(iterations: int = 1000):
    b = Board()
    start = time.perf_counter()
    for _ in range(iterations):
        list(generate_legal_moves(b))
    end = time.perf_counter()
    print(f"Generated moves {iterations} times in {end - start:.4f}s")


def bench_perft(depth: int = 3):
    b = Board()
    start = time.perf_counter()
    nodes = perft(b, depth)
    end = time.perf_counter()
    print(f"Perft(depth={depth}) = {nodes} in {end - start:.4f}s")


if __name__ == '__main__':
    print("Quick benchmarks")
    bench_movegen(100)
    bench_perft(3)
