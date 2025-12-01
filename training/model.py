"""Minimal policy+value net using PyTorch.
Designed to be small enough for RX580 (configurable channels/blocks).
"""
from __future__ import annotations
import torch
import torch.nn as nn


class ResidualBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        r = self.conv1(x)
        r = self.bn1(r)
        r = torch.relu(r)
        r = self.conv2(r)
        r = self.bn2(r)
        return torch.relu(x + r)


class SmallNet(nn.Module):
    def __init__(self, in_planes=13, channels=64, blocks=6, action_size=20480):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(in_planes, channels, 3, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU()
        )
        self.blocks = nn.Sequential(*[ResidualBlock(channels) for _ in range(blocks)])

        # policy head
        self.policy = nn.Sequential(
            nn.Conv2d(channels, 2, 1),
            nn.BatchNorm2d(2),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * 8 * 8, action_size)
        )

        # value head
        self.value = nn.Sequential(
            nn.Conv2d(channels, 1, 1),
            nn.BatchNorm2d(1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(1 * 8 * 8, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.stem(x)
        x = self.blocks(x)
        pi = self.policy(x)
        v = self.value(x).squeeze(-1)
        return pi, v


def make_model(device=None, **kwargs):
    m = SmallNet(**kwargs)
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return m.to(device)
