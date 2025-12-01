"""Dynamic batch sizing to fit within VRAM constraints."""
from __future__ import annotations
import torch
from typing import List, Tuple


def count_tokens_in_batch(batch: List[Tuple]) -> int:
    """Estimate token count in batch (state size * batch_size)."""
    if not batch:
        return 0
    # Each state is (13, 8, 8) = 832 floats; count as 832 tokens
    state_tokens = 13 * 8 * 8
    return len(batch) * state_tokens


def adjust_batch_size(
    initial_batch_size: int,
    max_tokens: int,
    batch_gen,
    device: str = 'cpu',
    verbose: bool = True,
) -> int:
    """Binary search for largest batch_size that fits within max_tokens."""
    low, high = 1, initial_batch_size
    best_size = 1
    
    while low <= high:
        mid = (low + high) // 2
        batch = list(batch_gen(mid))
        tokens = count_tokens_in_batch(batch)
        
        if tokens <= max_tokens:
            best_size = mid
            low = mid + 1
        else:
            high = mid - 1
    
    if verbose:
        print(f"Adjusted batch_size: {best_size} (max_tokens={max_tokens})")
    
    return best_size


class DynamicBatchSampler:
    """Samples batches dynamically, adjusting size based on available VRAM."""
    
    def __init__(self, buffer, initial_batch_size: int = 128, max_tokens: int = 65536):
        self.buffer = buffer
        self.batch_size = initial_batch_size
        self.max_tokens = max_tokens
    
    def sample(self, target_size: int = None) -> List[Tuple]:
        """Sample a batch, auto-adjusting size if needed."""
        if target_size is None:
            target_size = self.batch_size
        
        batch = self.buffer.sample(target_size)
        tokens = count_tokens_in_batch(batch)
        
        # Adjust down if over limit
        while tokens > self.max_tokens and len(batch) > 1:
            batch = batch[:-1]
            tokens = count_tokens_in_batch(batch)
        
        return batch
