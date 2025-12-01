"""Example 2: Engine vs Engine

Run a match between two engine instances at different search depths.
Logs all moves and terminates on checkmate/draw.

Usage:
    python3 examples/game_mode_engine_vs_engine.py [depth] [time_ms] [max_moves]
    
Examples:
    python3 examples/game_mode_engine_vs_engine.py 3 500 50
    python3 examples/game_mode_engine_vs_engine.py 4 1000 100
"""
import asyncio
import sys
from core.board.board import Board
from game_manager import GameManager, GameMode


async def main():
    # Parse arguments
    depth = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    time_ms = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    max_moves = int(sys.argv[3]) if len(sys.argv) > 3 else 50

    # Create game manager for Engine vs Engine
    gm = GameManager.from_mode(
        GameMode.ENGINE_VS_ENGINE,
        engine_depth=depth,
        engine_time_ms=time_ms,
    )

    print("=" * 70)
    print("ENGINE VS ENGINE")
    print("=" * 70)
    print(f"White: {gm.white_agent.name()}")
    print(f"Black: {gm.black_agent.name()}")
    print(f"Max moves: {max_moves}")
    print()

    move_count = 0
    while not gm.game_over and move_count < max_moves:
        color_name = "White" if gm.board.side_to_move.name == "WHITE" else "Black"

        # Get move from current agent
        move = await gm.get_next_move()

        if not move:
            gm.game_over = True
            gm.termination_reason = f"{color_name} has no legal move"
            break

        # Play move
        await gm.play_move(move)
        move_count += 1

        # Print move info
        print(f"{move_count:3d}. {move.to_uci():6s} ({color_name:5s}) | FEN: {gm.board.to_fen()[:50]}...")

        # Check if game is over
        gm.check_game_over()

        await asyncio.sleep(0.05)  # small delay for output readability

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
