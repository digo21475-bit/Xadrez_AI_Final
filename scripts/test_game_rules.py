#!/usr/bin/env python3
"""
Script para testar regras do jogo internamente.
Roda um jogo simulado e valida se regras funcionam corretamente.
"""
import sys
sys.path.insert(0, '/home/mike/PycharmProjects/Xadrez_AI_Final')

from core.board.board import Board
from core.moves.legal_movegen import generate_legal_moves
from core.rules.draw_repetition import is_insufficient_material, is_fifty_move_rule
from interface.tui.commands import check_game_status
import random

def play_game(max_moves=500):
    """Simula um jogo, rastreando regras."""
    board = Board()
    move_count = 0
    
    print("=== SIMULAÇÃO DE JOGO ===\n")
    print(f"Posição inicial FEN: {board.to_fen()}\n")
    
    while move_count < max_moves:
        # Gerar movimentos legais
        try:
            legal_moves = list(generate_legal_moves(board))
        except Exception as e:
            print(f"❌ ERRO ao gerar movimentos legais: {e}")
            break
        
        # Verificar regras de término
        status, is_over = check_game_status(board, generate_legal_moves, board.is_in_check)
        
        print(f"\n[Movimento {move_count + 1}] STM: {board.side_to_move} | Movimentos: {len(legal_moves)}")
        print(f"  Status: {status}")
        print(f"  Halfmove clock: {board.halfmove_clock} | Fullmove: {board.fullmove_number}")
        
        # Verificar material insuficiente
        if is_insufficient_material(board):
            print("  ✓ Material insuficiente detectado")
        
        # Verificar regra dos 50 lances
        if is_fifty_move_rule(board):
            print("  ✓ Regra dos 50 lances ativa (contador >= 50)")
        
        if is_over:
            print(f"\n🎯 JOGO TERMINOU: {status}")
            print(f"FEN final: {board.to_fen()}")
            return move_count, True
        
        if not legal_moves:
            print("\n❌ ERRO: Sem movimentos legais mas status não detectou término!")
            print(f"FEN: {board.to_fen()}")
            print(f"In check: {board.is_in_check(board.side_to_move)}")
            return move_count, False
        
        # Fazer movimento aleatório
        move = random.choice(legal_moves)
        try:
            board.make_move(move)
            move_count += 1
        except Exception as e:
            print(f"\n❌ ERRO ao fazer movimento: {e}")
            print(f"Movimento: {move}")
            return move_count, False
        
        # Validar board após movimento
        try:
            board.validate()
        except Exception as e:
            print(f"\n❌ ERRO na validação do board: {e}")
            print(f"FEN: {board.to_fen()}")
            return move_count, False
    
    print(f"\n⚠️  Jogo atingiu limite de {max_moves} movimentos sem terminar!")
    print(f"FEN final: {board.to_fen()}")
    return move_count, False

if __name__ == "__main__":
    moves_played, terminated = play_game(max_moves=5000)
    print(f"\n=== RESUMO ===")
    print(f"Movimentos jogados: {moves_played}")
    print(f"Jogo terminou: {'✓ SIM' if terminated else '❌ NÃO'}")
    sys.exit(0 if terminated else 1)
