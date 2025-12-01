# scripts/perft_deep.py

from core.board.board import Board
from core.perft import perft

# ==========================
# Test Positions
# ==========================

TESTS = [
    {
        "name": "startpos",
        "fen": "startpos",
        "expected": {
            4: 197281,
            5: 4865609,
        }
    },
    {
        "name": "kiwipete",
        "fen": "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        "expected": {
            3: 97862,
            4: 4085603,
        }
    },
]


# ==========================
# Runner
# ==========================

def run_perft_test(name: str, fen: str, expected: dict):
    print("=" * 60)
    print(f"TEST: {name}")
    print(f"FEN: {fen}\n")

    board = Board()

    if fen != "startpos":
        board.set_fen(fen)

    for depth, exp_nodes in expected.items():
        print(f"Running perft(depth={depth})...")
        nodes = perft(board, depth)

        print(f"  Result:   {nodes}")
        print(f"  Expected: {exp_nodes}")

        if nodes != exp_nodes:
            print("  ❌ MISMATCH")
            print("  -> Investigate this depth before proceeding\n")
            return False
        else:
            print("  ✅ OK\n")

    return True


def main():
    all_ok = True

    for test in TESTS:
        ok = run_perft_test(
            test["name"],
            test["fen"],
            test["expected"]
        )
        if not ok:
            all_ok = False
            break

    print("=" * 60)

    if all_ok:
        print("✅ ALL PERFT TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")


if __name__ == "__main__":
    main()
