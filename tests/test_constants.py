# tests/test_constants.py
from utils.constants import (
    FILE_A, FILE_H,
    RANK_1, RANK_8,
    CENTER_4_MASK,
    PIECE_COUNT, COLOR_COUNT, MOVE_TYPE_COUNT,
    SQUARE_BB, sq
)


def test_bitboard_file_rank_integrity():
    assert FILE_A & RANK_1  # A1
    assert FILE_H & RANK_8  # H8

    assert bin(FILE_A).count("1") == 8
    assert bin(RANK_1).count("1") == 8


def test_square_mapping_is_linear():
    for file in range(8):
        for rank in range(8):
            s = sq(file, rank)
            assert 0 <= s < 64
            assert s == (rank << 3) + file


def test_square_bb_is_power_of_two():
    for i, bb in enumerate(SQUARE_BB):
        assert bb == (1 << i)


def test_center_4_geometry():
    # D4, E4, D5, E5
    expected = (
        (1 << sq(3, 3)) |
        (1 << sq(4, 3)) |
        (1 << sq(3, 4)) |
        (1 << sq(4, 4))
    )
    assert CENTER_4_MASK == expected


def test_global_counts():
    assert PIECE_COUNT == 12
    assert COLOR_COUNT == 2
    assert MOVE_TYPE_COUNT == 6

def test_directions_offsets():
    from utils.constants import NORTH, SOUTH, EAST, WEST
    assert NORTH == 8
    assert SOUTH == -8
    assert EAST == 1
    assert WEST == -1

def test_file_masks_no_overlap():
    from utils.constants import FILES_MASKS

    for i in range(8):
        for j in range(8):
            if i != j:
                assert (FILES_MASKS[i] & FILES_MASKS[j]) == 0

def test_file_a_excludes_file_b():
    from utils.constants import NOT_FILE_A, FILE_B
    assert NOT_FILE_A & FILE_B == FILE_B


def test_square_file_rank_consistency():
    from utils.constants import sq, SQUARE_TO_FILE, SQUARE_TO_RANK

    for f in range(8):
        for r in range(8):
            s = sq(f, r)
            assert SQUARE_TO_FILE[s] == f
            assert SQUARE_TO_RANK[s] == r
