"""
Módulo de comandos para a TUI do Xadrez_AI_Final.

Funções exportadas:
    parse_command(cmd: str) -> (name, args)
    is_move_format(s: str) -> bool
    format_status(board) -> str
    find_move(board, lan: str, generate_legal_moves) -> Move|None
    check_game_status(board, generate_legal_moves, is_in_check) -> (msg, ended)
"""

from __future__ import annotations

__all__ = [
    "parse_command",
    "is_move_format",
    "format_status",
    "find_move",
    "check_game_status",
]

# ------------------------------------------------------------
# Imports necessários para detecção de empate
# ------------------------------------------------------------

try:
    from core.rules.draw_repetition import fast_draw_status, DrawResult
except Exception:
    # fallback mínimo para desenvolvimento
    class DrawResult:
        NONE = 0
        REPETITION = 1
        FIFTY = 2
        INSUFFICIENT = 3

    def fast_draw_status(board):
        return DrawResult.NONE


# ------------------------------------------------------------
# Parsing de comandos
# ------------------------------------------------------------

def parse_command(cmd: str):
    """Divide a string em comando + argumentos."""
    if not cmd:
        return "", []
    parts = cmd.strip().split()
    return parts[0].lower(), parts[1:]


# ------------------------------------------------------------
# Detecção de formato LAN
# ------------------------------------------------------------

def is_move_format(s: str) -> bool:
    """Detecta strings como e2e4, e7e8q etc."""
    if len(s) not in (4, 5):
        return False
    f1, r1, f2, r2 = s[0], s[1], s[2], s[3]
    return (
        f1 in "abcdefgh"
        and f2 in "abcdefgh"
        and r1 in "12345678"
        and r2 in "12345678"
    )


# ------------------------------------------------------------
# Formatação de status (para painel)
# ------------------------------------------------------------

def format_status(board) -> str:
    stm = getattr(board, "side_to_move", "?")
    half = getattr(board, "halfmove_clock", "?")
    try:
        zob = hex(board.zobrist_key)
    except Exception:
        zob = "?"
    return f"STM: {stm} | halfmove: {half} | zobrist: {zob}"


# ------------------------------------------------------------
# Busca de movimento
# ------------------------------------------------------------

def find_move(board, lan: str, generate_legal_moves):
    """
    Tenta encontrar o movimento correspondente a 'lan' dentro dos legais.
    Usa parse_move se existir, senão compara UCI / str(m).
    """
    # Tenta parse_move do próprio board
    if hasattr(board, "parse_move"):
        try:
            mv = board.parse_move(lan)
            if mv is not None:
                return mv
        except Exception:
            pass

    # Busca manual entre os legais
    try:
        for m in generate_legal_moves(board):
            uci = (m.to_uci() if hasattr(m, "to_uci") else str(m)).lower()
            if uci == lan.lower() or uci.startswith(lan.lower()):
                return m
    except Exception:
        pass

    return None


# ------------------------------------------------------------
# Verificação de término do jogo
# ------------------------------------------------------------

def check_game_status(board, generate_legal_moves, is_in_check):
    """
    Retorna:
        msg (str), ended (bool)

    Verifica na ordem:
      1. empates rápidos (repetição / 50 lances / material)
      2. ausência de movimentos legais → mate ou stalemate
    """

    # 1. Empates detectados pelo módulo rápido (draw_repetition)
    try:
        draw = fast_draw_status(board)
    except Exception:
        draw = DrawResult.NONE

    if draw != DrawResult.NONE:
        if draw == DrawResult.REPETITION:
            return "Empate por repetição de posição.", True
        if draw == DrawResult.FIFTY_MOVE:
            return "Empate pela regra dos 50 lances.", True
        if draw == DrawResult.INSUFFICIENT_MATERIAL:
            return "Empate por material insuficiente.", True

    # 2. Verificar lista de movimentos
    try:
        legal = list(generate_legal_moves(board))
    except Exception:
        return "Erro ao gerar movimentos legais", False

    if legal:
        return "Em andamento", False

    # 3. Sem movimentos → mate ou stalemate
    stm = board.side_to_move
    try:
        in_check = is_in_check(stm)
    except Exception:
        in_check = False

    if in_check:
        return "Xeque-mate! Jogo terminado.", True
    else:
        return "Empate por afogamento (stalemate).", True
