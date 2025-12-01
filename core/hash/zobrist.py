# core/hash/zobrist.py
from __future__ import annotations

"""
Zobrist hashing utilities for Xadrez_AI_Final — final, documented and optimized.

Features:
- Deterministic initialization from a seed.
- Thread-safe, idempotent init() with optional forced reinit.
- Compact, masked 64-bit values (U64).
- Incremental XOR helpers used by Board.
- Diagnostic helpers used by tests (entropy, signature).
- Small micro-optimizations (local lookups) in hot helpers.
"""

from typing import ClassVar, List, Optional
import threading
import random

from utils.constants import U64
from utils.enums import PieceIndex  # project enum mapping piece -> 0..11

# Constants describing table sizes
_PIECE_INDEX_COUNT = 12
_CASTLING_STATES = 16
_ENPASSANT_SLOTS = 64

# Module-level synchronization and state flag
_init_lock = threading.Lock()
_initialized = False


class Zobrist:
    """Global Zobrist table holder and utilities.

    Typical usage
        Zobrist.init(seed=0xC0FFEE)
        h = 0
        h = Zobrist.xor_piece(h, piece_index, square)
        h = Zobrist.xor_side(h)
        h = Zobrist.xor_castling(h, castling_rights)
        h = Zobrist.xor_enpassant(h, enpassant_sq)
    """

    # Class-level storages populated by init()
    piece_square: ClassVar[List[List[int]]] = []
    castling: ClassVar[List[int]] = []
    enpassant: ClassVar[List[int]] = []
    side_to_move: ClassVar[int] = 0

    # Backwards-compatible alias some code/tests may expect
    piece_keys: ClassVar[List[List[int]]] = []

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------
    @classmethod
    def init(cls, seed: int = 0xC0FFEE, force: bool = False) -> None:
        """
        Initialize Zobrist tables deterministically from `seed`.

        Args:
            seed: integer seed for deterministic RNG (default: 0xC0FFEE).
            force: when True reinitializes even if already initialized.
        """
        global _initialized
        with _init_lock:
            if _initialized and not force:
                return

            rng = random.Random(seed)

            # piece_square: _PIECE_INDEX_COUNT lists of 64 64-bit keys
            cls.piece_square = [
                [rng.getrandbits(64) & U64 for _ in range(64)]
                for _ in range(_PIECE_INDEX_COUNT)
            ]

            # castling states (0..15)
            cls.castling = [rng.getrandbits(64) & U64 for _ in range(_CASTLING_STATES)]

            # enpassant keys per-square (0..63)
            cls.enpassant = [rng.getrandbits(64) & U64 for _ in range(_ENPASSANT_SLOTS)]

            # side-to-move key
            cls.side_to_move = rng.getrandbits(64) & U64

            # alias
            cls.piece_keys = cls.piece_square

            _initialized = True

    @classmethod
    def reset(cls) -> None:
        """
        Reset Zobrist tables to uninitialized state.

        Intended for tests only.
        """
        global _initialized
        with _init_lock:
            cls.piece_square = []
            cls.castling = []
            cls.enpassant = []
            cls.side_to_move = 0
            cls.piece_keys = []
            _initialized = False

    @classmethod
    def ensure_initialized(cls, seed: int = 0xC0FFEE) -> None:
        """Convenience: initialize if not already done (idempotent)."""
        cls.init(seed=seed)

    # ---------------------------------------------------------
    # Incremental XOR helpers (hot paths)
    # ---------------------------------------------------------
    @classmethod
    def xor_piece(cls, h: int, piece_index: PieceIndex | int, square: int) -> int:
        """
        XOR a piece at `square` into hash `h` and return new hash.
        Accepts either PieceIndex enum or integer index (0..11).
        """
        # micro-opt: local lookup to avoid repeated attribute access
        idx = int(piece_index)
        return (h ^ cls.piece_square[idx][square]) & U64

    @classmethod
    def xor_castling(cls, h: int, castling_rights: int) -> int:
        """XOR castling rights encoded 0..15 into hash and return new value."""
        return (h ^ cls.castling[castling_rights & 0xF]) & U64

    @classmethod
    def xor_enpassant(cls, h: int, enpassant_sq: Optional[int]) -> int:
        """XOR en-passant square into hash; if enpassant_sq is None or -1, returns h unchanged."""
        if enpassant_sq is None or enpassant_sq == -1:
            return h
        return (h ^ cls.enpassant[enpassant_sq & 63]) & U64

    @classmethod
    def xor_side(cls, h: int) -> int:
        """Toggle side-to-move bit in hash and return new value."""
        return (h ^ cls.side_to_move) & U64

    # ---------------------------------------------------------
    # Diagnostics / test helpers
    # ---------------------------------------------------------
    @classmethod
    def verify_entropy(cls) -> float:
        """
        Return fraction of unique keys across piece_square (0.0..1.0).
        Useful for tests that validate randomness/determinism.
        """
        if not cls.piece_square:
            raise RuntimeError("Zobrist not initialized")

        seen = set()
        total = 0
        for row in cls.piece_square:
            for v in row:
                seen.add(v)
                total += 1
        return len(seen) / total if total else 0.0

    @classmethod
    def signature(cls) -> bytes:
        """
        Deterministic, compact signature of current tables.

        Produces a bytes blob built from stable samples of the tables
        (not the whole tables) so it's fast and deterministic for tests.
        """
        if not cls.piece_square:
            return b""
        parts = []
        # sample first N piece rows to keep signature compact and stable
        N = min(len(cls.piece_square), 6)
        for i in range(N):
            sample = cls.piece_square[i][:16]
            parts.append(repr(sample).encode("utf-8"))
        parts.append(repr(cls.castling[:8]).encode("utf-8"))
        parts.append(repr(cls.enpassant[:8]).encode("utf-8"))
        parts.append(repr(cls.side_to_move).encode("utf-8"))
        return b"||".join(parts)


# Module-level convenience wrappers for backwards compatibility
_default = Zobrist

def init(seed: int = 0xC0FFEE, force: bool = False) -> None:
    Zobrist.init(seed=seed, force=force)


def reset() -> None:
    Zobrist.reset()


def ensure_initialized(seed: int = 0xC0FFEE) -> None:
    Zobrist.ensure_initialized(seed=seed)


def xor_piece(h: int, piece_index: PieceIndex | int, square: int) -> int:
    return Zobrist.xor_piece(h, piece_index, square)


def xor_castling(h: int, castling_rights: int) -> int:
    return Zobrist.xor_castling(h, castling_rights)


def xor_enpassant(h: int, enpassant_sq: Optional[int]) -> int:
    return Zobrist.xor_enpassant(h, enpassant_sq)


def xor_side(h: int) -> int:
    return Zobrist.xor_side(h)


def verify_entropy() -> float:
    return Zobrist.verify_entropy()


def signature() -> bytes:
    return Zobrist.signature()


__all__ = [
    "Zobrist",
    "init",
    "reset",
    "ensure_initialized",
    "xor_piece",
    "xor_castling",
    "xor_enpassant",
    "xor_side",
    "verify_entropy",
    "signature",
    "_default",
]
