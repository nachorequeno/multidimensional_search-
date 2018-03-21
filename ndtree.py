from rectangle import *
from point import *

class NDTree:
    # root: Node
    def __init__(self):
        self.root = Node()

    def insert(self):
        return 0

    def split(self):
        return 0

    def update(self, x):
        if self.empty():
            self.root = Node()
            self.root.add(x)
        else:
            n = self.root
            res = n.updateNode(x)
            if x not in self.root:
                n.insert(x)
        return 0

class Node:
    # nodes: list(1,..,n) of nodes
    # rect: Rectangle
    # L: list() of solutions
    def __init__(self):
        zero = (0, )
        self.rect = Rectangle(zero, zero)
        self.nodes = []
        self.L = []

    def isEmptySolution(self):
        return len(self.L) == 0

    def isLeaf(self):
        return self.numSubnodes() == 0

    def numSubnodes(self):
        return len(self.nodes)

    def addNode(self, np):
        self.nodes.append(np)

    def removeNode(self, np):
        self.nodes.remove(np)

    def add(self, x):
        self.L.append(x)

    def remove(self, x):
        self.L.remove(x)

    def insert(self, x):
        if self.isLeaf():
            self.add(x)
            self.updateIdealNadir(x)
            if len(self.nodes) > M:
                self.split()
            else:
                np = self.find(x)
                np.insert(x)
        return 0

    def split(self):
        y = self.findHighestEuclideanDistance()
        np = Node()
        np.add(y)
        np.updateIdealNadir(y)
        self.remove(y)
        while self.numSubnodes() < M:
            y = self.findHighestEuclideanDistance()
            np = Node()
            np.add(y)
            np.updateIdealNadir(y)
            self.remove(y)
        while not self.isEmptySolution():
            y = self.L.pop()
            np.add(y)
            np.updateIdealNadir(y)
            self.remove(y)
        return 0

    def findHighestEuclideanDistance(self):
        mean_max_distance = 0
        temp_mean_max_distance = 0
        y = Node()
        for yp in self.nodes:
            max_distance = 0
            for xp in self.nodes:
                max_distance += distance(yp.getPoint(), xp.getPoint())
            mean_max_distance = max_distance / (len(self.nodes) - 1)
            if mean_max_distance > temp_mean_max_distance:
                temp_mean_max_distance = mean_max_distance
                y = yp
        return y, mean_max_distance

    def updateNode(self, x):
        # self = n (node)
        S = self.getSn()
        minim = (0. ) #####
        maxim = (0. ) #####
        rect = Rectangle(minim, maxim)
        if min(rect.max_corner, x):
            # x is rejected
            return 0
        elif min(x, rect.min_corner):
            # remove n and its whole sub-tree
            return -1
        elif min(rect.min_corner, x) or min(x, rect.max_corner):
            if self.isLeaf():
                for y in self.L:
                    if min(y, x):
                        # x is rejected
                        return 0
                    elif min(x, y):
                        self.L.remove(y)
            else:
                for np in self.nodes:
                    np.updateNode(x)
                    if np.isEmptySolution():
                        self.nodes.remove(np)
        return 0

    def updateIdealNadir(self, x):
        np = Node()
        rect = self.getRectangleSn()
        if less(x, rect.min_corner) or greater(x, rect.max_corner):
            if not self.isRoot():
                np
                np.updateIdealNadir(x)
        return 0

    def getSn(self):
        if self.empty():
            return set(self.L)
        else:
            temp = set()
            for i in self.nodes:
                temp.union(i.getSn())

    def getRectangleSn(self):
        sn = self.getSn()
        min_c
        max_c
        return Rectangle(min_c, max_c)