# scripts/ep_probe_fix.py
from core.board.board import Board
from utils.constants import SQUARE_BB
from utils.enums import Color, PieceType

def coord(sq: int) -> str:
    file = sq % 8
    rank = sq // 8
    return f"{'abcdefgh'[file]}{rank+1}"

b = Board.from_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPP2PPP/RNBQKBNR b KQkq e3 0 3")

print("side_to_move:", b.side_to_move)
ep = b.en_passant_square
print("en_passant:", ep, "coord:", coord(ep) if ep is not None else None)

candidates = [ep - 9, ep - 7, ep + 7, ep + 9] if ep is not None else []
print("candidates indices:", candidates)

for sq in candidates:
    if 0 <= sq < 64:
        cell = b.mailbox[sq]
        print(f"sq={sq:2} coord={coord(sq):3} mailbox={cell}")
    else:
        print(f"sq={sq:2} out_of_board")
