# tests/test_attack_tables_geometry.py
from core.moves.tables import attack_tables as at

at.init()

KNIGHT_ATTACKS = at.KNIGHT_ATTACKS
KING_ATTACKS = at.KING_ATTACKS
PAWN_ATTACKS = at.PAWN_ATTACKS
from utils.enums import Color

def mirror_square(sq: int) -> int:
    file = sq & 7
    rank = sq >> 3
    return (rank << 3) | (7 - file)

def mirror_bitboard(bb: int) -> int:
    res = 0
    for sq in range(64):
        if (bb >> sq) & 1:
            res |= 1 << mirror_square(sq)
    return res

def bitcount(x: int) -> int:
    return x.bit_count()

def test_knight_geometry_extremes():
    # Cantos
    assert bitcount(KNIGHT_ATTACKS[0]) == 2      # A1
    assert bitcount(KNIGHT_ATTACKS[7]) == 2      # H1
    assert bitcount(KNIGHT_ATTACKS[56]) == 2     # A8
    assert bitcount(KNIGHT_ATTACKS[63]) == 2     # H8

    # Centro (D4 = 27)
    assert bitcount(KNIGHT_ATTACKS[27]) == 8

def test_king_geometry_extremes():
    # Canto REI
    assert bitcount(KING_ATTACKS[0]) == 3

    # Centro
    assert bitcount(KING_ATTACKS[27]) == 8

def test_pawn_attack_geometry():
    # Pawn branco não ataca para baixo
    assert PAWN_ATTACKS[Color.WHITE][8] & (1 << 0) == 0

    # Pawn preto não ataca para cima
    assert PAWN_ATTACKS[Color.BLACK][55] & (1 << 63) == 0

def test_knight_symmetry_horizontal():
    for sq in range(64):
        mirrored = mirror_square(sq)

        orig = KNIGHT_ATTACKS[sq]
        flipped = mirror_bitboard(KNIGHT_ATTACKS[mirrored])

        assert orig == flipped, f"Knight symmetry broken em sq={sq}"

def test_king_symmetry_horizontal():
    for sq in range(64):
        mirrored = mirror_square(sq)

        orig = KING_ATTACKS[sq]
        flipped = mirror_bitboard(KING_ATTACKS[mirrored])

        assert orig == flipped, f"King symmetry broken em sq={sq}"
