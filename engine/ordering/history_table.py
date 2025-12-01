class HistoryTable:
    def __init__(self):
        # key: (from_sq, to_sq) or move representation
        self.table: dict[object, int] = {}

    def add(self, move, depth: int):
        key = getattr(move, 'uci', None) or repr(move)
        self.table[key] = self.table.get(key, 0) + (1 << depth)

    def score(self, move) -> int:
        key = getattr(move, 'uci', None) or repr(move)
        return self.table.get(key, 0)

    def clear(self):
        self.table.clear()
