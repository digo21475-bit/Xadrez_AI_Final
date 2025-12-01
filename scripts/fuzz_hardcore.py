"""
Fuzz hardcore para Xadrez_AI_Final.

Cobre:
- invariantes profundas
- ataques (_is_square_attacked)
- pseudo vs legal (consistência)
- estabilidade de estado (make/unmake)
- copy()
- from_fen / to_fen
- long random walks

Se qualquer regra estrutural ou lógica estiver quebrada, falhará.
"""

import random
import sys
import traceback

from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.moves.movegen import generate_pseudo_legal_moves
from utils.enums import Color
from utils.enums import PieceType


SEED = 1337
ITERATIONS = 500      # Ajuste conforme necessário
MAX_PLIES = 300        # Caminho aleatório por iteração


# ------------------------------------------------------------
# Logging de falha
# ------------------------------------------------------------

def log_failure(board, history, err):
    print("\n======================= FUZZ FAILURE =======================")
    print("Erro:", err)
    print("\nFEN atual:")
    try:
        print(board.to_fen())
    except:
        print("<board.to_fen() indisponível>")

    print("\nSide to move:", board.side_to_move)
    print("Castling rights:", board.castling_rights)
    print("En-passant:", board.en_passant_square)

    print("\nÚltimos 50 movimentos:")
    for mv in history[-50:]:
        print(mv.to_uci(), end=" ")
    print("\n")

    print("Stacktrace:")
    traceback.print_exc()

    sys.exit(1)


# ------------------------------------------------------------
# Verificações
# ------------------------------------------------------------



def verify_invariants(board: Board):
    # Ocupações coerentes
    assert board.all_occupancy == (board.occupancy[0] | board.occupancy[1])

    # Sem sobreposição entre cores
    assert (board.occupancy[0] & board.occupancy[1]) == 0

    # Mailbox consistente
    mailbox_mask = 0
    for sq, cell in enumerate(board.mailbox):
        if cell is not None:
            mailbox_mask |= (1 << sq)
    assert mailbox_mask == board.all_occupancy

    # Cada cor tem no máximo 1 rei
    for c in (Color.WHITE, Color.BLACK):
        king_bb = board.bitboards[int(c)][int(PieceType.KING)]
        if king_bb:
            assert king_bb.bit_count() == 1



def verify_attacks(board: Board):
    """
    Verifica se o sistema de ataque é consistente.
    NÃO é erro casas atacadas por ambos.
    """

    for sq in range(64):
        w_attacked = board._is_square_attacked(sq, Color.WHITE)
        b_attacked = board._is_square_attacked(sq, Color.BLACK)

        # Nenhuma casa pode estar atacada por uma cor inexistente
        if w_attacked not in (True, False):
            raise RuntimeError(f"Estado inválido ataque branco em {sq}")

        if b_attacked not in (True, False):
            raise RuntimeError(f"Estado inválido ataque preto em {sq}")

    # Apenas log opcional
    both = [
        sq for sq in range(64)
        if board._is_square_attacked(sq, Color.WHITE)
        and board._is_square_attacked(sq, Color.BLACK)
    ]

    if both:
        print(f"[INFO] Casas atacadas por ambos (normal): {both}")


def verify_king_safety(board: Board):
    """
    Garante que ambos os reis não estão simultaneamente em cheque.
    Isso sim seria ilegal.
    """

    white_check = board.is_in_check(Color.WHITE)
    black_check = board.is_in_check(Color.BLACK)

    if white_check and black_check:
        raise RuntimeError("Posição ilegal: ambos os reis em cheque")



def verify_pseudo_vs_legal(board: Board):
    pseudo = list(generate_pseudo_legal_moves(board))
    legal = list(generate_legal_moves(board))
    legal_set = {m.to_uci() for m in legal}

    for mv in pseudo:
        # teste se movimento pseudo é realmente ilegal (por descoberta de cheque)
        board.make_move(mv)
        illegal = board.is_in_check(board.side_to_move ^ 1)
        board.unmake_move()

        if not illegal and mv.to_uci() not in legal_set:
            raise RuntimeError(
                f"Movimento legal não aparece no legal_movegen: {mv.to_uci()}"
            )


def verify_copy(board: Board):
    clone = board.copy()

    assert clone.all_occupancy == board.all_occupancy
    assert clone.castling_rights == board.castling_rights
    assert clone.en_passant_square == board.en_passant_square
    assert clone.side_to_move == board.side_to_move


def verify_fen(board: Board):
    if not hasattr(board, "to_fen"):
        return

    fen = board.to_fen()
    rebuilt = Board.from_fen(fen)

    assert rebuilt.all_occupancy == board.all_occupancy
    assert rebuilt.castling_rights == board.castling_rights
    assert rebuilt.en_passant_square == board.en_passant_square
    assert rebuilt.side_to_move == board.side_to_move


# ------------------------------------------------------------
# Um ciclo de fuzz
# ------------------------------------------------------------

def fuzz_once():
    board = Board()
    history = []

    plies = random.randint(40, MAX_PLIES)

    for _ in range(plies):
        verify_invariants(board)
        verify_attacks(board)
        verify_pseudo_vs_legal(board)
        verify_copy(board)
        verify_fen(board)
        verify_king_safety(board)

        legal_moves = list(generate_legal_moves(board))
        if not legal_moves:
            return  # posição de mate ou stalemate

        mv = random.choice(legal_moves)
        history.append(mv)
        board.make_move(mv)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    random.seed(SEED)

    print("=== FUZZ HARDCORE: Xadrez_AI_Final ===")
    print("SEED:", SEED)
    print("ITERATIONS:", ITERATIONS)
    print("MAX_PLIES:", MAX_PLIES)
    print("------------------------------------------------------------")

    for i in range(ITERATIONS):
        try:
            fuzz_once()
        except Exception as e:
            # capturar o "board" e "history" do escopo local correto
            # (como fuzz_once cria board/history local, vamos recriar uma stack safety)
            # Em caso real, ideal salvar via closures, mas aqui:
            raise

        if i % 50 == 0:
            print(f"OK: {i}/{ITERATIONS} iterações")

    print("✓ Fuzz hardcore concluído sem falhas.")


if __name__ == "__main__":
    main()
