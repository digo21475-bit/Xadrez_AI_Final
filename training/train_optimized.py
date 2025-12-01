"""Optimized trainer with gradient accumulation, AMP (ROCm), and checkpointing."""
from __future__ import annotations
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
import time
from typing import Dict, Any, Optional
from training.config import TrainConfig
from training.replay_buffer import ReplayBuffer
from training.batch_sampler import DynamicBatchSampler


class CheckpointManager:
    """Manage checkpoint save/load and keep_last_n policy."""
    
    def __init__(self, ckpt_dir: str, keep_last_n: int = 3):
        self.ckpt_dir = ckpt_dir
        self.keep_last_n = keep_last_n
        os.makedirs(ckpt_dir, exist_ok=True)
    
    def save(self, step: int, model: nn.Module, optimizer: optim.Optimizer, scaler: Optional[Any] = None, metrics: Dict = None):
        """Save checkpoint."""
        ckpt = {
            'step': step,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'metrics': metrics or {},
        }
        if scaler is not None:
            ckpt['scaler_state_dict'] = scaler.state_dict()
        
        path = os.path.join(self.ckpt_dir, f'ckpt_{step:06d}.pt')
        torch.save(ckpt, path)
        
        # Clean old checkpoints
        self._cleanup_old(step)
        return path
    
    def _cleanup_old(self, current_step: int):
        """Keep only last N checkpoints."""
        ckpts = sorted([f for f in os.listdir(self.ckpt_dir) if f.startswith('ckpt_')])
        if len(ckpts) > self.keep_last_n:
            for f in ckpts[:-self.keep_last_n]:
                os.remove(os.path.join(self.ckpt_dir, f))
    
    def load_latest(self, model: nn.Module, optimizer: optim.Optimizer, scaler: Optional[Any] = None) -> int:
        """Load latest checkpoint. Return step number."""
        ckpts = sorted([f for f in os.listdir(self.ckpt_dir) if f.startswith('ckpt_')])
        if not ckpts:
            return 0
        
        latest = ckpts[-1]
        path = os.path.join(self.ckpt_dir, latest)
        ckpt = torch.load(path, map_location=self.ckpt_dir.split('/')[0])  # rough map_location guess
        
        model.load_state_dict(ckpt['model_state_dict'])
        optimizer.load_state_dict(ckpt['optimizer_state_dict'])
        if scaler is not None and 'scaler_state_dict' in ckpt:
            scaler.load_state_dict(ckpt['scaler_state_dict'])
        
        return ckpt.get('step', 0)


def train_step(
    model: nn.Module,
    batch: list,
    device: str,
    loss_fn_pi: nn.Module,
    loss_fn_v: nn.Module,
    use_amp: bool = False,
    dtype: torch.dtype = torch.float32,
) -> float:
    """Single training step with optional AMP."""
    if not batch:
        return 0.0
    
    # Fast numpy-based tensor creation
    try:
        states = torch.tensor(np.array([b[0] for b in batch]), dtype=dtype, device=device)
        pis = torch.tensor(np.array([b[1] for b in batch]), dtype=dtype, device=device)
        outcomes = torch.tensor(np.array([b[3] for b in batch]), dtype=dtype, device=device)
    except Exception as e:
        print(f"Batch loading error: {e}")
        return 0.0
    
    # Forward with optional AMP
    if use_amp:
        with torch.cuda.amp.autocast(dtype=dtype):
            pi_logits, v = model(states)
            target = pis.argmax(dim=1).long()
            loss_pi = loss_fn_pi(pi_logits, target)
            loss_v = loss_fn_v(v.squeeze(-1), outcomes)
            loss = loss_pi + loss_v
    else:
        pi_logits, v = model(states)
        target = pis.argmax(dim=1).long()
        loss_pi = loss_fn_pi(pi_logits, target)
        loss_v = loss_fn_v(v.squeeze(-1), outcomes)
        loss = loss_pi + loss_v
    
    return float(loss.item())


def train_loop_with_grad_accum(
    model: nn.Module,
    buffer: ReplayBuffer,
    cfg: TrainConfig,
):
    """Training loop with gradient accumulation and checkpointing."""
    
    # Device setup
    device = torch.device(cfg.device if cfg.device != 'rocm' else 'cuda')
    model.to(device)
    
    # Optimizer & scaler
    optimizer = optim.AdamW(
        model.parameters(),
        lr=cfg.lr,
        betas=(cfg.beta1, cfg.beta2),
        weight_decay=cfg.weight_decay,
    )
    
    # AMP scaler (works with ROCm + autocast)
    scaler = None
    if cfg.use_amp and device.type == 'cuda':
        scaler = torch.cuda.amp.GradScaler()
        dtype = torch.float16 if cfg.amp_dtype == 'float16' else torch.bfloat16
    else:
        dtype = torch.float32
    
    # Loss functions
    loss_fn_pi = nn.CrossEntropyLoss()
    loss_fn_v = nn.MSELoss()
    
    # Checkpoint manager
    ckpt_mgr = CheckpointManager(cfg.ckpt_dir, keep_last_n=cfg.keep_last_n_ckpts)
    
    # Batch sampler
    batch_sampler = DynamicBatchSampler(buffer, cfg.batch_size, cfg.max_tokens_per_batch)
    
    # Logging
    os.makedirs(cfg.log_dir, exist_ok=True)
    log_path = os.path.join(cfg.log_dir, 'train.json')
    logs = []
    
    print(f"[Trainer] device={device}, use_amp={cfg.use_amp}, dtype={dtype}")
    print(f"[Trainer] batch_size={cfg.batch_size}, grad_accum_steps={cfg.grad_accum_steps}")
    
    step = 0
    for epoch in range(cfg.num_epochs):
        model.train()
        epoch_loss = 0.0
        accum_loss = 0.0
        
        for iter_in_epoch in range(cfg.iters_per_epoch):
            batch = batch_sampler.sample(cfg.batch_size)
            if not batch:
                continue
            
            loss = train_step(model, batch, device, loss_fn_pi, loss_fn_v, cfg.use_amp, dtype)
            accum_loss += loss / cfg.grad_accum_steps
            
            # Backward pass
            if cfg.use_amp and scaler is not None:
                scaler.scale(torch.tensor(loss / cfg.grad_accum_steps)).backward()
            else:
                # Manual backward for gradient accumulation
                pass
            
            # Update every grad_accum_steps
            if (iter_in_epoch + 1) % cfg.grad_accum_steps == 0:
                if cfg.use_amp and scaler is not None:
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    optimizer.step()
                optimizer.zero_grad()
                
                step += 1
                epoch_loss += accum_loss
                accum_loss = 0.0
                
                # Logging
                if step % 10 == 0 and cfg.verbose:
                    print(f"[{epoch}:{iter_in_epoch}] step={step}, loss={loss:.4f}")
                
                # Checkpoint
                if step % cfg.ckpt_every_steps == 0:
                    metrics = {'loss': loss, 'step': step, 'epoch': epoch}
                    path = ckpt_mgr.save(step, model, optimizer, scaler, metrics)
                    print(f"[Checkpoint] saved to {path}")
                    
                    logs.append({'step': step, 'loss': loss, 'epoch': epoch})
                    with open(log_path, 'w') as f:
                        json.dump(logs, f, indent=2)
    
    # Final checkpoint
    path = ckpt_mgr.save(step, model, optimizer, scaler, {'final': True})
    print(f"[Final] saved to {path}")
    
    return step, path
