#!/usr/bin/env python3
"""
Script para testar autoplay (play tico teco).
Monitora por que jogo não termina.
"""
import sys
sys.path.insert(0, '/home/mike/PycharmProjects/Xadrez_AI_Final')

from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.rules.draw_repetition import is_insufficient_material, is_fifty_move_rule, fast_draw_status
from interface.tui.commands import check_game_status
import random

def count_pieces(board):
    """Contar peças no board."""
    total = 0
    for color in [0, 1]:
        for piece in range(6):
            total += bin(board.bitboards[color][piece]).count('1')
    return total

def autoplay_game(max_moves=10000):
    """Simula autoplay, monitorando regras de término."""
    board = Board()
    move_count = 0
    
    print("=== AUTOPLAY GAME ===\n")
    print(f"Posição inicial: {board.to_fen()}\n")
    
    while move_count < max_moves:
        # Debug: verificar material insuficiente
        pieces = count_pieces(board)
        
        # Gerar movimentos legais
        try:
            legal_moves = list(generate_legal_moves(board))
        except Exception as e:
            print(f"❌ ERRO ao gerar movimentos: {e}")
            break
        
        # Verificar draw status
        draw_status = fast_draw_status(board)
        status, is_over = check_game_status(board, generate_legal_moves, board.is_in_check)
        
        if move_count % 50 == 0 or move_count < 10:
            print(f"[{move_count}] Peças: {pieces} | Movs: {len(legal_moves)} | Status: {status}")
            print(f"       Halfmove: {board.halfmove_clock} | Draw result: {draw_status}")
            
            if pieces <= 2:
                print(f"       ⚠️  APENAS 2 REIS! Insuf material: {is_insufficient_material(board)}")
        
        if is_over:
            print(f"\n✓ JOGO TERMINOU: {status}")
            print(f"  FEN: {board.to_fen()}")
            print(f"  Peças: {pieces}")
            return move_count, True
        
        if not legal_moves:
            in_check = board.is_in_check(board.side_to_move)
            print(f"\n❌ Sem movimentos legais mas status não detectou! In check: {in_check}")
            return move_count, False
        
        # Fazer movimento aleatório
        move = random.choice(legal_moves)
        try:
            board.make_move(move)
            move_count += 1
        except Exception as e:
            print(f"\n❌ ERRO ao fazer movimento: {e}")
            return move_count, False
    
    print(f"\n⚠️  Atingiu limite de {max_moves} movimentos!")
    print(f"  FEN: {board.to_fen()}")
    print(f"  Peças: {count_pieces(board)}")
    return move_count, False

if __name__ == "__main__":
    moves, ended = autoplay_game(max_moves=10000)
    print(f"\n=== RESULTADO ===")
    print(f"Movimentos: {moves}")
    print(f"Terminou: {'✓' if ended else '❌'}")
    sys.exit(0 if ended else 1)
