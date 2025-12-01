# tico.py
# Random move generator for testing in CLI

import random
from core.moves.legal_movegen import generate_legal_moves

def choose_move(board):
    """Return a random legal move for the current board state."""
    moves = list(generate_legal_moves(board))
    if not moves:
        return None
    return random.choice(moves)
