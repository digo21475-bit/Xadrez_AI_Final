import pytest

from core.board.board import Board
from core.rules.game_status import get_game_status
from core.rules.draw_repetition import RepetitionTable
from core.moves.legal_movegen import generate_legal_moves
from utils.enums import GameResult


# ======================
# CHECKMATE
# ======================
def test_checkmate():
    # Mate: rei preto em h8, dama em g7, rei branco em h6
    board = Board.from_fen("7k/6Q1/7K/8/8/8/8/8 b - - 0 1")

    status = get_game_status(board)

    assert status == GameResult.WHITE_WIN


# ======================
# STALEMATE
# ======================
def test_stalemate():
    # Posição clássica de afogamento
    board = Board.from_fen("7k/5Q2/5K2/8/8/8/8/8 b - - 0 1")

    status = get_game_status(board)

    assert status == GameResult.DRAW_STALEMATE


# ======================
# THREEFOLD REPETITION
# ======================
def test_threefold_repetition():
    board = Board.from_fen("8/8/8/8/8/6N1/5K2/6k1 w - - 0 1")

    repetition_table = RepetitionTable()
    repetition_table.push(board.zobrist_key)

    # repetir posição base 3 vezes
    for _ in range(2):
        white_move = list(generate_legal_moves(board))[0]
        board.make_move(white_move)
        repetition_table.push(board.zobrist_key)

        black_move = list(generate_legal_moves(board))[0]
        board.make_move(black_move)
        repetition_table.push(board.zobrist_key)

        board.unmake_move()
        repetition_table.push(board.zobrist_key)

        board.unmake_move()
        repetition_table.push(board.zobrist_key)

    status = get_game_status(board, repetition_table)

    assert status == GameResult.DRAW_REPETITION


# ======================
# FIFTY MOVE RULE
# ======================
def test_fifty_move_rule():
    board = Board.from_fen("8/8/8/8/8/8/5K2/6k1 w - - 100 75")

    status = get_game_status(board)

    assert status == GameResult.DRAW_FIFTY_MOVE


# ======================
# INSUFFICIENT MATERIAL
# ======================
@pytest.mark.parametrize(
    "fen",
    [
        "8/8/8/8/8/8/5K2/6k1 w - - 0 1",   # K vs K
        "8/8/8/8/8/8/5K2/6kB w - - 0 1",   # K + B vs K
        "8/8/8/8/8/8/5K2/6kN w - - 0 1",   # K + N vs K
    ]
)
def test_insufficient_material(fen):
    board = Board.from_fen(fen)

    status = get_game_status(board)

    assert status == GameResult.DRAW_INSUFFICIENT_MATERIAL


# ======================
# GAME ONGOING
# ======================
def test_game_ongoing():
    board = Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    status = get_game_status(board)

    assert status == GameResult.ONGOING
