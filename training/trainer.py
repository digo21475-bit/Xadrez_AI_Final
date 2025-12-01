"""Trainer: sample from replay buffer and train the net.
Minimal implementation: runs K gradient steps and saves checkpoints.
"""
from __future__ import annotations
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from training.replay_buffer import ReplayBuffer


def train_loop(model: nn.Module, buffer: ReplayBuffer, cfg: dict, device=None):
    # run pre-training integrity checks
    try:
        from training.prechecks import run_prechecks
        run_prechecks()
    except Exception as e:
        print(f"Prechecks failed: {e}")
        raise
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    opt = optim.AdamW(model.parameters(), lr=cfg.get('lr', 1e-3), weight_decay=cfg.get('wd', 1e-4))
    bsz = cfg.get('batch_size', 128)
    iters = cfg.get('iters', 100)
    loss_fn_pi = nn.CrossEntropyLoss()
    loss_fn_v = nn.MSELoss()

    best_win = -1.0
    for it in range(iters):
        batch = buffer.sample(bsz)
        if not batch:
            continue
        # fast tensor creation via numpy stacking
        states = torch.tensor(np.array([b[0] for b in batch]), dtype=torch.float32, device=device)
        pis = torch.tensor(np.array([b[1] for b in batch]), dtype=torch.float32, device=device)
        outcomes = torch.tensor(np.array([b[3] for b in batch]), dtype=torch.float32, device=device)

        opt.zero_grad()
        pi_logits, v = model(states)
        # policy loss: CE between pi (visit dist) and logits
        target = pis.argmax(axis=1).long()
        loss_pi = loss_fn_pi(pi_logits, target)
        loss_v = loss_fn_v(v.squeeze(-1), outcomes)
        loss = loss_pi + loss_v
        loss.backward()
        opt.step()

    # checkpoint: latest + optional best promotion left to eval loop
    os.makedirs(cfg['ckpt_dir'], exist_ok=True)
    latest = os.path.join(cfg['ckpt_dir'], f"latest.pt")
    torch.save(model.state_dict(), latest)
    return latest
