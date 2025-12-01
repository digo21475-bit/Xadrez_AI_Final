# scripts/debug_perft_ep.py
from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.perft import perft
import pprint
import sys

FEN = "rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2"

def snapshot(board):
    return {
        "mailbox": list(board.mailbox),
        "bitboards": [list(board.bitboards[0]), list(board.bitboards[1])],
        "occupancy": [int(board.occupancy[0]), int(board.occupancy[1])],
        "all_occupancy": int(board.all_occupancy),
        "en_passant": None if board.en_passant_square is None else int(board.en_passant_square),
        "castling": int(board.castling_rights),
        "halfmove": int(board.halfmove_clock),
        "fullmove": int(board.fullmove_number),
        "side": board.side_to_move,
    }

def equal_snap(a, b):
    # simple deep-equality for our snapshot shape
    return a == b

def main():
    b = Board.from_fen(FEN)
    print("Initial en_passant:", b.en_passant_square)
    moves = list(generate_legal_moves(b))
    print("Total legal moves:", len(moves))
    print()

    # Baseline perft on root for reference
    baseline_perft2 = perft(b, 2)
    print("Baseline perft(2):", baseline_perft2)
    print()

    problematic = []

    for i, m in enumerate(moves):
        print(f"[{i+1}/{len(moves)}] Move: {m}")
        root_snap = snapshot(b)

        # compute perft after making the move: number of child nodes (perft depth=1 from child)
        try:
            b.make_move(m)
        except Exception as e:
            print("  make_move raised:", e)
            problematic.append((m, "make_error", str(e)))
            # try to recover by restoring if possible
            try:
                b.unmake_move()
            except Exception:
                print("  failed to unmake after make error; abort")
                sys.exit(1)
            continue

        child_count = list(generate_legal_moves(b))
        # perft child nodes count via perft(b,1) is same as child_count
        # but compute perft(b,1) anyway
        perft1_from_child = perft(b, 1)

        child_snap = snapshot(b)

        try:
            b.unmake_move()
        except Exception as e:
            print("  unmake_move raised:", e)
            problematic.append((m, "unmake_error", str(e)))
            print("  abandoning script (board may be inconsistent).")
            sys.exit(1)

        restored_snap = snapshot(b)

        snaps_equal = equal_snap(root_snap, restored_snap)

        # Print details
        print("  child_count (legal moves after make):", child_count)
        print("  perft(child,1):", perft1_from_child)
        print("  snapshot equal after unmake:", snaps_equal)

        if not snaps_equal:
            # compute diffs (naive)
            diffs = {}
            for k in root_snap:
                if root_snap[k] != restored_snap[k]:
                    diffs[k] = {"before": root_snap[k], "after": restored_snap[k]}
            print("  SNAPSHOT DIFFS:")
            pprint.pprint(diffs, width=120)
            problematic.append((m, "snapshot_mismatch", diffs))

        # specifically flag en-passant related moves or changes
        if root_snap["en_passant"] is not None or restored_snap["en_passant"] is not None:
            if root_snap["en_passant"] != restored_snap["en_passant"]:
                print("  en_passant changed: before -> after:", root_snap["en_passant"], "->", restored_snap["en_passant"])
                problematic.append((m, "en_passant_changed", (root_snap["en_passant"], restored_snap["en_passant"])))

        print()

    print("=== SUMMARY ===")
    print("Total moves inspected:", len(moves))
    print("Problematic entries:", len(problematic))
    for entry in problematic:
        print("-", entry[0], "| reason:", entry[1])
    print()
    print("If problematic entries are non-empty, paste their printed diffs here for further analysis.")

if __name__ == "__main__":
    main()
