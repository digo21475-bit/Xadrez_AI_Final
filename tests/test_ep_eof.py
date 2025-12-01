# tests/test_ep_eof.py
import pytest

from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.moves.move import Move
from utils.constants import square_index
from utils.enums import PieceType, Color


def snapshot(board: Board):
    """
    Captura um snapshot minimalista mas suficiente para detectar regressões
    después de make/unmake.
    """
    return {
        "zobrist": board.zobrist_key,
        "side": board.side_to_move,
        "castling": board.castling_rights,
        "ep": board.en_passant_square,
        "half": board.halfmove_clock,
        "full": board.fullmove_number,
        "occ_white": board.occupancy[Color.WHITE],
        "occ_black": board.occupancy[Color.BLACK],
        # bitboards completos
        "bbs": tuple(tuple(row) for row in board.bitboards),
    }


def test_eof_make_unmake_integrity_after_ep_cycle():
    """
    EOF: executa um ciclo de lances com possibilidade de en passant e desfaz tudo,
    verificando que o estado do board é idêntico ao inicial.
    """

    board = Board.from_fen(
        "r3k2r/8/8/3Pp3/8/8/8/R3K2R w KQkq e6 0 1"
    )

    initial = snapshot(board)

    # Gera lances legais
    legal = list(generate_legal_moves(board))

    # Tenta achar um lance de en passant se existir
    ep_moves = [m for m in legal if m.piece == PieceType.PAWN and m.to_sq == board.en_passant_square]

    # Mesmo que o EP seja ilegal futuramente, este teste valida integridade do make/unmake
    for move in legal:
        board.make_move(move)
        board.unmake_move()

    final = snapshot(board)

    assert initial == final, "Estado do board foi corrompido após make/unmake."


def test_eof_ep_exposes_check_should_be_filtered():
    board = Board.from_fen(
        "4r3/8/8/4P3/3p4/8/8/4K3 w - d6 0 1"
    )

    moves = generate_legal_moves(board)
    moves_uci = [m.to_uci() for m in moves]

    assert "e5d6" not in moves_uci  # en passant ilegal


