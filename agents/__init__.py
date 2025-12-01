"""Agents package for Xadrez_AI_Final.

Provides agent classes that decide moves for different player types:
- HumanAgent: awaits user input (LAN/UCI moves)
- RandomAgent: selects random legal moves
- EngineAgent: uses chess engine (alpha-beta + iterative deepening)
"""

from .agent_base import Agent
from .human_agent import HumanAgent
from .random_agent import RandomAgent
from .engine_agent import EngineAgent

__all__ = ["Agent", "HumanAgent", "RandomAgent", "EngineAgent"]
