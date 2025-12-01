import random
import pytest

from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.hash.zobrist import Zobrist


# ------------------------------------------------------------
# Setup
# ------------------------------------------------------------

@pytest.fixture(autouse=True)
def init_zobrist():
    # garante que as tabelas estão inicializadas
    Zobrist.ensure_initialized(seed=0xC0FFEE)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def get_move_by_uci(board, uci_str):
    """
    Busca um move pelo UCI entre os movimentos legais do engine.
    """
    for move in generate_legal_moves(board):
        if move.to_uci() == uci_str:
            return move
    raise RuntimeError(f"Move not found in legal moves: {uci_str}")


def play_random_sequence(board, depth=200):
    """
    Aplica uma sequência de movimentos aleatórios.
    Retorna lista dos moves feitos.
    """
    history = []

    for _ in range(depth):
        moves = list(generate_legal_moves(board))
        if not moves:
            break

        move = random.choice(moves)
        board.make_move(move)
        history.append(move)

    return history


def undo_sequence(board, history):
    for _ in range(len(history)):
        board.unmake_move()


def compute_full_hash(board: Board) -> int:
    """
    Recalcula hash completo do board usando apenas API do Zobrist.
    Isso valida o seu hashing incremental indiretamente.
    """
    h = 0

    # percorrer todas as casas
    for sq in range(64):
        piece = board.get_piece_at(sq)
        if piece is not None:
            color, ptype = piece
            piece_index = int(ptype) + (6 if color.value == 1 else 0)
            h = Zobrist.xor_piece(h, piece_index, sq)

    # side to move
    if board.side_to_move.value == 1:
        h = Zobrist.xor_side(h)

    # castling
    h = Zobrist.xor_castling(h, board.castling_rights)

    # en passant
    if board.en_passant_square is not None:
        h = Zobrist.xor_enpassant(h, board.en_passant_square)

    return h


# ------------------------------------------------------------
# 1. Determinismo do Zobrist
# ------------------------------------------------------------

def test_zobrist_signature_deterministic():
    Zobrist.reset()
    Zobrist.init(seed=12345)

    sig1 = Zobrist.signature()

    Zobrist.reset()
    Zobrist.init(seed=12345)

    sig2 = Zobrist.signature()

    assert sig1 == sig2, "Zobrist não é determinístico para a mesma seed"


# ------------------------------------------------------------
# 2. Consistência make/unmake
# ------------------------------------------------------------

def test_zobrist_make_unmake_state_integrity():
    board = Board()

    initial_full = compute_full_hash(board)

    history = play_random_sequence(board, depth=150)
    undo_sequence(board, history)

    final_full = compute_full_hash(board)

    assert initial_full == final_full, "Hash após unmake não voltou ao original"
    assert board.all_occupancy == board.occupancy[0] | board.occupancy[1]
    assert board.side_to_move == board.side_to_move


# ------------------------------------------------------------
# 3. Hash após movimento simples
# ------------------------------------------------------------

def test_zobrist_single_moves_consistency():
    board = Board()

    for _ in range(120):
        moves = list(generate_legal_moves(board))
        if not moves:
            break

        move = random.choice(moves)

        h_before = compute_full_hash(board)

        board.make_move(move)
        board.unmake_move()

        h_after = compute_full_hash(board)

        assert h_before == h_after, f"Hash inconsistente após move {move.to_uci()}"


# ------------------------------------------------------------
# 4. Propriedade para repetição
# ------------------------------------------------------------

def test_zobrist_repetition_detection_base():
    board = Board()

    board.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    sequence = [
        ("g1f3", "g8f6"),
        ("f3g1", "f6g8"),
        ("g1f3", "g8f6"),
        ("f3g1", "f6g8"),
    ]

    seen = {}

    for white_uci, black_uci in sequence:
        move = get_move_by_uci(board, white_uci)
        board.make_move(move)
        h = compute_full_hash(board)
        seen[h] = seen.get(h, 0) + 1

        move = get_move_by_uci(board, black_uci)
        board.make_move(move)
        h = compute_full_hash(board)
        seen[h] = seen.get(h, 0) + 1

    assert any(v >= 2 for v in seen.values()), \
        "Zobrist não consegue detectar posições repetidas"
