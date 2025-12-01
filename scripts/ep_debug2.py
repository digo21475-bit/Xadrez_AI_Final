# scripts/ep_debug2.py
from core.board.board import Board
from utils.constants import SQUARE_BB

b = Board.from_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPP2PPP/RNBQKBNR b KQkq e3 0 3")

ep = b.en_passant_square
print("EP", ep, "->", SQUARE_BB[ep])

# candidate squares that COULD capture ep (both colors)
cands = []
for d in (-9, -7, 7, 9):
    sq = ep + d
    if 0 <= sq < 64:
        cands.append((d, sq, SQUARE_BB[sq], b.mailbox[sq]))

print("CANDIDATES:")
for d, sq, name, cell in cands:
    print(f"  d={d:>3} sq={sq:2} {name:4} -> {cell}")

# also show which pawns bitboard has set (to cross-check)
from utils.enums import Color, PieceType
pw = b.bitboards[int(Color.WHITE)][int(PieceType.PAWN)]
pb = b.bitboards[int(Color.BLACK)][int(PieceType.PAWN)]
print("WHITE PAWNS (bits):", hex(pw))
print("BLACK PAWNS (bits):", hex(pb))
