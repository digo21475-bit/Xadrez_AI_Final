"""Example 4: Human vs Engine (scripted)

Simulates human moves via a predefined move sequence.
Useful for testing the agent system without interactive TUI.

The human "player" is controlled by a script that sends moves in UCI format.

Usage:
    python3 examples/game_mode_human_vs_engine.py

Run against specific positions:
    # Edit HUMAN_MOVES below to test different openings/endgames
"""
import asyncio
from core.board.board import Board
from core.moves.move import Move
from core.moves.tables.attack_tables import square_index
from game_manager import GameManager, GameMode


# Predefined sequence of moves for the "human" player (as UCI strings)
HUMAN_MOVES = [
    "e2e4",
    "e7e5",
    "g1f3",
    "b8c6",
    "f1c4",
    "f8c5",
]


def find_move_by_uci(board, uci: str):
    """Find a Move object matching a UCI string."""
    uci = uci.strip()
    if len(uci) < 4:
        return None
    try:
        from_sq = square_index(uci[0:2])
        to_sq = square_index(uci[2:4])
        promo = uci[4] if len(uci) >= 5 else None

        for m in board.generate_legal_moves():
            if m.from_sq == from_sq and m.to_sq == to_sq:
                if promo and m.promotion:
                    # match promotion type
                    p = m.promotion
                    if promo.lower() in ("q", "r", "b", "n"):
                        return m
                elif not promo:
                    return m
        return None
    except Exception:
        return None


async def main():
    # Create game manager for Human vs Engine
    gm = GameManager.from_mode(
        GameMode.HUMAN_VS_ENGINE,
        engine_depth=3,
        engine_time_ms=500,
    )

    print("=" * 70)
    print("HUMAN VS ENGINE (scripted)")
    print("=" * 70)
    print(f"White: {gm.white_agent.name()}")
    print(f"Black: {gm.black_agent.name()}")
    print()

    move_count = 0
    human_move_idx = 0

    while not gm.game_over and move_count < 50:
        color_name = "White" if gm.board.side_to_move.name == "WHITE" else "Black"
        is_white = gm.board.side_to_move.name == "WHITE"

        if is_white:
            # White is human: use predefined moves
            if human_move_idx >= len(HUMAN_MOVES):
                print(f"{color_name}: out of predefined moves, stopping.")
                break

            uci = HUMAN_MOVES[human_move_idx]
            move = find_move_by_uci(gm.board, uci)
            human_move_idx += 1

            if not move:
                print(f"{color_name}: {uci} is not legal, stopping.")
                gm.game_over = True
                gm.termination_reason = f"Illegal move: {uci}"
                break

            print(f"{move_count + 1}. {move.to_uci()} ({color_name}) [human input]")
        else:
            # Black is engine
            move = await gm.get_next_move()

            if not move:
                gm.game_over = True
                gm.termination_reason = f"{color_name} has no legal move"
                break

            print(f"{move_count + 1}... {move.to_uci()} ({color_name}) [engine]")

        await gm.play_move(move)
        move_count += 1
        gm.check_game_over()

        await asyncio.sleep(0.05)

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
