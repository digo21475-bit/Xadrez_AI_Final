# diag_pawn_specific.py
from core.moves.tables import attack_tables as at
from tests.test_attack_tables import _slow_pawn_attacks
from utils.enums import Color

def pc(x): return x.bit_count()

at.init()
for sq in (0, 7, 56, 63, 27):
    a_w = at.pawn_attacks(sq, Color.WHITE)
    s_w = _slow_pawn_attacks(sq, Color.WHITE)
    a_b = at.pawn_attacks(sq, Color.BLACK)
    s_b = _slow_pawn_attacks(sq, Color.BLACK)

    print(f"sq={sq}")
    print(f"  WHITE got:  {a_w:#018x} pop={pc(a_w)}; slow: {s_w:#018x} pop={pc(s_w)}")
    print(f"  BLACK got:  {a_b:#018x} pop={pc(a_b)}; slow: {s_b:#018x} pop={pc(s_b)}")
    if a_w != s_w or a_b != s_b:
        print("  -> MISMATCH")
    else:
        print("  -> OK")
