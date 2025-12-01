PIECE_VALUE = {
    'PAWN': 100,
    'KNIGHT': 320,
    'BISHOP': 330,
    'ROOK': 500,
    'QUEEN': 900,
    'KING': 10000,
}


def score_capture(move) -> int:
    """Return higher score for captures: victim value * 1000 - attacker value.

    Move object is expected to expose `captured` with piece name or None,
    and `piece` as attacker piece name; if missing, return 0.
    """
    try:
        victim = move.captured
        attacker = move.piece
        v = PIECE_VALUE.get(str(victim).upper(), 0) if victim is not None else 0
        a = PIECE_VALUE.get(str(attacker).upper(), 0) if attacker is not None else 0
        return v * 1000 - a
    except Exception:
        return 0
