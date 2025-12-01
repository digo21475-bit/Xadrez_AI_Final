# tests/test_movegen.py
from core.moves.movegen import generate_pseudo_legal_moves
from core.board.board import Board, square_index  # adapt if path differs
from utils.enums import Color, PieceType


def test_initial_position_moves():
    b = Board()
    b.set_startpos()  # or use whatever initializer you have
    moves = generate_pseudo_legal_moves(b)
    # quick sanity: should be > 15 (pawns + knights)
    assert len(moves) >= 16

# Perft stub (compare known perft numbers if you have perft reference)
def test_perft_depth_1_startpos():
    b = Board()
    b.set_startpos()
    moves = generate_pseudo_legal_moves(b)
    assert len(moves) == 20  # typical initial pseudo-legal moves = 20

def test_startpos_piece_counts():
    b = Board()
    b.set_startpos()

    assert bin(b.bitboards[Color.WHITE][PieceType.PAWN]).count("1") == 8
    assert bin(b.bitboards[Color.BLACK][PieceType.PAWN]).count("1") == 8

    assert bin(b.bitboards[Color.WHITE][PieceType.ROOK]).count("1") == 2
    assert bin(b.bitboards[Color.BLACK][PieceType.ROOK]).count("1") == 2

    assert bin(b.all_occupancy).count("1") == 32

def test_perft_startpos_d1():
    b = Board()
    b.set_startpos()

    moves = generate_pseudo_legal_moves(b)
    assert len(moves) == 20


def test_bishop_free_diagonal():
    b = Board(setup=False)

    b.clear()
    b.place(PieceType.BISHOP, Color.WHITE, "d4")

    moves = generate_pseudo_legal_moves(b)

    # 13 casas possíveis para bispo em d4 em tabuleiro vazio
    bishop_moves = [m for m in moves if m.piece == PieceType.BISHOP]
    assert len(bishop_moves) == 13


def test_rook_free_lines():
    b = Board(setup=False)

    b.clear()
    b.place(PieceType.ROOK, Color.WHITE, "d4")

    moves = generate_pseudo_legal_moves(b)

    rook_moves = [m for m in moves if m.piece == PieceType.ROOK]
    assert len(rook_moves) == 14


def test_knight_center():
    b = Board(setup=False)

    b.clear()
    b.place(PieceType.KNIGHT, Color.WHITE, "d4")

    moves = generate_pseudo_legal_moves(b)

    knight_moves = [m for m in moves if m.piece == PieceType.KNIGHT]
    assert len(knight_moves) == 8


def test_blocked_by_own_piece():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.ROOK, Color.WHITE, "d4")
    b.place(PieceType.PAWN, Color.WHITE, "d6")

    moves = generate_pseudo_legal_moves(b)

    rook_moves = [m for m in moves if m.piece == PieceType.ROOK]

    # rook não pode ir para além de d6
    for m in rook_moves:
        assert m.to_sq != square_index("d7")
        assert m.to_sq != square_index("d8")


def test_capture_generation():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.ROOK, Color.WHITE, "d4")
    b.place(PieceType.KNIGHT, Color.BLACK, "d6")

    moves = generate_pseudo_legal_moves(b)

    capture_moves = [m for m in moves if m.is_capture]

    assert len(capture_moves) == 1


def test_movegen_all_pieces_interaction():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.QUEEN, Color.WHITE, "d4")
    b.place(PieceType.KNIGHT, Color.WHITE, "f4")
    b.place(PieceType.PAWN, Color.BLACK, "d7")

    moves = generate_pseudo_legal_moves(b)

    assert any(m.from_sq == square_index("d4") for m in moves)
    assert any(m.from_sq == square_index("f4") for m in moves)


def test_no_duplicates():
    b = Board()
    b.set_startpos()

    moves = generate_pseudo_legal_moves(b)

    seen = set()
    for m in moves:
        key = (m.from_sq, m.to_sq, m.piece)
        assert key not in seen
        seen.add(key)
