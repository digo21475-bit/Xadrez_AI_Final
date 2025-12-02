"""Device selector utility for the training package.
Provides a single place to decide which torch device to use.
"""
from __future__ import annotations
import torch


def get_device(preferred: str | None = None) -> torch.device:
    """Return a torch.device.

    preferred: optional string like 'cpu', 'cuda', 'rocm'. If None, prefer CUDA when available.
    """
    if preferred:
        if preferred == 'rocm':
            return torch.device('cuda')
        return torch.device(preferred)
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
