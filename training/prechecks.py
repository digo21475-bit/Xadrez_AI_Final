"""Pre-training integrity checks run before each training iteration.
Lightweight and fast: perft depth 1, encoder mapping roundtrip on root moves.
Raises RuntimeError on failure.
"""
from __future__ import annotations
from training.checks import check_perft, check_mapping_roundtrip


def run_prechecks():
    # perft depth 1 is tiny and verifies movegen integrity
    nodes = check_perft(1)
    if nodes <= 0:
        raise RuntimeError(f"precheck perft failed: nodes={nodes}")

    ok = check_mapping_roundtrip()
    if not ok:
        raise RuntimeError("precheck mapping roundtrip failed")

    return True


if __name__ == '__main__':
    run_prechecks()
