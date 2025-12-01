"""
Example property-based tests using Hypothesis to demonstrate possible expansions.
This file provides a starting point for property tests (not exhaustive).
"""

from hypothesis import given, strategies as st
from core.moves.move import Move
from utils.enums import PieceType

# Simple property: UCI strings are always 4 chars or 5 with promotion
@given(
    from_sq=st.integers(min_value=0, max_value=63),
    to_sq=st.integers(min_value=0, max_value=63),
    piece=st.sampled_from(list(PieceType)),
)
def test_move_to_uci_format(from_sq, to_sq, piece):
    move = Move(from_sq=from_sq, to_sq=to_sq, piece=piece)
    uci = move.to_uci()

    # UCI length is 4 for normal, 5 if promotion (we don't set promotions here)
    assert len(uci) == 4
    assert uci[0].isalpha() and uci[2].isalpha()
    assert uci[1].isdigit() and uci[3].isdigit()
