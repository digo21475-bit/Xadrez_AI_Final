#!/usr/bin/env python3
"""Teste de todos os modos de jogo sem GUI."""
import asyncio
from game_manager import GameManager, GameMode

async def play_game(mode: GameMode, moves_limit: int = 30) -> int:
    """Joga uma partida e retorna número de movimentos."""
    gm = GameManager.from_mode(mode, engine_depth=1, engine_time_ms=50)
    board = gm.board
    move_count = 0
    
    try:
        for _ in range(moves_limit):
            from core.rules.game_status import get_game_status
            
            # Check game end
            status = get_game_status(board)
            if status.is_checkmate or status.is_stalemate:
                break
            
            agent = gm.white_agent if board.side_to_move == 0 else gm.black_agent
            move = await agent.get_move(board)
            if not move:
                break
            
            board.make_move(move)
            move_count += 1
    except Exception as e:
        print(f"  ERROR: {e}")
        return move_count
    
    return move_count

async def main():
    modes = [
        (GameMode.RANDOM_VS_RANDOM, "Random vs Random"),
        (GameMode.RANDOM_VS_ENGINE, "Random vs Engine"),
        (GameMode.ENGINE_VS_ENGINE, "Engine vs Engine"),
    ]
    
    for mode, name in modes:
        print(f"\n{name}:")
        try:
            moves = await play_game(mode)
            status = "✓ OK" if moves > 5 else "✗ FAIL (too few moves)"
            print(f"  {moves} moves {status}")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
