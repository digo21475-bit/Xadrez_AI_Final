"""
Módulo para rastrear histórico de movimentos e motivo do término do jogo.
Sem dependências de Textual ou Rich — apenas lógica pura.

Exporta:
    GameHistory: classe para manter histórico
    format_game_summary: formata resumo para exibição
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MoveRecord:
    """Registro de um movimento jogado."""
    move_number: int  # número do movimento (1-indexed)
    fullmove: int    # número do lance completo (começa em 1)
    side: int        # 0=WHITE, 1=BLACK
    move_uci: str    # notação UCI (ex: "e2e4")
    halfmove_clock: int  # contador de 50 lances


@dataclass
class GameEnd:
    """Informações sobre término do jogo."""
    reason: str  # "Xeque-mate", "Empate por ...", etc
    fullmove: int
    is_checkmate: bool
    is_stalemate: bool
    is_fifty_move: bool
    is_insufficient_material: bool
    is_repetition: bool


class GameHistory:
    """Rastreia histórico de movimentos e fim do jogo."""
    
    __slots__ = ("_moves", "_game_end")
    
    def __init__(self):
        self._moves: List[MoveRecord] = []
        self._game_end: Optional[GameEnd] = None
    
    def add_move(
        self,
        side: int,
        move_uci: str,
        fullmove: int,
        halfmove_clock: int
    ) -> None:
        """Adiciona um movimento ao histórico."""
        move_number = len(self._moves) + 1
        record = MoveRecord(
            move_number=move_number,
            fullmove=fullmove,
            side=side,
            move_uci=move_uci,
            halfmove_clock=halfmove_clock
        )
        self._moves.append(record)
    
    def set_game_end(
        self,
        reason: str,
        fullmove: int,
        is_checkmate: bool = False,
        is_stalemate: bool = False,
        is_fifty_move: bool = False,
        is_insufficient_material: bool = False,
        is_repetition: bool = False
    ) -> None:
        """Define o motivo do término do jogo."""
        self._game_end = GameEnd(
            reason=reason,
            fullmove=fullmove,
            is_checkmate=is_checkmate,
            is_stalemate=is_stalemate,
            is_fifty_move=is_fifty_move,
            is_insufficient_material=is_insufficient_material,
            is_repetition=is_repetition
        )
    
    def pop_move(self) -> Optional[MoveRecord]:
        """Remove e retorna último movimento (para undo)."""
        if self._moves:
            return self._moves.pop()
        return None
    
    def undo_game_end(self) -> None:
        """Limpa término do jogo (para undo após fim)."""
        self._game_end = None
    
    def get_moves(self) -> List[MoveRecord]:
        """Retorna lista de movimentos."""
        return self._moves.copy()
    
    def get_game_end(self) -> Optional[GameEnd]:
        """Retorna info de término ou None."""
        return self._game_end
    
    def clear(self) -> None:
        """Limpa histórico."""
        self._moves.clear()
        self._game_end = None
    
    def count_moves(self) -> int:
        """Total de movimentos jogados."""
        return len(self._moves)


def format_game_summary(history: GameHistory) -> str:
    """
    Formata resumo do jogo em texto simples (sem Rich formatting).
    
    Retorna string com:
      - Tabela de movimentos
      - Motivo do término
    """
    lines = []
    
    moves = history.get_moves()
    end = history.get_game_end()
    
    # Cabeçalho
    lines.append("=" * 70)
    lines.append("HISTÓRICO DO JOGO")
    lines.append("=" * 70)
    lines.append("")
    
    if not moves:
        lines.append("Nenhum movimento jogado.")
        lines.append("")
    else:
        # Tabela de movimentos (2 colunas: white e black)
        lines.append(f"{'Mv':<4} {'Brancas':<20} {'Halfmove':<10} {'Pretas':<20} {'Halfmove':<10}")
        lines.append("-" * 70)
        
        for i in range(0, len(moves), 2):
            white_move = moves[i]
            black_move = moves[i + 1] if i + 1 < len(moves) else None
            
            white_str = f"{white_move.move_uci}"
            white_hm = f"{white_move.halfmove_clock}"
            
            if black_move:
                black_str = f"{black_move.move_uci}"
                black_hm = f"{black_move.halfmove_clock}"
            else:
                black_str = "-"
                black_hm = "-"
            
            mv_num = (i // 2) + 1
            lines.append(f"{mv_num:<4} {white_str:<20} {white_hm:<10} {black_str:<20} {black_hm:<10}")
        
        lines.append("")
    
    # Motivo do término
    lines.append("=" * 70)
    if end:
        lines.append("TÉRMINO DO JOGO")
        lines.append("-" * 70)
        lines.append(f"Razão: {end.reason}")
        lines.append(f"Lance completo: {end.fullmove}")
        
        # Tipo
        if end.is_checkmate:
            lines.append("Tipo: Xeque-mate")
        elif end.is_stalemate:
            lines.append("Tipo: Afogamento (Stalemate)")
        elif end.is_fifty_move:
            lines.append("Tipo: Regra dos 50 lances")
        elif end.is_insufficient_material:
            lines.append("Tipo: Material insuficiente")
        elif end.is_repetition:
            lines.append("Tipo: Repetição de posição")
        else:
            lines.append("Tipo: Não especificado")
        
        lines.append(f"Total de movimentos: {len(moves)}")
    else:
        lines.append("Jogo em andamento ou não foi definido término.")
    
    lines.append("=" * 70)
    lines.append("")
    
    return "\n".join(lines)


def format_game_table(history: GameHistory) -> str:
    """
    Versão compacta: apenas tabela de movimentos (sem motivo).
    Útil para exibição em painel fixo.
    """
    lines = []
    moves = history.get_moves()
    
    if not moves:
        return "(Sem movimentos)"
    
    # Cabeçalho muito compacto
    lines.append(f"{'#':<2} {'W':<7} {'B':<7}")
    lines.append("-" * 17)
    
    for i in range(0, len(moves), 2):
        white = moves[i]
        black = moves[i + 1] if i + 1 < len(moves) else None
        
        mv_num = (i // 2) + 1
        white_str = white.move_uci[:6]  # Truncar se necessário
        black_str = (black.move_uci[:6] if black else "")
        
        lines.append(f"{mv_num:<2} {white_str:<7} {black_str:<7}")
    
    return "\n".join(lines)
