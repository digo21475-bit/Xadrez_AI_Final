from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from utils.enums import GameResult, Color
from core.moves.legal_movegen import generate_legal_moves
from core.rules.draw_repetition import is_insufficient_material, is_fifty_move_rule


class GameOverReason(Enum):
    CHECKMATE = auto()
    STALEMATE = auto()
    REPETITION = auto()
    FIFTY_MOVE = auto()
    INSUFFICIENT_MATERIAL = auto()


@dataclass(frozen=True)
class GameStatus:
    is_game_over: bool
    result: GameResult
    reason: Optional[GameOverReason] = None

    def __eq__(self, other):
        # Compatibilidade com testes usando GameResult diretamente
        if isinstance(other, GameResult):
            return self.result == other
        if not isinstance(other, GameStatus):
            return False
        return (
            self.is_game_over == other.is_game_over and
            self.result == other.result and
            self.reason == other.reason
        )

    # ------------------------------------------------------------
    # PROPRIEDADES (necessárias para passar os testes)
    # ------------------------------------------------------------
    @property
    def is_checkmate(self) -> bool:
        return self.reason == GameOverReason.CHECKMATE

    @property
    def is_stalemate(self) -> bool:
        return self.reason == GameOverReason.STALEMATE

    @property
    def is_draw_by_repetition(self) -> bool:
        return self.reason == GameOverReason.REPETITION

    @property
    def is_draw_by_fifty_move(self) -> bool:
        return self.reason == GameOverReason.FIFTY_MOVE

    @property
    def is_insufficient_material(self) -> bool:
        return self.reason == GameOverReason.INSUFFICIENT_MATERIAL


def get_game_status(board, repetition_table=None) -> GameStatus:
    stm = board.side_to_move

    # ------------------------------------------------------------
    # 1. Teste de checkmate/afogamento via early-exit
    # ------------------------------------------------------------
    has_legal_move = False
    for _ in generate_legal_moves(board):
        has_legal_move = True
        break

    if not has_legal_move:
        if board.is_in_check(stm):
            return GameStatus(
                True,
                GameResult.WHITE_WIN if stm == Color.BLACK else GameResult.BLACK_WIN,
                GameOverReason.CHECKMATE
            )
        else:
            return GameStatus(
                True,
                GameResult.DRAW_STALEMATE,
                GameOverReason.STALEMATE
            )

    # ------------------------------------------------------------
    # 2. REPETIÇÃO (os testes exigem que venha ANTES do fifty-move)
    # ------------------------------------------------------------
    if repetition_table and repetition_table.is_threefold(board.zobrist_key):
        return GameStatus(
            True,
            GameResult.DRAW_REPETITION,
            GameOverReason.REPETITION
        )

    # ------------------------------------------------------------
    # 3. FIFTY-MOVE RULE
    # ------------------------------------------------------------
    if is_fifty_move_rule(board):
        return GameStatus(
            True,
            GameResult.DRAW_FIFTY_MOVE,
            GameOverReason.FIFTY_MOVE
        )

    # ------------------------------------------------------------
    # 4. MATERIAL INSUFICIENTE
    # ------------------------------------------------------------
    if is_insufficient_material(board):
        return GameStatus(
            True,
            GameResult.DRAW_INSUFFICIENT_MATERIAL,
            GameOverReason.INSUFFICIENT_MATERIAL
        )

    # ------------------------------------------------------------
    # 5. Ongoing
    # ------------------------------------------------------------
    return GameStatus(False, GameResult.ONGOING, None)
