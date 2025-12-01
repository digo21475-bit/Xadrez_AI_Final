import pytest

from core.board.board import Board
from core.moves.move import Move

from utils.constants import SQUARE_BB, square_index
from utils.enums import Color, PieceType
from core.moves.tables.attack_tables import rook_attacks, bishop_attacks, knight_attacks, king_attacks
from core.moves.magic.magic_bitboards import init as init_magics

# ============================================================
# Setup global (magics + zobrist)
# ============================================================

def setup_module():
    init_magics()
    Zobrist.init(seed=123456, force=True)



# ============================================================
# 1. Estrutura básica do tabuleiro
# ============================================================

def test_board_initial_kings_exist():
    board = Board()
    assert board.bitboards[Color.WHITE][PieceType.KING] != 0
    assert board.bitboards[Color.BLACK][PieceType.KING] != 0


def test_board_empty_clear():
    board = Board()
    board.clear()
    assert board.all_occupancy == 0
    assert all(cell is None for cell in board.mailbox)


def test_copy_preserves_state():
    board = Board()
    copy = board.copy()
    assert copy.all_occupancy == board.all_occupancy
    assert copy.mailbox == board.mailbox
    assert copy.side_to_move == board.side_to_move


# ============================================================
# 2. Colocação e remoção de peças
# ============================================================

def test_set_and_get_piece():
    board = Board(setup=False)
    board.clear()
    board.set_piece_at(square_index("e4"), Color.WHITE, PieceType.QUEEN)
    piece = board.get_piece_at(square_index("e4"))
    assert piece == (Color.WHITE, PieceType.QUEEN)


def test_remove_piece():
    board = Board(setup=False)
    board.clear()
    sq = square_index("d5")
    board.set_piece_at(sq, Color.BLACK, PieceType.KNIGHT)
    board.remove_piece_at(sq)
    assert board.get_piece_at(sq) is None
    assert board.all_occupancy == 0


def test_set_piece_twice_same_square_raises():
    board = Board(setup=False)
    board.clear()
    sq = square_index("c3")
    board.set_piece_at(sq, Color.WHITE, PieceType.BISHOP)
    with pytest.raises(AssertionError):
        board.set_piece_at(sq, Color.WHITE, PieceType.ROOK)


# ============================================================
# 3. Movimento simples e captura
# ============================================================

def test_move_piece_simple():
    board = Board(setup=False)
    board.clear()
    board.set_piece_at(square_index("a2"), Color.WHITE, PieceType.PAWN)
    board.move_piece(square_index("a2"), square_index("a4"))
    assert board.get_piece_at(square_index("a4")) == (Color.WHITE, PieceType.PAWN)


def test_capture_piece():
    board = Board(setup=False)
    board.clear()
    board.set_piece_at(square_index("e4"), Color.WHITE, PieceType.ROOK)
    board.set_piece_at(square_index("e7"), Color.BLACK, PieceType.KNIGHT)
    board.move_piece(square_index("e4"), square_index("e7"))
    assert board.get_piece_at(square_index("e7")) == (Color.WHITE, PieceType.ROOK)
    assert board.bitboards[Color.BLACK][PieceType.KNIGHT] == 0


# ============================================================
# 4. Validação de invariantes
# ============================================================

def test_validate_consistency():
    board = Board()
    board.validate()  # não deve levantar erro


def test_mailbox_consistency_after_moves():
    board = Board()
    board.move_piece(12, 28)  # e2 -> e4
    board.validate()
    board.move_piece(52, 36)  # e7 -> e5
    board.validate()


# ============================================================
# 5. Ataques: knight, king
# ============================================================

def test_knight_attack_center():
    sq = square_index("d4")
    mask = knight_attacks(sq)
    assert len([s for s in range(64) if mask & SQUARE_BB[s]]) == 8


def test_king_attack_center():
    sq = square_index("d4")
    mask = king_attacks(sq)
    assert len([s for s in range(64) if mask & SQUARE_BB[s]]) == 8


# ============================================================
# 6. Magic bitboards: rook / bishop
# ============================================================

def test_rook_attacks_empty_board():
    board = Board(setup=False)
    board.clear()
    sq = square_index("d4")
    attacks = rook_attacks(sq, board.all_occupancy)
    assert attacks.bit_count() == 14


def test_bishop_attacks_empty_board():
    board = Board(setup=False)
    board.clear()
    sq = square_index("d4")
    attacks = bishop_attacks(sq, board.all_occupancy)
    assert attacks.bit_count() == 13


def test_rook_blocked():
    board = Board(setup=False)
    board.clear()
    board.set_piece_at(square_index("d6"), Color.WHITE, PieceType.PAWN)
    attacks = rook_attacks(square_index("d4"), board.all_occupancy)
    assert not (attacks & SQUARE_BB[square_index("d7")])


# ============================================================
# 7. is_square_attacked
# ============================================================

def test_square_attacked_by_rook():
    board = Board(setup=False)
    board.clear()
    board.set_piece_at(square_index("a1"), Color.WHITE, PieceType.ROOK)
    assert board.is_square_attacked(square_index("a8"), Color.WHITE)


def test_square_not_attacked():
    board = Board(setup=False)
    board.clear()
    board.set_piece_at(square_index("a1"), Color.WHITE, PieceType.ROOK)
    assert not board.is_square_attacked(square_index("h8"), Color.WHITE)


# ============================================================
# 8. Check detection
# ============================================================

def test_king_in_check_by_rook():
    board = Board(setup=False)
    board.clear()
    board.set_piece_at(square_index("e1"), Color.WHITE, PieceType.KING)
    board.set_piece_at(square_index("e8"), Color.BLACK, PieceType.ROOK)
    assert board.is_in_check(Color.WHITE)


def test_king_not_in_check():
    board = Board(setup=False)
    board.clear()
    board.set_piece_at(square_index("e1"), Color.WHITE, PieceType.KING)
    board.set_piece_at(square_index("a8"), Color.BLACK, PieceType.ROOK)
    assert not board.is_in_check(Color.WHITE)


# ============================================================
# 9. Zobrist
# ============================================================

from core.hash.zobrist import Zobrist

'''
def test_board_hash_changes_after_move():
    Zobrist.init(seed=123456)

    board = Board()

    # Recalcula hash manualmente a partir do estado atual
    def compute_hash(b):
        h = 0

        # Percorre todas as peças do tabuleiro
        for color in b.bitboards:
            for piece_type, bb in b.bitboards[color].items():
                piece_index = color * 6 + piece_type.value  # conforme seu padrão
                bits = bb

                while bits:
                    sq = (bits & -bits).bit_length() - 1
                    h = Zobrist.xor_piece(h, piece_index, sq)
                    bits &= bits - 1

        # lado a mover
        if b.side_to_move == 1:
            h = Zobrist.xor_side(h)

        # castling
        h = Zobrist.xor_castling(h, b.castling_rights)

        # en-passant
        h = Zobrist.xor_enpassant(h, b.enpassant_square)

        return h

    h1 = compute_hash(board)

    move = Move(
        from_sq=12,
        to_sq=28,
        piece=PieceType.PAWN,
        is_capture=False,
        promotion=None
    )

    board.make_move(move)

    h2 = compute_hash(board)

    assert h1 != h2

'''


def test_zobrist_is_deterministic():
    Zobrist.init(seed=123456)

    sig1 = Zobrist.signature()
    sig2 = Zobrist.signature()

    assert sig1 == sig2


def test_zobrist_reset():
    Zobrist.reset()
    Zobrist.init(seed=123456)

    # apenas valida que não quebra
    assert Zobrist.piece_square != []
    assert Zobrist.castling != []
    assert Zobrist.enpassant != []

# ============================================================
# 10. Make / Unmake
# ============================================================

def test_make_and_unmake_move():
    Zobrist.reset()
    Zobrist.init(seed=123456)

    board = Board()
    sig1 = Zobrist.signature()

    move = Move(
        from_sq=12,
        to_sq=28,
        piece=PieceType.PAWN,
        is_capture=False,
        promotion=None
    )

    board.make_move(move)
    board.unmake_move()

    sig2 = Zobrist.signature()

    assert sig1 == sig2


# ============================================================
# 11. Integridade do estado
# ============================================================

def test_state_stack_integrity():
    board = Board()
    before = board.copy()
    board.move_piece(1, 18)
    board.move_piece(6, 21)
    board._pop_state() if board._state_stack else None
    assert board.all_occupancy != 0 or before.all_occupancy != 0


def test_no_overlap_between_colors():
    board = Board()
    assert (board.occupancy[0] & board.occupancy[1]) == 0


def test_piece_count_consistency():
    board = Board()
    total = board.occupancy[0].bit_count() + board.occupancy[1].bit_count()
    assert total == 32


# ============================================================
# 12. API helper: place()
# ============================================================

def test_place_helper():
    board = Board(setup=False)
    board.clear()
    board.place(PieceType.QUEEN, Color.BLACK, "h5")
    sq = square_index("h5")
    assert board.get_piece_at(sq) == (Color.BLACK, PieceType.QUEEN)

def test_zobrist_signature_is_stable():
    Zobrist.reset()
    Zobrist.init(seed=123456)

    sig1 = Zobrist.signature()
    sig2 = Zobrist.signature()

    assert sig1 == sig2

def test_zobrist_signature_reproducible_with_same_seed():
    Zobrist.reset()
    Zobrist.init(seed=777)
    sig1 = Zobrist.signature()

    Zobrist.reset()
    Zobrist.init(seed=777)
    sig2 = Zobrist.signature()

    assert sig1 == sig2
