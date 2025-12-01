from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from utils.enums import PieceType, Color
from utils.constants import square_index


# =========================
# HELPERS
# =========================

def _assert_all_moves_resolve_check(board, moves, color):
    for m in moves:
        b2 = board.copy()
        b2.make_move(m)
        assert not b2.is_in_check(color), f"Movimento ilegal manteve check: {m}"


# =========================
# 1. CHECKS DIRETOS POR PEÇA
# =========================

def test_king_in_check_by_rook():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.ROOK, Color.BLACK, "e8")
    b.place(PieceType.KING, Color.WHITE, "e1")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    _assert_all_moves_resolve_check(b, moves, Color.WHITE)


def test_king_in_check_by_bishop():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.BISHOP, Color.BLACK, "h4")
    b.place(PieceType.KING, Color.WHITE, "e1")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    _assert_all_moves_resolve_check(b, moves, Color.WHITE)


def test_king_in_check_by_knight():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.KNIGHT, Color.BLACK, "f6")
    b.place(PieceType.KING, Color.WHITE, "e4")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    _assert_all_moves_resolve_check(b, moves, Color.WHITE)


def test_king_in_check_by_pawn():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.PAWN, Color.BLACK, "d5")
    b.place(PieceType.KING, Color.WHITE, "e4")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    _assert_all_moves_resolve_check(b, moves, Color.WHITE)


def test_king_in_check_by_queen():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.QUEEN, Color.BLACK, "d8")
    b.place(PieceType.KING, Color.WHITE, "d1")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    _assert_all_moves_resolve_check(b, moves, Color.WHITE)


# =========================
# 2. CHECK BLOQUEÁVEL
# =========================

def test_blocking_check_from_rook():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.ROOK, Color.BLACK, "e8")
    b.place(PieceType.KING, Color.WHITE, "e1")
    b.place(PieceType.BISHOP, Color.WHITE, "c4")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    block_squares = {
        square_index("e2"),
        square_index("e3"),
        square_index("e4"),
        square_index("e5"),
        square_index("e6"),
        square_index("e7"),
    }

    assert any(m.to_sq in block_squares for m in moves), "Nenhum bloqueio gerado"
    _assert_all_moves_resolve_check(b, moves, Color.WHITE)


# =========================
# 3. CHECK POR DESCOBERTA
# =========================

def test_discovered_check_illegal_move():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.ROOK, Color.BLACK, "e8")
    b.place(PieceType.KING, Color.WHITE, "e1")
    b.place(PieceType.ROOK, Color.WHITE, "e2")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    for m in moves:
        if m.from_sq == square_index("e2"):
            b2 = b.copy()
            b2.make_move(m)
            assert not b2.is_in_check(Color.WHITE)


# =========================
# 4. CAPTURA DO ATACANTE (CORRIGIDO)
# =========================

def test_capture_adjacent_attacker():
    """
    Rei branco em e4, cavalo preto em f5.
    Rei pode capturar o cavalo (adjacente).
    """
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.KNIGHT, Color.BLACK, "f5")  # ADJACENTE
    b.place(PieceType.KING, Color.WHITE, "e4")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    knight_sq = square_index("f5")

    assert any(
        m.to_sq == knight_sq and m.is_capture for m in moves
    ), "Rei deveria poder capturar o cavalo em f5"

    _assert_all_moves_resolve_check(b, moves, Color.WHITE)


# =========================
# 5. POSIÇÃO NEUTRA
# =========================

def test_no_check_all_moves_are_legal():
    b = Board(setup=False)
    b.clear()

    b.place(PieceType.KING, Color.WHITE, "e1")
    b.place(PieceType.ROOK, Color.WHITE, "a1")
    b.place(PieceType.BISHOP, Color.WHITE, "c1")
    b.place(PieceType.KING, Color.BLACK, "e8")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    assert len(moves) > 0
    _assert_all_moves_resolve_check(b, moves, Color.WHITE)


# =========================
# 6. CHECKMATE REAL (CORRIGIDO)
# =========================

def test_simple_checkmate_results_no_moves():
    """
    Checkmate verdadeiro:
    Rei branco em h1,
    Dama preta em g2,
    Torre preta em h2.
    """

    b = Board(setup=False)
    b.clear()

    b.place(PieceType.KING, Color.WHITE, "h1")
    b.place(PieceType.QUEEN, Color.BLACK, "g2")  # corrigido
    b.place(PieceType.ROOK, Color.BLACK, "h2")

    b.side_to_move = Color.WHITE
    moves = generate_legal_moves(b)

    assert len(moves) == 0, "Era para ser checkmate real"
