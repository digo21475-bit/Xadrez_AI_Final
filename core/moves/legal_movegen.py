# core/moves/legal_movegen.py
from __future__ import annotations

from core.moves.castling import _gen_castling_moves
from core.moves.movegen import generate_pseudo_legal_moves
from utils.enums import PieceType


# ---------------------------------------------------------------
# Helpers extremamente otimizados
# ---------------------------------------------------------------

def _is_legal_ep(board, move, is_in_check):
    """
    Versão otimizada: reduz lookups, inline local, sem lógica extra.
    """
    stm = board.side_to_move
    board.make_move(move)
    try:
        return not is_in_check(stm)
    finally:
        board.unmake_move()


def generate_legal_moves(board):
    """
    Versão otimizada para velocidade máxima.
    Mantém legalidade 100% consistente com perft.
    """

    # Bind locais (reduz attribute lookup)
    stm = board.side_to_move
    mailbox = board.mailbox
    ep_sq = board.en_passant_square

    is_in_check = board.is_in_check
    make_move = board.make_move
    unmake_move = board.unmake_move

    PT_KING = PieceType.KING
    PT_PAWN = PieceType.PAWN

    # ---------------------------------------------------------------
    # 1. Pseudolegais (já otimizados no gerador)
    # ---------------------------------------------------------------
    pseudo = list(generate_pseudo_legal_moves(board))

    # ---------------------------------------------------------------
    # 2. Roques — minimiza tuplas temporárias
    # ---------------------------------------------------------------
    seen = set()
    add = seen.add

    for m in pseudo:
        add((m.from_sq, m.to_sq, int(m.piece)))

    for c in _gen_castling_moves(board):
        sig = (c.from_sq, c.to_sq, int(c.piece))
        if sig not in seen:
            pseudo.append(c)
            add(sig)

    # ---------------------------------------------------------------
    # 3. Loop de filtragem — crítico de desempenho
    # ---------------------------------------------------------------
    legal = []
    legal_append = legal.append

    for move in pseudo:

        to_sq = move.to_sq

        # -----------------------------------------------------------
        # (A) Captura de rei — checagem imediata, custo mínimo
        # -----------------------------------------------------------
        target = mailbox[to_sq]
        if target is not None:
            # Unpack local reduz overhead
            _, t_piece = target
            if t_piece == PT_KING:
                continue

        # -----------------------------------------------------------
        # (B) EP — caminho raro; evitar branches quando possível
        # -----------------------------------------------------------
        if (
            ep_sq is not None
            and move.piece == PT_PAWN
            and move.is_capture
            and to_sq == ep_sq
        ):
            if not _is_legal_ep(board, move, is_in_check):
                continue

        # -----------------------------------------------------------
        # (C) Teste universal via make/unmake — maior custo
        # -----------------------------------------------------------
        make_move(move)
        try:
            # Verificar se rei próprio fica em cheque
            if not is_in_check(stm):
                legal_append(move)
        finally:
            unmake_move()

    return legal
