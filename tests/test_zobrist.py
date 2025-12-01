# tests/test_zobrist.py
from core.hash.zobrist import Zobrist
from utils.enums import Color, PieceType, piece_index


def test_zobrist_is_deterministic():
    Zobrist.init(seed=42)

    snapshot = (
        Zobrist.piece_square.copy(),
        Zobrist.castling.copy(),
        Zobrist.enpassant.copy(),
        Zobrist.side_to_move,
    )

    Zobrist.init(seed=42)

    assert snapshot[0] == Zobrist.piece_square
    assert snapshot[1] == Zobrist.castling
    assert snapshot[2] == Zobrist.enpassant
    assert snapshot[3] == Zobrist.side_to_move


def test_piece_square_uniqueness():
    Zobrist.init(seed=1)

    seen = set()
    for color in Color:
        for piece in PieceType:
            idx = piece_index(piece, color)
            for sq in range(64):
                k = Zobrist.piece_square[idx][sq]
                assert k not in seen
                seen.add(k)


def test_side_key_valid():
    Zobrist.init(seed=999)
    assert isinstance(Zobrist.side_to_move, int)
    assert Zobrist.side_to_move != 0


def test_castling_keys_shape():
    Zobrist.init(seed=999)

    assert len(Zobrist.castling) == 16
    for key in Zobrist.castling:
        assert isinstance(key, int)
        assert key != 0  # heurística mínima de entropia


def test_enpassant_keys_shape():
    Zobrist.init(seed=999)

    assert len(Zobrist.enpassant) == 64

    for i, key in enumerate(Zobrist.enpassant):
        assert isinstance(key, int)
        assert 0 <= i < 64


def test_zobrist_incrementality():
    """
    h ^ Z[p] ^ Z[p] == h (involução do XOR)
    """
    Zobrist.init(seed=7)

    h0 = 0
    idx = piece_index(PieceType.KNIGHT, Color.WHITE)

    h1 = Zobrist.xor_piece(h0, idx, 18)
    h2 = Zobrist.xor_piece(h1, idx, 18)

    assert h2 == h0

def test_zobrist_avalanche():
    Zobrist.init(seed=2025)

    h1 = 0
    h1 = Zobrist.xor_piece(h1, 0, 10)

    h2 = 0
    h2 = Zobrist.xor_piece(h2, 0, 11)

    # Espera-se diferença significativa em bits
    diff = h1 ^ h2
    assert bin(diff).count("1") > 20

def test_castling_toggle_reversibility():
    Zobrist.init(seed=55)

    h = 0
    h = Zobrist.xor_castling(h, 3)
    h = Zobrist.xor_castling(h, 3)

    assert h == 0

def test_enpassant_toggle_reversibility():
    Zobrist.init(seed=77)

    h = 0
    h = Zobrist.xor_enpassant(h, 24)
    h = Zobrist.xor_enpassant(h, 24)

    assert h == 0
