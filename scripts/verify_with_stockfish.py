import chess

print("python-chess:", chess.__version__)
print("arquivo:", chess.__file__)
print("classe:", chess.Board)

def perft(board, depth):
    if depth == 0:
        return 1
    total = 0
    for mv in board.legal_moves:
        board.push(mv)
        total += perft(board, depth - 1)
        board.pop()
    return total

tests = [
    ("kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"),
    ("en-passant-basic", "rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2"),
    ("castling-only", "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"),
]

for name, fen in tests:
    b = chess.Board(fen)

    print("\n===", name, "===")
    print("objeto:", b)
    print("classe real:", type(b))

    print("perft(1):", perft(b, 1))
    print("perft(2):", perft(b, 2))
    print(type(b).__module__)

