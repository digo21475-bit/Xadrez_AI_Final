"""Alpha-beta pruning search with quiescence and transposition tables.

This module provides the core alpha-beta search algorithm with:
- Transposition table lookups and stores
- Quiescence search for tactical positions
- Move ordering (TT moves, captures, killers, history)
- Draw detection (50-move rule, insufficient material, stalemate)
"""
from typing import Any, Optional
from engine.tt.transposition import TranspositionTable, EXACT, LOWERBOUND, UPPERBOUND
from engine.utils.constants import MATE_SCORE
from engine.eval.evaluator import evaluate
from engine.search.move_picker import MovePicker
from engine.ordering.killers import Killers
from engine.ordering.history_table import HistoryTable
from core.moves.legal_movegen import generate_legal_moves as core_generate_legal_moves
from core.rules.game_status import get_game_status
from utils.enums import Color


class SearchState:
    """Maintains state during a search: transposition table, killers, history, nodes."""
    def __init__(self):
        self.tt = TranspositionTable()
        self.nodes = 0
        self.killers = Killers()
        self.history = HistoryTable()


def _get_legal_moves(board: Any) -> list:
    """Helper: get legal moves, trying board method first, then core function."""
    try:
        if hasattr(board, 'generate_legal_moves'):
            return list(board.generate_legal_moves())
        else:
            return list(core_generate_legal_moves(board))
    except Exception:
        return []


def quiescence(board: Any, alpha: int, beta: int, state: SearchState, ply: int) -> int:
    """Quiescence search for tactical positions: only looks at captures.
    
    Args:
        board: Chess position
        alpha: Best score for maximizing player
        beta: Best score for minimizing player
        state: SearchState with TT, killers, history
        ply: Current search depth
    
    Returns:
        Evaluation score
    """
    state.nodes += 1
    
    # Stand-pat: position is good enough to not search captures
    stand = evaluate(board)
    if stand >= beta:
        return stand
    if alpha < stand:
        alpha = stand

    # Generate only captures
    moves_all = _get_legal_moves(board)
    moves = [m for m in moves_all if getattr(m, 'is_capture', False)]

    # Order captures by MVV-LVA
    mp = MovePicker(board, moves, ply=ply, killers=state.killers, history=state.history)

    while True:
        m = mp.next()
        if m is None:
            break
        try:
            board.make_move(m)
        except Exception:
            continue
        
        score = -quiescence(board, -beta, -alpha, state, ply + 1)
        board.unmake_move()

        if score >= beta:
            return score
        if score > alpha:
            alpha = score

    return alpha


def alpha_beta(board: Any, depth: int, alpha: int, beta: int, state: SearchState, ply: int = 0) -> int:
    """Alpha-beta search with transposition table, draw detection, and quiescence.
    
    Args:
        board: Chess position
        depth: Remaining depth to search
        alpha: Best score for maximizing player
        beta: Best score for minimizing player
        state: SearchState with TT, killers, history
        ply: Current ply (for mate distance)
    
    Returns:
        Evaluation score from perspective of side to move
    """
    state.nodes += 1

    # Probe transposition table
    key = getattr(board, 'zobrist_key', None)
    if key is not None:
        entry = state.tt.probe(key)
        if entry is not None and entry.depth >= depth:
            if entry.flag == EXACT:
                return entry.score
            if entry.flag == LOWERBOUND:
                alpha = max(alpha, entry.score)
            elif entry.flag == UPPERBOUND:
                beta = min(beta, entry.score)
            if alpha >= beta:
                return entry.score

    # Draw detection: fifty-move rule, insufficient material, stalemate via game_status
    try:
        gs = get_game_status(board)
        if gs.is_stalemate or gs.is_insufficient_material or gs.is_draw_by_fifty_move or gs.is_draw_by_repetition:
            return 0
    except Exception:
        pass

    # Depth 0: switch to quiescence search
    if depth <= 0:
        return quiescence(board, alpha, beta, state, ply)

    # Generate legal moves
    moves = _get_legal_moves(board)

    # Terminal: no legal moves = checkmate or stalemate
    if not moves:
        if board.is_in_check(board.side_to_move):
            return -MATE_SCORE + ply
        return 0

    best_score = -9999999
    best_move = None

    mp = MovePicker(board, moves, ply=ply, tt_move=None, killers=state.killers, history=state.history)

    for _ in range(len(moves)):
        m = mp.next()
        if m is None:
            break
        try:
            board.make_move(m)
        except Exception:
            continue
        
        score = -alpha_beta(board, depth - 1, -beta, -alpha, state, ply + 1)
        board.unmake_move()

        if score >= beta:
            # Store killer if quiet move (not capture)
            try:
                if not getattr(m, 'is_capture', False):
                    state.killers.add(ply, m)
            except Exception:
                pass
            state.tt.store(getattr(board, 'zobrist_key', 0), depth, score, LOWERBOUND, m)
            return score

        if score > best_score:
            best_score = score
            best_move = m
        if score > alpha:
            alpha = score

    # Store result in transposition table
    flag = EXACT if best_score > alpha else UPPERBOUND
    state.tt.store(getattr(board, 'zobrist_key', 0), depth, best_score, flag, best_move)

    return best_score
