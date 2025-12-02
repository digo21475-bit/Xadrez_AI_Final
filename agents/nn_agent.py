"""Neural-network based agent that selects moves from a policy network.

Loads a PyTorch checkpoint (optional) using the training model factory and
chooses the highest-probability legal move according to the network policy.
"""
from __future__ import annotations
from typing import Optional, Any, List, Tuple
import os
import torch

from .agent_base import Agent

try:
    from training.model import make_model
    from training.encoder import board_to_tensor, move_to_index, ACTION_SIZE
except Exception:
    make_model = None
    board_to_tensor = None
    move_to_index = None
    ACTION_SIZE = None


class NeuralAgent(Agent):
    """Simple policy-based agent using the training `SmallNet`.

    It does not run search; it evaluates the policy head and picks the
    highest-scoring legal move. If no model is provided or loading fails,
    the agent will still attempt to call the model factory (if available)
    and otherwise will return a random legal move via fallback.
    """

    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = torch.device(device)
        self.model_path = model_path
        self.model = None
        if make_model is not None:
            # create model skeleton; action size inferred from encoder if available
            kwargs = {}
            if ACTION_SIZE is not None:
                kwargs['action_size'] = ACTION_SIZE
            try:
                self.model = make_model(device=self.device, **kwargs)
                if model_path and os.path.exists(model_path):
                    ckpt = torch.load(model_path, map_location=self.device)
                    # support both state_dict and full model dumps
                    if isinstance(ckpt, dict) and 'state_dict' in ckpt:
                        sd = ckpt['state_dict']
                    else:
                        sd = ckpt
                    try:
                        self.model.load_state_dict(sd)
                    except Exception:
                        # try relaxed loading
                        self.model.load_state_dict(sd, strict=False)
                self.model.eval()
            except Exception:
                self.model = None

    async def get_move(self, board: Any) -> Optional[object]:
        # collect legal moves
        try:
            moves = list(board.generate_legal_moves())
        except Exception:
            try:
                from core.moves.legal_movegen import generate_legal_moves as core_gen

                moves = list(core_gen(board))
            except Exception:
                moves = []

        if not moves:
            return None

        # If we don't have a model, fall back to first legal move
        if self.model is None or board_to_tensor is None or move_to_index is None:
            return moves[0]

        # prepare input
        try:
            import numpy as np
            arr = board_to_tensor(board)
            t = torch.from_numpy(arr).unsqueeze(0).to(self.device)
        except Exception:
            return moves[0]

        with torch.no_grad():
            try:
                pi, v = self.model(t)
            except Exception:
                # model forward failed
                return moves[0]

        # pi is logits of shape (1, ACTION_SIZE)
        logits = pi.squeeze(0).cpu().numpy()

        # build mapping (move -> score)
        best_move = None
        best_score = None
        for m in moves:
            try:
                idx = move_to_index(m)
                score = float(logits[idx])
            except Exception:
                # mapping failed for this move; skip
                continue
            if best_move is None or score > best_score:
                best_move = m
                best_score = score

        if best_move is None:
            return moves[0]
        return best_move

    def name(self) -> str:
        base = "NeuralAgent"
        if self.model_path:
            return f"{base} ({os.path.basename(self.model_path)})"
        return base


def list_available_models(models_dir: str = 'models') -> List[Tuple[str, Optional[str]]]:
    """Return a list of (model_name, checkpoint_path_or_None).

    Scans top-level folders in `models_dir` and finds a file under
    `checkpoints/` (first match) if present.
    """
    out = []
    if not os.path.isdir(models_dir):
        return out
    for name in sorted(os.listdir(models_dir)):
        p = os.path.join(models_dir, name)
        if not os.path.isdir(p):
            continue
        ck = None
        ckdir = os.path.join(p, 'checkpoints')
        if os.path.isdir(ckdir):
            # pick 'latest.pt' or first .pt
            for candidate in ('latest.pt', 'ckpt_000000.pt'):
                cp = os.path.join(ckdir, candidate)
                if os.path.exists(cp):
                    ck = cp
                    break
            if ck is None:
                for f in sorted(os.listdir(ckdir)):
                    if f.endswith('.pt'):
                        ck = os.path.join(ckdir, f)
                        break
        out.append((name, ck))
    return out
