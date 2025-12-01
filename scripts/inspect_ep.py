# scripts/inspect_ep.py
from core.board.board import Board
from core.moves.movegen import generate_pseudo_legal_moves
from core.moves.legal_movegen import generate_legal_moves

b = Board.from_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPP2PPP/RNBQKBNR b KQkq e3 0 3")
print("en_passant:", b.en_passant_square)

pseudo = list(generate_pseudo_legal_moves(b))
legal = list(generate_legal_moves(b))

pseudo_ep = [m for m in pseudo if m.piece == 0 and m.is_capture and m.to_sq == b.en_passant_square]
legal_ep = [m for m in legal if m.piece == 0 and m.is_capture and m.to_sq == b.en_passant_square]

print("PSEUDO TOTAL", len(pseudo))
print("PSEUDO EP", pseudo_ep)
print("LEGAL TOTAL", len(legal))
print("LEGAL EP", legal_ep)


from core.moves.legal_movegen import generate_legal_moves


# Teste 1: En Passant
print("="*60)
print("TESTE 1: EN PASSANT")
print("="*60)
fen = 'rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPP2PPP/RNBQKBNR b KQkq e3 0 3'
b = Board.from_fen(fen)
moves = list(generate_legal_moves(b))
print(f"FEN: {fen}")
print(f"Total movimentos: {len(moves)} (esperado 29, faltam {29-len(moves)})")
print("\nMovimentos listados:")
for i, m in enumerate(moves, 1):
    print(f"  {i:2d}. {m}")

# Teste 2: Verificar se en passant está lá
print("\n" + "="*60)
print("BUSCANDO EN PASSANT...")
print("="*60)
ep_moves = [str(m) for m in moves if 'e' in str(m).lower() and 'd' in str(m).lower()]
print(f"Movimentos com 'e' e 'd': {ep_moves}")
print("Esperado: movimento como 'exd3' ou similar\n")

# Teste 3: Middlegame
print("="*60)
print("TESTE 2: MIDDLEGAME")
print("="*60)
fen2 = 'r4rk1/1pp1qppp/p1n2n2/3p4/3P4/2N1PN2/PPP2PPP/R1BQR1K1 w - - 0 1'
b2 = Board.from_fen(fen2)
moves2 = list(generate_legal_moves(b2))
print(f"FEN: {fen2}")
print(f"Total movimentos: {len(moves2)} (esperado 33, faltam {33-len(moves2)})")
print("\nMovimentos listados:")
for i, m in enumerate(moves2, 1):
    print(f"  {i:2d}. {m}")