from rectangle import *
from point import *

VERBOSE=False
VERBOSE=True

if VERBOSE:
    def vprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        for arg in args:
            print arg,
        print
else:
    vprint = lambda *a: None  # do-nothing function

class NDTree:
    # root: Node
    def __init__(self):
        self.root = None

    # Membership
    def __contains__(self, x):
        #return item in self.root
        return self.root.hasPointRec(x)

    # Printers
    def __repr__(self):
        return self.root.toStrRec(0)

    def __str__(self):
        return self.root.toStrRec(0)

    # Report functions
    def report(self):
        self.root.reportRec()


    def getPoints(self):
        # type: (NDTree) -> set
        points = self.root.getPointsRec() if self.root is not None else set()
        return points

    def removePoint(self, p):
        # type: (NDTree, tuple) -> None
        self.root.removePointRec(p) if self.root is not None else None

    def update(self, p):
        # type: (NDTree, tuple) -> None
        if self.root is None:
            self.root = Node()
            self.root.insert(p)
        elif self.root.updateNode(p):
            self.root.insert(p)

    #TODO: Revise dynamicNonDominance function
    def dynamicNonDominance(self, p):
        # type: (NDTree, tuple) -> None
        set_points = self.getPoints()
        points_greater_than_p = [ppoint for ppoint in set_points if greater_equal(ppoint, p)]
        points_smaller_than_p = [ppoint for ppoint in set_points if greater_equal(p, ppoint)]
        if len(points_greater_than_p) == 0:
            #self.root.insertPoint(p)
            self.updateNode(p)
            for ppoint in points_smaller_than_p:
                #self.root.removePointRec(ppoint)
                self.removePoint(ppoint)

class Node:
    # nodes: list(1,..,n) of nodes
    # rect: Rectangle
    # L: list() of solutions
    MAX_POINTS = 4
    MIN_CHILDREN = 2
    def __init__(self, parent=None):
        zero = (0, )
        self.rect = Rectangle(zero, zero)
        if parent is not None: parent.addNode(self)
        self.setParent(parent)
        self.nodes = []
        self.L = []

    # Membership function
    def hasPoint(self, x):
        # type: (Node, tuple) -> bool
        # return item in self.rect
        return x in self.L

    def hasPointRec(self, x):
        # type: (Node, tuple) -> bool
        if self.isLeaf():
            return self.hasPoint(x)
        else:
            _hasPoints = [x.hasPointRec(x) for x in self.nodes]
            _hasPoint = True
            for i in _hasPoints:
                _hasPoint = _hasPoint and i
            return _hasPoint

    def __contains__(self, x):
        # type: (Node, tuple) -> bool
        return self.hasPointRec(x)

    # Printers
    def toStr(self, nesting_level=0):
        # type: (Node, int) -> str
        _string = "\t" * nesting_level
        _string += "["
        for i, x in enumerate(self.L):
            _string += str(x)
            _string += ", " if i < (len(self.L) - 1) else "]"
            #_string += ", " if i < (len(self.L)-1) else ""
        #_string += "]\n"
        return _string

    def toStrRec(self, nesting_level=0):
        # type: (Node, int) -> str
        if self.isLeaf():
            return self.toStr(nesting_level)
        else:
            _strings = [x.toStrRec(nesting_level+1) for x in self.nodes]
            return "\n".join(_strings)

    def __repr__(self):
        return self.toStrRec(0)

    def __str__(self):
        return self.toStrRec(0)

    # Report functions
    def report(self):
        vprint('\tCurrent ', id(self) ) #self type(self).__name__
        vprint('\tParent ', id(self.parent)) #self.parent type(self.parent).__name__
        vprint('\tNum Successors ', len(self.nodes))
        vprint('\tSuccessors ', [id(n) for n in self.nodes])
        vprint('\tNum Points ', len(self.L))
        vprint('\tPoints ', self.L)
        vprint('\tRect ', str(self.rect))

    def reportRec(self):
        # type: (Node) -> None
        self.report()
        vprint('\n')
        [n.reportRec() for n in self.nodes]

    # Rectangle
    def getRectangleSn(self):
        # type: (Node) -> Rectangle
        sn = self.S()
        vprint('S(n) ', str(sn))
        #key_function = lambda x, y: x if min(x,y) else y
        #sn_sorted = sorted(sn, key=key_function)
        #sn_sorted = sorted(sn, key=min)
        sn_sorted = sorted(sn, key=norm)

        # Ideal point
        min_c = sn_sorted[0]
        # Nadir point
        max_c = sn_sorted.pop()
        self.rect = Rectangle(min_c, max_c)
        vprint('Rectangle ', str(self.rect))
        return self.rect

    # Functions for checking the type of node
    def isEmptySolution(self):
        # type: (Node) -> bool
        return len(self.L) == 0

    def isRoot(self):
        # type: (Node) -> bool
        return self.parent is None

    def isLeaf(self):
        # type: (Node) -> bool
        return self.numSubnodes() == 0

    # Node operations
    def addNode(self, n, pos=-1):
        # type: (Node, Node, int) -> None
        if n not in self.L:
            n.setParent(self)
            if (pos >= 0) and (pos < len(self.nodes)):
                self.nodes.insert(pos, n)
            else:
                self.nodes.append(n)

    def removeNode(self, n):
        # type: (Node, Node) -> None
        if n in self.nodes:
            self.nodes.remove(n)
            del n

    def removeNodeRec(self, n):
        # type: (Node, Node) -> None
        [np.removeNodeRec(n) for np in self.nodes]
        self.removeNode(n)

    def replaceNode(self, n, np):
        # type: (Node, Node, Node) -> None
        if n in self.nodes:
            index = self.nodes.index(n)
            self.addNode(np, index)
            self.removeNode(n)

    def replaceNodeRec(self, n, np):
        # type: (Node, Node) -> None
        [x.replaceNodeRec(n, np) for x in self.nodes]
        self.replaceNode(n, np)

    def getSubnode(self, pos=0):
        # type: (Node, int) -> Node
        return self.nodes[pos]

    def getSubnodes(self):
        # type: (Node) -> set
        return set(self.nodes)

    def getSubnodesRec(self):
        # type: (Node) -> set
        nodes = set(x.getSubnodesRec() for x in self.nodes)
        return nodes.union(self.getSubnodes())

    def numSubnodes(self):
        # type: (Node) -> int
        return len(self.nodes)

    # Point operations
    def addPoint(self, x, pos=-1):
        # type: (Node, tuple, int) -> None
        if (pos >= 0) and (pos < len(self.nodes)):
            self.L.insert(pos, x)
        else:
            self.L.append(x)

    def removePoint(self, x):
        # type: (Node, tuple) -> None
        if x in self.L:
            self.L.remove(x)
            del x

    def removePointRec(self, x):
        # type: (Node, tuple) -> None
        [n.removePointRec(x) for n in self.nodes]
        self.removePoint(x)

    def replacePoint(self, x, xp):
        # type: (Node, tuple, tuple) -> None
        if x in self.L:
            index = self.L.index(x)
            self.addPoint(xp, index)
            self.removePoint(x)

    def replacePointRec(self, x, xp):
        # type: (Node, tuple, tuple) -> None
        [n.replacePointRec(x, xp) for n in self.nodes]
        self.replacePoint(x, xp)

    def getPoint(self, pos=0):
        # type: (Node, int) -> tuple
        return self.L[pos]

    def getPoints(self):
        # type: (Node) -> set
        return set(self.L)

    def getPointsRec(self):
        # type: (Node) -> set
        points = set(n.getPointsRec() for n in self.nodes)
        return points.union(self.getPoints())

    def numPoints(self):
        # type: (Node) -> int
        return len(self.L)

    # Relationship functions
    def getParent(self):
        # type: (Node) -> Node
        return self.parent

    def setParent(self, parent):
        # type: (Node, Node) -> None
        self.parent = parent

    # NDTree operations
    def findClosestNode(self, x):
        # type: (Node, tuple) -> Node
        key_function = lambda node: node.rect.distanceToCenter(x)
        lsorted = sorted(self.nodes, key=key_function)
        #lsorted = sorted(self.nodes, key=Rectangle.distanceToCenter(_, x))
        return lsorted[0]

    def insert(self, x):
        # type: (Node, tuple) -> None
        vprint('Inserting\n', x)
        if self.isLeaf():
            self.addPoint(x)
            self.updateIdealNadir(x)
            vprint('Leaf\n', self.toStrRec())
            if self.numPoints() > self.MAX_POINTS:
                self.split()
        else:
            vprint('Internal\n', self.toStrRec())
            np = self.findClosestNode(x)
            vprint('Closest node\n', np.toStrRec())
            vprint('with rectangle ', np.getRectangleSn())
            np.insert(x)

    def findPointHighestAverageEuclideanDistance(self):
        # type: (Node) -> (Node, int)
        #y = Node()
        d = dim(self.L[0]) if self.numPoints() > 0 else 1
        y = (0,) * d
        mean_max_distance = 0
        for yp in self.L:
            max_distance = 0
            for xp in self.L:
                max_distance += distance(yp, xp)
            temp_mean_max_distance = max_distance / (self.numPoints() - 1)
            if temp_mean_max_distance > mean_max_distance:
                mean_max_distance = temp_mean_max_distance
                y = yp
        return y, mean_max_distance

    def split(self):
        # type: (Node) -> None
        parent = self.getParent()
        vprint('Splitting\n', self.toStrRec())
        y, _ = self.findPointHighestAverageEuclideanDistance()
        vprint('Point Highets Avg Eucl Dist', y)
        np = Node(self)
        #self.addNode(np)
        np.addPoint(y)
        vprint('New node\n%s\nwith y: %s' % (np.toStrRec(), y))
        np.updateIdealNadir(y)
        self.removePoint(y)
        vprint('Adding subnode\n', np.toStrRec())
        vprint('Current status of\n', self.toStrRec())
        while self.numSubnodes() < self.MIN_CHILDREN:
            y, _ = self.findPointHighestAverageEuclideanDistance()
            np = Node(self)
            #self.addNode(np)
            np.addPoint(y)
            vprint('New node\n%s\nwith y: %s' % (np.toStrRec(), y))
            np.updateIdealNadir(y)
            self.removePoint(y)
            vprint('Adding subnode\n', np.toStrRec())
            vprint('Current status of\n', self.toStrRec())
        while not self.isEmptySolution():
            #y = self.L.pop()
            #y, _ = self.findPointHighestAverageEuclideanDistance()
            y = self.L[0]
            np = self.findClosestNode(y)
            vprint('Closest node\n%s' % (np.toStrRec()))
            np.addPoint(y)
            np.updateIdealNadir(y)
            vprint('Removing point %s from node\n%s' % (y, self.toStrRec()))
            self.removePoint(y)
            vprint('Current status of\n', self.toStrRec())
        vprint('After splitting\n', parent.toStrRec() if parent is not None else '')

    def updateNode(self, x):
        # type: (Node, tuple) -> bool
        # n = self
        rect = self.getRectangleSn()
        vprint('Updating ', str(x))
        if greater_equal(rect.max_corner, x):
            # x is rejected
            vprint('Point ', str(x), ' rejected (1)')
            return False
        elif greater_equal(x, rect.min_corner):
            # remove n and its whole sub-tree
            vprint('Removing node\n', self.toStrRec())
            nparent = self.getParent()
            nparent.removeNode(self) if nparent is not None else None
            vprint('After removing \n', nparent.toStrRec() if nparent is not None else '')
        elif greater_equal(rect.min_corner, x) or greater_equal(x, rect.max_corner):
            if self.isLeaf():
                for y in self.L:
                    if greater_equal(y, x):
                        # x is rejected
                        vprint('Point ', str(x), ' rejected (2)')
                        return False
                    elif greater_equal(x, y):
                        vprint('Removing point ', str(y))
                        self.removePoint(y)
            else:
                for np in self.nodes:
                    if not np.updateNode(x):
                        return False
                    else:
                        if np.isEmptySolution():
                            vprint('Removing node\n', np.toStrRec())
                            self.removeNode(np)
                if self.numSubnodes() == 1:
                    vprint('Simplifying\n', self.toStrRec())
                    # Remove node n and use np in place of n
                    np = self.getSubnode()
                    nparent = self.getParent()
                    nparent.replaceNode(self, np)
        else:
            # Skip this node
            vprint('Skipping\n', self.toStrRec())
            None
        return True

    def updateIdealNadir(self, x):
        # type: (Node, tuple) -> None
        self.rect = self.getRectangleSn()
        updateIdeal = less(x, self.rect.min_corner)
        updateNadir = greater(x, self.rect.max_corner)
        vprint_string = 'Updating rectangle ' + str(self.rect)
        self.rect.min_corner = x if updateIdeal else self.rect.min_corner
        self.rect.max_corner = x if updateNadir else self.rect.max_corner
        vprint_string += ' to ' + str(self)
        if updateIdeal or updateNadir:
            if not self.isRoot():
                np = self.getParent()
                np.updateIdealNadir(x)
        else:
            vprint_string = 'Rectangle ' + str(self.rect) + ' remains constant\n'
            vprint_string += 'Point tested: ' + str(x)
        vprint(vprint_string)

    def S(self):
        # type: (Node) -> set
        #vprint("Node " + str(self))
        if self.isLeaf():
            #vprint("L " + str(self.L))
            return set(self.L)
        else:
            temp = set()
            for i in self.nodes:
                temp = temp.union(i.S())
                #vprint("temp " + str(temp))
            return temp
