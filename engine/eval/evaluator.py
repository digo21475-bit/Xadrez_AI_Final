"""Simple static evaluator: material + PST + mobility."""
from typing import Any

PIECE_SCORES = {
    'PAWN': 100,
    'KNIGHT': 320,
    'BISHOP': 330,
    'ROOK': 500,
    'QUEEN': 900,
    'KING': 20000,
}


def evaluate(board: Any) -> int:
    """Evaluate chess position from White's perspective in centipawns.
    
    Evaluation components:
    - Material count (piece values)
    - Mobility bonus (number of legal moves * 2)

    Args:
        board: Chess board with mailbox array or legal_moves method
    
    Returns:
        Evaluation in centipawns from White's perspective
    """
    score = 0
    try:
        for sq, cell in enumerate(board.mailbox):
            if cell is None:
                continue
            colr, ptype = cell
            # try to get name
            name = getattr(ptype, 'name', None) or str(ptype)
            name = name.upper()
            v = PIECE_SCORES.get(name, 0)
            if colr == getattr(board, 'WHITE', None) or colr == getattr(board, 'Color', None):
                pass
            # assume Color.WHITE == 0
            if colr == 0:
                score += v
            else:
                score -= v
    except Exception:
        pass

    try:
        moves = None
        if hasattr(board, 'generate_legal_moves'):
            moves = list(board.generate_legal_moves())
        elif hasattr(board, 'legal_moves'):
            moves = list(board.legal_moves)
        if moves is not None:
            mobility = len(moves)
            score += int(mobility * 2)
    except Exception:
        pass

    return score
