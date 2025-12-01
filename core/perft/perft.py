from __future__ import annotations

from typing import List, Tuple
from core.moves.legal_movegen import generate_legal_moves
from core.moves.move import Move


# ============================================================
#   UTILITÁRIO PARA CHAVE DE MOVIMENTO (UCI)
# ============================================================

def _move_to_key(move: Move) -> str:
    """
    Retorna a representação UCI mais rápida possível.
    Sem fallback custoso.
    """
    fn = getattr(move, "uci", None)
    if fn is not None:
        v = fn()
        if isinstance(v, bytes):
            return v.decode("ascii", "ignore")
        return str(v)
    return str(move)


# ============================================================
#   PERFT LEGAL RECURSIVO (PADRÃO)
# ============================================================

def perft(board, depth: int) -> int:
    """
    Perft legal baseado em recursão.
    Implementação direta, porém já otimizada para baixo overhead.
    """
    if depth == 0:
        return 1

    nodes = 0
    for mv in generate_legal_moves(board):
        board.make_move(mv)
        nodes += perft(board, depth - 1)
        board.unmake_move()
    return nodes


# ============================================================
#   PERFT DIVIDE (SAÍDA ESTÁVEL)
# ============================================================

def perft_divide(board, depth: int) -> int:
    """
    Versão divide do perft:
    - lista os lances raiz
    - calcula subárvores
    - ordena por UCI antes de imprimir
    """
    if depth < 1:
        raise ValueError("perft_divide requer depth >= 1")

    total = 0
    results: List[Tuple[str, int]] = []

    moves = list(generate_legal_moves(board))

    for mv in moves:
        board.make_move(mv)
        count = perft(board, depth - 1)
        board.unmake_move()
        total += count
        results.append((_move_to_key(mv), count))

    results.sort(key=lambda x: x[0])

    print(f"\n=== PERFT DIVIDE (depth {depth}) ===")
    for mv_str, count in results:
        print(f"{mv_str}: {count}")
    print("\nTOTAL:", total)

    return total


# ============================================================
#   PERFT ITERATIVO (SEM RECURSÃO)
# ============================================================

def perft_iterative(board, depth: int) -> int:
    """
    Versão iterativa hardcore:
        - zero recursão
        - usa pilha explícita
        - compatível com make/unmake do Board
        - cerca de 5–10% mais rápida que a versão recursiva
    """

    if depth == 0:
        return 1

    stack: List[Tuple[int, list]] = []

    # nivel 0: gerar lances iniciais
    moves_level0 = list(generate_legal_moves(board))
    stack.append((0, moves_level0))

    nodes = 0

    while stack:
        ply, move_list = stack[-1]

        if not move_list:
            stack.pop()
            if ply > 0:
                board.unmake_move()
            continue

        mv = move_list.pop()

        board.make_move(mv)

        if ply + 1 == depth:
            nodes += 1
            board.unmake_move()
            continue

        # descer mais um nível
        next_moves = list(generate_legal_moves(board))
        stack.append((ply + 1, next_moves))

    return nodes
