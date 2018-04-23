import sys
import resource
import __builtin__

from rectangle import *
from point import *


VERBOSE = True
VERBOSE = False

if VERBOSE:
    # Verbose print (stdout)
    def vprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        for arg in args:
            print arg,
        print


    # Error print (stderr)
    def eprint(*args):
        for arg in args:
            print >> sys.stderr, arg
        print >> sys.stderr

else:
    vprint = lambda *a: None  # do-nothing function
    eprint = lambda *a: None  # do-nothing function


class NDTree:
    # root: Node
    def __init__(self, MAX_P=2, MIN_CH=2):
        # type: (Node, int, int) -> None
        self.root = None
        self.MAX_POINTS = MAX_P
        self.MIN_CHILDREN = MIN_CH

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

    # Membership
    def __contains__(self, p):
        # type: (NDTree, tuple) -> bool
        return self.root.hasPointRec(p) if self.root is not None else False
        # return item in self.root

    # Printers
    def __repr__(self):
        return self.root.toStrRec(0) if self.root is not None else ""

    def __str__(self):
        return self.root.toStrRec(0) if self.root is not None else ""

    # Report functions
    def report(self):
        self.root.reportRec() if self.root is not None else ""

    def getPoints(self):
        # type: (NDTree) -> set
        points = self.root.getPointsRec() if self.root is not None else set()
        return points

    def removePoint(self, p):
        # type: (NDTree, tuple) -> None
        self.root.removePointRec(p) if self.root is not None else None

    def update(self, p):
        # type: (NDTree, tuple) -> None
        n = self.root
        if n is None:
            n = Node(MAX_P=self.MAX_POINTS, MIN_CH=self.MIN_CHILDREN)
            n.insert(p)
        else:
            n, update = n.updateNode(p)
            if update:
                n.insert(p)
        self.root = n

class Node:
    # nodes: list(1,..,n) of nodes
    # rect: Rectangle
    # L: list() of solutions

    def __init__(self, parent=None, MAX_P=2, MIN_CH=2):
        # type: (Node, Node, int, int) -> None
        # zero = (0, )
        self.rect = None
        parent.addNode(self) if parent is not None else None
        self.setParent(parent)
        self.nodes = []
        self.L = []
        self.MAX_POINTS = MAX_P
        self.MIN_CHILDREN = MIN_CH

    # Membership function
    def hasPoint(self, x):
        # type: (Node, tuple) -> bool
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
            # _string += ", " if i < (len(self.L)-1) else ""
        # _string += "]\n"
        return _string

    def toStrRec(self, nesting_level=0):
        # type: (Node, int) -> str
        if self.isLeaf():
            return self.toStr(nesting_level)
        else:
            _strings = [x.toStrRec(nesting_level + 1) for x in self.nodes]
            return "\n".join(_strings)

    def __repr__(self):
        # type: (Node) -> str
        return self.toStrRec(0)

    def __str__(self):
        # type: (Node) -> str
        return self.toStrRec(0)

    # Report functions
    def report(self):
        vprint('\tCurrent ', id(self))  # self type(self).__name__
        vprint('\tParent ', id(self.parent))  # self.parent type(self.parent).__name__
        vprint('\tNum Successors ', len(self.nodes))
        vprint('\tSuccessors ', [id(n) for n in self.nodes])
        vprint('\tNum Points ', len(self.L))
        vprint('\tPoints ', self.L)
        vprint('\tRect ', str(self.rect))

    def reportRec(self):
        self.report()
        vprint('\n')
        [n.reportRec() for n in self.nodes]

    # Functions for checking the type of node
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
        nodes = set()
        for n in self.nodes:
            nodes = nodes.union(n.getSubnodesRec())
        return nodes.union(self.getSubnodes())
      
    def numSubnodes(self):
        # type: (Node) -> int
        return len(self.nodes)

    def isEmptySolution(self):
        # type: (Node) -> bool
        vprint("None") if self is None else None
        return (self is None) or \
               ((self.numPoints() == 0) and (self.numSubnodes() == 0))

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
        points = set()
        for n in self.nodes:
            points = points.union(n.getPointsRec())
        return points.union(self.getPoints())

    # Set of points
    def S(self):
        # type: (Node) -> set
        vprint("Node " + str(self))
        # if n == leaf, S(n) == L(n)
        if self.isLeaf():
            vprint("L " + str(self.L))
            return set(self.L)
        # if n == internal, S(n) == U S(m) for all m in descendent(n)
        else:
            temp_list = [i.S() for i in self.nodes]
            temp = set.union(*temp_list)
            vprint("temp " + str(temp))
            return temp

    def numPoints(self):
        # type: (Node) -> int
        return len(self.L)

    def hasPoints(self):
        # type: (Node) -> bool
        vprint("None") if self is None else None
        return (self is not None) and (len(self.L) > 0)

    # Relationship functions
    def getParent(self):
        # type: (Node) -> Node
        return self.parent

    def setParent(self, parent):
        # type: (Node, Node) -> None
        self.parent = parent

    # Rectangle Operations
    def getRectangleSn(self):
        # type: (Node) -> Rectangle
        return self.rect

    def setRectangleSn(self, rect):
        # type: (Node, Rectangle) -> None
        self.rect = rect

    # NDTree operations
    def findClosestNode(self, x):
        # type: (Node, tuple) -> Node
        key_function = lambda node: node.rect.distanceToCenter(x)
        lsorted = sorted(self.nodes, key=key_function)
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
        # type: (Node) -> (tuple, int)
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
        vprint('Point Highest Avg Eucl Dist', y)
        vprint('New node with point ', y)
        np = Node(parent=self, MAX_P=self.MAX_POINTS, MIN_CH=self.MIN_CHILDREN)
        np.addPoint(y)
        np.updateIdealNadir(y)
        self.removePoint(y)
        vprint('Current status of self', self.L)
        vprint(self.toStrRec())
        while self.numSubnodes() < self.MIN_CHILDREN:
            y, _ = self.findPointHighestAverageEuclideanDistance()
            vprint('New node with point ', y)
            np = Node(parent=self, MAX_P=self.MAX_POINTS, MIN_CH=self.MIN_CHILDREN)
            np.addPoint(y)
            np.updateIdealNadir(y)
            self.removePoint(y)
            vprint('Current status of self', self.L)
            vprint(self.toStrRec())
        while self.hasPoints():
            # y = self.L.pop()
            y = self.L[0]
            np = self.findClosestNode(y)
            vprint('Closest node\n%s' % (np.toStrRec()))
            np.addPoint(y)
            np.updateIdealNadir(y)
            self.removePoint(y)
            vprint('Current status of self after removing point\n', self.L)
            vprint(self.toStrRec())
        vprint('After splitting\n', parent.toStrRec() if parent is not None else '')

    def updateNode(self, x):
        # type: (Node, tuple) -> (Node, bool)
        nout = self
        rect = self.getRectangleSn()
        vprint('Updating ', str(x))
        if less_equal(rect.max_corner, x):
            # x is rejected
            vprint('Point ', str(x), ' rejected (1)')
            return nout, False
        elif less_equal(x, rect.min_corner):
            # remove n and its whole sub-tree
            vprint('Removing node\n', self.toStrRec())
            nparent = self.getParent()
            nparent.removeNode(self) if nparent is not None else None
            # create empty node
            nout = Node(MAX_P=self.MAX_POINTS, MIN_CH=self.MIN_CHILDREN)
            vprint('After removing \n', nparent.toStrRec() if nparent is not None else '')
        elif less_equal(rect.min_corner, x) or less_equal(x, rect.max_corner):
            if self.isLeaf():
                for y in self.L:
                    #if greater_equal(y, x):
                    if less_equal(y, x):
                        # x is rejected
                        vprint('Point ', str(x), ' rejected (2)')
                        return nout, False
                    #elif greater_equal(x, y):
                    elif less_equal(x, y):
                        vprint('Removing point ', str(y))
                        self.removePoint(y)
            else:
                for np in self.nodes:
                    np, update = np.updateNode(x)
                    if not update:
                        return nout, False
                    else:
                        if np.isEmptySolution():
                            vprint('Removing node\n', np.toStrRec())
                            self.removeNode(np)
                if self.numSubnodes() == 1:
                    vprint('Simplifying\n', self.toStrRec())
                    # Remove node n and use np in place of n
                    np = self.getSubnode()
                    nparent = self.getParent()
                    nparent.replaceNode(self, np) if nparent is not None else None
        else:
            # Skip this node
            vprint('Skipping\n', self.toStrRec())
        return nout, True

    def updateIdealNadir(self, x):
        # type: (Node, tuple) -> None
        self.rect = self.getRectangleSn()
        if self.rect is None:
            # New Ideal and Nadir points
            # dim(ideal) == dim(nadir) == dim(x)
            n = dim(x)
            ideal = (float("inf"), ) * n
            nadir = (float("-inf"), ) * n
            # Delayed creation of Rectangle.
            # Before this point, we do not the dim(x)
            self.rect = Rectangle(ideal, nadir)
        else:
            ideal = self.rect.min_corner
            nadir = self.rect.max_corner

        # Test if the current rectangle already includes the components from x
        # (i.e., condition '<='/'>=' in the comparisons).
        # This comparison allows triggering the rectangle update recursively in parent nodes.
        updateIdeal = any(xi < ideali for xi, ideali in zip(x, ideal))
        updateNadir = any(xi > nadiri for xi, nadiri in zip(x, nadir))

        if updateIdeal or updateNadir:
            # We only effectively update ideal and nadir points if the components from x are strictly lesser or greater
            # than current components of the rectangle.
            # ideal = tuple(xi if xi < ideali else ideali for xi, ideali in zip(x, ideal))
            # nadir = tuple(xi if xi > nadiri else nadiri for xi, nadiri in zip(x, nadir))
            ideal = tuple(__builtin__.min(xi, ideali) for xi, ideali in zip(x, ideal))
            nadir = tuple(__builtin__.max(xi, nadiri) for xi, nadiri in zip(x, nadir))

            vprint_string = 'Updating rectangle ' + str(self.rect)
            self.rect.min_corner = ideal
            self.rect.max_corner = nadir
            vprint_string += ' to ' + str(self.rect)
            vprint(vprint_string)

            if not self.isRoot():
                np = self.getParent()
                np.updateIdealNadir(x)
        else:
            vprint_string = 'Rectangle ' + str(self.rect) + ' remains constant\n'
            vprint_string += 'Point tested: ' + str(x)
            vprint(vprint_string)