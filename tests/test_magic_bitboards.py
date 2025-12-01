# Fallback slow attack generators if not present in magic_bitboards
import core.moves.magic.magic_bitboards as mb

mb.init(validate=False)


def _slow_rook_attacks_fallback(square, occ):
    attacks = 0
    file = square & 7
    rank = square >> 3
    # North
    r = rank + 1
    while r < 8:
        sq = (r << 3) | file
        attacks |= 1 << sq
        if (occ >> sq) & 1: break
        r += 1
    # South
    r = rank - 1
    while r >= 0:
        sq = (r << 3) | file
        attacks |= 1 << sq
        if (occ >> sq) & 1: break
        r -= 1
    # East
    f = file + 1
    while f < 8:
        sq = (rank << 3) | f
        attacks |= 1 << sq
        if (occ >> sq) & 1: break
        f += 1
    # West
    f = file - 1
    while f >= 0:
        sq = (rank << 3) | f
        attacks |= 1 << sq
        if (occ >> sq) & 1: break
        f -= 1
    return attacks

def _slow_bishop_attacks_fallback(square, occ):
    attacks = 0
    file = square & 7
    rank = square >> 3
    # NE
    f, r = file + 1, rank + 1
    while f < 8 and r < 8:
        sq = (r << 3) | f
        attacks |= 1 << sq
        if (occ >> sq) & 1: break
        f += 1; r += 1
    # NW
    f, r = file - 1, rank + 1
    while f >= 0 and r < 8:
        sq = (r << 3) | f
        attacks |= 1 << sq
        if (occ >> sq) & 1: break
        f -= 1; r += 1
    # SE
    f, r = file + 1, rank - 1
    while f < 8 and r >= 0:
        sq = (r << 3) | f
        attacks |= 1 << sq
        if (occ >> sq) & 1: break
        f += 1; r -= 1
    # SW
    f, r = file - 1, rank - 1
    while f >= 0 and r >= 0:
        sq = (r << 3) | f
        attacks |= 1 << sq
        if (occ >> sq) & 1: break
        f -= 1; r -= 1
    return attacks


from core.moves.magic import magic_bitboards as mb

# SQUARES not defined in constants
SQUARES = range(64)


def test_init_runs_without_error():
    mb.init()
    assert mb._INITIALIZED is True


def test_tables_sizes():
    mb.init()

    assert len(mb.ROOK_GOOD_MAGICS) == 64
    assert len(mb.BISHOP_GOOD_MAGICS) == 64

    assert len(mb.ROOK_MASKS) == 64
    assert len(mb.BISHOP_MASKS) == 64

    assert len(mb.ROOK_SHIFTS) == 64
    assert len(mb.BISHOP_SHIFTS) == 64

    assert len(mb.ROOK_ATTACK_OFFSETS) == 64
    assert len(mb.BISHOP_ATTACK_OFFSETS) == 64

    assert len(mb._ROOK_ATT_TABLE) > 0
    assert len(mb._BISHOP_ATT_TABLE) > 0


def test_no_collisions_in_tables():
    mb.init()

    for square in range(64):
        rmask = mb.ROOK_MASKS[square]
        bmask = mb.BISHOP_MASKS[square]

        rook_indices = set()
        bishop_indices = set()

        rmagic = mb.ROOK_GOOD_MAGICS[square]
        bmagic = mb.BISHOP_GOOD_MAGICS[square]
        rshift = mb.ROOK_SHIFTS[square]
        bshift = mb.BISHOP_SHIFTS[square]

        rook_bits = mb._MASK_POSITIONS[(square, True)]
        bishop_bits = mb._MASK_POSITIONS[(square, False)]

        for idx in range(1 << len(rook_bits)):
            occ = mb.index_to_occupancy(idx, rook_bits)
            index = ((occ & rmask) * rmagic) >> rshift
            assert index not in rook_indices, f"Rook magic collision on square {square}"
            rook_indices.add(index)

        for idx in range(1 << len(bishop_bits)):
            occ = mb.index_to_occupancy(idx, bishop_bits)
            index = ((occ & bmask) * bmagic) >> bshift
            assert index not in bishop_indices, f"Bishop magic collision on square {square}"
            bishop_indices.add(index)


def test_rook_attacks_consistency():
    mb.init()
    for square in range(64):
        bits = mb._MASK_POSITIONS[(square, True)]

        for idx in range(min(256, 1 << len(bits))):
            occ = mb.index_to_occupancy(idx, bits)
            atk1 = mb.rook_attacks(square, occ)
            atk2 = getattr(mb, '_slow_rook_attacks', _slow_rook_attacks_fallback)(square, occ)
            assert atk1 == atk2


def test_bishop_attacks_consistency():
    mb.init()
    for square in range(64):
        bits = mb._MASK_POSITIONS[(square, False)]

        for idx in range(min(256, 1 << len(bits))):
            occ = mb.index_to_occupancy(idx, bits)
            atk1 = mb.bishop_attacks(square, occ)
            atk2 = getattr(mb, '_slow_bishop_attacks', _slow_bishop_attacks_fallback)(square, occ)
            assert atk1 == atk2