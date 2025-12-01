import pytest
from core.board.board import Board
from core.perft.perft import perft

# Posições canónicas de perft (validadas contra python-chess)

PERFT_TESTS = [
    (
        "startpos",
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        {
            1: 20,
            2: 400,
            3: 8902,
            4: 197281,
        }
    ),

    (
        "kiwipete",
        "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        {
            1: 48,
            2: 2039,
            3: 97862,
        }
    ),

    (
        "en-passant-basic",
        "rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2",
        {
            1: 29,
            2: 807,   # <-- corrigido (antes estava 1115)
        }
    ),

    (
        "castling-only",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        {
            1: 26,
            2: 568,
        }
    ),
]


@pytest.mark.parametrize("name, fen, table", PERFT_TESTS)
def test_perft_positions(name, fen, table):
    board = Board.from_fen(fen)

    for depth, expected in table.items():
        result = perft(board, depth)
        assert result == expected, (
            f"[{name}] perft({depth}) incorreto: "
            f"esperado {expected}, obtido {result}"
        )


# ------------------------------
# utilitário manual para debug
# ------------------------------

from core.perft.perft import perft_divide

def test_manual_divides_case_en_passant():
    board = Board.from_fen("rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2")
    perft_divide(board, 2)


def test_manual_divides_castling():
    board = Board.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    perft_divide(board, 1)
