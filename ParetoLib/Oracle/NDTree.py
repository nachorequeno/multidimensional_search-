import sys
import resource
import __builtin__

from ParetoLib.Geometry.Rectangle import *
from ParetoLib.Geometry.Point import *

# from ParetoLib.Oracle import #vprint
from . import vprint


class NDTree:
    # root: Node
    def __init__(self, MAX_P=2, MIN_CH=2):
        # type: (NDTree, int, int) -> None
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
        return self.root.hasPointRec(p) if not self.isEmpty() else False
        # return item in self.root

    # Printers
    def __repr__(self):
        # type: (NDTree) -> str
        return self.root.toStrRec(0) if not self.isEmpty() else ""

    def __str__(self):
        # type: (NDTree) -> str
        return self.root.toStrRec(0) if not self.isEmpty() else ""

    # Equality functions
    def __eq__(self, other):
        # type: (NDTree, NDTree) -> bool
        sameContent = (other.MAX_POINTS == self.MAX_POINTS) and \
                      (other.MIN_CHILDREN == self.MIN_CHILDREN)
        return (hash(self.root) == hash(other.root)) and \
               sameContent

    def __ne__(self, other):
        # type: (NDTree, NDTree) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (NDTree) -> int
        return hash((self.root, self.MAX_POINTS, self.MIN_CHILDREN))

    # Report functions
    def report(self):
        self.root.reportRec() if not self.isEmpty() else ""

    def dim(self):
        # type: (NDTree) -> int
        rect = self.getRectangle()
        if rect is not None:
            return Rectangle.dim(rect)
        else:
            return 0

    def isEmpty(self):
        # type: (NDTree) -> bool
        return self.root is None

    def getRectangle(self):
        # type: (NDTree) -> Rectangle
        # return self.root.getRectangleSn() if not self.isEmpty() else None
        return self.root.getRectangleSn() if not self.isEmpty() else Rectangle()

    def getPoints(self):
        # type: (NDTree) -> set
        points = self.root.getPointsRec() if self.root is not None else set()
        return points

    def removePoint(self, p):
        # type: (NDTree, tuple) -> None
        self.root.removePointRec(p) if self.root is not None else None

    def updatePoint(self, p):
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

    def dominates(self, p):
        # type: (NDTree, tuple) -> True
        # Returns 'True' if p is dominated by any point stored in the Pareto archive
        return self.root.dominates(p)


class Node:
    # nodes: list(1,..,n) of nodes
    # rect: Rectangle
    # L: list() of solutions

    def __init__(self, parent=None, MAX_P=2, MIN_CH=2):
        # type: (Node, Node, int, int) -> None
        # zero = (0, )
        self.rect = None
        self.parent = parent
        self.nodes = []
        self.L = []
        self.MAX_POINTS = MAX_P
        self.MIN_CHILDREN = MIN_CH
        parent.addNode(self) if parent is not None else None
        # self.setParent(parent)

    # Membership function
    def hasPoint(self, x):
        # type: (Node, tuple) -> bool
        return x in self.L

    def hasPointRec(self, x):
        # type: (Node, tuple) -> bool
        if self.isLeaf():
            return self.hasPoint(x)
        else:
            _hasPoint = (n.hasPointRec(x) for n in self.nodes)
            return any(_hasPoint)

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
            _strings = (x.toStrRec(nesting_level + 1) for x in self.nodes)
            return "\n".join(_strings)

    def __repr__(self):
        # type: (Node) -> str
        return self.toStrRec(0)

    def __str__(self):
        # type: (Node) -> str
        return self.toStrRec(0)

    # Equality functions
    def __eq__(self, other):
        # type: (Node, Node) -> bool
        eqRect = (hash(other.rect) == hash(self.rect))
        eqParent = (hash(other.parent) == hash(self.parent))
        sameContent = (other.nodes == self.nodes) and \
                      (other.L == self.L) and \
                      (other.MAX_POINTS == self.MAX_POINTS) and \
                      (other.MIN_CHILDREN == self.MIN_CHILDREN)

        return eqRect and eqParent and sameContent

    def __ne__(self, other):
        # type: (Node, Node) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Node) -> int
        # hash cannot be computed over 'list'; use 'tuple' instead
        # return hash((self.rect, self.parent, tuple(self.nodes), tuple(self.L), self.MAX_POINTS, self.MIN_CHILDREN))
        return hash((self.rect, self.parent, tuple(self.L), self.MAX_POINTS, self.MIN_CHILDREN))

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
        #vprint('\n')
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
        if n not in self.nodes:
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
        [npr.removeNodeRec(n) for npr in self.nodes]
        self.removeNode(n)

    def replaceNode(self, n, npr):
        # type: (Node, Node, Node) -> None
        if n in self.nodes:
            index = self.nodes.index(n)
            self.addNode(npr, index)
            self.removeNode(n)

    def replaceNodeRec(self, n, npr):
        # type: (Node, Node) -> None
        [x.replaceNodeRec(n, npr) for x in self.nodes]
        self.replaceNode(n, npr)

    def getSubnode(self, pos=0):
        # type: (Node, int) -> Node
        return self.nodes[pos]

    def getSubnodes(self):
        # type: (Node) -> set
        return set(self.nodes)

    def getSubnodesRec(self):
        # type: (Node) -> set
        subnode_list = [n.getSubnodesRec() for n in self.nodes]
        nodes = set.union(*subnode_list)
        return nodes.union(self.getSubnodes())

    def numSubnodes(self):
        # type: (Node) -> int
        return len(self.nodes)

    def isEmptySolution(self):
        # type: (Node) -> bool
        return (self is None) or \
               ((self.numPoints() == 0) and (self.numSubnodes() == 0))

    # Point operations
    def addPoint(self, x, pos=-1):
        # type: (Node, tuple, int) -> None
        if (pos >= 0) and (pos < len(self.L)):
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

    #def getPointsRec(self):
    #    # type: (Node) -> set
    #    pointrec_list = [n.getPointsRec() for n in self.nodes]
    #    points = set.union(*pointrec_list)
    #    return points.union(self.getPoints())

    def getPointsRec(self):
        # type: (Node) -> set
        return self.S()

    # Set of points
    def S(self):
        # type: (Node) -> set
        # if n == leaf, S(n) == L(n)
        if self.isLeaf():
            return set(self.L)
        # if n == internal, S(n) == U S(m) for all m in descendent(n)
        else:
            temp_list = (i.S() for i in self.nodes)
            temp = set.union(*temp_list)
            return temp

    def numPoints(self):
        # type: (Node) -> int
        return len(self.L)

    def hasPoints(self):
        # type: (Node) -> bool
        #vprint("None") if self is None else None
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
        if self.isLeaf():
            self.addPoint(x)
            self.updateIdealNadir(x)
            if self.numPoints() > self.MAX_POINTS:
                self.split()
        else:
            # Internal point
            npr = self.findClosestNode(x)
            npr.insert(x)

    def findPointHighestAverageEuclideanDistance(self):
        # type: (Node) -> (tuple, int)
        d = dim(self.L[0]) if self.numPoints() > 0 else 1
        y = (0,) * d
        mean_max_distance = 0
        for yp in self.L:
            dist_list = (distance(yp, xp) for xp in self.L)
            max_distance = sum(dist_list)
            temp_mean_max_distance = max_distance / (self.numPoints() - 1)
            if temp_mean_max_distance > mean_max_distance:
                mean_max_distance = temp_mean_max_distance
                y = yp
        return y, mean_max_distance

    def split(self):
        # type: (Node) -> None
        y, _ = self.findPointHighestAverageEuclideanDistance()
        npr = Node(parent=self, MAX_P=self.MAX_POINTS, MIN_CH=self.MIN_CHILDREN)
        npr.addPoint(y)
        npr.updateIdealNadir(y)
        self.removePoint(y)
        while self.numSubnodes() < self.MIN_CHILDREN:
            y, _ = self.findPointHighestAverageEuclideanDistance()
            npr = Node(parent=self, MAX_P=self.MAX_POINTS, MIN_CH=self.MIN_CHILDREN)
            npr.addPoint(y)
            npr.updateIdealNadir(y)
            self.removePoint(y)
        while self.hasPoints():
            # y = self.L.pop()
            y = self.L[0]
            npr = self.findClosestNode(y)
            npr.addPoint(y)
            npr.updateIdealNadir(y)
            self.removePoint(y)

    def updateNode(self, x):
        # type: (Node, tuple) -> (Node, bool)
        nout = self
        rect = self.getRectangleSn()
        if less_equal(rect.max_corner, x):
            # x is rejected
            return nout, False
        elif less_equal(x, rect.min_corner):
            # remove n and its whole sub-tree
            nparent = self.getParent()
            nparent.removeNode(self) if nparent is not None else None
            # create empty node
            nout = Node(MAX_P=self.MAX_POINTS, MIN_CH=self.MIN_CHILDREN)
        elif less_equal(rect.min_corner, x) or less_equal(x, rect.max_corner):
            if self.isLeaf():
                for y in self.L:
                    if less_equal(y, x):
                        # x is rejected
                        return nout, False
                    elif less_equal(x, y):
                        # y is removed
                        self.removePoint(y)
            else:
                for npr in self.nodes:
                    npr, update = npr.updateNode(x)
                    if not update:
                        return nout, False
                    elif npr.isEmptySolution():
                        self.removeNode(npr)
                if self.numSubnodes() == 1:
                    # Remove node n and use npr in place of n
                    npr = self.getSubnode()
                    nparent = self.getParent()
                    nparent.replaceNode(self, npr) if nparent is not None else None
                    #nparent.replaceNode(self, npr) if nparent is not None else self = npr
        #else:
            # Skip this node
        return nout, True

    def updateIdealNadir(self, x):
        # type: (Node, tuple) -> None
        self.rect = self.getRectangleSn()
        if self.rect is None:
            # New Ideal and Nadir points
            # dim(ideal) == dim(nadir) == dim(x)
            # n = Point.dim(x)
            n = dim(x)
            ideal = (float("inf"),) * n
            nadir = (float("-inf"),) * n
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

            self.rect.min_corner = ideal
            self.rect.max_corner = nadir

            if not self.isRoot():
                npr = self.getParent()
                npr.updateIdealNadir(x)

    def dominates(self, x):
        # type: (Node, tuple) -> bool
        # Returns 'True' if x is dominated by any point stored in the Pareto archive
        # Use the rectangle associated to the Node for speeding up the evaluation
        rect = self.getRectangleSn()
        if less_equal(rect.max_corner, x):
            # x is dominated by the Pareto front
            return True
        elif less_equal(rect.min_corner, x) or less_equal(x, rect.max_corner):
            # x is inside the rectangle enclosing the Pareto front
            return any(n.dominates(x) for n in self.nodes)
        #elif less_equal(x, rect.min_corner):
            # x dominates the Pareto front
            # return False
        else:
            return False