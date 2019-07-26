class Node:

    def __init__(self, pos):
        self.pos = pos
        self.neighbors = []
        self.vel = [0, 0]

    def addNieghbor(self, n):
        if n not in self.neighbors and n != self:
            self.neighbors.append(n)
