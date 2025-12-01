class Killers:
    def __init__(self, max_ply=256):
        self.max_ply = max_ply
        # two killers per ply
        self.killers = [[None, None] for _ in range(max_ply)]

    def add(self, ply: int, move):
        if ply >= self.max_ply:
            return
        if move == self.killers[ply][0]:
            return
        # shift existing
        self.killers[ply][1] = self.killers[ply][0]
        self.killers[ply][0] = move

    def get(self, ply: int):
        if ply >= self.max_ply:
            return [None, None]
        return self.killers[ply]
