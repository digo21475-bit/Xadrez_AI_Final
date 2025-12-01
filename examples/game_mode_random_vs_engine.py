"""Example 1: Random vs Engine

Run a match between a random player and the engine.
Shows per-move logging with move, score, depth, and PV.

Usage:
    python3 examples/game_mode_random_vs_engine.py
"""
import asyncio
from core.board.board import Board
from game_manager import GameManager, GameMode


async def main():
    # Create game manager for Random vs Engine
    gm = GameManager.from_mode(
        GameMode.RANDOM_VS_ENGINE,
        engine_depth=3,
        engine_time_ms=500,
    )

    print("=" * 60)
    print("RANDOM VS ENGINE")
    print("=" * 60)
    print(f"White: {gm.white_agent.name()}")
    print(f"Black: {gm.black_agent.name()}")
    print()

    move_count = 0
    while not gm.game_over and move_count < 100:
        color_name = "White" if gm.board.side_to_move.name == "WHITE" else "Black"
        agent_name = gm.get_agent_for_side(gm.board.side_to_move).name()

        print(f"[Move {move_count + 1}] {color_name} ({agent_name}) thinking...")

        move = await gm.get_next_move()

        if not move:
            gm.game_over = True
            gm.termination_reason = f"{color_name} has no legal move"
            break

        print(f"  → {move.to_uci()}")
        await gm.play_move(move)
        gm.check_game_over()

        move_count += 1
        await asyncio.sleep(0.1)  # small delay for readability

    print()
    print("=" * 60)
    print("GAME OVER")
    print("=" * 60)
    result = gm.get_result()
    print(f"Reason: {result['reason']}")
    print(f"Fullmove: {result['fullmove']}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
