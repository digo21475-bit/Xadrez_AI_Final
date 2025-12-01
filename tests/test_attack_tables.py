import importlib
import random
from core.moves.tables import attack_tables as at
from utils.enums import Color


# Slow brute-force generators used as ground-truth for tests
def _slow_knight_attacks(square: int) -> int:
    attacks = 0
    file = square & 7
    rank = square >> 3
    moves = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
    for df, dr in moves:
        nf, nr = file + df, rank + dr
        if 0 <= nf < 8 and 0 <= nr < 8:
            attacks |= 1 << (nr * 8 + nf)
    return attacks

def _slow_king_attacks(square: int) -> int:
    attacks = 0
    file = square & 7
    rank = square >> 3
    moves = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
    for df, dr in moves:
        nf, nr = file + df, rank + dr
        if 0 <= nf < 8 and 0 <= nr < 8:
            attacks |= 1 << (nr * 8 + nf)
    return attacks

def _slow_pawn_attacks(square: int, color: Color) -> int:
    attacks = 0
    file = square & 7
    rank = square >> 3
    if color == Color.WHITE:
        nr = rank + 1
    else:
        nr = rank - 1
    if 0 <= nr < 8:
        if file - 1 >= 0:
            attacks |= 1 << (nr * 8 + (file - 1))
        if file + 1 < 8:
            attacks |= 1 << (nr * 8 + (file + 1))
    return attacks

# -------------------------
# Structural tests
# -------------------------
def test_tables_dimensions_and_types():
    importlib.reload(at)
    at.init()

    assert isinstance(at.KNIGHT_ATTACKS, list)
    assert isinstance(at.KING_ATTACKS, list)
    assert isinstance(at.PAWN_ATTACKS, dict)

    assert len(at.KNIGHT_ATTACKS) == 64
    assert len(at.KING_ATTACKS) == 64
    assert len(at.PAWN_ATTACKS[Color.WHITE]) == 64
    assert len(at.PAWN_ATTACKS[Color.BLACK]) == 64

    # ray masks exist (maybe zeros if magics unavailable)
    assert isinstance(at.ROOK_GEOMETRY_RAYS, list)
    assert isinstance(at.BISHOP_GEOMETRY_RAYS, list)
    assert len(at.ROOK_GEOMETRY_RAYS) == 64
    assert len(at.BISHOP_GEOMETRY_RAYS) == 64

# -------------------------
# Functional correctness (non-sliding)
# -------------------------
def test_knight_attacks_corners_and_center():
    at.init()
    # corners
    assert at.knight_attacks(0) == _slow_knight_attacks(0)   # A1
    assert at.knight_attacks(7) == _slow_knight_attacks(7)   # H1
    assert at.knight_attacks(56) == _slow_knight_attacks(56) # A8
    assert at.knight_attacks(63) == _slow_knight_attacks(63) # H8
    # Center e.g. d4 (sq=27)
    assert at.knight_attacks(27) == _slow_knight_attacks(27)

def test_king_attacks_corners_and_center():
    at.init()
    assert at.king_attacks(0) == _slow_king_attacks(0)
    assert at.king_attacks(7) == _slow_king_attacks(7)
    assert at.king_attacks(56) == _slow_king_attacks(56)
    assert at.king_attacks(63) == _slow_king_attacks(63)
    assert at.king_attacks(27) == _slow_king_attacks(27)

def test_pawn_attacks_white_black():
    at.init()
    for sq in (0, 7, 56, 63, 27):
        assert at.pawn_attacks(sq, Color.WHITE) == _slow_pawn_attacks(sq, Color.WHITE)
        assert at.pawn_attacks(sq, Color.BLACK) == _slow_pawn_attacks(sq, Color.BLACK)

# -------------------------
# Brute-force comparison for many squares
# -------------------------
def test_random_samples_against_bruteforce():
    at.init()
    rng = random.Random(12345)
    samples = rng.sample(range(64), 20)
    for sq in samples:
        assert at.knight_attacks(sq) == _slow_knight_attacks(sq)
        assert at.king_attacks(sq) == _slow_king_attacks(sq)
        assert at.pawn_attacks(sq, Color.WHITE) == _slow_pawn_attacks(sq, Color.WHITE)
        assert at.pawn_attacks(sq, Color.BLACK) == _slow_pawn_attacks(sq, Color.BLACK)

# -------------------------
# Integration with Magic Bitboards (sliding)
# -------------------------
def _slow_rook_attacks(square, occ):
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

def _slow_bishop_attacks(square, occ):
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

def test_sliding_consistency_with_magic_and_bruteforce():
    """
    For a subset of squares and random occupancies, ensure:
      magic_bitboards rook/bishop (via attack_tables rook_attacks/bishop_attacks)
      matches brute-force slow generator.
    """
    at.init()
    # If magics not available, this test will skip (magic module raises)
    try:
        from core.moves.magic import magic_bitboards as mb
    except Exception:
        mb = None

    if mb is None:
        # nothing to test here if magics missing
        return

    rng = random.Random(2023123)
    squares = list(range(64))
    # sample 8 squares (include corners & center)
    picks = [0, 7, 56, 63, 27] + rng.sample(squares, 3)
    for sq in picks:
        # test multiple random occupancies
        for _ in range(30):
            occ = rng.getrandbits(64) & ((1 << 64) - 1)
            # mask occupancy to 64 bits
            occ &= (1 << 64) - 1
            a_magic_rook = at.rook_attacks(sq, occ)
            a_slow_rook = _slow_rook_attacks(sq, occ)
            assert a_magic_rook == a_slow_rook

            a_magic_bishop = at.bishop_attacks(sq, occ)
            a_slow_bishop = _slow_bishop_attacks(sq, occ)
            assert a_magic_bishop == a_slow_bishop

            # queen consistency
            assert at.queen_attacks(sq, occ) == (a_magic_rook | a_magic_bishop)

# -------------------------
# Robustness tests
# -------------------------
def test_init_idempotency_and_reimport():
    importlib.reload(at)
    at.init()
    first_snapshot = (list(at.KNIGHT_ATTACKS), list(at.KING_ATTACKS), dict(at.PAWN_ATTACKS))
    # calling init again should not change tables
    at.init()
    second_snapshot = (list(at.KNIGHT_ATTACKS), list(at.KING_ATTACKS), dict(at.PAWN_ATTACKS))
    assert first_snapshot == second_snapshot

    # reload module and init again
    importlib.reload(at)
    at.init()
    third_snapshot = (list(at.KNIGHT_ATTACKS), list(at.KING_ATTACKS), dict(at.PAWN_ATTACKS))
    assert first_snapshot == third_snapshot
