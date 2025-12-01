"""Main train.py script integrating config, model, optimizer, gradient accumulation, and checkpointing."""
from __future__ import annotations
import argparse
import os
import torch
import torch.nn as nn
from training.config import TrainConfig
from training.model import make_model
from training.replay_buffer import ReplayBuffer
from training.train_optimized import train_loop_with_grad_accum
from training.metadata_utils import update_metadata


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--agent-dir', default='models/AgentA')
    p.add_argument('--device', default='cpu', choices=['cpu', 'cuda', 'rocm'])
    p.add_argument('--batch-size', type=int, default=128)
    p.add_argument('--grad-accum-steps', type=int, default=1)
    p.add_argument('--lr', type=float, default=1e-3)
    p.add_argument('--epochs', type=int, default=10)
    p.add_argument('--iters-per-epoch', type=int, default=100)
    p.add_argument('--ckpt-every-steps', type=int, default=500)
    p.add_argument('--use-amp', action='store_true')
    p.add_argument('--verbose', action='store_true', default=True)
    args = p.parse_args()

    # Load or create config
    cfg = TrainConfig.from_device(args.device, args.agent_dir)
    cfg.batch_size = args.batch_size
    cfg.grad_accum_steps = args.grad_accum_steps
    cfg.lr = args.lr
    cfg.num_epochs = args.epochs
    cfg.iters_per_epoch = args.iters_per_epoch
    cfg.ckpt_every_steps = args.ckpt_every_steps
    cfg.use_amp = args.use_amp
    cfg.verbose = args.verbose

    print(f"[Config] {cfg.to_dict()}")

    # Create model
    model = make_model(
        device=cfg.device,
        channels=cfg.model_channels,
        blocks=cfg.model_blocks,
        in_planes=cfg.model_in_planes,
        action_size=cfg.action_size,
    )

    # Load replay buffer
    buffer = ReplayBuffer(cfg.replay_path, capacity=cfg.replay_capacity)
    if len(buffer) == 0:
        print("[Warning] Replay buffer is empty. Add samples before training.")

    # Train
    print(f"[Train] Starting with {len(buffer)} samples...")
    step, final_ckpt = train_loop_with_grad_accum(model, buffer, cfg)
    
    # Update metadata
    update_metadata(args.agent_dir, trained_steps=step, final_checkpoint=final_ckpt)
    print(f"[Done] Trained {step} steps. Final checkpoint: {final_ckpt}")


if __name__ == '__main__':
    main()
