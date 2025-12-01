# core/rules/draw_repetition.py

from enum import Enum
from utils.enums import Color, PieceType


# ============================================================
# Helper: bit count para Python 3.8+ compatibility
# ============================================================

def _bit_count(x: int) -> int:
    """Count set bits in integer (Python 3.8 compatible fallback)."""
    try:
        return x.bit_count()  # Python 3.10+
    except AttributeError:
        return bin(x).count('1')  # Python 3.8/3.9


# ============================================================
# ENUM MAIS RÁPIDO (valores fixos)
# ============================================================

class DrawResult(Enum):
    NONE = 0
    REPETITION = 1
    FIFTY_MOVE = 2
    INSUFFICIENT_MATERIAL = 3


# ============================================================
# REPETITION TABLE — COMPATIBILIDADE COM TESTS
# ============================================================

class RepetitionTable:
    """Tabela simples usada nos testes. Mantém contagem global."""
    __slots__ = ("_count", "_stack")

    def __init__(self):
        self._count = {}
        self._stack = []

    def push(self, zobrist_key: int):
        self._stack.append(zobrist_key)
        self._count[zobrist_key] = self._count.get(zobrist_key, 0) + 1

    def pop(self):
        key = self._stack.pop()
        cnt = self._count[key] - 1
        if cnt <= 0:
            del self._count[key]
        else:
            self._count[key] = cnt

    def is_threefold(self, zobrist_key: int) -> bool:
        return self._count.get(zobrist_key, 0) >= 3


# ============================================================
# FAST REPETITION — PARA A ENGINE
# ============================================================

class FastRepetition:
    """
    Controle otimizado de repetição para engines:

    - frames = lista de dicionários
    - push_irreversible → cria novo frame
    - push_reversible   → incrementa dentro do frame atual
    """

    __slots__ = ("_frames",)

    def __init__(self):
        self._frames = [{}]  # frame base

    def push_reversible(self, zobrist_key: int):
        frame = self._frames[-1]
        frame[zobrist_key] = frame.get(zobrist_key, 0) + 1

    def push_irreversible(self, zobrist_key: int):
        self._frames.append({zobrist_key: 1})

    def pop(self):
        if len(self._frames) > 1:
            self._frames.pop()

    def is_threefold(self, zobrist_key: int) -> bool:
        return self._frames[-1].get(zobrist_key, 0) >= 3


# ============================================================
# MATERIAL INSUFICIENTE — ULTRA OTIMIZADO
# ============================================================

def _square_color(sq: int) -> int:
    return ((sq >> 3) + (sq & 7)) & 1


def _single_piece_square(bb: int) -> int:
    return (bb & -bb).bit_length() - 1


def _is_insufficient_material_fast(board) -> bool:
    wbb = board.bitboards[int(Color.WHITE)]
    bbb = board.bitboards[int(Color.BLACK)]

    # Contagem total por cor
    wcnt = (
        _bit_count(wbb[0]) +
        _bit_count(wbb[1]) +
        _bit_count(wbb[2]) +
        _bit_count(wbb[3]) +
        _bit_count(wbb[4]) +
        _bit_count(wbb[5])
    )
    bcnt = (
        _bit_count(bbb[0]) +
        _bit_count(bbb[1]) +
        _bit_count(bbb[2]) +
        _bit_count(bbb[3]) +
        _bit_count(bbb[4]) +
        _bit_count(bbb[5])
    )

    # K vs K
    if wcnt == 1 and bcnt == 1:
        return True

    # K vs K+B / K+N (lado preto)
    if wcnt == 1 and bcnt == 2:
        if _bit_count(bbb[int(PieceType.BISHOP)]) == 1:
            return True
        if _bit_count(bbb[int(PieceType.KNIGHT)]) == 1:
            return True

    # K vs K+B / K+N (lado branco)
    if bcnt == 1 and wcnt == 2:
        if _bit_count(wbb[int(PieceType.BISHOP)]) == 1:
            return True
        if _bit_count(wbb[int(PieceType.KNIGHT)]) == 1:
            return True

    # K+B vs K+B (mesma cor)
    if wcnt == 2 and bcnt == 2:
        if (
            _bit_count(wbb[int(PieceType.BISHOP)]) == 1 and
            _bit_count(bbb[int(PieceType.BISHOP)]) == 1
        ):
            wb = _single_piece_square(wbb[int(PieceType.BISHOP)])
            bb = _single_piece_square(bbb[int(PieceType.BISHOP)])
            if _square_color(wb) == _square_color(bb):
                return True

    # K+N vs K+N
    if wcnt == 2 and bcnt == 2:
        if (
            _bit_count(wbb[int(PieceType.KNIGHT)]) == 1 and
            _bit_count(bbb[int(PieceType.KNIGHT)]) == 1
        ):
            return True

    return False


# ============================================================
# FIFTY MOVES — O MAIS BARATO POSSÍVEL
# ============================================================

def _fifty_move_fast(board) -> bool:
    return board.halfmove_clock >= 100


# ============================================================
# FUNÇÃO ÚNICA PARA A ENGINE
# ============================================================

def fast_draw_status(board, repetition_table: FastRepetition = None) -> DrawResult:
    """
    Ordem conforme o test-suite:
        1) REPETITION
        2) FIFTY_MOVE
        3) INSUFFICIENT_MATERIAL
    """

    z = board.zobrist_key

    # 1. Repetição
    if repetition_table is not None:
        if repetition_table.is_threefold(z):
            return DrawResult.REPETITION

    # 2. 50 lances
    if board.halfmove_clock >= 100:
        return DrawResult.FIFTY_MOVE

    # 3. Material insuficiente
    if _is_insufficient_material_fast(board):
        return DrawResult.INSUFFICIENT_MATERIAL

    return DrawResult.NONE


# ============================================================
# EXPORTS DE COMPATIBILIDADE — NÃO REMOVER
# ============================================================

def is_insufficient_material(board) -> bool:
    return _is_insufficient_material_fast(board)


def is_fifty_move_rule(board) -> bool:
    return _fifty_move_fast(board)
