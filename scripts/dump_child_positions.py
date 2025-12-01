# scripts/dump_child_positions.py
from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.moves.move import Move
from core.perft import perft
import sys

ROOT_FEN = "rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2"

def fmt_move(m: Move) -> str:
    return f"{m}"

def main():
    b = Board.from_fen(ROOT_FEN)
    moves = generate_legal_moves(b)
    print("ROOT FEN:", ROOT_FEN)
    print("Root legal moves count:", len(moves))
    print()

    for idx, m in enumerate(moves, start=1):
        print("========")
        print(f"[{idx}/{len(moves)}] ROOT MOVE: {fmt_move(m)}")
        # snapshot root FEN for reference
        try:
            from core.board.board import board_to_fen
        except Exception:
            # fallback: Board should have to_fen or similar; try attributes
            board_to_fen = None

        # Make move, collect child data
        b.make_move(m)

        # Try to get FEN from board (prefer method on Board if available)
        child_fen = None
        if hasattr(b, "to_fen"):
            try:
                child_fen = b.to_fen()
            except Exception:
                child_fen = None
        if child_fen is None and board_to_fen is not None:
            try:
                child_fen = board_to_fen(b)
            except Exception:
                child_fen = None

        # If still None, construct a minimal identifying description
        if child_fen is None:
            child_fen = f"FEN unavailable; side={b.side_to_move} ep={b.en_passant_square}"

        legal = generate_legal_moves(b)
        child_count = len(legal)
        perft1 = perft(b, 1)

        print("CHILD FEN:", child_fen)
        print("child_count (legal moves):", child_count)
        print("perft(child,1):", perft1)
        print("--- legal moves (their repr) ---")
        for lm in legal:
            print(" ", fmt_move(lm))
        print("--- end moves ---")
        print()

        b.unmake_move()

    print("DONE")

if __name__ == '__main__':
    main()
