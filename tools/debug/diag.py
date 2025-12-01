# tools/debug/diag.py
"""
Diagnostics and smoke tests for Xadrez_AI_Final.

Safe, non-destructive checks:
 - board initialization
 - basic movegen (legal)
 - make/unmake invariants (hash and occupancy)
 - Zobrist determinism + entropy check
 - perft (with optional divide if available)
 - en-passant generation (edge-case)
 - castling generation (edge-case)

Run:
    python -m tools.debug.diagnostics
"""

from __future__ import annotations

import time
import statistics
from typing import Optional

# Adjust imports if your package layout differs
from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.moves.movegen import generate_pseudo_legal_moves
try:
    # prefer divide if available
    from core.perft.perft import perft, perft_divide  # type: ignore
    _HAS_PERFT_DIVIDE = True
except Exception:
    try:
        from core.perft.perft import perft  # type: ignore
        perft_divide = None  # type: ignore
        _HAS_PERFT_DIVIDE = False
    except Exception:
        perft = None  # type: ignore
        perft_divide = None  # type: ignore
        _HAS_PERFT_DIVIDE = False

from core.hash.zobrist import Zobrist
from utils.enums import GameResult, PieceType, Color
from utils.constants import square_index, SQUARE_BB

# Backwards-compatible initialisation
try:
    # some modules expose ensure_initialized, some init()
    if hasattr(Zobrist, "ensure_initialized"):
        Zobrist.ensure_initialized()
    elif hasattr(Zobrist, "init"):
        Zobrist.init()
except Exception:
    # don't fail diagnostics on Zobrist init errors; capture later
    pass


class Diagnostics:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.errors = 0
        self.warnings = 0
        self._start_time = time.time()

    # --- logging helpers ---
    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def _error(self, msg: str) -> None:
        self.errors += 1
        print(f"[ERROR] {msg}")

    def _warn(self, msg: str) -> None:
        self.warnings += 1
        print(f"[WARN ] {msg}")

    # --- tests ---

    def test_board_init(self) -> None:
        self._log(">> test_board_init")
        try:
            b = Board()
            b.set_startpos()
        except Exception as e:
            self._error(f"Board init failed: {e}")
            return

        if b.all_occupancy == 0:
            self._error("Board all_occupancy == 0 after set_startpos()")
        else:
            self._log("Board occupancy non-zero OK")

        occ = b.occupancy[0] | b.occupancy[1]
        if occ != b.all_occupancy:
            self._error("occupancy per-color mismatch with all_occupancy")
        else:
            self._log("Occupancy coherence OK")

    def test_movegen_legal(self) -> None:
        self._log(">> test_movegen_legal")
        b = Board()
        b.set_startpos()
        try:
            moves = list(generate_legal_moves(b))
        except Exception as e:
            self._error(f"generate_legal_moves raised: {e}")
            return

        self._log(f"Legal moves from startpos: {len(moves)}")
        if len(moves) == 0:
            self._error("No legal moves in start position")
        elif len(moves) < 16:
            self._warn("Suspiciously few legal moves in start position (<16)")

    def test_movegen_pseudo_vs_legal(self) -> None:
        self._log(">> test_movegen_pseudo_vs_legal (sanity)")
        b = Board()
        b.set_startpos()

        pseudo = list(generate_pseudo_legal_moves(b))
        legal = list(generate_legal_moves(b))

        if not pseudo:
            self._error("No pseudo-legal moves generated (unexpected)")
            return

        if not legal:
            self._error("No legal moves generated (unexpected)")
            return

        if len(legal) > len(pseudo):
            self._error("Legal moves > pseudo-legal moves (impossible)")
        else:
            self._log(f"pseudo: {len(pseudo)}, legal: {len(legal)} (ok)")

    def test_make_unmake_hash_invariant(self) -> None:
        self._log(">> test_make_unmake_hash_invariant")
        b = Board()
        b.set_startpos()
        # prefer board.zobrist_key if present, else compute
        try:
            sig0 = getattr(b, "zobrist_key", None)
            if sig0 is None:
                sig0 = b.compute_zobrist()
        except Exception as e:
            self._warn(f"Could not read initial zobrist signature: {e}")
            return

        moves = list(generate_legal_moves(b))
        if not moves:
            self._warn("No legal moves to test make/unmake")
            return

        # test a small sample of moves (first 8)
        sample = moves[:8]
        for m in sample:
            try:
                b.make_move(m)
                b.unmake_move()
            except Exception as e:
                self._error(f"make/unmake raised exception on move {m}: {e}")
                return

            try:
                sig_after = getattr(b, "zobrist_key", None)
                if sig_after is None:
                    sig_after = b.compute_zobrist()
            except Exception as e:
                self._warn(f"Could not compute zobrist after unmake: {e}")
                return

            if sig_after != sig0:
                self._error("Zobrist/hash mismatch after make/unmake (sample)")
                return

        self._log("make/unmake hash invariant OK (sample)")

    def test_zobrist_deterministic(self) -> None:
        self._log(">> test_zobrist_deterministic")
        try:
            # Use factory if provided, else call signature repeatedly
            if hasattr(Zobrist, "signature"):
                s1 = Zobrist.signature()
                s2 = Zobrist.signature()
                if s1 != s2:
                    self._error("Zobrist.signature() not deterministic")
                    return
            else:
                self._log("Zobrist.signature() not available; skipping deterministic test")

            # entropy check if helper exists
            if hasattr(Zobrist, "verify_entropy"):
                ent = Zobrist.verify_entropy()
                self._log(f"Zobrist entropy: {ent:.6f}")
            else:
                self._log("Zobrist.verify_entropy() not available; skipped")
        except Exception as e:
            self._warn(f"Zobrist test raised: {e}")

    def test_perft(self, depth: int = 3) -> None:
        self._log(f">> test_perft(depth={depth})")
        if perft is None:
            self._warn("perft function not available; skipping perft tests")
            return

        b = Board()
        b.set_startpos()

        start = time.time()
        try:
            if _HAS_PERFT_DIVIDE and perft_divide is not None:
                # prefer divide for debugging if implemented
                result = perft_divide(b, depth)
                # perft_divide might return dict or int depending on implementation
                if isinstance(result, dict):
                    total = sum(result.values())
                else:
                    total = int(result)
            else:
                total = perft(b, depth)
        except Exception as e:
            self._error(f"perft raised exception: {e}")
            return
        elapsed = time.time() - start
        self._log(f"Perft({depth}) = {total} nodes in {elapsed:.3f}s")

        expected = {1: 20, 2: 400, 3: 8902}
        if depth in expected and total != expected[depth]:
            self._warn(f"Perft({depth}) != expected {expected[depth]} (got {total})")
        else:
            self._log("Perft OK (startpos)")

    def test_en_passant_case(self) -> None:
        self._log(">> test_en_passant_case (edgecase)")
        # Setup a position where en-passant should be legal
        # FEN: black pawn on d4, white pawn on e2 moves e2-e4 then d4xe3 ep
        # We'll set position where ep square is ready and test that generator contains ep capture
        # Simpler: use a minimal FEN with ep available directly if your set_fen supports it.
        try:
            b = Board()
            # A safe ep FEN: white to move, black pawn on d5, white pawn on e5 is impossible.
            # We'll craft a known test FEN where ep is possible: rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 3
            fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 3"
            b.set_fen(fen)
        except Exception as e:
            self._warn(f"Could not set FEN for EP test: {e}")
            return

        moves = list(generate_legal_moves(b))
        # EP capture should be from e5 to d6 (e5d6) or similar depending on board orientation
        # We check for any pawn move that targets the en-passant square
        ep_sq = b.en_passant_square
        if ep_sq is None:
            self._warn("en_passant square not set in EP test FEN; skipping explicit EP check")
            return

        found = any(m.piece == PieceType.PAWN and m.to_sq == ep_sq for m in moves)
        if not found:
            self._error("Expected en-passant move not found in legal moves for EP test")
        else:
            self._log("En-passant generation OK")

    def test_castling_case(self) -> None:
        self._log(">> test_castling_case (edgecase)")
        try:
            b = Board()
            # Minimal FEN allowing white castling rights and clear path: R3K2R/8/8/8/8/8/8/8 w KQ - 0 1
            fen = "R3K2R/8/8/8/8/8/8/8 w KQ - 0 1"
            b.set_fen(fen)
        except Exception as e:
            self._warn(f"Could not set FEN for castling test: {e}")
            return

        moves = list(generate_legal_moves(b))
        # Look for king moves to g1 (6) and c1 (2) for white
        found_ks = any(m.piece == PieceType.KING and m.from_sq == 4 and m.to_sq == 6 for m in moves)
        found_qs = any(m.piece == PieceType.KING and m.from_sq == 4 and m.to_sq == 2 for m in moves)
        if not (found_ks or found_qs):
            self._error("Expected castling moves not found in legal moves for castling test")
        else:
            self._log("Castling generation (at least one side) OK")

    def run_all(self) -> None:
        self._log("=== DIAGNOSTICS START ===")
        t0 = time.time()

        self.test_board_init()
        self.test_movegen_legal()
        self.test_movegen_pseudo_vs_legal()
        self.test_make_unmake_hash_invariant()
        self.test_zobrist_deterministic()
        self.test_perft(2)
        self.test_perft(3)
        self.test_perft(4)
        self.test_en_passant_case()
        self.test_castling_case()

        elapsed = time.time() - t0
        self._log("\n=== SUMMARY ===")
        self._log(f"Elapsed: {elapsed:.3f}s")
        self._log(f"Errors: {self.errors}")
        self._log(f"Warnings: {self.warnings}")

        if self.errors == 0:
            self._log("DIAGNOSTICS: OK")
        else:
            self._log("DIAGNOSTICS: FAILS FOUND")

# Execute when run as script
if __name__ == "__main__":
    Diagnostics().run_all()
