"""Tests for new engine helpers `tico` and `teco`."""

import random
from unittest.mock import patch

from hypothesis import given, strategies as st

from engine import tico, teco
from core.board.board import Board
from core.moves.move import Move
from utils.enums import PieceType


def _preserve_random_seed(func, *args, **kwargs):
    state = random.getstate()
    try:
        return func(*args, **kwargs)
    finally:
        random.setstate(state)


def test_choose_move_returns_none_on_empty_board():
    board = Board(setup=False)
    board.clear()

    assert tico.choose_move(board) is None
    assert teco.choose_move(board) is None


def test_choose_move_returns_legal_move_startpos():
    board = Board()  # starting position

    mv = _preserve_random_seed(tico.choose_move, board)
    assert mv is not None
    # move must be one of legal moves
    legal = list(__import__('core.moves.legal_movegen', fromlist=['generate_legal_moves']).generate_legal_moves(board))
    assert mv in legal


def test_choose_move_is_deterministic_with_seed():
    board = Board()

    state = random.getstate()
    try:
        random.seed(42)
        mv1 = tico.choose_move(board)

        random.seed(42)
        mv2 = teco.choose_move(board)

        assert mv1 == mv2
    finally:
        random.setstate(state)


def test_choose_move_with_mocked_choice():
    board = Board()
    legal = list(__import__('core.moves.legal_movegen', fromlist=['generate_legal_moves']).generate_legal_moves(board))

    # Force random.choice to return the first legal move
    with patch('random.choice', side_effect=lambda seq: seq[0]):
        mv = tico.choose_move(board)
        assert mv == legal[0]


def test_choose_move_propagates_generate_error():
    board = Board()

    with patch('engine.tico.generate_legal_moves', side_effect=ValueError("boom")):
        try:
            tico.choose_move(board)
            assert False, "Expected exception"
        except ValueError:
            pass


@given(st.lists(st.tuples(st.integers(0, 63), st.integers(0, 63), st.sampled_from(list(PieceType))), min_size=1, max_size=10))
def test_choose_move_hypothesis_moves(mock_moves):
    # Build Move objects from tuples and patch generate_legal_moves to return them
    moves = [Move(from_sq=a, to_sq=b, piece=c) for (a, b, c) in mock_moves]
    board = Board()

    with patch('engine.tico.generate_legal_moves', return_value=moves):
        with patch('random.choice', side_effect=lambda seq: seq[0]):
            mv = tico.choose_move(board)
            assert mv in moves
            assert 0 <= mv.from_sq <= 63 and 0 <= mv.to_sq <= 63
