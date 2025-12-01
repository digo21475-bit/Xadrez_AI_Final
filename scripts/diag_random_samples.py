# diag_random_samples.py
import random
from core.moves.tables import attack_tables as at
from tests.test_attack_tables import _slow_knight_attacks, _slow_king_attacks, _slow_pawn_attacks
from utils.enums import Color

def popcount(x): return x.bit_count()

at.init()
rng = random.Random(12345)
samples = rng.sample(range(64), 20)

bad = []
for sq in samples:
    a_k = at.knight_attacks(sq)
    s_k = _slow_knight_attacks(sq)
    a_kg = at.king_attacks(sq)
    s_kg = _slow_king_attacks(sq)
    a_pw = at.pawn_attacks(sq, Color.WHITE)
    s_pw = _slow_pawn_attacks(sq, Color.WHITE)
    a_pb = at.pawn_attacks(sq, Color.BLACK)
    s_pb = _slow_pawn_attacks(sq, Color.BLACK)

    if a_k != s_k:
        bad.append(("knight", sq, a_k, s_k))
    if a_kg != s_kg:
        bad.append(("king", sq, a_kg, s_kg))
    if a_pw != s_pw:
        bad.append(("pawnW", sq, a_pw, s_pw))
    if a_pb != s_pb:
        bad.append(("pawnB", sq, a_pb, s_pb))

if not bad:
    print("No mismatches for RNG sample.")
else:
    for kind, sq, a, s in bad:
        print(f"{kind} mismatch at sq={sq}:")
        print(f"  got   = {a} (hex {a:#018x}, pop {popcount(a)})")
        print(f"  slow  = {s} (hex {s:#018x}, pop {popcount(s)})")
