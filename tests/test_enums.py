# tests/test_enums.py
from utils.enums import Color, PieceType, MoveType, GameResult, piece_index


def test_color_layout():
    assert Color.WHITE == 0
    assert Color.BLACK == 1
    assert list(Color) == [Color.WHITE, Color.BLACK]


def test_piece_type_layout():
    assert [p.value for p in PieceType] == list(range(6))


def test_move_type_layout():
    # ABI explícita
    assert MoveType.QUIET == 0
    assert MoveType.CAPTURE == 1
    assert MoveType.PROMOTION == 2
    assert MoveType.PROMO_CAP == 3
    assert MoveType.EN_PASSANT == 4
    assert MoveType.CASTLE == 5
    assert len(MoveType) == 6


def test_game_result_layout():
    assert [r.value for r in GameResult] == [0, 1, 2, 3, 4, 5, 6]


def test_piece_index_mapping():
    # WHITE block: 0..5
    for pt in PieceType:
        assert piece_index(pt, Color.WHITE) == pt.value

    # BLACK block: 6..11
    for pt in PieceType:
        assert piece_index(pt, Color.BLACK) == pt.value + 6


def test_enum_reverse_lookup():
    for e in PieceType:
        assert PieceType(e.value) is e
