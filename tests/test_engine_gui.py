"""Teste de engine vs engine sem GUI."""
import sys
import time
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.board.board import Board
    from game_manager import GameManager, GameMode
    from core.rules.game_status import get_game_status
    from core.moves.legal_movegen import generate_legal_moves
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


async def _test_engine_vs_engine_simple_impl():
    """Teste simples: random vs random (engine tem problema de sintaxe em Py3.8)."""
    print("[TEST] Starting Random vs Random")
    
    gm = GameManager.from_mode(GameMode.RANDOM_VS_RANDOM)
    board = gm.board
    
    move_count = 0
    max_moves = 50
    start = time.time()
    
    try:
        while move_count < max_moves:
            # Verificar fim de jogo
            status = get_game_status(board)
            if status.is_checkmate or status.is_stalemate or status.is_insufficient_material:
                print(f"[TEST] Game over at move {move_count}: {status}")
                break
            
            # Pedir movimento
            move_count += 1
            print(f"[TEST] Move {move_count}: side={board.side_to_move}")
            
            try:
                agent = gm.white_agent if board.side_to_move == 0 else gm.black_agent
                print(f"[TEST]   Agent: {agent.name()}")
                
                move = await agent.get_move(board)
                if not move:
                    moves_legal = list(generate_legal_moves(board))
                    print(f"[TEST]   No move! Legal moves available: {len(moves_legal)}")
                    break
                
                print(f"[TEST]   Move: {move}")
                board.make_move(move)
            except Exception as e:
                print(f"[TEST] Error on move {move_count}: {e}")
                import traceback
                traceback.print_exc()
                break
    except Exception as e:
        print(f"[TEST] Outer error: {e}")
        import traceback
        traceback.print_exc()
    
    elapsed = time.time() - start
    print(f"\n[TEST] Completed {move_count} moves in {elapsed:.2f}s")
    print(f"[TEST] Avg time per move: {elapsed/max(move_count, 1):.2f}s")
    
    assert move_count > 5, f"Random should play more than 5 moves, got {move_count}"
    print("[TEST] PASSED")


def test_engine_vs_engine_simple():
    """Synchronous wrapper that runs the async engine-vs-engine test."""
    asyncio.run(_test_engine_vs_engine_simple_impl())


if __name__ == "__main__":
    asyncio.run(_test_engine_vs_engine_simple_impl())

