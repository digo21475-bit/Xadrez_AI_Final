from typing import List, Optional


class PVTable:
    """Stores principal variation lines by depth (unused, but kept for compatibility)."""
    def __init__(self, max_ply: int = 256):
        """Initialize PV table.
        
        Args:
            max_ply: Maximum ply to store PV lines for
        """
        self.max_ply = max_ply
        self.pv = [[] for _ in range(max_ply)]

    def set_line(self, depth: int, moves: List[object]):
        """Store a PV line at given depth.
        
        Args:
            depth: Depth to store at
            moves: List of moves in PV line
        """
        if depth >= self.max_ply:
            depth = self.max_ply - 1
        self.pv[depth] = list(moves)

    def get_root(self) -> List[object]:
        """Get PV line from root (depth 0).
        
        Returns:
            List of moves in PV line
        """
        return list(self.pv[0])

    def clear(self) -> None:
        """Clear all PV lines."""
        self.pv = [[] for _ in range(self.max_ply)]
