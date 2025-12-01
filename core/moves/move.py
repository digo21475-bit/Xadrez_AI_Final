# core/moves/move.py
from __future__ import annotations

from dataclasses import dataclass
from utils.enums import PieceType

# Tabelas UCI usadas por todos os movimentos
FILES = "abcdefgh"
RANKS = "12345678"

PROMOTION_UCI = {
    PieceType.QUEEN:  "q",
    PieceType.ROOK:   "r",
    PieceType.BISHOP: "b",
    PieceType.KNIGHT: "n",
}


@dataclass(frozen=True)
class Move:
    """
    Representação simples de um movimento para GUI, debug e conversão UCI.

    Observações:
        - O engine e o core usam movimentos inteiros (move_int).
        - Esta classe é apenas uma interface mais amigável ao humano.
        - Pode ser estendida futuramente com:
            move_type, flags, score, san, annotations, etc.

    Campos:
        from_sq: origem (0..63)
        to_sq  : destino (0..63)
        piece  : tipo da peça que realizou o movimento
        is_capture: booleano auxiliar para GUI/depuração (não impacta engine)
        promotion: tipo de peça promovida (ou None)
    """
    from_sq: int
    to_sq: int
    piece: PieceType
    is_capture: bool = False
    promotion: PieceType | None = None

    def to_uci(self) -> str:
        """Converte o movimento para notação UCI, ex: e2e4, e7e8q."""
        f = FILES[self.from_sq & 7] + RANKS[self.from_sq >> 3]
        t = FILES[self.to_sq & 7]   + RANKS[self.to_sq >> 3]

        if self.promotion:
            return f + t + PROMOTION_UCI[self.promotion]
        return f + t
