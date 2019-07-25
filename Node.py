class Node:
    num = 0

    def __init__(self, pos):
        self.pos = pos
        self.neighbors = []
        self.vel = [0, 0]
        self.name = Node.num
        Node.num = Node.num+1

    def addNieghbor(self, n):
        if n not in self.neighbors and n != self:
            self.neighbors.append(n)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
       return self.__str__()
