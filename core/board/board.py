# board.py — Xadrez_AI_Final
# Bitboard-first + mailbox, A1=0, sem regras, sem movegen, sem GUI.
# Objetivo: implementação eficiente do objeto de tabuleiro com caminhos quentes
# invariantes preservadas (A1=0, enums, serialização externa, APIs públicas).
# Hot paths: set_piece_at, remove_piece_at, move_piece, validate, copy.
from __future__ import annotations

from typing import Optional, Tuple, List, Union
from core.hash.zobrist import Zobrist
from core.moves.tables.attack_tables import knight_attacks, king_attacks
from core.moves.magic.magic_bitboards import bishop_attacks, rook_attacks
from core.moves.move import Move
from utils.constants import (
    CASTLE_WHITE_K, CASTLE_WHITE_Q, CASTLE_BLACK_K, CASTLE_BLACK_Q,
    PIECE_COUNT, COLOR_COUNT, NOT_FILE_H, NOT_FILE_A, square_index
)
from utils.enums import Color, PieceType

__all__ = ["Board", "square_index"]

# ------------------------------------------------------------
# Precomputed bit masks
# ------------------------------------------------------------
# PERF: Precompute single-square bit masks to avoid repeated shifts in hot paths.
SQUARE_BB: tuple[int, ...] = tuple(1 << sq for sq in range(64))

# mailbox cell: None | (Color, PieceType)
MailboxCell = Optional[Tuple[Color, PieceType]]


# ------------------------------------------------------------
# Board
# ------------------------------------------------------------
class Board:
    """Board container combining bitboards and a mailbox.

    Invariants:
        - Indexing A1=0..H8=63
        - bitboards[color][piece] holds piece bitboard (uint64)
        - occupancy[color] holds occupancy bitboard
        - all_occupancy == occupancy[0] | occupancy[1]
        - mailbox contains None or (Color, PieceType) consistent with bitboards

    Public API kept identical:
        - __init__(setup: bool = True)
        - clear()
        - copy() -> Board
        - get_piece_at(square: int) -> MailboxCell
        - set_piece_at(square: int, color: Color, piece: PieceType) -> None
        - remove_piece_at(square: int) -> None
        - move_piece(from_sq: int, to_sq: int) -> None
        - validate() -> None
    """

    __slots__ = (
        "bitboards", "occupancy", "all_occupancy", "mailbox",
        "side_to_move", "_state_stack", "zobrist_key", "castling_rights",
        "en_passant_square", "halfmove_clock", "fullmove_number"
    )

    def __init__(self, setup: bool = True) -> None:
        self.zobrist_key = 0
        # bitboards[color][piece] -> uint64
        # PERF: use list-of-lists for mutability; inner lists are small and fixed-length.
        self.bitboards: List[List[int]] = [
            [0 for _ in range(PIECE_COUNT)] for _ in range(COLOR_COUNT)
        ]
        # occupancy[color] -> uint64
        self.occupancy: List[int] = [0, 0]
        # all occupancy
        self.all_occupancy: int = 0
        # mailbox[64] -> None | (Color, PieceType)
        self.mailbox: List[MailboxCell] = [None] * 64

        self._state_stack: List[Tuple] = []
        self.side_to_move: Color = Color.WHITE
        self.castling_rights: int = 0
        self.en_passant_square: Optional[int] = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1

        if setup:
            self._set_starting_position()

        self.validate()
        Zobrist.ensure_initialized()  # garante tabelas
        self.zobrist_key = self.compute_zobrist()

    def compute_zobrist(self) -> int:
        """Recalcula o hash Zobrist completo do tabuleiro."""
        h = 0

        # Peças
        for color in Color:
            ci = int(color)
            for piece in PieceType:
                pi = int(piece)
                bb = self.bitboards[ci][pi]
                piece_index = ci * 6 + pi  # 0..11

                while bb:
                    lsb = bb & -bb
                    sq = lsb.bit_length() - 1
                    h = Zobrist.xor_piece(h, piece_index, sq)
                    bb ^= lsb

        # Castling
        h = Zobrist.xor_castling(h, self.castling_rights)

        # En passant
        if self.en_passant_square is not None:
            h = Zobrist.xor_enpassant(h, self.en_passant_square)

        # Side to move
        if self.side_to_move == Color.BLACK:
            h = Zobrist.xor_side(h)

        return h

    # ------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------
    def clear(self) -> None:
        """Clear the board to an empty state.

        Complexity: O(PIECE_COUNT * COLOR_COUNT) ~ constant.
        """
        # PERF: assign lists directly to avoid many Python-level assignments where valid.
        for c in range(COLOR_COUNT):
            self.occupancy[c] = 0
            bb_row = self.bitboards[c]
            for p in range(PIECE_COUNT):
                bb_row[p] = 0
        self.all_occupancy = 0
        # PERF: recreate mailbox list (fast) instead of mutating each entry.
        self.mailbox = [None] * 64
        self.side_to_move = Color.WHITE
        self.castling_rights = 0
        self.en_passant_square = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    def copy(self) -> Board:
        """Create a deep copy of the board.

        Returns:
            Board: A new independent copy of the board instance
        """
        new = Board.__new__(Board)

        # Copy mutable data structures
        new.bitboards = [row.copy() for row in self.bitboards]
        new.occupancy = self.occupancy.copy()
        new.all_occupancy = self.all_occupancy
        new.mailbox = self.mailbox.copy()

        # Copy primitive attributes
        new.side_to_move = self.side_to_move
        new.castling_rights = self.castling_rights
        new.en_passant_square = self.en_passant_square
        new.halfmove_clock = self.halfmove_clock
        new.fullmove_number = self.fullmove_number

        # State stack is not copied (fresh undo stack)
        new._state_stack = []

        return new

    def get_piece_at(self, square: int) -> MailboxCell:
        """Return mailbox cell at `square`.

        Args:
            square: Board square index (0-63)

        Returns:
            Optional tuple of (Color, PieceType) if square occupied, None otherwise
        """
        return self.mailbox[square]

    def set_piece_at(self, square: int, color: Color, piece: PieceType) -> None:
        """Place a piece on `square`. Raises assertion if square already occupied.

        Complexity: O(1)

        Args:
            square: Target square index (0-63)
            color: Piece color
            piece: Piece type

        Raises:
            AssertionError: If square is already occupied
        """
        bit = SQUARE_BB[square]  # PERF: local lookup
        assert (self.all_occupancy & bit) == 0, "Square already occupied"

        ci = int(color)
        pi = int(piece)

        # PERF: local references to reduce attribute lookups
        self.bitboards[ci][pi] |= bit
        self.occupancy[ci] |= bit
        self.all_occupancy |= bit
        self.mailbox[square] = (color, piece)

        # Validation limited to invariants touched — cheap but important in debug.
        self._validate_local(color)

    def remove_piece_at(self, square: int) -> None:
        """Remove any piece at `square`. No-op if square empty.

        Complexity: O(1) average.

        Args:
            square: Square index to clear (0-63)
        """
        cell = self.mailbox[square]
        if cell is None:
            return

        color, piece = cell
        bit = SQUARE_BB[square]

        ci = int(color)
        pi = int(piece)

        self.bitboards[ci][pi] &= ~bit
        self.occupancy[ci] &= ~bit
        self.all_occupancy &= ~bit
        self.mailbox[square] = None

        self._validate_local(color)

    def move_piece(self, from_sq: int, to_sq: int) -> None:
        """Move piece from `from_sq` to `to_sq`. Handles capturing automatically.

        Complexity: O(1)

        Args:
            from_sq: Source square index (0-63)
            to_sq: Destination square index (0-63)

        Raises:
            AssertionError: If no piece at source square
        """
        if from_sq == to_sq:
            return

        src = self.mailbox[from_sq]
        assert src is not None, "No piece at from_sq"

        color, piece = src
        src_bit = SQUARE_BB[from_sq]
        dst_bit = SQUARE_BB[to_sq]
        ci = int(color)
        pi = int(piece)

        # Capture if necessary
        if self.mailbox[to_sq] is not None:
            # PERF: reuse remove_piece_at (very fast) to keep correctness centralized
            self.remove_piece_at(to_sq)

        # Move bitboards — explicit clear/set to avoid XOR ambiguities
        self.bitboards[ci][pi] &= ~src_bit
        self.bitboards[ci][pi] |= dst_bit

        # Move occupancy
        self.occupancy[ci] &= ~src_bit
        self.occupancy[ci] |= dst_bit

        # Move mailbox
        self.mailbox[from_sq] = None
        self.mailbox[to_sq] = (color, piece)

        # Update global occupancy
        self.all_occupancy = self.occupancy[0] | self.occupancy[1]

        self._validate_local(color)

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------
    def _validate_local(self, color: Color) -> None:
        """Validate local invariants related to `color`.

        Complexity: O(#pieces + 64) worst-case; optimized with local variables.

        Args:
            color: Color to validate invariants for

        Raises:
            AssertionError: If any board invariant is violated
        """
        ci = int(color)

        # Color overlap check
        assert (self.occupancy[0] & self.occupancy[1]) == 0

        # Global occupancy consistency
        assert self.all_occupancy == (self.occupancy[0] | self.occupancy[1])

        # Mailbox consistency (only check recently affected squares)
        bb_rows = self.bitboards
        mailbox = self.mailbox
        all_occ = self.all_occupancy

        # PERF: iterate only over set bits in all_occupancy to validate occupied squares.
        occ_mask = all_occ
        while occ_mask:
            lsb = occ_mask & -occ_mask
            sq = lsb.bit_length() - 1
            cell = mailbox[sq]
            assert cell is not None, "Mailbox missing piece on occupied square"
            c, p = cell
            assert bb_rows[int(c)][int(p)] & SQUARE_BB[sq], "Bitboard/mailbox inconsistency"
            occ_mask &= occ_mask - 1

        # Validate that mailbox entries for empty squares are None
        mailbox_mask = 0
        for i, cell in enumerate(mailbox):
            if cell is not None:
                mailbox_mask |= SQUARE_BB[i]
        assert mailbox_mask == all_occ, "Mailbox claims do not match occupancy"

    def validate(self) -> None:
        """Full validation: recompute occupancies and check mailbox consistency.

        Complexity: O(PIECE_COUNT * COLOR_COUNT + 64)

        Raises:
            AssertionError: If any board invariant is violated
        """
        # Recompute occupancy from bitboards
        recomputed_occ = [0, 0]
        for c in range(COLOR_COUNT):
            row = self.bitboards[c]
            acc = 0
            # PERF: iterate inner list directly
            for p in range(PIECE_COUNT):
                acc |= row[p]
            recomputed_occ[c] = acc

        assert recomputed_occ[0] == self.occupancy[0]
        assert recomputed_occ[1] == self.occupancy[1]
        assert (self.occupancy[0] & self.occupancy[1]) == 0
        assert self.all_occupancy == (self.occupancy[0] | self.occupancy[1])

        # Mailbox full check
        mailbox = self.mailbox
        all_occ = self.all_occupancy
        bb_rows = self.bitboards

        # PERF: validate occupied squares by iterating set bits (pieces count usually << 64)
        occ_mask = all_occ
        seen_mask = 0
        while occ_mask:
            lsb = occ_mask & -occ_mask
            sq = lsb.bit_length() - 1
            cell = mailbox[sq]
            assert cell is not None
            c, p = cell
            assert bb_rows[int(c)][int(p)] & SQUARE_BB[sq]
            seen_mask |= lsb
            occ_mask &= occ_mask - 1

        # All other squares must have mailbox None
        if seen_mask != ((1 << 64) - 1):
            # Empty squares mask
            empty_mask = (~seen_mask) & ((1 << 64) - 1)
            # PERF: iterate empties by checking mailbox entries for nones
            for sq in range(64):
                if empty_mask & SQUARE_BB[sq]:
                    assert mailbox[sq] is None

        # King invariants - exactly one king per color
        king_index = int(PieceType.KING)
        for c in Color:
            king_bb = self.bitboards[int(c)][king_index]
            if king_bb != 0:  # only validate if king exists
                # bit_count() is Python 3.10+; fallback for 3.8/3.9
                count = bin(king_bb).count('1')
                assert count == 1, f"Invalid king count for {c}"

    # ------------------------------------------------------------
    # Starting Position
    # ------------------------------------------------------------
    def _set_starting_position(self) -> None:
        """Set standard chess starting position.

        Complexity: O(1) (constant number of placements)
        """
        self.clear()

        def place(color: Color, piece: PieceType, squares: List[int]) -> None:
            for sq in squares:
                self.set_piece_at(sq, color, piece)

        W, B = Color.WHITE, Color.BLACK

        # White pieces
        place(W, PieceType.ROOK, [0, 7])
        place(W, PieceType.KNIGHT, [1, 6])
        place(W, PieceType.BISHOP, [2, 5])
        place(W, PieceType.QUEEN, [3])
        place(W, PieceType.KING, [4])
        place(W, PieceType.PAWN, list(range(8, 16)))

        # Black pieces
        place(B, PieceType.ROOK, [56, 63])
        place(B, PieceType.KNIGHT, [57, 62])
        place(B, PieceType.BISHOP, [58, 61])
        place(B, PieceType.QUEEN, [59])
        place(B, PieceType.KING, [60])
        place(B, PieceType.PAWN, list(range(48, 56)))

        self.all_occupancy = self.occupancy[0] | self.occupancy[1]
        self.side_to_move = Color.WHITE
        self.validate()

    def set_startpos(self) -> None:
        """Set standard starting position and white to move."""
        self._set_starting_position()
        self.side_to_move = Color.WHITE

    def place(self, piece: PieceType, color: Color, square: str) -> None:
        """Convenience method to place piece using algebraic notation.

        Args:
            piece: Piece type to place
            color: Piece color
            square: Algebraic notation (e.g., 'e4')
        """
        sqi = square_index(square)
        self.set_piece_at(sqi, color, piece)

    # ------------------------------------------------------------
    # Attack / check helpers
    # ------------------------------------------------------------
    def _pawn_attacked(self, sq: int, by_color: Color) -> bool:
        """Return True if square `sq` is attacked by a pawn of `by_color`."""

        pawns = self.bitboards[int(by_color)][int(PieceType.PAWN)]
        target = SQUARE_BB[sq]

        if by_color == Color.WHITE:
            # white pawns attack upwards: diagonals +7 and +9
            attacks = ((pawns << 7) & NOT_FILE_H) | ((pawns << 9) & NOT_FILE_A)
        else:
            # black pawns attack downwards: diagonals -7 and -9
            attacks = ((pawns >> 7) & NOT_FILE_A) | ((pawns >> 9) & NOT_FILE_H)

        return bool(attacks & target)

    def is_square_attacked(self, sq: int, by_color: Color) -> bool:
        """Return True if square `sq` is attacked by any piece of `by_color`."""
        occ = self.all_occupancy
        ci = int(by_color)

        # ------------------------
        # Pawn attacks
        # ------------------------
        if self._pawn_attacked(sq, by_color):
            return True

        # ------------------------
        # Knight attacks
        # ------------------------
        knights = self.bitboards[ci][int(PieceType.KNIGHT)]
        if knights & knight_attacks(sq):
            return True

        # ------------------------
        # Bishop/Queen diagonals
        # ------------------------
        diag_attackers = (
                self.bitboards[ci][int(PieceType.BISHOP)]
                | self.bitboards[ci][int(PieceType.QUEEN)]
        )
        if diag_attackers and (bishop_attacks(sq, occ) & diag_attackers):
            return True

        # ------------------------
        # Rook/Queen straight lines
        # ------------------------
        straight_attackers = (
                self.bitboards[ci][int(PieceType.ROOK)]
                | self.bitboards[ci][int(PieceType.QUEEN)]
        )
        if straight_attackers and (rook_attacks(sq, occ) & straight_attackers):
            return True

        # ------------------------
        # King adjacency
        # ------------------------
        king_bb = self.bitboards[ci][int(PieceType.KING)]
        if king_bb:
            # extrai o único bit do rei
            king_sq = (king_bb & -king_bb).bit_length() - 1
            if king_attacks(king_sq) & (1 << sq):
                return True

        return False

    def is_in_check(self, color: Color) -> bool:
        """Check if king of specified color is in check.

        Args:
            color: Color to check for king safety

        Returns:
            bool: True if king is in check
        """
        enemy = Color.BLACK if color == Color.WHITE else Color.WHITE

        king_bb = self.bitboards[int(color)][int(PieceType.KING)]
        if king_bb == 0:
            return False

        king_sq = (king_bb & -king_bb).bit_length() - 1
        return self.is_square_attacked(king_sq, enemy)

    def make_move(self, move: Move) -> None:
        """
        Aplica um movimento completo:
        - atualização consistente de bitboards, mailbox, occupancies
        - roque, promoção, en-passant corretos
        - castling rights corrigidos

        Args:
            move: Move object containing move information
        """
        self._push_state()
        old_castling = self.castling_rights
        old_ep = self.en_passant_square

        # remover estado antigo do hash
        self.zobrist_key = Zobrist.xor_castling(self.zobrist_key, old_castling)
        if old_ep is not None:
            self.zobrist_key = Zobrist.xor_enpassant(self.zobrist_key, old_ep)

        stm = self.side_to_move
        enemy = Color.BLACK if stm == Color.WHITE else Color.WHITE

        from_sq = move.from_sq
        to_sq = move.to_sq
        piece = move.piece

        old_ep = self.en_passant_square
        self.en_passant_square = None

        # ====================================================
        # CAPTURA (normal + en-passant)
        # ====================================================
        self._do_capture(move, stm, enemy, to_sq, old_ep)

        # ====================================================
        # MOVIMENTO PRINCIPAL
        # ====================================================
        self._do_move_piece(stm, piece, from_sq, to_sq)

        # ====================================================
        # ROQUE
        # ====================================================
        if piece == PieceType.KING and abs(to_sq - from_sq) == 2:
            self._do_castling(stm, from_sq, to_sq)

        # ====================================================
        # PROMOÇÃO
        # ====================================================
        self._do_promotion(stm, move, to_sq)

        # ====================================================
        # CASTLING RIGHTS
        # ====================================================
        self._do_castling_rights_update(stm, piece, from_sq, to_sq, move)

        # ====================================================
        # EN PASSANT (already handled)
        # ====================================================
        self._do_en_passant_update(piece, from_sq, to_sq)

        # ====================================================
        # HALF-MOVE / FULLMOVE UPDATE (helper)
        # ====================================================
        self._do_fullmove_halfmove_update(stm, piece, move)

        # ====================================================
        # ATUALIZAR OCCUPANCY
        # ====================================================
        self._update_occupancy()

        # ====================================================
        # TROCA DE LADO
        # ====================================================
        self.side_to_move = enemy

        # ====================================================
        # ZOBRIST: aplicar novos estados
        # ====================================================
        self.zobrist_key = Zobrist.xor_castling(self.zobrist_key, self.castling_rights)

        if self.en_passant_square is not None:
            self.zobrist_key = Zobrist.xor_enpassant(self.zobrist_key, self.en_passant_square)

        self.zobrist_key = Zobrist.xor_side(self.zobrist_key)

    def unmake_move(self) -> None:
        """Restore board state to before last move."""
        self._pop_state()

    def _push_state(self) -> None:
        """
        Save full snapshot of mutable board state required to unmake moves.
        Snapshot order is deliberate and must match _pop_state exactly.
        """
        # Copy bitboards: two lists (one per color) of piece bitboards
        bitboards_copy = [list(self.bitboards[0]), list(self.bitboards[1])]

        # Mailbox is list of tuples or None; list() makes a shallow copy (tuples immutable)
        mailbox_copy = list(self.mailbox)

        # Occupancy per color (ints)
        occupancy_copy = [int(self.occupancy[0]), int(self.occupancy[1])]

        # Global occupancy
        all_occ_copy = int(self.all_occupancy)

        # Primitives
        castling_copy = int(self.castling_rights)
        enpass_copy = None if self.en_passant_square is None else int(self.en_passant_square)
        halfmove_copy = int(self.halfmove_clock)
        fullmove_copy = int(self.fullmove_number)
        side_copy = self.side_to_move

        # Segurança extra em _push_state()
        if not hasattr(self, "zobrist_key"):
            from core.hash.zobrist import Zobrist
            Zobrist.ensure_initialized()
            self.zobrist_key = self.compute_zobrist()

        # Push tuple in this exact order (must match _pop_state)
        self._state_stack.append((
            bitboards_copy, mailbox_copy, occupancy_copy, all_occ_copy,
            castling_copy, enpass_copy, halfmove_copy, fullmove_copy, side_copy,
            self.zobrist_key,
        ))

    def _pop_state(self) -> None:
        """
        Restore snapshot saved by _push_state. Must match the push order exactly.

        Raises:
            RuntimeError: If no state to pop
        """
        if not self._state_stack:
            raise RuntimeError("No state to pop")

        (
            bitboards_copy, mailbox_copy, occupancy_copy, all_occ_copy,
            castling_copy, enpass_copy, halfmove_copy, fullmove_copy, side_copy,
            zobrist_copy,
        ) = self._state_stack.pop()
        self.zobrist_key = zobrist_copy

        # Restore bitboards (ensure lists-of-lists shape)
        self.bitboards = [list(bitboards_copy[0]), list(bitboards_copy[1])]

        # Mailbox
        self.mailbox = list(mailbox_copy)

        # Occupancy / all_occupancy
        self.occupancy = [int(occupancy_copy[0]), int(occupancy_copy[1])]
        self.all_occupancy = int(all_occ_copy)

        # Other primitives
        self.castling_rights = int(castling_copy)
        self.en_passant_square = None if enpass_copy is None else int(enpass_copy)
        self.halfmove_clock = int(halfmove_copy)
        self.fullmove_number = int(fullmove_copy)
        self.side_to_move = side_copy

        # Final sanity check: union of piece bitboards must equal all_occupancy
        bb_union = 0
        for c in (0, 1):
            for p in range(len(self.bitboards[c])):
                bb_union |= int(self.bitboards[c][p])
        assert self.all_occupancy == bb_union, "all_occupancy mismatch after pop_state"

    # ------------------------------------------------------------
    # FEN operations
    # ------------------------------------------------------------
    @classmethod
    def from_fen(cls, fen: str) -> Board:
        """Create board from FEN string.

        Args:
            fen: FEN string representation

        Returns:
            Board: New board instance with position from FEN
        """
        board = cls(setup=False)
        board.set_fen(fen)
        return board

    def set_fen(self, fen: str) -> None:
        """
        Load a position from a FEN string.
        Minimal implementation for perft validation.

        Args:
            fen: FEN string representation

        Raises:
            ValueError: If FEN string is invalid
        """
        self.clear()

        parts = fen.strip().split()
        if len(parts) < 4:
            raise ValueError("Invalid FEN: must have at least 4 fields")

        placement, side, castling, en_passant = parts[0], parts[1], parts[2], parts[3]

        # Parse piece placement
        rank = 7
        file = 0

        for ch in placement:
            if ch == "/":
                rank -= 1
                file = 0
                continue

            if ch.isdigit():
                file += int(ch)
                continue

            color = Color.WHITE if ch.isupper() else Color.BLACK
            piece = {
                "p": PieceType.PAWN, "n": PieceType.KNIGHT, "b": PieceType.BISHOP,
                "r": PieceType.ROOK, "q": PieceType.QUEEN, "k": PieceType.KING,
            }[ch.lower()]

            square = rank * 8 + file
            self.set_piece_at(square, color, piece)
            file += 1

        # Side to move
        self.side_to_move = Color.WHITE if side == "w" else Color.BLACK

        # Castling rights (use canonical CASTLE_* constants)
        self.castling_rights = 0
        if castling != "-":
            if "K" in castling:
                self.castling_rights |= CASTLE_WHITE_K
            if "Q" in castling:
                self.castling_rights |= CASTLE_WHITE_Q
            if "k" in castling:
                self.castling_rights |= CASTLE_BLACK_K
            if "q" in castling:
                self.castling_rights |= CASTLE_BLACK_Q

        # En passant
        if en_passant == "-":
            self.en_passant_square = None
        else:
            file_char, rank_char = en_passant
            file = ord(file_char) - ord("a")
            rank = int(rank_char) - 1
            self.en_passant_square = rank * 8 + file

        # Recalculate occupancy
        self._update_occupancy()

        # Optional FEN fields
        if len(parts) >= 5:
            self.halfmove_clock = int(parts[4])
        else:
            self.halfmove_clock = 0

        if len(parts) >= 6:
            self.fullmove_number = int(parts[5])
        else:
            self.fullmove_number = 1

        self.validate()
        Zobrist.ensure_initialized()
        self.zobrist_key = self.compute_zobrist()

    def to_fen(self) -> str:
        """
        Serializa o tabuleiro atual em FEN.

        Returns:
            str: FEN string representation of current position
        """
        pieces = {
            (Color.WHITE, PieceType.PAWN): "P",
            (Color.WHITE, PieceType.KNIGHT): "N",
            (Color.WHITE, PieceType.BISHOP): "B",
            (Color.WHITE, PieceType.ROOK): "R",
            (Color.WHITE, PieceType.QUEEN): "Q",
            (Color.WHITE, PieceType.KING): "K",

            (Color.BLACK, PieceType.PAWN): "p",
            (Color.BLACK, PieceType.KNIGHT): "n",
            (Color.BLACK, PieceType.BISHOP): "b",
            (Color.BLACK, PieceType.ROOK): "r",
            (Color.BLACK, PieceType.QUEEN): "q",
            (Color.BLACK, PieceType.KING): "k",
        }

        rows = []

        for rank in range(7, -1, -1):
            empty = 0
            row = ""

            for file in range(8):
                sq = rank * 8 + file
                cell = self.mailbox[sq]

                if cell is None:
                    empty += 1
                else:
                    if empty > 0:
                        row += str(empty)
                        empty = 0

                    color, piece = cell
                    row += pieces[(color, piece)]

            if empty > 0:
                row += str(empty)

            rows.append(row)

        board_part = "/".join(rows)

        # Side to move
        side = "w" if self.side_to_move == Color.WHITE else "b"

        # Castling
        castling = ""
        if self.castling_rights & CASTLE_WHITE_K:
            castling += "K"
        if self.castling_rights & CASTLE_WHITE_Q:
            castling += "Q"
        if self.castling_rights & CASTLE_BLACK_K:
            castling += "k"
        if self.castling_rights & CASTLE_BLACK_Q:
            castling += "q"
        if castling == "":
            castling = "-"

        # En passant
        if self.en_passant_square is None:
            ep = "-"
        else:
            file = self.en_passant_square % 8
            rank = self.en_passant_square // 8
            ep = f"{chr(ord('a') + file)}{rank + 1}"

        return f"{board_part} {side} {castling} {ep} {self.halfmove_clock} {self.fullmove_number}"

    # ------------------------------------------------------------
    # Internal helper methods
    # ------------------------------------------------------------

    def _clear_square(self, sq: int) -> None:
        """Remove qualquer peça do square, atualizando bitboards e mailbox.

        Args:
            sq: Square index to clear
        """
        cell = self.mailbox[sq]
        if cell is None:
            return

        color, ptype = cell
        bit = (1 << sq)

        # mailbox
        self.mailbox[sq] = None

        # bitboard removal (AND-NOT)
        ci = int(color)
        pi = int(ptype)
        self.bitboards[ci][pi] &= ~bit

        # occupancy
        self.occupancy[ci] &= ~bit
        self.all_occupancy &= ~bit

    def _place_piece(self, color: Color, ptype: PieceType, sq: int) -> None:
        """Coloca uma peça no square, atualizando bitboards e mailbox.

        Args:
            color: Piece color
            ptype: Piece type
            sq: Target square index
        """
        bit = (1 << sq)
        ci = int(color)
        pi = int(ptype)

        # mailbox
        self.mailbox[sq] = (color, ptype)

        # bitboards
        self.bitboards[ci][pi] |= bit

        # occupancy
        self.occupancy[ci] |= bit
        self.all_occupancy |= bit

    def _update_occupancy(self) -> None:
        """Recalculate occupancy bitboards from piece bitboards."""
        self.occupancy[0] = (
                self.bitboards[0][0] | self.bitboards[0][1] | self.bitboards[0][2] |
                self.bitboards[0][3] | self.bitboards[0][4] | self.bitboards[0][5]
        )

        self.occupancy[1] = (
                self.bitboards[1][0] | self.bitboards[1][1] | self.bitboards[1][2] |
                self.bitboards[1][3] | self.bitboards[1][4] | self.bitboards[1][5]
        )

        self.all_occupancy = self.occupancy[0] | self.occupancy[1]

    def _do_capture(self, move: Move, stm: Color, enemy: Color, to_sq: int, old_ep: Optional[int]) -> None:
        """Executa captura normal ou en-passant, com atualização Zobrist."""

        # En passant capture
        if (move.piece == PieceType.PAWN and move.is_capture and
                old_ep is not None and to_sq == old_ep):
            cap_sq = to_sq - 8 if stm == Color.WHITE else to_sq + 8
            self._clear_square(cap_sq)

            cap_index = int(enemy) * 6 + int(PieceType.PAWN)
            self.zobrist_key = Zobrist.xor_piece(self.zobrist_key, cap_index, cap_sq)
            return

        # Captura normal
        if move.is_capture:
            captured = self.mailbox[to_sq]  # leitura real do board
            if captured is not None:
                cap_color, cap_piece = captured
                cap_index = int(cap_color) * 6 + int(cap_piece)
                self.zobrist_key = Zobrist.xor_piece(self.zobrist_key, cap_index, to_sq)

            self._clear_square(to_sq)

    def _do_move_piece(self, stm: Color, piece: PieceType, from_sq: int, to_sq: int) -> None:
        """Execute the main piece move (clear source, place on dest) and update Zobrist."""
        # clear origem e coloca destino usando helpers já existentes
        self._clear_square(from_sq)
        self._place_piece(stm, piece, to_sq)

        # atualizar hash: remove peça na origem, adiciona no destino
        piece_index = int(stm) * 6 + int(piece)
        self.zobrist_key = Zobrist.xor_piece(self.zobrist_key, piece_index, from_sq)
        self.zobrist_key = Zobrist.xor_piece(self.zobrist_key, piece_index, to_sq)

    def _do_castling(self, stm: Color, from_sq: int, to_sq: int) -> None:
        """Executa roque, atualizando bitboards, mailbox e Zobrist.

        Pré-condição: chamada somente quando piece == KING e abs(to_sq - from_sq) == 2.
        """
        rook_index = int(stm) * 6 + int(PieceType.ROOK)

        # Determinar origem/destino da torre
        if stm == Color.WHITE:
            if to_sq == 6:  # O-O (e1 -> g1)
                rook_from, rook_to = 7, 5  # h1 -> f1
            elif to_sq == 2:  # O-O-O (e1 -> c1)
                rook_from, rook_to = 0, 3  # a1 -> d1
            else:
                return
        else:  # BLACK
            if to_sq == 62:  # O-O (e8 -> g8)
                rook_from, rook_to = 63, 61  # h8 -> f8
            elif to_sq == 58:  # O-O-O (e8 -> c8)
                rook_from, rook_to = 56, 59  # a8 -> d8
            else:
                return

        # remover torre da origem
        self._clear_square(rook_from)
        self.zobrist_key = Zobrist.xor_piece(self.zobrist_key, rook_index, rook_from)

        # colocar torre no destino
        self._place_piece(stm, PieceType.ROOK, rook_to)
        self.zobrist_key = Zobrist.xor_piece(self.zobrist_key, rook_index, rook_to)

    def _do_promotion(self, stm: Color, move: Move, to_sq: int) -> None:
        """Executa promoção: remove o peão e coloca a peça promovida.
           Atualiza Zobrist exatamente como no código original.
        """
        promo = move.promotion
        if promo is None:
            return

        # remover o peão que chegou no destino
        self._clear_square(to_sq)

        # colocar a peça promovida
        self._place_piece(stm, promo, to_sq)

        pawn_index = int(stm) * 6 + int(PieceType.PAWN)
        promo_index = int(stm) * 6 + int(promo)

        # atualizar Zobrist: remove PAWN no destino, adiciona promoção
        self.zobrist_key = Zobrist.xor_piece(self.zobrist_key, pawn_index, to_sq)
        self.zobrist_key = Zobrist.xor_piece(self.zobrist_key, promo_index, to_sq)

    def _do_castling_rights_update(self, stm: Color, piece: PieceType, from_sq: int, to_sq: int, move: Move) -> None:
        """Atualiza direitos de roque exatamente como no código original."""
        # King move removes castling rights
        if piece == PieceType.KING:
            if stm == Color.WHITE:
                self.castling_rights &= ~(CASTLE_WHITE_K | CASTLE_WHITE_Q)
            else:
                self.castling_rights &= ~(CASTLE_BLACK_K | CASTLE_BLACK_Q)

        # Rook move removes corresponding castling right
        if piece == PieceType.ROOK:
            if stm == Color.WHITE:
                if from_sq == 0:
                    self.castling_rights &= ~CASTLE_WHITE_Q
                elif from_sq == 7:
                    self.castling_rights &= ~CASTLE_WHITE_K
            else:
                if from_sq == 56:
                    self.castling_rights &= ~CASTLE_BLACK_Q
                elif from_sq == 63:
                    self.castling_rights &= ~CASTLE_BLACK_K

        # Capture on rook square removes corresponding castling right
        if move.is_capture:
            if to_sq == 0:
                self.castling_rights &= ~CASTLE_WHITE_Q
            elif to_sq == 7:
                self.castling_rights &= ~CASTLE_WHITE_K
            elif to_sq == 56:
                self.castling_rights &= ~CASTLE_BLACK_Q
            elif to_sq == 63:
                self.castling_rights &= ~CASTLE_BLACK_K

    def _do_en_passant_update(self, piece: PieceType, from_sq: int, to_sq: int) -> None:
        """Atualiza corretamente a square de en-passant."""
        # reset sempre antes (regra padrão)
        self.en_passant_square = None

        # só peão que avança 2 casas cria uma EP square
        if piece == PieceType.PAWN and abs(to_sq - from_sq) == 16:
            self.en_passant_square = (from_sq + to_sq) // 2

    def _do_fullmove_halfmove_update(
            self,
            stm: Color,
            piece: PieceType,
            move: "Move"
    ) -> None:
        """Atualiza halfmove_clock (regra dos 50 lances) e fullmove_number."""
        # -------------------------------------
        # HALF-MOVE CLOCK (regra dos 50 lances)
        # -------------------------------------
        # Reset sempre se: peão moveu, houve captura, ou houve promoção
        if piece == PieceType.PAWN or move.is_capture or (move.promotion is not None):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # -------------------------------------
        # FULLMOVE NUMBER (incrementa após lance das pretas)
        # -------------------------------------
        if stm == Color.BLACK:
            self.fullmove_number += 1
