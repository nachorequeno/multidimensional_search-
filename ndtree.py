from rectangle import *
from point import *
from point import *

class NDTree:
    # root: Node
    def __init__(self):
        self.root = None

    # Membership
    def __contains__(self, item):
        #return item in self.root
        return self.root.hasPointRec(item)

    # Printers
    def __repr__(self):
        return self.root.toStrRec(0)

    def __str__(self):
        return self.root.toStrRec(0)

    def getPoints(self):
        points = self.root.getPointsRec() if self.root is not None else set()
        return points

    def removePoint(self, p):
        self.root.removePointRec(p) if self.root is not None else None

    def update(self, p):
        # type: (Node, tuple) -> None
        if self.root is None:
            self.root = Node()
            self.root.addPoint(p)
        elif self.root.updateNode(p):
            self.root.insert(p)

    def dynamicNonDominance(self, p):
        # type: (NDTree, tuple) -> None
        set_points = self.getPoints()
        points_greater_than_p = [ppoint for ppoint in set_points if greater_equal(ppoint, p)]
        points_smaller_than_p = [ppoint for ppoint in set_points if greater_equal(p, ppoint)]
        if len(points_greater_than_p) == 0:
            #self.root.insertPoint(p)
            self.update(p)
            for ppoint in points_smaller_than_p:
                #self.root.removePointRec(ppoint)
                self.removePoint(p)

class Node:
    # nodes: list(1,..,n) of nodes
    # rect: Rectangle
    # L: list() of solutions
    MAX_CHILDREN = 4
    MIN_CHILDREN = 2
    def __init__(self, parent=None):
        zero = (0, )
        self.rect = Rectangle(zero, zero)
        self.parent = parent
        self.nodes = []
        self.L = []

    # Membership
    def hasPointRec(self, item):
        if self.isLeaf():
            return self.hasPoint(item)
        else:
            _hasPoints = [x.hasPointRec(item) for x in self.nodes]
            _hasPoint = True
            for i in _hasPoints:
                _hasPoint = _hasPoint and i
            return _hasPoint

    def hasPoint(self, item):
        #return item in self.rect
        return item in self.L

    def __contains__(self, item):
        return self.hasPointRec(item)

    # Printers
    def toStrRec(self, nesting_level):
        if self.isLeaf():
            return self.toStr(nesting_level)
        else:
            _strings = [x.toStrRec(nesting_level+1) for x in self.nodes]
            '\n'.join(_strings)

    def toStr(self, nesting_level=0):
        _string = "\t" * nesting_level
        _string += "["
        for i, x in enumerate(self.L):
            _string += str(x)
            _string += ", " if i < (len(self.L) - 1) else "]"
            #_string += ", " if i < (len(self.L)-1) else ""
        #_string += "]\n"
        return _string

    def __repr__(self):
        return self.toStrRec(0)

    def __str__(self):
        return self.toStrRec(0)

    def getRectangleSn(self):
        sn = self.S()
        #key_function = lambda x, y: x if min(x,y) else y
        #sn_sorted = sorted(sn, key=key_function)
        #sn_sorted = sorted(sn, key=min)
        sn_sorted = sorted(sn, key=norm)

        # Ideal point
        min_c = sn_sorted[0]
        # Nadir point
        max_c = sn_sorted.pop()
        self.rect = Rectangle(min_c, max_c)
        return self.rect

    def isEmptySolution(self):
        return len(self.L) == 0

    def isRoot(self):
        return self.parent is None

    def isLeaf(self):
        return self.numSubnodes() == 0

    def numSubnodes(self):
        return len(self.nodes)

    def addNode(self, np):
        # type: (Node, Node) -> None
        self.nodes.append(np)

    def removeNode(self, np):
        # type: (Node, Node) -> None
        self.nodes.remove(np)
        del np

    def replaceNode(self, n, np):
        index = self.L.index(n)
        self.L.insert(index, np)
        self.L.remove(n)
        del n

    def getSubnode(self, pos=0):
        return self.nodes[pos]

    def addPoint(self, x):
        # type: (Node, tuple) -> None
        self.L.append(x)

    def removePoint(self, x):
        # type: (Node, tuple) -> None
        self.L.remove(x)
        del x

    def removePointRec(self, x):
        # type: (Node, tuple) -> None
        if self.isLeaf():
            self.removePoint(x)
        else:
            [x.removePointRec() for x in self.getPoints()]

    def getPoints(self):
        return self.L

    def getPointsRec(self):
        if self.isLeaf():
            return self.getPoints()
        else:
            points = set(x.getPointsRec() for x in self.getPoints())
            return points.union(self.getPoints())

    def getParent(self):
        return self.parent

    def setParent(self, parent):
        self.parent = parent

    def findClosestNode(self, x):
        # type: (Node, tuple) -> Node
        key_function = lambda node: node.rect.distanceToCenter(x)
        lsorted = sorted(self.nodes, key=key_function)
        #lsorted = sorted(self.nodes, key=Rectangle.distanceToCenter(_, x))
        return lsorted[0]

    def insert(self, x):
        # type: (Node, tuple) -> _
        if self.isLeaf():
            self.addPoint(x)
            self.updateIdealNadir(x)
            if len(self.nodes) > self.MAX_CHILDREN:
                self.split()
            else:
                np = self.findClosestNode(x)
                np.insert(x)
        return 0

    def findPointHighestAverageEuclideanDistance(self):
        y = Node()
        mean_max_distance = 0
        for yp in self.L:
            max_distance = 0
            for xp in self.L:
                max_distance += distance(yp, xp)
            temp_mean_max_distance = max_distance / (len(self.nodes) - 1)
            if temp_mean_max_distance > mean_max_distance:
                mean_max_distance = temp_mean_max_distance
                y = yp
        return y, mean_max_distance

    def split(self):
        y = self.findPointHighestAverageEuclideanDistance()
        np = Node(self)
        self.addNode(np)
        np.addPoint(y)
        np.updateIdealNadir(y)
        self.removePoint(y)
        while self.numSubnodes() < self.MIN_CHILDREN:
            y = self.findPointHighestAverageEuclideanDistance()
            np = Node(self)
            self.addNode(np)
            np.addPoint(y)
            np.updateIdealNadir(y)
            self.removePoint(y)
        while not self.isEmptySolution():
            y = self.L.pop()
            np = self.findClosestNode(y)
            np.addPoint(y)
            np.updateIdealNadir(y)
            self.removePoint(y)

    def updateNode(self, x):
        # type: (Node, tuple) -> bool
        # n = self
        rect = self.getRectangleSn()
        if less_equal(rect.max_corner, x):
            # x is rejected
            return False
        elif less_equal(x, rect.min_corner):
            # remove n and its whole sub-tree
            nparent = self.getParent()
            nparent.removeNode(self)
        elif greater_equal(rect.min_corner, x) or greater_equal(x, rect.max_corner):
            if self.isLeaf():
                for y in self.L:
                    if greater_equal(y, x):
                        # x is rejected
                        return False
                    elif greater_equal(x, y):
                        self.L.remove(y)
            else:
                for np in self.nodes:
                    if not np.updateNode(x):
                        return False
                    else:
                        if np.isEmptySolution():
                            self.removeNode(np)
                if self.numSubnodes() == 1:
                    # Remove node n and use np in place of n
                    np = self.getSubnode()
                    nparent = self.getParent()
                    nparent.replaceNode(self, np)
        else:
            # Skip this node
            None
        return True

    def updateIdealNadir(self, x):
        # type: (Node, tuple) -> None
        self.rect = self.getRectangleSn()
        updateIdeal = less(x, self.rect .min_corner)
        updateNadir = greater(x, self.rect .max_corner)
        self.rect.min_corner = x if updateIdeal else self.rect .min_corner
        self.rect.max_corner = x if updateNadir else self.rect .max_corner
        if updateIdeal or updateNadir:
            if not self.isRoot():
                np = self.getParent()
                np.updateIdealNadir(x)

    def S(self):
        if self.isLeaf():
            return set(self.L)
        else:
            temp = set()
            for i in self.nodes:
                temp.union(i.S())
