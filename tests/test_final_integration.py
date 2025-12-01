#!/usr/bin/env python3
"""Teste final consolidado: verifica que todos os componentes funcionam."""
import asyncio
import sys

def test_random_agent():
    """Test 1: RandomAgent funciona."""
    from agents.random_agent import RandomAgent
    from core.board.board import Board
    
    async def test():
        agent = RandomAgent()
        board = Board()
        move = await agent.get_move(board)
        assert move is not None, "RandomAgent should return a move"
        return True
    
    try:
        result = asyncio.run(test())
        print("✓ Test 1: RandomAgent works")
        return True
    except Exception as e:
        print(f"✗ Test 1: RandomAgent failed: {e}")
        return False

def test_engine_agent():
    """Test 2: EngineAgent funciona."""
    from agents.engine_agent import EngineAgent
    from core.board.board import Board
    
    async def test():
        agent = EngineAgent(max_time_ms=50, max_depth=1)
        board = Board()
        move = await agent.get_move(board)
        assert move is not None, "EngineAgent should return a move"
        return True
    
    try:
        result = asyncio.run(test())
        print("✓ Test 2: EngineAgent works")
        return True
    except Exception as e:
        print(f"✗ Test 2: EngineAgent failed: {e}")
        return False

def test_random_vs_random():
    """Test 3: Random vs Random plays 20+ moves."""
    from game_manager import GameManager, GameMode
    
    async def test():
        gm = GameManager.from_mode(GameMode.RANDOM_VS_RANDOM)
        board = gm.board
        move_count = 0
        
        for _ in range(50):
            agent = gm.white_agent if board.side_to_move == 0 else gm.black_agent
            move = await agent.get_move(board)
            if not move:
                break
            board.make_move(move)
            move_count += 1
        
        assert move_count > 20, f"Random vs Random should play >20 moves, got {move_count}"
        return move_count
    
    try:
        result = asyncio.run(test())
        print(f"✓ Test 3: Random vs Random ({result} moves)")
        return True
    except Exception as e:
        print(f"✗ Test 3: Random vs Random failed: {e}")
        return False

def test_engine_vs_engine():
    """Test 4: Engine vs Engine plays 5+ moves (quick test)."""
    from game_manager import GameManager, GameMode
    
    async def test():
        gm = GameManager.from_mode(GameMode.ENGINE_VS_ENGINE, engine_depth=1, engine_time_ms=30)
        board = gm.board
        move_count = 0
        
        for _ in range(10):
            agent = gm.white_agent if board.side_to_move == 0 else gm.black_agent
            move = await agent.get_move(board)
            if not move:
                break
            board.make_move(move)
            move_count += 1
        
        assert move_count > 5, f"Engine vs Engine should play >5 moves, got {move_count}"
        return move_count
    
    try:
        result = asyncio.run(test())
        print(f"✓ Test 4: Engine vs Engine ({result} moves)")
        return True
    except Exception as e:
        print(f"✗ Test 4: Engine vs Engine failed: {e}")
        return False

def test_tui_draw_counter():
    """Test 5: TUI draw counter unified (if textual available)."""
    try:
        from interface.tui.renderer import PlayerStatsHeader
        header = PlayerStatsHeader()
        assert hasattr(header, 'draws'), "PlayerStatsHeader should have 'draws' reactive"
        # Try to render it
        output = header.render()
        assert output is not None, "Should be able to render header"
        print("✓ Test 5: TUI draw counter unified")
        return True
    except ModuleNotFoundError:
        print("⊘ Test 5: TUI draw counter (textual not installed, skipped)")
        return True
    except Exception as e:
        print(f"✗ Test 5: TUI draw counter failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("FINAL INTEGRATION TESTS")
    print("="*50 + "\n")
    
    tests = [
        test_random_agent,
        test_engine_agent,
        test_random_vs_random,
        test_engine_vs_engine,
        test_tui_draw_counter,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    status = "ALL PASS ✓" if passed == total else f"PARTIAL ({passed}/{total})"
    print(f"RESULT: {status}")
    print("="*50 + "\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
