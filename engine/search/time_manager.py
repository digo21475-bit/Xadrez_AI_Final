import time
from typing import Optional


class TimeManager:
    """Manages time budget for iterative deepening search."""
    def __init__(self):
        """Initialize time manager with no deadline."""
        self.deadline = None

    def start(self, time_ms: Optional[int]):
        """Set time limit for search.
        
        Args:
            time_ms: Time limit in milliseconds, or None for unlimited
        """
        if time_ms is None:
            self.deadline = None
        else:
            self.deadline = time.time() + time_ms / 1000.0

    def expired(self) -> bool:
        """Check if time limit has been exceeded.
        
        Returns:
            True if deadline passed, False if unlimited or time remaining
        """
        if self.deadline is None:
            return False
        return time.time() >= self.deadline

    def should_stop_nodes(self, nodes_visited: int) -> bool:
        """Check if search should stop due to time or node limit.
        
        Args:
            nodes_visited: Number of nodes visited so far
        
        Returns:
            True if search should stop
        """
        # simple heuristic: if more than 1e7 nodes, stop
        if nodes_visited > 10_000_000:
            return True
        return self.expired()
