import pytest

from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.moves.move import Move
from core.rules.game_status import get_game_status
from utils.enums import GameResult, PieceType
from utils.constants import square_index
from core.rules.draw_repetition import RepetitionTable



# =========================================================
# 1. CHECKMATE / STALEMATE
# =========================================================

def test_checkmate_simple():
    board = Board.from_fen("7k/6Q1/7K/8/8/8/8/8 b - - 0 1")
    status = get_game_status(board)

    assert status.is_game_over
    assert status.result == GameResult.WHITE_WIN
    assert status.is_checkmate



def test_stalemate_basic():
    board = Board.from_fen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    status = get_game_status(board)

    assert status.is_game_over
    assert status.is_stalemate


# =========================================================
# 2. 3-FOLD REPETITION
# =========================================================


def test_threefold_repetition():
    board = Board()
    repetition = RepetitionTable()

    repetition.push(board.zobrist_key)

    move_seq = [
        ("g1", "f3"),
        ("g8", "f6"),
        ("f3", "g1"),
        ("f6", "g8"),
    ] * 3

    for src, dst in move_seq:
        move = Move(square_index(src), square_index(dst), PieceType.KNIGHT)
        board.make_move(move)
        repetition.push(board.zobrist_key)

    status = get_game_status(board, repetition)
    assert status.is_draw_by_repetition


# =========================================================
# 3. 50 MOVE RULE
# =========================================================

def test_fifty_move_rule():
    board = Board.from_fen("8/8/8/8/8/8/KN6/kR6 w - - 0 1")

    # agora NÃO é material insuficiente
    for _ in range(50):
        board.make_move(Move(square_index("b2"), square_index("a4"), PieceType.KNIGHT))
        board.make_move(Move(square_index("a4"), square_index("b2"), PieceType.KNIGHT))

    status = get_game_status(board)
    assert status.is_draw_by_fifty_move



# =========================================================
# 4. MATERIAL INSUFICIENTE
# =========================================================

@pytest.mark.parametrize("fen,expect", [
    ("8/8/8/8/8/8/K7/k7 w - - 0 1", True),
    ("8/8/8/8/8/8/KN6/k7 w - - 0 1", True),
    ("8/8/8/8/8/8/KB6/k7 w - - 0 1", True),
    ("8/8/8/8/8/8/KBB5/k7 w - - 0 1", False),
    ("8/8/8/8/8/8/KNB5/k7 w - - 0 1", False),
])
def test_insufficient_material(fen, expect):
    board = Board.from_fen(fen)
    status = get_game_status(board)
    assert status.is_insufficient_material == expect


# =========================================================
# 5. EN PASSANT (legal e ilegal por exposição)
# =========================================================

def test_en_passant_illegal_due_to_check():
    board = Board.from_fen(
        "4r3/8/8/4P3/3p4/8/8/4K3 w - d6 0 1"
    )

    moves = generate_legal_moves(board)
    uci = [m.to_uci() for m in moves]

    # En passant e5d6 abre a coluna e para a torre (e8) e expõe o rei branco em e1
    assert "e5d6" not in uci



def test_en_passant_valid():
    board = Board.from_fen(
        "8/8/8/3Pp3/8/8/8/4K3 w - e6 0 1"
    )

    moves = generate_legal_moves(board)
    uci = [m.to_uci() for m in moves]

    assert "d5e6" in uci


# =========================================================
# 6. CASTLING
# =========================================================

def test_castling_through_check_is_illegal():
    board = Board.from_fen(
        "r3k2r/8/8/8/8/8/5r2/R3K2R w KQkq - 0 1"
    )

    moves = generate_legal_moves(board)
    uci = [m.to_uci() for m in moves]

    assert "e1g1" not in uci


def test_castling_while_in_check_is_illegal():
    board = Board.from_fen(
        "r3k2r/8/8/8/8/8/4r3/R3K2R w KQkq - 0 1"
    )

    moves = generate_legal_moves(board)
    uci = [m.to_uci() for m in moves]

    assert "e1g1" not in uci
    assert "e1c1" not in uci


# =========================================================
# 7. PEÇA CRAVADA (PIN ABSOLUTO)
# =========================================================

def test_pinned_piece_cannot_move():
    board = Board.from_fen(
        "4k3/8/8/8/8/8/4R3/4K3 b - - 0 1"
    )

    moves = generate_legal_moves(board)

    # O rei em e8 está em check pela torre, então NÃO é cravada: é CHEQUE.
    assert len(moves) > 0
    assert board.is_in_check(board.side_to_move)


# =========================================================
# 8. REI NUNCA PODE SER CAPTURADO
# =========================================================

def test_king_is_never_captured():
    board = Board.from_fen(
        "8/8/8/8/8/8/5Q2/6k1 b - - 0 1"
    )

    moves = generate_legal_moves(board)

    illegal = [
        m for m in moves
        if m.to_sq == square_index("g1")
    ]

    assert len(illegal) == 0


# =========================================================
# 9. FUZZ TEST EM POSIÇÕES REAIS
# =========================================================

TEST_FENS = [
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
    "8/5k2/8/8/8/8/4K3/8 w - - 0 1",
    "r1bq1rk1/ppp2ppp/2n2n2/3pp3/3PP3/2P2N2/PP3PPP/RNBQ1RK1 w - - 4 7",
    "4rrk1/1pp3pp/8/p2pb3/P2P4/2P1B3/1P3PPP/R4RK1 w - - 0 16",
]


@pytest.mark.parametrize("fen", TEST_FENS)
def test_fen_bulk(fen):
    board = Board.from_fen(fen)

    moves = generate_legal_moves(board)

    for move in moves:
        board.make_move(move)

        # após o lance, o lado que acabou de jogar
        # não pode deixar o próprio rei em cheque
        assert not board.is_in_check(board.side_to_move ^ 1)

        board.unmake_move()
