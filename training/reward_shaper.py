"""Reward shaping for self-play training.
Calculates incremental rewards based on material, position, and game progress.
"""
from __future__ import annotations
from enum import IntEnum
from utils.enums import PieceType


class RewardShaper:
    """Calculate shaped rewards during self-play to guide learning.
    
    Rewards include:
    - Material change (capture bonus/penalty)
    - Positional evaluation (pawn promotion, king safety, etc.)
    - Game progress (move count bonus for longer games)
    """
    
    # Material values (centipawns)
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 0,  # not traded
    }
    
    def __init__(self, scale_material=1.0, scale_position=0.5, scale_progress=0.1):
        """
        Args:
            scale_material: weight for material change reward
            scale_position: weight for positional evaluation
            scale_progress: weight for game length bonus
        """
        self.scale_material = scale_material
        self.scale_position = scale_position
        self.scale_progress = scale_progress
    
    def evaluate_material(self, board) -> float:
        """Evaluate material balance. Positive = current side ahead.
        
        Returns score in range roughly [-3900, 3900] (queen to king difference).
        """
        side = board.side_to_move
        score = 0.0
        
        # Count material for each side
        try:
            # Iterate through mailbox; piece at index (color, ptype)
            for sq in range(64):
                piece = board.mailbox[sq]
                if piece is None:
                    continue
                color, ptype = piece
                val = self.PIECE_VALUES.get(ptype, 0)
                
                if color == side:
                    score += val
                else:
                    score -= val
        except Exception:
            pass
        
        return score / 100.0  # normalize to pawn units
    
    def evaluate_pawn_advancement(self, board) -> float:
        """Bonus for advanced pawns (closer to promotion).
        
        Returns small positional bonus.
        """
        bonus = 0.0
        side = board.side_to_move
        
        try:
            for sq in range(64):
                piece = board.mailbox[sq]
                if piece is None:
                    continue
                color, ptype = piece
                if ptype != PieceType.PAWN:
                    continue
                
                # rank-based bonus (higher rank = closer to promotion)
                rank = sq // 8
                if color == side:
                    # White pawns: rank 7 is promotion, rank 6 is strong, etc.
                    # Black pawns: rank 0 is promotion, rank 1 is strong, etc.
                    if side == 0:  # White (rank increases toward 7)
                        bonus += (rank - 1) * 0.05
                    else:  # Black (rank decreases toward 0)
                        bonus += (6 - rank) * 0.05
                else:
                    # Penalize opponent's advanced pawns
                    if side == 0:  # White, penalize black advanced pawns
                        bonus -= (6 - rank) * 0.05
                    else:  # Black, penalize white advanced pawns
                        bonus -= (rank - 1) * 0.05
        except Exception:
            pass
        
        return bonus
    
    def evaluate_king_safety(self, board) -> float:
        """Bonus/penalty based on king position and nearby pieces.
        
        Simplified: encourage castling and penalize exposed king.
        """
        safety = 0.0
        side = board.side_to_move
        
        try:
            # Find king position
            king_sq = None
            for sq in range(64):
                piece = board.mailbox[sq]
                if piece and piece[1] == PieceType.KING and piece[0] == side:
                    king_sq = sq
                    break
            
            if king_sq is not None:
                # Penalty if king in center (rank 3-4, file 2-5)
                rank = king_sq // 8
                file = king_sq % 8
                if 2 <= rank <= 4 and 2 <= file <= 5:
                    safety -= 0.1
                
                # Bonus if king in corner (castled side)
                if side == 0 and king_sq in [1, 6]:  # White kingside/queenside castled
                    safety += 0.1
                elif side == 1 and king_sq in [57, 62]:  # Black kingside/queenside castled
                    safety += 0.1
        except Exception:
            pass
        
        return safety
    
    def calculate_shaped_reward(self, board_before, board_after, move_count: int = 0) -> float:
        """Calculate reward for a single move.
        
        Args:
            board_before: board state before move
            board_after: board state after move
            move_count: number of moves so far (for progress bonus)
        
        Returns:
            float reward signal (typically in range [-1, 1] after scaling)
        """
        reward = 0.0
        
        # Material change (from mover's perspective)
        mat_before = self.evaluate_material(board_before)
        mat_after = self.evaluate_material(board_after)
        material_delta = mat_after - mat_before
        reward += self.scale_material * material_delta
        
        # Positional factors
        pos_reward = self.evaluate_pawn_advancement(board_after) + \
                     self.evaluate_king_safety(board_after)
        reward += self.scale_position * pos_reward
        
        # Game progress (longer games = more exploration)
        progress_reward = self.scale_progress * (move_count / 100.0)
        reward += progress_reward
        
        # Clip to reasonable range
        return max(-2.0, min(2.0, reward))
    
    def calculate_final_reward(self, outcome: int) -> float:
        """Convert game outcome to reward.
        
        Args:
            outcome: 1 (win), 0 (draw), -1 (loss)
        
        Returns:
            float reward (1.0 for win, 0.0 for draw, -1.0 for loss)
        """
        return float(outcome)
