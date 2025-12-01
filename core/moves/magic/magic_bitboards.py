from __future__ import annotations

# ============================================================
# Helper: bit count para Python 3.8+ compatibility
# ============================================================

def _bit_count(x: int) -> int:
    """Count set bits in integer (Python 3.8 compatible fallback)."""
    try:
        return x.bit_count()  # Python 3.10+
    except AttributeError:
        return bin(x).count('1')  # Python 3.8/3.9


"""
Magic bitboards implementation — versão final, test-compatible.

Características:
- Compatível com os nomes públicos exigidos pelos testes (ROOK_MASKS, ROOK_GOOD_MAGICS, etc).
- Lazy init thread-safe que constrói máscaras, tabelas e rebinds de funções rápidas.
- Implementação em Python puro; sem dependência de bitops nativos.
- Placeholders seguros que chamam init() e delegam para as implementações rápidas.
- Expõe utilitários de debug/validação (index_to_occupancy, mask_bits_positions, _rook_attacks_from_occupancy, ...).
"""

from typing import Callable, Dict, List, Tuple, Optional, Union
import threading

from utils.constants import SQUARE_TO_FILE, SQUARE_TO_RANK, U64
from .magic_autogen import ROOK_MAGICS, BISHOP_MAGICS

# ------------------------
# Bit-scan helpers
# ------------------------
def lsb_index(bb: int) -> int:
    """Index of least-significant 1-bit, or -1 if bb == 0."""
    return -1 if bb == 0 else (bb & -bb).bit_length() - 1

def msb_index(bb: int) -> int:
    """Index of most-significant 1-bit, or -1 if bb == 0."""
    return -1 if bb == 0 else bb.bit_length() - 1

# ------------------------
# Public symbols expected by tests
# ------------------------
ROOK_GOOD_MAGICS = tuple(ROOK_MAGICS)
BISHOP_GOOD_MAGICS = tuple(BISHOP_MAGICS)

ROOK_MASKS: Tuple[int, ...] = tuple(0 for _ in range(64))
BISHOP_MASKS: Tuple[int, ...] = tuple(0 for _ in range(64))

ROOK_RELEVANT_BITS: Tuple[int, ...] = tuple(0 for _ in range(64))
BISHOP_RELEVANT_BITS: Tuple[int, ...] = tuple(0 for _ in range(64))

ROOK_SHIFTS: Tuple[int, ...] = tuple(0 for _ in range(64))
BISHOP_SHIFTS: Tuple[int, ...] = tuple(0 for _ in range(64))

ROOK_ATTACK_OFFSETS: Tuple[int, ...] = tuple(0 for _ in range(64))
BISHOP_ATTACK_OFFSETS: Tuple[int, ...] = tuple(0 for _ in range(64))

_ROOK_ATT_TABLE: Tuple[int, ...] = tuple()
_BISHOP_ATT_TABLE: Tuple[int, ...] = tuple()

_MASK_POSITIONS: Dict[Tuple[int, bool], Tuple[int, ...]] = {}

_INITIALIZED = False
_init_lock = threading.Lock()

# ------------------------
# Mask generation (exclude board edges)
# ------------------------
def mask_rook_attacks(sq: int) -> int:
    f = SQUARE_TO_FILE[sq]
    r = SQUARE_TO_RANK[sq]
    m = 0
    # up (r+1 .. 6)
    for rr in range(r + 1, 7):
        m |= 1 << (rr * 8 + f)
    # down (r-1 .. 1)
    for rr in range(r - 1, 0, -1):
        m |= 1 << (rr * 8 + f)
    # right (f+1 .. 6)
    for ff in range(f + 1, 7):
        m |= 1 << (r * 8 + ff)
    # left (f-1 .. 1)
    for ff in range(f - 1, 0, -1):
        m |= 1 << (r * 8 + ff)
    return m & U64

def mask_bishop_attacks(sq: int) -> int:
    f = SQUARE_TO_FILE[sq]
    r = SQUARE_TO_RANK[sq]
    m = 0
    ff, rr = f + 1, r + 1
    while ff <= 6 and rr <= 6:
        m |= 1 << (rr * 8 + ff)
        ff += 1; rr += 1
    ff, rr = f - 1, r - 1
    while ff >= 1 and rr >= 1:
        m |= 1 << (rr * 8 + ff)
        ff -= 1; rr -= 1
    ff, rr = f - 1, r + 1
    while ff >= 1 and rr <= 6:
        m |= 1 << (rr * 8 + ff)
        ff -= 1; rr += 1
    ff, rr = f + 1, r - 1
    while ff <= 6 and rr >= 1:
        m |= 1 << (rr * 8 + ff)
        ff += 1; rr -= 1
    return m & U64

# ------------------------
# Ray-walk fallbacks (used during table generation / tests)
# ------------------------
def _rook_attacks_from_occupancy(sq: int, occ: int) -> int:
    f = SQUARE_TO_FILE[sq]; r = SQUARE_TO_RANK[sq]
    a = 0
    for rr in range(r + 1, 8):
        s = rr * 8 + f
        a |= 1 << s
        if occ & (1 << s):
            break
    for rr in range(r - 1, -1, -1):
        s = rr * 8 + f
        a |= 1 << s
        if occ & (1 << s):
            break
    for ff in range(f + 1, 8):
        s = r * 8 + ff
        a |= 1 << s
        if occ & (1 << s):
            break
    for ff in range(f - 1, -1, -1):
        s = r * 8 + ff
        a |= 1 << s
        if occ & (1 << s):
            break
    return a & U64

def _bishop_attacks_from_occupancy(sq: int, occ: int) -> int:
    f = SQUARE_TO_FILE[sq]; r = SQUARE_TO_RANK[sq]
    a = 0
    ff, rr = f + 1, r + 1
    while ff < 8 and rr < 8:
        s = rr * 8 + ff
        a |= 1 << s
        if occ & (1 << s):
            break
        ff += 1; rr += 1
    ff, rr = f - 1, r - 1
    while ff >= 0 and rr >= 0:
        s = rr * 8 + ff
        a |= 1 << s
        if occ & (1 << s):
            break
        ff -= 1; rr -= 1
    ff, rr = f - 1, r + 1
    while ff >= 0 and rr < 8:
        s = rr * 8 + ff
        a |= 1 << s
        if occ & (1 << s):
            break
        ff -= 1; rr += 1
    ff, rr = f + 1, r - 1
    while ff < 8 and rr >= 0:
        s = rr * 8 + ff
        a |= 1 << s
        if occ & (1 << s):
            break
        ff += 1; rr -= 1
    return a & U64

# ------------------------
# Utilities used during table construction
# ------------------------
def mask_bits_positions(mask: int) -> Tuple[int, ...]:
    pos: List[int] = []
    m = mask
    while m:
        lsb = m & -m
        pos.append(lsb.bit_length() - 1)
        m ^= lsb
    return tuple(pos)

def index_to_occupancy(index: int, positions: Tuple[int, ...]) -> int:
    occ = 0
    for i, sq in enumerate(positions):
        if index & (1 << i):
            occ |= 1 << sq
    return occ & U64

def _build_attack_table_for_square(
    sq: int,
    mask: int,
    positions: Tuple[int, ...],
    is_rook: bool,
    magic: int,
    shift: int,
) -> Tuple[int, ...]:
    bits = _bit_count(mask)
    size = 1 << bits
    table: List[Optional[int]] = [None] * size
    mask_local = mask & U64
    magic_local = magic & U64
    attacks_func = _rook_attacks_from_occupancy if is_rook else _bishop_attacks_from_occupancy

    for idx in range(size):
        occ = index_to_occupancy(idx, positions)
        att = attacks_func(sq, occ)
        comp = (((occ & mask_local) * magic_local) & U64) >> shift
        if comp >= size:
            raise RuntimeError(f"Magic index out of range: sq={sq} comp={comp} size={size}")
        existing = table[comp]
        if existing is None:
            table[comp] = att
        elif existing != att:
            raise RuntimeError(f"Magic collision: sq={sq} idx={idx} comp={comp}")
    return tuple(v if v is not None else 0 for v in table)

# ------------------------
# Factories to create fast callables
# ------------------------
def _make_fast_rook_attacks(masks, magics, shifts, offsets, table) -> Callable[[int, int], int]:
    u64 = U64
    def _rook(sq: int, occ: int) -> int:
        idx = (((occ & masks[sq]) * magics[sq]) & u64) >> shifts[sq]
        return table[offsets[sq] + idx]
    return _rook

def _make_fast_bishop_attacks(masks, magics, shifts, offsets, table) -> Callable[[int, int], int]:
    u64 = U64
    def _bishop(sq: int, occ: int) -> int:
        idx = (((occ & masks[sq]) * magics[sq]) & u64) >> shifts[sq]
        return table[offsets[sq] + idx]
    return _bishop

def _make_fast_sliding_attacks(rook_fn: Callable[[int, int], int], bishop_fn: Callable[[int, int], int]) -> Callable[[int, int], int]:
    def _sliding(sq: int, occ: int) -> int:
        return rook_fn(sq, occ) | bishop_fn(sq, occ)
    return _sliding

# ------------------------
# Placeholders / delegators (safe: call init then delegate to impl)
# ------------------------
# Implementations are stored in these private callables and swapped in init().
def _placeholder_not_initialized(*args, **kwargs):
    raise RuntimeError("magic_bitboards.init() not yet called")

_rook_attacks_impl: Callable[[int, int], int] = _placeholder_not_initialized
_bishop_attacks_impl: Callable[[int, int], int] = _placeholder_not_initialized
_sliding_attacks_impl: Callable[[int, int], int] = _placeholder_not_initialized

def rook_attacks(sq: int, occ: int) -> int:
    """Public API: ensure init and delegate."""
    if not _INITIALIZED:
        init()
    return _rook_attacks_impl(sq, occ)

def bishop_attacks(sq: int, occ: int) -> int:
    if not _INITIALIZED:
        init()
    return _bishop_attacks_impl(sq, occ)

def sliding_attacks(sq: int, occ: int) -> int:
    if not _INITIALIZED:
        init()
    return _sliding_attacks_impl(sq, occ)

# ------------------------
# Init: build masks, tables and rebind fast callables
# ------------------------
def _validate_magics() -> None:
    if len(ROOK_MAGICS) != 64 or len(BISHOP_MAGICS) != 64:
        raise RuntimeError("Autogenerated magics must contain 64 entries each.")
    for arr, name in ((ROOK_MAGICS, "ROOK"), (BISHOP_MAGICS, "BISHOP")):
        for i, v in enumerate(arr):
            if not isinstance(v, int) or v == 0:
                raise RuntimeError(f"Invalid {name}_MAGIC at {i}: {v!r}")

def init(validate: bool = True) -> None:
    """Thread-safe lazy initialization. Idempotent."""
    global _INITIALIZED
    global ROOK_MASKS, BISHOP_MASKS
    global ROOK_RELEVANT_BITS, BISHOP_RELEVANT_BITS
    global ROOK_SHIFTS, BISHOP_SHIFTS
    global ROOK_ATTACK_OFFSETS, BISHOP_ATTACK_OFFSETS
    global _ROOK_ATT_TABLE, _BISHOP_ATT_TABLE, _MASK_POSITIONS
    global _rook_attacks_impl, _bishop_attacks_impl, _sliding_attacks_impl

    with _init_lock:
        if _INITIALIZED:
            return

        if validate:
            _validate_magics()

        _MASK_POSITIONS.clear()

        rook_masks_list: List[int] = []
        bishop_masks_list: List[int] = []
        rook_bits_list: List[int] = []
        bishop_bits_list: List[int] = []
        rook_shifts_list: List[int] = []
        bishop_shifts_list: List[int] = []

        # masks, positions, shifts
        for sq in range(64):
            rmask = mask_rook_attacks(sq)
            bmask = mask_bishop_attacks(sq)
            rook_masks_list.append(rmask)
            bishop_masks_list.append(bmask)

            rb = _bit_count(rmask)
            bb = _bit_count(bmask)
            rook_bits_list.append(rb)
            bishop_bits_list.append(bb)

            rook_shifts_list.append(64 - rb)
            bishop_shifts_list.append(64 - bb)

            _MASK_POSITIONS[(sq, True)] = mask_bits_positions(rmask)
            _MASK_POSITIONS[(sq, False)] = mask_bits_positions(bmask)

        ROOK_MASKS = tuple(rook_masks_list)
        BISHOP_MASKS = tuple(bishop_masks_list)
        ROOK_RELEVANT_BITS = tuple(rook_bits_list)
        BISHOP_RELEVANT_BITS = tuple(bishop_bits_list)
        ROOK_SHIFTS = tuple(rook_shifts_list)
        BISHOP_SHIFTS = tuple(bishop_shifts_list)

        # offsets for flattened tables
        rook_offsets: List[int] = []
        off = 0
        for sq in range(64):
            rook_offsets.append(off)
            off += 1 << ROOK_RELEVANT_BITS[sq]
        ROOK_ATTACK_OFFSETS = tuple(rook_offsets)

        bishop_offsets: List[int] = []
        off = 0
        for sq in range(64):
            bishop_offsets.append(off)
            off += 1 << BISHOP_RELEVANT_BITS[sq]
        BISHOP_ATTACK_OFFSETS = tuple(bishop_offsets)

        # build per-square tables and flatten
        rook_table_list: List[int] = []
        bishop_table_list: List[int] = []
        for sq in range(64):
            rpos = _MASK_POSITIONS[(sq, True)]
            bpos = _MASK_POSITIONS[(sq, False)]

            rtab = _build_attack_table_for_square(
                sq, ROOK_MASKS[sq], rpos, True, ROOK_MAGICS[sq], ROOK_SHIFTS[sq]
            )
            rook_table_list.extend(rtab)

            btab = _build_attack_table_for_square(
                sq, BISHOP_MASKS[sq], bpos, False, BISHOP_MAGICS[sq], BISHOP_SHIFTS[sq]
            )
            bishop_table_list.extend(btab)

        _ROOK_ATT_TABLE = tuple(rook_table_list)
        _BISHOP_ATT_TABLE = tuple(bishop_table_list)

        # create fast callables and bind to impl slots
        fast_rook = _make_fast_rook_attacks(ROOK_MASKS, tuple(ROOK_MAGICS), ROOK_SHIFTS, ROOK_ATTACK_OFFSETS, _ROOK_ATT_TABLE)
        fast_bishop = _make_fast_bishop_attacks(BISHOP_MASKS, tuple(BISHOP_MAGICS), BISHOP_SHIFTS, BISHOP_ATTACK_OFFSETS, _BISHOP_ATT_TABLE)
        fast_sliding = _make_fast_sliding_attacks(fast_rook, fast_bishop)

        _rook_attacks_impl = fast_rook
        _bishop_attacks_impl = fast_bishop
        _sliding_attacks_impl = fast_sliding

        _INITIALIZED = True

# ------------------------
# Debug helper
# ------------------------
def show_bitboard(bb: int) -> str:
    rows: List[str] = []
    for rank in range(7, -1, -1):
        row = []
        base = rank * 8
        for file in range(8):
            sq = base + file
            row.append("1" if (bb >> sq) & 1 else ".")
        rows.append(" ".join(row))
    return "\n".join(rows)

# ------------------------
# Exports
# ------------------------
__all__ = [
    "init",
    "rook_attacks",
    "bishop_attacks",
    "sliding_attacks",
    "lsb_index",
    "msb_index",
    "ROOK_MASKS",
    "BISHOP_MASKS",
    "ROOK_GOOD_MAGICS",
    "BISHOP_GOOD_MAGICS",
    "ROOK_RELEVANT_BITS",
    "BISHOP_RELEVANT_BITS",
    "ROOK_SHIFTS",
    "BISHOP_SHIFTS",
    "ROOK_ATTACK_OFFSETS",
    "BISHOP_ATTACK_OFFSETS",
    "_MASK_POSITIONS",
    "_ROOK_ATT_TABLE",
    "_BISHOP_ATT_TABLE",
    "_INITIALIZED",
    "mask_rook_attacks",
    "mask_bishop_attacks",
    "index_to_occupancy",
    "mask_bits_positions",
    "_rook_attacks_from_occupancy",
    "_bishop_attacks_from_occupancy",
    "show_bitboard",
]
