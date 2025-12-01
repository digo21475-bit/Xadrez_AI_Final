"""Training configuration with sensible defaults for RX580 (8GB VRAM)."""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrainConfig:
    """Training hyperparameters."""
    # Device
    device: str = 'cpu'  # 'cpu', 'cuda', 'rocm'
    
    # Model
    model_channels: int = 64
    model_blocks: int = 6
    model_in_planes: int = 13
    action_size: int = 20480
    
    # Optimizer
    lr: float = 1e-3
    weight_decay: float = 1e-4
    beta1: float = 0.9
    beta2: float = 0.999
    
    # Batch & accumulation
    batch_size: int = 128
    grad_accum_steps: int = 1  # gradient accumulation steps
    max_tokens_per_batch: int = 65536  # dynamic batch sizing
    
    # Training loop
    num_epochs: int = 10
    iters_per_epoch: int = 100
    warmup_steps: int = 100
    
    # Checkpointing
    ckpt_dir: str = 'models/AgentA/checkpoints'
    ckpt_every_steps: int = 500
    keep_last_n_ckpts: int = 3
    
    # Evaluation
    eval_every_steps: int = 500
    eval_batch_size: int = 256
    
    # Replay buffer
    replay_capacity: int = 200_000
    replay_path: str = 'models/AgentA/checkpoints/replay.pt'
    
    # MCTS & self-play
    mcts_sims: int = 50
    selfplay_games: int = 10
    
    # Mixed precision (ROCm AMP support)
    use_amp: bool = True
    amp_dtype: str = 'float16'  # 'float16', 'bfloat16'
    
    # Logging
    log_dir: str = 'models/AgentA/experiments'
    verbose: bool = True

    @classmethod
    def from_device(cls, device: str = 'cpu', agent_dir: str = 'models/AgentA') -> 'TrainConfig':
        """Create config with device-specific defaults."""
        cfg = cls()
        cfg.device = device
        cfg.ckpt_dir = os.path.join(agent_dir, 'checkpoints')
        cfg.replay_path = os.path.join(agent_dir, 'checkpoints/replay.pt')
        cfg.log_dir = os.path.join(agent_dir, 'experiments')
        
        # Adjust for device
        if device in ('cuda', 'rocm'):
            cfg.batch_size = 128
            cfg.grad_accum_steps = 1
            cfg.use_amp = True
        else:
            cfg.batch_size = 32
            cfg.grad_accum_steps = 4
            cfg.use_amp = False
        
        return cfg

    def to_dict(self):
        """Convert to dict for logging."""
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


# Default for RX580
DEFAULT_CONFIG = TrainConfig.from_device('cpu')
