"""Top-level evaluation wrapper for simple material + mobility evaluator.

"""
from .eval.evaluator import evaluate as _evaluate


def evaluate(board: object) -> int:
    """Evaluate board position in centipawns from White's perspective.
    
    Args:
        board: Chess board object with mailbox and legal move generation
    
    Returns:
        Evaluation in centipawns (positive = White better, negative = Black better)
    """
    return int(_evaluate(board))
