"""Self-play worker: uses MCTS + net to generate games and store (state, pi, player, reward_step, reward_final).
Includes reward shaping for incremental feedback during training.
"""
from __future__ import annotations
import time
from training.encoder import board_to_tensor, move_to_index, index_to_move, ACTION_SIZE
from core.moves.legal_movegen import generate_legal_moves
from core.moves.move import Move


class SelfPlayWorker:
    def __init__(self, net_predict, mcts_sims=50, use_reward_shaping=True):
        """
        Args:
            net_predict: network predictor
            mcts_sims: number of MCTS simulations per move
            use_reward_shaping: if True, calculate incremental rewards; else use only final outcome
        """
        self.net = net_predict
        from training.mcts import MCTS
        self.mcts = MCTS(net_predict, action_size=ACTION_SIZE, sims=mcts_sims)
        self.use_reward_shaping = use_reward_shaping
        
        if use_reward_shaping:
            from training.reward_shaper import RewardShaper
            self.reward_shaper = RewardShaper()
        else:
            self.reward_shaper = None

    def play_game(self, board, temperature=1.0, max_moves=512):
        records = []
        move_count = 0
        while move_count < max_moves:
            pi = self.mcts.run(board)
            # store state and pi
            state = board_to_tensor(board)
            
            # select move among legal moves (temperature)
            legal_moves = list(generate_legal_moves(board))
            legal_indices = []
            for m in legal_moves:
                idx = move_to_index(m)
                if idx is not None:
                    legal_indices.append(idx)

            if not legal_indices:
                # no legal moves -> terminal
                break

            if temperature == 0 or move_count > 20:
                # argmax among legal indices
                a = max(legal_indices, key=lambda i: pi[i])
            else:
                import random
                probs = [pi[i] for i in legal_indices]
                total = sum(probs)
                if total <= 0:
                    # fallback uniform
                    probs = [1.0 / len(probs)] * len(probs)
                else:
                    probs = [p / total for p in probs]
                r = random.random()
                cum = 0.0
                chosen = 0
                for idx, p in enumerate(probs):
                    cum += p
                    if r <= cum:
                        chosen = idx
                        break
                a = legal_indices[chosen]
            
            # apply move by index (board must implement make_move_index)
            # translate index -> Move and apply using core Board.make_move
            try:
                f, t, promo = index_to_move(a)
                cell = board.mailbox[f]
                if cell is None:
                    outcome = -1 if board.side_to_move else 1
                    # Convert records to 5-field format before returning
                    final_reward = self.reward_shaper.calculate_final_reward(outcome) if self.reward_shaper else float(outcome)
                    records_with_final = [(state, pi, player, step_reward, final_reward) for state, pi, player, step_reward in records]
                    return records_with_final, outcome
                _, ptype = cell
                mv = Move(from_sq=f, to_sq=t, piece=ptype, is_capture=False, promotion=promo)
                
                # Capture player BEFORE move (since side_to_move changes after make_move)
                player = board.side_to_move
                
                # Calculate step reward before move (if using reward shaping)
                step_reward = 0.0
                if self.use_reward_shaping and self.reward_shaper:
                    board_before_copy = board.copy() if hasattr(board, 'copy') else None
                    board.make_move(mv)
                    if board_before_copy:
                        step_reward = self.reward_shaper.calculate_shaped_reward(
                            board_before_copy, board, move_count
                        )
                else:
                    board.make_move(mv)
                
                # Store record with step reward (will be updated with final outcome later)
                # Record: (state, pi, player, step_reward)
                # After game: will be converted to (state, pi, player, step_reward, final_reward)
                records.append((state, pi, player, step_reward))
                
            except Exception:
                outcome = -1 if board.side_to_move else 1
                # Convert records to 5-field format before returning
                final_reward = self.reward_shaper.calculate_final_reward(outcome) if self.reward_shaper else float(outcome)
                records_with_final = [(state, pi, player, step_reward, final_reward) for state, pi, player, step_reward in records]
                return records_with_final, outcome
            
            move_count += 1
            # terminal detection
            if getattr(board, 'is_game_over', lambda: False)():
                break

        # determine outcome
        if hasattr(board, 'game_result'):
            outcome = board.game_result()
        else:
            outcome = 0
        
        # Convert outcome to final reward and update all records
        final_reward = self.reward_shaper.calculate_final_reward(outcome) if self.reward_shaper else float(outcome)
        
        # Update records: convert (state, pi, player, step_reward) to (state, pi, player, step_reward, final_reward)
        records_with_final = []
        for state, pi, player, step_reward in records:
            records_with_final.append((state, pi, player, step_reward, final_reward))
        
        return records_with_final, outcome
