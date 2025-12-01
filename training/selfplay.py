"""Self-play worker: uses MCTS + net to generate games and store (state, pi, player).
"""
from __future__ import annotations
import time
from training.encoder import board_to_tensor, move_to_index, index_to_move, ACTION_SIZE
from core.moves.move import Move


class SelfPlayWorker:
    def __init__(self, net_predict, mcts_sims=50):
        self.net = net_predict
        from training.mcts import MCTS
        self.mcts = MCTS(net_predict, action_size=ACTION_SIZE, sims=mcts_sims)

    def play_game(self, board, temperature=1.0, max_moves=512):
        records = []
        move_count = 0
        while move_count < max_moves:
            pi = self.mcts.run(board)
            # store state and pi
            state = board_to_tensor(board)
            records.append((state, pi, board.side_to_move))
            # select move (temperature)
            if temperature == 0 or move_count > 20:
                # argmax
                a = max(range(len(pi)), key=lambda i: pi[i])
            else:
                import random
                probs = pi
                r = random.random()
                cum = 0.0
                a = 0
                for i, p in enumerate(probs):
                    cum += p
                    if r <= cum:
                        a = i
                        break
            # apply move by index (board must implement make_move_index)
            # translate index -> Move and apply using core Board.make_move
            try:
                f, t, promo = index_to_move(a)
                mv = Move(from_sq=f, to_sq=t, piece=None, is_capture=False, promotion=promo)
                cell = board.mailbox[f]
                if cell is None:
                    outcome = -1 if board.side_to_move else 1
                    return records, outcome
                _, ptype = cell
                mv.piece = ptype
                board.make_move(mv)
            except Exception:
                outcome = -1 if board.side_to_move else 1
                return records, outcome
            move_count += 1
            # terminal detection
            if getattr(board, 'is_game_over', lambda: False)():
                break

        # determine outcome
        if hasattr(board, 'game_result'):
            outcome = board.game_result()
        else:
            outcome = 0
        return records, outcome
