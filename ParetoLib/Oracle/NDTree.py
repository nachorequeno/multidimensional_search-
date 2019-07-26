# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""NDTree.

This module implements a NDTree [1], a data structure that is optimised
for storing a Pareto front by removing redundant non-dominating points
from the surface. The data structure definition, notation and algorithms
are directly extracted from [1].

[1] Andrzej Jaszkiewicz and Thibaut Lust.
ND-Tree-based update: a fast algorithm for the dynamic non-dominance problem.
IEEE Transactions on Evolutionary Computation, 2018.
https://ieeexplore.ieee.org/document/8274915/
"""

import sys
import resource
import os
import io
import pickle

from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Geometry.Point import less, less_equal, distance, dim, r
import ParetoLib.Oracle as RootOracle


class NDTree:
    def __init__(self, max_points=2, min_children=2):
        # type: (NDTree, int, int) -> None
        """
        A NDTree is a tree with a Node in the root.
        The root has max_children descendants of type Node.
        Each Node (including the root) stores up to max_points.
        """
        self.root = None
        self.max_points = max_points
        self.min_children = min_children

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

    def __contains__(self, p):
        # type: (NDTree, tuple) -> bool
        """
        Membership function that checks whether a point is
        in the NDTree or not.

        Args:
            self (NDTree): The NDTree.
            p (tuple): The point.

        Returns:
            bool: True if p is in the NDTree.

        Example:
        >>> x = (0,0,0)
        >>> nd = NDTree()
        >>> nd.update_point(x)
        >>> x in nd
        >>> True
        """
        p = tuple(r(pi) for pi in p)
        return self.root.has_point_rec(p) if not self.is_empty() else False
        # return item in self.root

    def __repr__(self):
        # type: (NDTree) -> str
        """
        Printer.
        """
        return self.root.to_str_rec(0) if not self.is_empty() else ''

    def __str__(self):
        # type: (NDTree) -> str
        """
        Printer.
        """
        return self.root.to_str_rec(0) if not self.is_empty() else ''

    def __eq__(self, other):
        # type: (NDTree, NDTree) -> bool
        """
        self == other
        """
        sameContent = (other.max_points == self.max_points) and \
                      (other.min_children == self.min_children)
        return (hash(self.root) == hash(other.root)) and sameContent

    def __ne__(self, other):
        # type: (NDTree, NDTree) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    def __hash__(self):
        # type: (NDTree) -> int
        """
        Identity function (via hashing)
        """
        return hash((self.root, self.max_points, self.min_children))

    def _report(self):
        """
        Report function
        """
        self.root.report_rec() if not self.is_empty() else ''

    def dim(self):
        # type: (NDTree) -> int
        """
        Dimension of the points stored in the NDTree.

        Args:
            self (NDTree): The NDTree.

        Returns:
            int: Dimension of the points in the NDTree.

        Example:
        >>> x = (0,0,0)
        >>> nd = NDTree()
        >>> nd.update_point(x)
        >>> nd.dim()
        >>> 3
        """
        rect = self.get_rectangle()
        # if rect is not None:
        #    return Rectangle.dim(rect)
        if isinstance(rect, Rectangle):
            return rect.dim()
        else:
            return 0

    def is_empty(self):
        # type: (NDTree) -> bool
        """
        Testing the emptiness of the NDTree.

        Args:
            self (NDTree): The NDTree.

        Returns:
            bool: True if there is no point in the NDTree.

        Example:
        >>> nd = NDTree()
        >>> nd.is_empty()
        >>> True
        """
        return self.root is None

    def get_rectangle(self):
        # type: (NDTree) -> Rectangle
        """
        Rectangle that encloses all the points in the NDTree.

        Args:
            self (NDTree): The NDTree.

        Returns:
            Rectangle: Rectangle that encloses all the points in the NDTree.
            If the NDTree is empty, it returns a Rectangle() (i.e., default value).

        Example:
        >>> x = (0,0,0)
        >>> y = (1,1,1)
        >>> nd = NDTree()
        >>> nd.update_point(x)
        >>> nd.update_point(y)
        >>> nd.get_rectangle()
        >>> [(0,0,0), (0,0,0)]
        """
        # return self.root.getRectangleSn() if not self.isEmpty() else None
        return self.root.get_rectangle_sn() if not self.is_empty() else Rectangle()

    def get_points(self):
        # type: (NDTree) -> set
        """
        Set of the points stored in the NDTree.

        Args:
            self (NDTree): The NDTree.

        Returns:
            set: Set of the points in the NDTree.

        Example:
        >>> x = (0,0,0)
        >>> y = (1,1,1)
        >>> nd = NDTree()
        >>> nd.update_point(x)
        >>> nd.update_point(y)
        >>> nd.get_points()
        >>> {(0,0,0), (1,1,1)}
        """
        points = self.root.s() if self.root is not None else set()
        return points

    def update_point(self, p):
        # type: (NDTree, tuple) -> None
        """
        Addition of a point to the NDTree.

        Args:
            self (NDTree): The NDTree.
            p (tuple): The point

        Returns:
            None: p is inserted in the NDTree if it is not dominated by
            any point of the NDTree.
            Side effect: all the points that are dominated by p
            are discarded.

        Example:
        >>> x = (0,0,0)
        >>> nd = NDTree()
        >>> nd.update_point(x)
        """
        p = tuple(r(pi) for pi in p)
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
        """
        Testing the dominance of the NDTree over a point.

        Args:
            self (NDTree): The NDTree.

        Returns:
            bool: True if p is dominated by any point stored in the Pareto archive.

        Example:
        >>> x = (0,0,0)
        >>> y = (1,1,1)
        >>> nd = NDTree()
        >>> nd.update_point(x)
        >>> nd.dominates(y)
        >>> True
        """
        p = tuple(r(pi) for pi in p)
        return self.root.dominates(p)

    # Read/Write file functions
    def from_file(self, fname='', human_readable=False):
        # type: (NDTree, str, bool) -> None
        """
        Loading an NDTree from a file.

        Args:
            self (NDTree): The NDTree.
            fname (string): The file name where the NDTree is saved.
            human_readable (bool): Boolean indicating if the
                           NDTree will be loaded from a binary or
                           text file.

        Returns:
            None: The NDTree is loaded from fname.

        Example:
        >>> ndt = NDTree()
        >>> ndt.from_file('filename')
        """
        assert (fname != ''), 'Filename should not be null'
        assert os.path.isfile(fname), 'File {0} does not exists or it is not a file'.format(fname)

        mode = 'r'
        if human_readable:
            finput = open(fname, mode)
            self.from_file_text(finput)
        else:
            mode = mode + 'b'
            finput = open(fname, mode)
            self.from_file_binary(finput)
        finput.close()

    def from_file_binary(self, finput=None):
        # type: (NDTree, io.BinaryIO) -> None
        """
        Loading an NDTree from a binary file.

        Args:
            self (NDTree): The NDTree.
            finput (io.BinaryIO): The file where the NDTree is saved.

        Returns:
            None: The NDTree is loaded from finput.

        Example:
        >>> nd = NDTree()
        >>> infile = open('filename', 'rb')
        >>> nd.from_file_binary(infile)
        >>> infile.close()
        """
        assert (finput is not None), 'File object should not be null'

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

        self.root = pickle.load(finput)
        self.max_points = pickle.load(finput)
        self.min_children = pickle.load(finput)

    def from_file_text(self, finput=None):
        # type: (NDTree, io.BinaryIO) -> None
        """
        Loading an NDTree from a text file.

        Args:
            self (NDTree): The NDTree.
            finput (io.BinaryIO): The file where the NDTree is saved.

        Returns:
            None: The NDTree is loaded from finput.

        Example:
        >>> nd = NDTree()
        >>> infile = open('filename', 'r')
        >>> nd.from_file_text(infile)
        >>> infile.close()
        """
        assert (finput is not None), 'File object should not be null'

        def _line2tuple(inline):
            """
            line = (x1,x2,...,xn)
            """
            line = inline
            line = line.replace('(', '')
            line = line.replace(')', '')
            line = line.split(',')
            return tuple(float(pi) for pi in line)

        self.__init__()
        point_list = (_line2tuple(line) for line in finput)
        for point in point_list:
            self.update_point(point)

    def to_file(self, fname='', append=False, human_readable=False):
        # type: (NDTree, str, bool, bool) -> None
        """
        Writing of an NDTree to a file.

        Args:
            self (NDTree): The NDTree.
            fname (string): The file name where the NDTree will
                            be saved.
            append (bool): Boolean indicating if the NDTree will
                           be appended at the end of the file.
            human_readable (bool): Boolean indicating if the
                           NDTree will be saved in a binary or
                           text file.

        Returns:
            None: The NDTree is saved in fname.

        Example:
        >>> ndt = NDTree()
        >>> ndt.to_file('filename')
        """
        assert (fname != ''), 'Filename should not be null'

        if append:
            mode = 'a'
        else:
            mode = 'w'

        if human_readable:
            foutput = open(fname, mode)
            self.to_file_text(foutput)
        else:
            mode = mode + 'b'
            foutput = open(fname, mode)
            self.to_file_binary(foutput)
        foutput.close()

    def to_file_binary(self, foutput=None):
        # type: (NDTree, io.BinaryIO) -> None
        """
        Writing of an NDTree to a binary file.

        Args:
            self (NDTree): The Oracle.
            foutput (io.BinaryIO): The file where the NDTree will
                                   be saved.

        Returns:
            None: The NDTree is saved in foutput.

        Example:
        >>> nd = NDTree()
        >>> outfile = open('filename', 'wb')
        >>> nd.to_file_binary(outfile)
        >>> outfile.close()
        """
        assert (foutput is not None), 'File object should not be null'

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

        pickle.dump(self.root, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.max_points, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.min_children, foutput, pickle.HIGHEST_PROTOCOL)

    def to_file_text(self, foutput=None):
        # type: (NDTree, io.BinaryIO) -> None
        """
        Writing of a NDTree to a text file.

        Args:
            self (NDTree): The NDTree.
            foutput (io.BinaryIO): The file where the NDTree will
                                   be saved.

        Returns:
            None: The NDTree is saved in foutput.

        Example:
        >>> nd = NDTree()
        >>> outfile = open('filename', 'w')
        >>> nd.to_file_text(outfile)
        >>> outfile.close()
        """
        assert (foutput is not None), 'File object should not be null'

        setPoints = self.get_points()
        for point in setPoints:
            # line = (x1, x2, ..., xn)
            foutput.write(str(point))
            foutput.write('\n')


class Node:
    def __init__(self, parent=None, max_points=2, min_children=2):
        # type: (Node, Node, int, int) -> None
        """
        A Node is composed of:
            - nodes: a list [n_1,..,n_n] of Nodes (i.e., descendants).
            - L: a list [p_1,..,p_n] of points stored in the current Node.
            - rect: a Rectangle that encloses all the points contained in L and the descendants.
            (Rectangle rect is used for optimising some operations by comparing a point with the
            corners of the rectangle)-

        Extra parameteres are:
            - parent: a pointer to the precedent Node.
            - max_children: an integer that specifies the maximum length of self.nodes.
            - max_points: an integer that specifies the maximum length of self.L.
        """
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
        """
        Checking if point x is contained in self.L.
        """
        return x in self.L

    def has_point_rec(self, x):
        # type: (Node, tuple) -> bool
        """
        Checking if point x is contained in self.L or in
        any descendant Node.
        """
        if self.is_leaf():
            return self.has_point(x)
        else:
            _hasPoint = (n.has_point_rec(x) for n in self.nodes)
            return any(_hasPoint)

    def __contains__(self, x):
        # type: (Node, tuple) -> bool
        """
        Synonym for self.has_point_rec(x)
        """
        return self.has_point_rec(x)

    def _to_str(self, nesting_level=0):
        # type: (Node, int) -> str
        """
        Printer.
        """
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
        """
        Printer.
        """
        if self.is_leaf():
            return self._to_str(nesting_level)
        else:
            _strings = (x.to_str_rec(nesting_level + 1) for x in self.nodes)
            return '\n'.join(_strings)

    def __repr__(self):
        # type: (Node) -> str
        """
        Printer.
        """
        return self.to_str_rec(0)

    def __str__(self):
        # type: (Node) -> str
        """
        Printer.
        """
        return self.to_str_rec(0)

    def __eq__(self, other):
        # type: (Node, Node) -> bool
        """
        self == other
        """
        eqRect = (hash(other.rect) == hash(self.rect))
        eqParent = (hash(other.parent) == hash(self.parent))
        sameContent = (other.nodes == self.nodes) and \
                      (other.L == self.L) and \
                      (other.max_points == self.max_points) and \
                      (other.min_children == self.min_children)

        return eqRect and eqParent and sameContent

    def __ne__(self, other):
        # type: (Node, Node) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    def __hash__(self):
        # type: (Node) -> int
        """
        Identity function (via hashing)
        """
        # hash cannot be computed over 'list'; use 'tuple' instead
        # return hash((self.rect, self.parent, tuple(self.nodes), tuple(self.L), self.MAX_POINTS, self.MIN_CHILDREN))
        return hash((self.rect, self.parent, tuple(self.L), self.max_points, self.min_children))

    # Report functions
    def _report(self):
        """
        Report function.
        """
        RootOracle.logger.info('\tCurrent {0}'.format(id(self)))  # self type(self).__name__
        RootOracle.logger.info('\tParent {0}'.format(id(self.parent)))  # self.parent type(self.parent).__name__
        RootOracle.logger.info('\tNum Successors {0}'.format(len(self.nodes)))
        RootOracle.logger.info('\tSuccessors {0}'.format([id(n) for n in self.nodes]))
        RootOracle.logger.info('\tNum Points {0}'.format(len(self.L)))
        RootOracle.logger.info('\tPoints {0}'.format(self.L))
        RootOracle.logger.info('\tRect {0}'.format(str(self.rect)))

    def report_rec(self):
        """
        Report function.
        """
        self._report()
        [n.report_rec() for n in self.nodes]

    # Functions for checking the type of node
    def is_root(self):
        # type: (Node) -> bool
        """
        Checking if self has a parent.
        """
        return self.parent is None

    def is_leaf(self):
        # type: (Node) -> bool
        """
        Checking if self has any descendant Node.
        """
        return self.num_subnodes() == 0

    # Node operations
    def add_node(self, n, pos=-1):
        # type: (Node, Node, int) -> None
        """
        Addition or update of Node n as descendant of self.
        """
        if n not in self.nodes:
            n.set_parent(self)
            if (pos >= 0) and (pos < len(self.nodes)):
                self.nodes.insert(pos, n)
            else:
                self.nodes.append(n)

    def remove_node(self, n):
        # type: (Node, Node) -> None
        """
        Removal of a direct descendant Node n.
        """
        if n in self.nodes:
            self.nodes.remove(n)
            del n

    def replace_node(self, n, npr):
        # type: (Node, Node, Node) -> None
        """
        Replacement of a direct descendant Node n by Node npr.
        """
        if n in self.nodes:
            index = self.nodes.index(n)
            self.add_node(npr, index)
            self.remove_node(n)

    def get_subnode(self, pos=0):
        # type: (Node, int) -> Node
        """
        Getting direct descendant at position pos.
        """
        return self.nodes[pos]

    def get_subnodes(self):
        # type: (Node) -> set
        """
        Set of direct descendant.
        """
        return set(self.nodes)

    def num_subnodes(self):
        # type: (Node) -> int
        """
        Number of direct descendants.
        """
        return len(self.nodes)

    def is_empty_solution(self):
        # type: (Node) -> bool
        """
        Testing the emptiness of current Node
        (i.e., no points and no descendants).
        """
        return (self is None) or \
               ((self.num_points() == 0) and (self.num_subnodes() == 0))

    # Point operations
    def add_point(self, x, pos=-1):
        # type: (Node, tuple, int) -> None
        """
        Addition of a new point to the current Node.
        """
        if (pos >= 0) and (pos < len(self.L)):
            self.L.insert(pos, x)
        else:
            self.L.append(x)

    def remove_point(self, x):
        # type: (Node, tuple) -> None
        """
        Removal of point x from current Node (if it is in).
        """
        if x in self.L:
            self.L.remove(x)
            del x

    def replace_point(self, x, xp):
        # type: (Node, tuple, tuple) -> None
        """
        Replacement of point x by point xp if x is in the current Node.
        """
        if x in self.L:
            index = self.L.index(x)
            self.add_point(xp, index)
            self.remove_point(x)

    def get_point(self, pos=0):
        # type: (Node, int) -> tuple
        """
        Getting point from the current Node.
        """
        return self.L[pos]

    def get_points(self):
        # type: (Node) -> set
        """
        Getting set of points from the current Node.
        """
        return set(self.L)

    # Set of points
    def s(self):
        # type: (Node) -> set
        """
        Getting set of points from the current Node and from
        its descendants.
        """
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
        """
        Number of points in the current Node.
        """
        return len(self.L)

    def has_points(self):
        # type: (Node) -> bool
        """
        self.num_points() > 0.
        """
        return (self is not None) and (len(self.L) > 0)

    # Relationship functions
    def get_parent(self):
        # type: (Node) -> Node
        """
        Getting parent Node.
        """
        return self.parent

    def set_parent(self, parent):
        # type: (Node, Node) -> None
        """
        Setting parent Node.
        """
        self.parent = parent

    # Rectangle Operations
    def get_rectangle_sn(self):
        # type: (Node) -> Rectangle
        """
        Getting rectangle self.rect.
        """
        return self.rect

    def set_rectangle_sn(self, rect):
        # type: (Node, Rectangle) -> None
        """
        Setting rectangle self.rect.
        """
        self.rect = rect

    # NDTree operations
    def find_closest_node(self, x):
        # type: (Node, tuple) -> Node
        """
        Searching for the Node containing the closest point to x.
        """
        lsorted = sorted(self.nodes, key=lambda node: node.rect.distance_to_center(x))
        return lsorted[0]

    def insert(self, x):
        # type: (Node, tuple) -> None
        """
        Insertion of a point into the Node.
        """
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
        """
        Computation of the 'center of mass' of the current Node,
        and the mean distance between this center and each point
        contained in the Node.
        """
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
        """
        Creation of new descendant Nodes of current Node.
        This function is called when the number of points hosted in
        the current node increases until reaching a threshold.
        """
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
        """
        Insertion of a new point in the Node; either in self.L
        or in any descendant Node.
        Side effect: removal of points that are dominated by x.
        """
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
        """
        Updating self.rect according to the value of point x.
        """
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

            ideal = tuple(min(xi, ideali) for xi, ideali in zip(x, ideal))
            nadir = tuple(max(xi, nadiri) for xi, nadiri in zip(x, nadir))

            self.rect.min_corner = ideal
            self.rect.max_corner = nadir

            if not self.is_root():
                npr = self.get_parent()
                npr.update_ideal_nadir(x)

    def dominates(self, x):
        # type: (Node, tuple) -> bool
        """
        Checking if a point x is dominated by any point stored in the
        current Node or in the descendants.
        """
        # Use the rectangle associated to the Node for speeding up the evaluation.
        rect = self.get_rectangle_sn()
        if less(rect.max_corner, x):
            # x is dominated by the Pareto front
            return True
        elif less(x, rect.min_corner):
            # x dominates the Pareto front
            return False
        elif (rect.min_corner == x) or (rect.max_corner == x):
            return True
        else:
            # x is inside the rectangle enclosing the Pareto front, or
            # x is incomparable to the min and max corners.
            # Therefore, we must explicitly check if x is dominated by
            # any point of the current subtree.
            test1 = any(less_equal(p, x) for p in self.L)
            test2 = any(n.dominates(x) for n in self.nodes)
            return test1 or test2
