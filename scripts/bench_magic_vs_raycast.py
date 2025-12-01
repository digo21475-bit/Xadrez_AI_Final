# bench_magic_vs_raycast.py
import time
import random

from core.moves.magic.magic_bitboards import (
    init,
    rook_attacks,
    bishop_attacks,
    _rook_attacks_from_occupancy,
    _bishop_attacks_from_occupancy,
)


# -----------------------------
# Configuração do benchmark
# -----------------------------
ITERATIONS = 10_000_000
SEED = 1337


def random_occupancy(density=0.3) -> int:
    """
    Gera ocupação pseudo-aleatória em 64 bits.
    density: probabilidade de cada bit ser 1.
    """
    occ = 0
    for sq in range(64):
        if random.random() < density:
            occ |= 1 << sq
    return occ


def benchmark_magic_rook(data):
    start = time.perf_counter()
    for sq, occ in data:
        rook_attacks(sq, occ)
    end = time.perf_counter()
    return end - start


def benchmark_magic_bishop(data):
    start = time.perf_counter()
    for sq, occ in data:
        bishop_attacks(sq, occ)
    end = time.perf_counter()
    return end - start


def benchmark_raycast_rook(data):
    start = time.perf_counter()
    for sq, occ in data:
        _rook_attacks_from_occupancy(sq, occ)
    end = time.perf_counter()
    return end - start


def benchmark_raycast_bishop(data):
    start = time.perf_counter()
    for sq, occ in data:
        _bishop_attacks_from_occupancy(sq, occ)
    end = time.perf_counter()
    return end - start


def print_results(label, elapsed):
    nodes_per_sec = ITERATIONS / elapsed
    print(f"{label:30} | {elapsed:8.3f}s | {nodes_per_sec:,.0f} nodes/sec")


if __name__ == "__main__":
    print("Inicializando Magic Bitboards...")
    init()

    random.seed(SEED)

    print("Gerando dados de teste...")
    test_data = [
        (random.randint(0, 63), random_occupancy(density=0.3))
        for _ in range(ITERATIONS)
    ]

    print(f"\nExecutando benchmark com {ITERATIONS:,} iterações")

    t_mr = benchmark_magic_rook(test_data)
    t_rr = benchmark_raycast_rook(test_data)

    t_mb = benchmark_magic_bishop(test_data)
    t_rb = benchmark_raycast_bishop(test_data)

    print("\n================ RESULTADOS ================\n")

    print_results("Magic Rook", t_mr)
    print_results("Ray-Walk Rook", t_rr)
    print_results("Magic Bishop", t_mb)
    print_results("Ray-Walk Bishop", t_rb)

    print("\nSpeedup:")
    print(f"Rook   : {t_rr / t_mr:.2f}x")
    print(f"Bishop : {t_rb / t_mb:.2f}x")
