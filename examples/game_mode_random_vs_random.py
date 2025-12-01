"""Example 3: Random vs Random

Simple auto-play between two random players.
Useful for stress-testing the board and move generation.

Usage:
    python3 examples/game_mode_random_vs_random.py [max_moves]

Examples:
    python3 examples/game_mode_random_vs_random.py 50
    python3 examples/game_mode_random_vs_random.py 200
"""
import asyncio
import sys
from core.board.board import Board
from game_manager import GameManager, GameMode


async def main():
    max_moves = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    # Create game manager for Random vs Random
    gm = GameManager.from_mode(GameMode.RANDOM_VS_RANDOM)

    print("=" * 70)
    print("RANDOM VS RANDOM")
    print("=" * 70)
    print(f"White: {gm.white_agent.name()}")
    print(f"Black: {gm.black_agent.name()}")
    print(f"Max moves: {max_moves}")
    print()

    move_count = 0
    while not gm.game_over and move_count < max_moves:
        color_name = "White" if gm.board.side_to_move.name == "WHITE" else "Black"

        move = await gm.get_next_move()

        if not move:
            gm.game_over = True
            gm.termination_reason = f"{color_name} has no legal move"
            break

        await gm.play_move(move)
        move_count += 1

        # Print move
        print(f"{move_count:3d}. {move.to_uci():6s} ({color_name:5s})")

        gm.check_game_over()

        await asyncio.sleep(0.01)  # minimal delay

    print()
    print("=" * 70)
    print("GAME OVER")
    print("=" * 70)
    result = gm.get_result()
    print(f"Reason: {result['reason']}")
    print(f"Total moves: {move_count}")
    print(f"Fullmove number: {result['fullmove']}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
