import sys
import resource
import __builtin__

from ParetoLib.Geometry.Rectangle import *
from ParetoLib.Geometry.Point import *


class NDTree:
    # The data structure definition, notation and algorithms are extracted from the paper
    # 'ND-Tree-based update: a Fast Algorithm for the Dynamic Non-Dominance Problem'
    # https://ieeexplore.ieee.org/document/8274915/

    # root: Node
    def __init__(self, max_points=2, min_children=2):
        # type: (NDTree, int, int) -> None
        self.root = None
        self.max_points = max_points
        self.min_children = min_children

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

    # Membership
    def __contains__(self, p):
        # type: (NDTree, tuple) -> bool
        return self.root.has_point_rec(p) if not self.is_empty() else False
        # return item in self.root

    # Printers
    def __repr__(self):
        # type: (NDTree) -> str
        return self.root.to_str_rec(0) if not self.is_empty() else ''

    def __str__(self):
        # type: (NDTree) -> str
        return self.root.to_str_rec(0) if not self.is_empty() else ''

    # Equality functions
    def __eq__(self, other):
        # type: (NDTree, NDTree) -> bool
        sameContent = (other.max_points == self.max_points) and \
                      (other.min_children == self.min_children)
        return (hash(self.root) == hash(other.root)) and sameContent

    def __ne__(self, other):
        # type: (NDTree, NDTree) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (NDTree) -> int
        return hash((self.root, self.max_points, self.min_children))

    # Report functions
    def report(self):
        self.root.report_rec() if not self.is_empty() else ''

    def dim(self):
        # type: (NDTree) -> int
        rect = self.get_rectangle()
        if rect is not None:
            return Rectangle.dim(rect)
        else:
            return 0

    def is_empty(self):
        # type: (NDTree) -> bool
        return self.root is None

    def get_rectangle(self):
        # type: (NDTree) -> Rectangle
        # return self.root.getRectangleSn() if not self.isEmpty() else None
        return self.root.get_rectangle_sn() if not self.is_empty() else Rectangle()

    def get_points(self):
        # type: (NDTree) -> set
        points = self.root.get_points_rec() if self.root is not None else set()
        return points

    def remove_point(self, p):
        # type: (NDTree, tuple) -> None
        self.root.remove_point_rec(p) if self.root is not None else None

    def update_point(self, p):
        # type: (NDTree, tuple) -> None
        n = self.root
        if n is None:
            n = Node(max_points=self.max_points, min_children=self.min_children)
            n.insert(p)
        else:
            n, update = n.update_node(p)
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

    def __init__(self, parent=None, max_points=2, min_children=2):
        # type: (Node, Node, int, int) -> None
        # zero = (0, )
        self.rect = None
        self.parent = parent
        self.nodes = []
        self.L = []
        self.max_points = max_points
        self.min_children = min_children
        parent.add_node(self) if parent is not None else None
        # self.setParent(parent)

    # Membership function
    def has_point(self, x):
        # type: (Node, tuple) -> bool
        return x in self.L

    def has_point_rec(self, x):
        # type: (Node, tuple) -> bool
        if self.is_leaf():
            return self.has_point(x)
        else:
            _hasPoint = (n.has_point_rec(x) for n in self.nodes)
            return any(_hasPoint)

    def __contains__(self, x):
        # type: (Node, tuple) -> bool
        return self.has_point_rec(x)

    # Printers
    def to_str(self, nesting_level=0):
        # type: (Node, int) -> str
        _string = '\t' * nesting_level
        _string += '['
        for i, x in enumerate(self.L):
            _string += str(x)
            _string += ', ' if i < (len(self.L) - 1) else ']'
            # _string += ', ' if i < (len(self.L)-1) else ''
        # _string += ']\n'
        return _string

    def to_str_rec(self, nesting_level=0):
        # type: (Node, int) -> str
        if self.is_leaf():
            return self.to_str(nesting_level)
        else:
            _strings = (x.to_str_rec(nesting_level + 1) for x in self.nodes)
            return '\n'.join(_strings)

    def __repr__(self):
        # type: (Node) -> str
        return self.to_str_rec(0)

    def __str__(self):
        # type: (Node) -> str
        return self.to_str_rec(0)

    # Equality functions
    def __eq__(self, other):
        # type: (Node, Node) -> bool
        eqRect = (hash(other.rect) == hash(self.rect))
        eqParent = (hash(other.parent) == hash(self.parent))
        sameContent = (other.nodes == self.nodes) and \
                      (other.L == self.L) and \
                      (other.max_points == self.max_points) and \
                      (other.min_children == self.min_children)

        return eqRect and eqParent and sameContent

    def __ne__(self, other):
        # type: (Node, Node) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Node) -> int
        # hash cannot be computed over 'list'; use 'tuple' instead
        # return hash((self.rect, self.parent, tuple(self.nodes), tuple(self.L), self.MAX_POINTS, self.MIN_CHILDREN))
        return hash((self.rect, self.parent, tuple(self.L), self.max_points, self.min_children))

    # Report functions
    def report(self):
        print('\tCurrent ', id(self))  # self type(self).__name__
        print('\tParent ', id(self.parent))  # self.parent type(self.parent).__name__
        print('\tNum Successors ', len(self.nodes))
        print('\tSuccessors ', [id(n) for n in self.nodes])
        print('\tNum Points ', len(self.L))
        print('\tPoints ', self.L)
        print('\tRect ', str(self.rect))

    def report_rec(self):
        self.report()
        # print('\n')
        [n.report_rec() for n in self.nodes]

    # Functions for checking the type of node
    def is_root(self):
        # type: (Node) -> bool
        return self.parent is None

    def is_leaf(self):
        # type: (Node) -> bool
        return self.num_subnodes() == 0

    # Node operations
    def add_node(self, n, pos=-1):
        # type: (Node, Node, int) -> None
        if n not in self.nodes:
            n.set_parent(self)
            if (pos >= 0) and (pos < len(self.nodes)):
                self.nodes.insert(pos, n)
            else:
                self.nodes.append(n)

    def remove_node(self, n):
        # type: (Node, Node) -> None
        if n in self.nodes:
            self.nodes.remove(n)
            del n

    def remove_node_rec(self, n):
        # type: (Node, Node) -> None
        [npr.remove_node_rec(n) for npr in self.nodes]
        self.remove_node(n)

    def replace_node(self, n, npr):
        # type: (Node, Node, Node) -> None
        if n in self.nodes:
            index = self.nodes.index(n)
            self.add_node(npr, index)
            self.remove_node(n)

    def replace_node_rec(self, n, npr):
        # type: (Node, Node) -> None
        [x.replace_node_rec(n, npr) for x in self.nodes]
        self.replace_node(n, npr)

    def get_subnode(self, pos=0):
        # type: (Node, int) -> Node
        return self.nodes[pos]

    def get_subnodes(self):
        # type: (Node) -> set
        return set(self.nodes)

    def get_subnodes_rec(self):
        # type: (Node) -> set
        subnode_list = [n.get_subnodes_rec() for n in self.nodes]
        nodes = set.union(*subnode_list)
        return nodes.union(self.get_subnodes())

    def num_subnodes(self):
        # type: (Node) -> int
        return len(self.nodes)

    def is_empty_solution(self):
        # type: (Node) -> bool
        return (self is None) or \
               ((self.num_points() == 0) and (self.num_subnodes() == 0))

    # Point operations
    def add_point(self, x, pos=-1):
        # type: (Node, tuple, int) -> None
        if (pos >= 0) and (pos < len(self.L)):
            self.L.insert(pos, x)
        else:
            self.L.append(x)

    def remove_point(self, x):
        # type: (Node, tuple) -> None
        if x in self.L:
            self.L.remove(x)
            del x

    def remove_point_rec(self, x):
        # type: (Node, tuple) -> None
        [n.remove_point_rec(x) for n in self.nodes]
        self.remove_point(x)

    def replace_point(self, x, xp):
        # type: (Node, tuple, tuple) -> None
        if x in self.L:
            index = self.L.index(x)
            self.add_point(xp, index)
            self.remove_point(x)

    def replace_point_rec(self, x, xp):
        # type: (Node, tuple, tuple) -> None
        [n.replace_point_rec(x, xp) for n in self.nodes]
        self.replace_point(x, xp)

    def get_point(self, pos=0):
        # type: (Node, int) -> tuple
        return self.L[pos]

    def get_points(self):
        # type: (Node) -> set
        return set(self.L)

    # def getPointsRec(self):
    #    # type: (Node) -> set
    #    pointrec_list = [n.getPointsRec() for n in self.nodes]
    #    points = set.union(*pointrec_list)
    #    return points.union(self.get_points())

    def get_points_rec(self):
        # type: (Node) -> set
        return self.s()

    # Set of points
    def s(self):
        # type: (Node) -> set
        # if n == leaf, S(n) == L(n)
        if self.is_leaf():
            return set(self.L)
        # if n == internal, S(n) == U S(m) for all m in descendent(n)
        else:
            temp_list = (i.s() for i in self.nodes)
            temp = set.union(*temp_list)
            return temp

    def num_points(self):
        # type: (Node) -> int
        return len(self.L)

    def has_points(self):
        # type: (Node) -> bool
        # print('None') if self is None else None
        return (self is not None) and (len(self.L) > 0)

    # Relationship functions
    def get_parent(self):
        # type: (Node) -> Node
        return self.parent

    def set_parent(self, parent):
        # type: (Node, Node) -> None
        self.parent = parent

    # Rectangle Operations
    def get_rectangle_sn(self):
        # type: (Node) -> Rectangle
        return self.rect

    def set_rectangle_sn(self, rect):
        # type: (Node, Rectangle) -> None
        self.rect = rect

    # NDTree operations
    def find_closest_node(self, x):
        # type: (Node, tuple) -> Node
        lsorted = sorted(self.nodes, key=lambda node: node.rect.distance_to_center(x))
        return lsorted[0]

    def insert(self, x):
        # type: (Node, tuple) -> None
        if self.is_leaf():
            self.add_point(x)
            self.update_ideal_nadir(x)
            if self.num_points() > self.max_points:
                self.split()
        else:
            # Internal point
            npr = self.find_closest_node(x)
            npr.insert(x)

    def find_point_highest_average_euclidean_distance(self):
        # type: (Node) -> (tuple, int)
        d = dim(self.L[0]) if self.num_points() > 0 else 1
        y = (0,) * d
        mean_max_distance = 0
        for yp in self.L:
            dist_list = (distance(yp, xp) for xp in self.L)
            max_distance = sum(dist_list)
            temp_mean_max_distance = max_distance / (self.num_points() - 1)
            if temp_mean_max_distance > mean_max_distance:
                mean_max_distance = temp_mean_max_distance
                y = yp
        return y, mean_max_distance

    def split(self):
        # type: (Node) -> None
        y, _ = self.find_point_highest_average_euclidean_distance()
        npr = Node(parent=self, max_points=self.max_points, min_children=self.min_children)
        npr.add_point(y)
        npr.update_ideal_nadir(y)
        self.remove_point(y)
        while self.num_subnodes() < self.min_children:
            y, _ = self.find_point_highest_average_euclidean_distance()
            npr = Node(parent=self, max_points=self.max_points, min_children=self.min_children)
            npr.add_point(y)
            npr.update_ideal_nadir(y)
            self.remove_point(y)
        while self.has_points():
            # y = self.L.pop()
            y = self.L[0]
            npr = self.find_closest_node(y)
            npr.add_point(y)
            npr.update_ideal_nadir(y)
            self.remove_point(y)

    def update_node(self, x):
        # type: (Node, tuple) -> (Node, bool)
        nout = self
        rect = self.get_rectangle_sn()
        if less_equal(rect.max_corner, x):
            # x is rejected
            return nout, False
        elif less_equal(x, rect.min_corner):
            # remove n and its whole sub-tree
            nparent = self.get_parent()
            nparent.remove_node(self) if nparent is not None else None
            # create empty node
            nout = Node(max_points=self.max_points, min_children=self.min_children)
        elif less_equal(rect.min_corner, x) or less_equal(x, rect.max_corner):
            if self.is_leaf():
                for y in self.L:
                    if less_equal(y, x):
                        # x is rejected
                        return nout, False
                    elif less_equal(x, y):
                        # y is removed
                        self.remove_point(y)
            else:
                for npr in self.nodes:
                    npr, update = npr.update_node(x)
                    if not update:
                        return nout, False
                    elif npr.is_empty_solution():
                        self.remove_node(npr)
                if self.num_subnodes() == 1:
                    # Remove node n and use npr in place of n
                    npr = self.get_subnode()
                    nparent = self.get_parent()
                    nparent.replace_node(self, npr) if nparent is not None else None
                    # nparent.replaceNode(self, npr) if nparent is not None else self = npr
        # else:
        # Skip this node
        return nout, True

    def update_ideal_nadir(self, x):
        # type: (Node, tuple) -> None
        self.rect = self.get_rectangle_sn()
        if self.rect is None:
            # New Ideal and Nadir points
            # dim(ideal) == dim(nadir) == dim(x)
            # n = Point.dim(x)
            n = dim(x)
            ideal = (float('inf'),) * n
            nadir = (float('-inf'),) * n
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

            if not self.is_root():
                npr = self.get_parent()
                npr.update_ideal_nadir(x)

    def dominates(self, x):
        # type: (Node, tuple) -> bool
        # Returns 'True' if x is dominated by any point stored in the Pareto archive
        # Use the rectangle associated to the Node for speeding up the evaluation
        rect = self.get_rectangle_sn()
        if less_equal(rect.max_corner, x):
            # x is dominated by the Pareto front
            return True
        elif less_equal(rect.min_corner, x) or less_equal(x, rect.max_corner):
            # x is inside the rectangle enclosing the Pareto front
            return any(n.dominates(x) for n in self.nodes)
        # elif less_equal(x, rect.min_corner):
        # x dominates the Pareto front
        # return False
        else:
            return False
