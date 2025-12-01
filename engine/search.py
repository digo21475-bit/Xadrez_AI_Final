"""Alpha-beta search with quiescence, TT probe/store, PV reconstruction and stop support."""
from typing import Any, Optional, List
from .tt import TranspositionTable, TTEntry, EXACT, LOWERBOUND, UPPERBOUND
from .movepicker import MovePicker, Killers
from .move_ordering import HistoryTable
from .eval import evaluate
from core.rules.game_status import get_game_status
from engine.search.pv import PVTable
from engine.search.time_manager import TimeManager
from engine.utils.constants import MATE_SCORE


class SearchController:
    def __init__(self):
        self.stop = False


class SearchState:
    def __init__(self):
        self.tt = TranspositionTable()
        self.killers = Killers()
        self.history = HistoryTable()
        self.nodes = 0
        self.controller = SearchController()


def build_pv_from_tt(board: Any, tt: TranspositionTable, max_depth: int = 64) -> List[object]:
    pv = []
    # make a copy of board by using board.copy() if available
    try:
        bcopy = board.copy()
    except Exception:
        # fallback: operate on original but ensure unmake_move is called
        bcopy = board

    for ply in range(max_depth):
        entry = tt.probe(getattr(bcopy, 'zobrist_key', 0))
        if not entry or not entry.best_move:
            break
        mv = entry.best_move
        pv.append(mv)
        try:
            if hasattr(bcopy, 'make_move'):
                bcopy.make_move(mv)
            elif hasattr(bcopy, 'make_move_int'):
                bcopy.make_move_int(mv)
            else:
                break
        except Exception:
            break

    # unwind if we used a copy that is original
    try:
        if bcopy is board:
            # unmake moves we did
            for _ in pv:
                if hasattr(board, 'unmake_move'):
                    board.unmake_move()
                elif hasattr(board, 'unmake_move_int'):
                    board.unmake_move_int()
    except Exception:
        pass

    return pv


def quiescence(board: Any, alpha: int, beta: int, state: SearchState, ply: int) -> int:
    state.nodes += 1
    if state.controller.stop:
        raise TimeoutError()

    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return stand_pat
    if alpha < stand_pat:
        alpha = stand_pat

    # generate captures only
    try:
        moves = list(board.generate_legal_moves())
    except Exception:
        from core.moves.legal_movegen import generate_legal_moves as core_gen
        moves = list(core_gen(board))

    captures = [m for m in moves if getattr(m, 'is_capture', False)]
    # delta pruning: ignore captures that are unlikely to raise above alpha
    # compute max captured value
    for m in captures:
        # trivial ordering via MVV-LVA implemented in MovePicker
        pass

    mp = MovePicker(board, captures, ply=ply, tt_move=None, killers=state.killers, history=state.history)

    while True:
        m = mp.next()
        if m is None:
            break
        try:
            if hasattr(board, 'make_move'):
                board.make_move(m)
            elif hasattr(board, 'make_move_int'):
                board.make_move_int(m)
            else:
                continue
        except Exception:
            continue

        try:
            score = -quiescence(board, -beta, -alpha, state, ply + 1)
        finally:
            if hasattr(board, 'unmake_move'):
                board.unmake_move()
            elif hasattr(board, 'unmake_move_int'):
                board.unmake_move_int()

        if score >= beta:
            return score
        if score > alpha:
            alpha = score

    return alpha


def alpha_beta(board: Any, depth: int, alpha: int, beta: int, state: SearchState, ply: int = 0) -> int:
    state.nodes += 1
    if state.controller.stop:
        raise TimeoutError()

    key = getattr(board, 'zobrist_key', 0)
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

    # terminal / draw checks
    try:
        gs = get_game_status(board)
        if gs.is_game_over:
            # mate or draw
            if gs.is_checkmate:
                # side to move is checkmated
                return -MATE_SCORE + ply
            return 0
    except Exception:
        pass

    if depth <= 0:
        return quiescence(board, alpha, beta, state, ply)

    # generate moves
    try:
        moves = list(board.generate_legal_moves())
    except Exception:
        from core.moves.legal_movegen import generate_legal_moves as core_gen
        moves = list(core_gen(board))

    if not moves:
        if board.is_in_check(board.side_to_move):
            return -MATE_SCORE + ply
        return 0

    # PV move from TT if present
    tt_move = entry.best_move if entry is not None else None
    mp = MovePicker(board, moves, ply=ply, tt_move=tt_move, killers=state.killers, history=state.history)

    best_score = -99999999
    best_move = None

    while True:
        m = mp.next()
        if m is None:
            break
        try:
            if hasattr(board, 'make_move'):
                board.make_move(m)
            elif hasattr(board, 'make_move_int'):
                board.make_move_int(m)
            else:
                continue
        except Exception:
            continue

        try:
            score = -alpha_beta(board, depth - 1, -beta, -alpha, state, ply + 1)
        finally:
            if hasattr(board, 'unmake_move'):
                board.unmake_move()
            elif hasattr(board, 'unmake_move_int'):
                board.unmake_move_int()

        if score >= beta:
            # store killer if non-capture
            if not getattr(m, 'is_capture', False):
                try:
                    state.killers.add(ply, m)
                except Exception:
                    pass
            state.tt.store(key, depth, score, LOWERBOUND, m)
            return score

        if score > best_score:
            best_score = score
            best_move = m
        if score > alpha:
            alpha = score

    # store as exact or upperbound
    flag = EXACT if best_score > alpha else UPPERBOUND
    state.tt.store(key, depth, best_score, flag, best_move)
    return best_score
