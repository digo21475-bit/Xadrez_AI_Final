# scripts/perft_compare.py

from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.perft import perft

import chess


# ==========================
# Helpers
# ==========================

def engine_root_counts(board: Board, depth: int):
    """
    Retorna {uci_move: nodes} do seu engine.
    """
    result = {}

    for move in generate_legal_moves(board):
        board.make_move(move)
        nodes = perft(board, depth - 1)
        board.unmake_move()

        uci = move.to_uci()
        result[uci] = nodes

    return result


def _pychess_perft(board: chess.Board, depth: int) -> int:
    """
    Implementação simples de perft para python-chess.
    """
    if depth == 0:
        return 1

    nodes = 0
    for move in board.legal_moves:
        board.push(move)
        nodes += _pychess_perft(board, depth - 1)
        board.pop()
    return nodes


def reference_root_counts(fen: str, depth: int):
    """
    Retorna {uci_move: nodes} usando python-chess.
    """
    board = chess.Board(fen)
    result = {}

    for move in board.legal_moves:
        board.push(move)
        nodes = _pychess_perft(board, depth - 1)
        board.pop()

        result[move.uci()] = nodes

    return result


def compare_positions(name: str, fen: str, depth: int):
    print("=" * 60)
    print(f"CASE: {name} (depth {depth})")
    print(f"FEN: {fen}\n")

    # Engine
    print("-- building engine root counts --")
    engine_board = Board()
    engine_board.set_fen(fen)

    engine_counts = engine_root_counts(engine_board, depth)
    print("engine root moves:", len(engine_counts))

    # Reference
    print("\n-- building reference (python-chess) root counts --")
    reference_counts = reference_root_counts(fen, depth)
    print("reference root moves:", len(reference_counts))

    # Comparação
    missing = {}
    extra = {}

    for k, v in reference_counts.items():
        if k not in engine_counts:
            missing[k] = v

    for k, v in engine_counts.items():
        if k not in reference_counts:
            extra[k] = v

    if missing:
        print("\nMISSING moves (present in reference, absent in engine):")
        for k in sorted(missing):
            print(f"  {k}: expected {missing[k]}")

    else:
        print("\nNo missing moves.")

    if extra:
        print("\nEXTRA moves (present in engine, absent in reference):")
        for k in sorted(extra):
            print(f"  {k}: got {extra[k]}")
    else:
        print("\nNo extra moves.")

    print("\nTotals:")
    print("  reference total:", sum(reference_counts.values()))
    print("  engine total:   ", sum(engine_counts.values()))
    print("\n")


# ==========================
# Test cases
# ==========================

CASES = [
    (
        "kiwipete",
        "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        1
    ),
    (
        "en-passant-basic",
        "rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2",
        2
    ),
    (
        "castling-only",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        1
    ),
]


if __name__ == "__main__":
    for name, fen, depth in CASES:
        compare_positions(name, fen, depth)

    print("Done.")
