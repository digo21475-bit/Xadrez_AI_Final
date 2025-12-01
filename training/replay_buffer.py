"""Persistent circular replay buffer using torch.save (pickle-backed).
Stores tuples (state_np, pi_np, player, outcome)
"""
from __future__ import annotations
import collections
import os
import torch
from typing import Deque, Tuple


class ReplayBuffer:
    def __init__(self, path: str, capacity: int = 100_000):
        self.path = path
        self.capacity = capacity
        self.buf: Deque = collections.deque(maxlen=capacity)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            try:
                data = torch.load(path)
                if isinstance(data, list):
                    self.buf = collections.deque(data, maxlen=capacity)
            except Exception:
                pass

    def add(self, item: Tuple):
        self.buf.append(item)

    def sample(self, batch_size: int):
        import random
        return random.sample(list(self.buf), min(batch_size, len(self.buf)))

    def save(self):
        try:
            torch.save(list(self.buf), self.path)
        except Exception:
            pass

    def __len__(self):
        return len(self.buf)
