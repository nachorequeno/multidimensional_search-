# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Rectangle.

This module introduces the Rectangle class. It includes a set of
operations for creating and handling rectangles. This module also
offers special features and methods for generating alpha vectors
and (in)comparable boxes.

##################
# Alpha generators
##################

Set of functions for generating the index words, i.e., 'alphas',
that will rule the creation of comparable and incomparable boxes.
Alpha is a word of length d in [0,1] (i.e., [0,1]^d), and
Alpha' is a word of length d in [0,1,*] (i.e., [0,1,*]^d),
according to the notation of [1].

The function for creating a list of comparable boxes via alphas is:
- comp(d)

The function for creating a list of incomparable boxes via alphas is:
- incomp(d, opt=True)

Option 'opt' means whether the result is a list of incomparable
alphas (opt=False) or a list of incomparable alphas' (opt=True).
- incomp_expanded(d)
- incomp_compressed(d)
- E(d)

Variable 'd' is the dimension of the space.

#################
# Cube generators
#################

Set of functions for generating rectangular half-spaces and cones,
according to the notation of [2].
These functions are:
- cpoint(i, alphai, ypoint, xspace)
- crect(i, alphai, yrectangle, xspace)
- bpoint(alpha, ypoint, xspace)
- brect(alpha, yrectangle, xspace)
- irect(alphaincomp, yrectangle, xspace)

They all return a rectangle, except for 'irect', that returns a list
of incomparable rectangles.

They require as input:
- A point (ypoint) or rectangle (yrectangle) close to the Pareto front,
- An index word (alpha) or the i-th component of the index word (alphai),
- The space (xspace).

[1] Learning Monotone Partitions of Partially-Ordered Domains,
Nicolas Basset, Oded Maler, J.I Requeno, in
doc/article.pdf.

[2] [Learning Monotone Partitions of Partially-Ordered Domains (Work in Progress) 2017.
〈hal-01556243〉] (https://hal.archives-ouvertes.fr/hal-01556243/)
"""

import math
import numpy as np
import matplotlib.patches as patches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from itertools import product, tee

import ParetoLib.Geometry as RootGeom
from ParetoLib.Geometry.Segment import Segment
from ParetoLib.Geometry.Point import greater, greater_equal, less, less_equal, add, subtract, div, mult, distance, dim, \
    incomparables, select, subt, int_to_bin_tuple #, r
from ParetoLib._py3k import red


class Rectangle(object):
    def __init__(self,
                 min_corner=(float('-inf'),) * 2,
                 max_corner=(float('+inf'),) * 2):
        # type: (Rectangle, tuple, tuple) -> None
        """
        A Rectangle is represented by a couple of points (x, x'), i.e., the
        minimal (left, bottom) corner x, and the maximal (right, up) corner x'.
        All the points contained in the rectangle are greater than x and
        smaller than x'.
        """
        assert dim(min_corner) == dim(max_corner)

        # min_corner, max_corner
        self.min_corner = tuple(min(mini, maxi) for mini, maxi in zip(min_corner, max_corner))
        self.max_corner = tuple(max(mini, maxi) for mini, maxi in zip(min_corner, max_corner))
        # self.min_corner = min_corner
        # self.max_corner = max_corner

        # Volume (self.vol) is calculated on demand the first time is accessed, and cached afterwards.
        # Using 'None' for indicating that attribute vol is outdated (e.g., user changes min_corner or max_corners).
        self.vol = None
        # Vertices are also cached.
        self.vertx = None

        assert greater_equal(self.max_corner, self.min_corner) or incomparables(self.min_corner, self.max_corner)

    def __setattr__(self, name, value):
        # type: (Rectangle, str, None) -> None
        """
        Assignation of a value to a class attribute.

        Args:
            self (Rectangle): The Rectangle.
            name (str): The attribute.
            value (None): The value

        Returns:
            None: self.name = value.

        Example:
        >>> x = (0,0,0)
        >>> y = (2,2,2)
        >>> r = Rectangle(x,y)
        >>> r.min_corner = x
        """
        str_vertx = 'vertx'
        if name != str_vertx:
            # self.__dict__[str_vertx] = None
            object.__setattr__(self, str_vertx, None)

        # Every time a corner is changed, the volume is marked as 'outdated'.
        # It is used for a lazy computation of volume when requested by the user,
        # and therefore avoiding unecessary computations
        str_vol = 'vol'
        if name != str_vol:
            # self.__dict__[str_vol] = None
            object.__setattr__(self, str_vol, None)

        # Round the elements of 'value' when assigning them to self.min_corner or self.max_corner
        # if type(value) == tuple:
        #     value = tuple(r(vi) for vi in value)

        # Round the elements of 'value' when assigning them to self.vol
        # if type(value) == float:
        #     value = r(value)

        # Round the elements of 'value' when assigning them to self.vertx
        # if type(value) == list:
        #     value = [tuple(r(vi) for vi in vertex) for vertex in value]

        # self.__dict__[name] = None
        object.__setattr__(self, name, value)

    #
    def __contains__(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        """
        Membership function that checks whether a point is
        strictly contained in the Rectangle or not.

        Args:
            self (Rectangle): The Rectangle.
            xpoint (tuple): The point.

        Returns:
            bool: True if xpoint is strictly inside the rectangle
            (i.e., it is not along the border).

        Example:
        >>> x = (0,0,0)
        >>> y = (2,2,2)
        >>> r = Rectangle(x,y)
        >>> x in r
        >>> False
        """
        return (greater(xpoint, self.min_corner) and
                less(xpoint, self.max_corner))

    def inside(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        """
        Membership function that checks whether a point is
        contained in the Rectangle or not.

        Args:
            self (Rectangle): The Rectangle.
            xpoint (tuple): The point.

        Returns:
            bool: True if xpoint is inside the rectangle
            or along the border.

        Example:
        >>> x = (0,0,0)
        >>> y = (2,2,2)
        >>> r = Rectangle(x,y)
        >>> r.inside(x)
        >>> True
        """
        # xpoint is inside the rectangle or along the border
        return (greater_equal(xpoint, self.min_corner) and
                less_equal(xpoint, self.max_corner))

    def _to_str(self):
        # type: (Rectangle) -> str
        """
        Printer.
        """
        _string = '[{0}, {1}]'.format(self.min_corner, self.max_corner)
        return _string

    def __repr__(self):
        # type: (Rectangle) -> str
        """
        Printer.
        """
        return self._to_str()

    def __str__(self):
        # type: (Rectangle) -> str
        """
        Printer.
        """
        return self._to_str()

    def __eq__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
        self == other
        """
        return (other.min_corner == self.min_corner) and (other.max_corner == self.max_corner)

    def __ne__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
        self < other
        """
        return less(self.max_corner, other.max_corner)

    def __le__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
        self <= other
        """
        return less_equal(self.max_corner, other.max_corner)

    def __gt__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
        self > other
        """
        return not self.__le__(other)

    def __ge__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
        self >= other
        """
        return not self.__lt__(other)

    def __hash__(self):
        # type: (Rectangle) -> int
        """
        Identity function (via hashing).
        """
        return hash((self.min_corner, self.max_corner))

    # Rectangle properties
    def dim(self):
        # type: (Rectangle) -> int
        """
        Dimension of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.

        Returns:
            int: Dimension of the Rectangle.

        Example:
        >>> x = (0,0,0)
        >>> y = (2,2,2)
        >>> r = Rectangle(x,y)
        >>> r.dim()
        >>> 3
        """
        return dim(self.min_corner)

    def _volume(self):
        # type: (Rectangle) -> float
        diagonal_length = self.diag_vector()
        _prod = red(lambda si, sj: si * sj, diagonal_length)
        return abs(_prod)

    def volume(self):
        # type: (Rectangle) -> float
        """
        Volume of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.

        Returns:
            float: Volume of the Rectangle.

        Example:
        >>> x = (0,0,0)
        >>> y = (2,2,2)
        >>> r = Rectangle(x,y)
        >>> r.volume()
        >>> 8.0
        """
        # Recalculate volume if it is outdated
        if self.vol is None:
            self.vol = self._volume()
        return self.vol

    def num_vertices(self):
        # type: (Rectangle) -> int
        """
        Number of vertices of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.

        Returns:
            int: 2**rectangle.dim().

        Example:
        >>> x = (0,0)
        >>> y = (1,1)
        >>> r = Rectangle(x,y)
        >>> r.num_vertices()
        >>> 4
        """
        return int(math.pow(2, self.dim()))

    def _vertices(self):
        # type: (Rectangle) -> list
        deltas = self.diag_vector()
        vertex = self.min_corner
        vertices = []
        # For dim = 3, indexes =
        # (0, 0, 0)
        # (0, 0, 1)
        # (0, 1, 0)
        # ....
        indexes = product([0, 1], repeat=self.dim())
        for delta_index in indexes:
            deltai = select(deltas, delta_index)
            vertices.append(add(vertex, deltai))
        assert (len(vertices) == self.num_vertices()), 'Error in the number of vertices'
        return vertices

    def _vertices_func(self):
        # type: (Rectangle) -> list
        deltas = self.diag_vector()
        vertex = self.min_corner
        num_vertex = self.num_vertices()
        d = self.dim()
        vertices = [None] * num_vertex
        for i in range(num_vertex):
            delta_index = int_to_bin_tuple(i, d)
            deltai = select(deltas, delta_index)
            vertices[i] = add(vertex, deltai)
        assert (len(vertices) == num_vertex), 'Error in the number of vertices'
        return vertices

    def vertices(self):
        # type: (Rectangle) -> list
        """
        List of vertices of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.

        Returns:
            list: List of vertices of the Rectangle.

        Example:
        >>> x = (0,0)
        >>> y = (1,1)
        >>> r = Rectangle(x,y)
        >>> r.vertices()
        >>> [(0.0,0.0), (0.0,1.0), (1.0,0.0), (1.0,1.0)]
        """
        # Recalculate vertices if it is outdated
        if self.vertx is None:
            self.vertx = self._vertices()
        return self.vertx

    def diag(self):
        # type: (Rectangle) -> Segment
        """
        Diagonal of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.

        Returns:
            Segment: Diagonal of the Rectangle.

        Example:
        >>> x = (0,0)
        >>> y = (1,1)
        >>> r = Rectangle(x,y)
        >>> r.diag()
        >>> (1.0,1.0)
        """
        return Segment(self.min_corner, self.max_corner)

    def diag_vector(self):
        # type: (Rectangle) -> tuple
        """
        Maximal distance between corners of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.

        Returns:
            tuple: Maximal distance between corners of the Rectangle.

        Example:
        >>> x = (0,0,0)
        >>> y = (2,2,2)
        >>> r = Rectangle(x,y)
        >>> r.diag_vector()
        >>> (2.0,2.0,2.0)
        """
        return subtract(self.max_corner, self.min_corner)

    def norm(self):
        # type: (Rectangle) -> float
        """
        Norm of the diagonal.

        Args:
            self (Rectangle): The Rectangle.

        Returns:
            float: Norm of the diagonal.

        Example:
        >>> x = (0,0,0)
        >>> y = (2,2,2)
        >>> r = Rectangle(x,y)
        >>> r.norm()
        >>> 3.464
        """
        diagonal = self.diag()
        return diagonal.norm()

    def center(self):
        # type: (Rectangle) -> tuple
        """
        Center of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.

        Returns:
            tuple: Center of the Rectangle.

        Example:
        >>> x = (0,0)
        >>> y = (1,1)
        >>> r = Rectangle(x,y)
        >>> r.center()
        >>> (0.5,0.5)
        """
        offset = div(self.diag_vector(), 2.0)
        return add(self.min_corner, offset)

    def distance_to_center(self, xpoint):
        # type: (Rectangle, tuple) -> float
        """
        Distance of a point to the center of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.
            xpoint (tuple): The point.

        Returns:
            float: Distance of xpoint to the center of the Rectangle.

        Example:
        >>> x = (0,0)
        >>> y = (1,1)
        >>> r = Rectangle(x,y)
        >>> r.distance_to_center(x)
        >>> 0.707
        """
        middle_point = self.center()
        euclidean_dist = distance(xpoint, middle_point)
        return euclidean_dist

    def get_points(self, n):
        # type: (Rectangle, int) -> list
        """
        List of points of the Rectangle.

        Args:
            self (Rectangle): The Rectangle.
            n (int): Number of points

        Returns:
            list: n points along the diagonal, excluding corners.

        Example:
        >>> x = (0,0)
        >>> y = (1,1)
        >>> r = Rectangle(x,y)
        >>> r.get_points(2)
        >>> [(0.333, 0.333), (0.666, 0.666)]
        """
        # n internal points = n + 1 internal segments
        m = float(n + 1)  # Type conversion required for point operations
        diag_step = div(self.diag_vector(), m)
        min_point = add(self.min_corner, diag_step)
        point_list = [add(min_point, mult(diag_step, i)) for i in range(n)]
        return point_list

    # Geometric operations between two rectangles
    def is_concatenable(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        """
         Adjacency of two rectangles.

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             bool: True if self and other are adjacent.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (1,0)
         >>> t = (2,1)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(z,t)
         >>> r2.is_concatenable(r1)
         >>> True
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        concatenable = False

        # Two rectangles are concatenable if d-1 coordinates are aligned and they only differ in 1 coordinate
        min_corner_eq = (self_i == other_i for self_i, other_i in zip(self.min_corner, other.min_corner))
        max_corner_eq = (self_i == other_i for self_i, other_i in zip(self.max_corner, other.max_corner))
        corner_eq = [min_c and max_c for min_c, max_c in zip(min_corner_eq, max_corner_eq)]

        if sum(corner_eq) == (self.dim() - 1):
            # Besides, the mismatching coordinate must have continuous interval
            mismatching_index = corner_eq.index(False)
            concatenable = (self.max_corner[mismatching_index] == other.min_corner[mismatching_index]) or \
                         (other.max_corner[mismatching_index] == self.min_corner[mismatching_index])

        return concatenable

    def is_concatenable_func(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        """
         Adjacency of two rectangles.

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             bool: True if self and other are adjacent.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (1,0)
         >>> t = (2,1)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(z,t)
         >>> r2.is_concatenable(r1)
         >>> True
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        d = self.dim()
        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)
        # (self != other)
        return (not self.overlaps(other)) \
               and len(vert_self) == len(vert_other) \
               and len(vert_self) == pow(2, d) \
               and len(inter) == pow(2, d - 1)

    def concatenate(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        """
         Rectangle resulting from the concatenation of two adjacent
         rectangles (if possible).

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             Rectangle: Concatenation of self and other, if possible.
             Else, self.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (1,0)
         >>> t = (2,1)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(z,t)
         >>> r2.concatenate(r1)
         >>> [(0.0,0.0), (2.0,1.0)]
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        assert (not self.overlaps(other)), 'Rectangles should not overlap: {0}, {1}'.format(self, other)

        rect = Rectangle(self.min_corner, self.max_corner)

        if self.is_concatenable(other):
            rect.min_corner = tuple(min(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
            rect.max_corner = tuple(max(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))

        return rect

    def concatenate_func(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        """
         Rectangle resulting from the concatenation of two adjacent
         rectangles (if possible).

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             Rectangle: Concatenation of self and other, if possible.
             Else, self.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (1,0)
         >>> t = (2,1)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(z,t)
         >>> r2.concatenate(r1)
         >>> [(0.0,0.0), (2.0,1.0)]
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        assert (not self.overlaps(other)), 'Rectangles should not overlap: {0}, {1}'.format(self, other)

        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)
        rect = Rectangle(self.min_corner, self.max_corner)

        # if len(vert_1) == len(vert_2) and \
        #    len(vert_1) == pow(2, d) and \
        #    len(inter) == pow(2, d - 1):
        # if 'self' and 'other' are concatenable
        if self.is_concatenable(other):
            new_union_vertices = (vert_self.union(vert_other)) - inter
            assert len(new_union_vertices) > 0, \
                'Error in computing vertices for the concatenation of "{0}" and "{1}"'.format(self, other)

            rect.min_corner = min(new_union_vertices)
            rect.max_corner = max(new_union_vertices)
        return rect

    def concatenate_update(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        """
         Rectangle resulting from the concatenation of two adjacent
         rectangles (if possible).

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             Rectangle: Concatenation of self and other, if possible.
             Else, self.
             Side effect: self is updated with the concatenation
             of self and other, if possible.
             Else, self keeps unchanged.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (1,0)
         >>> t = (2,1)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(z,t)
         >>> r2.concatenate_update(r1)
         >>> [(0.0,0.0), (2.0,1.0)]
        """

        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        assert (not self.overlaps(other)), 'Rectangles should not overlap: {0}, {1}'.format(self, other)

        # if 'self' and 'other' are concatenable
        if self.is_concatenable(other):
            min_corner = tuple(min(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
            max_corner = tuple(max(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))

            self.min_corner = min_corner
            self.max_corner = max_corner
        return self

    def concatenate_update_func(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        """
         Rectangle resulting from the concatenation of two adjacent
         rectangles (if possible).

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             Rectangle: Concatenation of self and other, if possible.
             Else, self.
             Side effect: self is updated with the concatenation
             of self and other, if possible.
             Else, self keeps unchanged.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (1,0)
         >>> t = (2,1)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(z,t)
         >>> r2.concatenate_update(r1)
         >>> [(0.0,0.0), (2.0,1.0)]
        """

        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        assert (not self.overlaps(other)), 'Rectangles should not overlap: {0}, {1}'.format(self, other)

        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)

        # if 'self' and 'other' are concatenable
        if self.is_concatenable(other):
            new_union_vertices = (vert_self.union(vert_other)) - inter
            assert len(new_union_vertices) > 0, \
                'Error in computing vertices for the concatenation of "{0}" and "{1}"'.format(self, other)

            self.min_corner = min(new_union_vertices)
            self.max_corner = max(new_union_vertices)
        return self

    def overlaps(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
         Existence of overlap between two rectangles.

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             bool: True if self and other intersects.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (2,2)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(x,z)
         >>> r2.overlaps(r1)
         >>> True
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        minc = tuple(max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
        maxc = tuple(min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))
        return less(minc, maxc)

    def intersection(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        """
         Rectangle resulting from the intersection of two rectangles (if any).

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             Rectangle: Intersection of self and other, if any.
             Else, self.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (2,2)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(x,z)
         >>> r2.intersection(r1)
         >>> [(0.0,0.0), (1.0,1.0)]
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        minc = tuple(max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
        maxc = tuple(min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))
        if less(minc, maxc):
            return Rectangle(minc, maxc)
        else:
            return Rectangle(self.min_corner, self.max_corner)

    def intersection_update(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        """
         Rectangle resulting from the intersection of two rectangles (if any).
         If there is no intersection, returns self.

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             Rectangle: Intersection of self and other.
             Side effect: self is updated with the intersection
             of self and other, if any.
             Else, self keeps unchanged.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (2,2)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(x,z)
         >>> r2.intersection_update(r1)
         >>> r2
         >>> [(0.0,0.0), (1.0,1.0)]
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        minc = tuple(max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
        maxc = tuple(min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))
        if less(minc, maxc):
            self.min_corner = minc
            self.max_corner = maxc
        return self

    __and__ = intersection
    """
    Synonym of intersection(self, other).
    """
    def difference(self, other):
        # type: (Rectangle, Rectangle) -> iter
        """
         Set of rectangles resulting from the difference of two rectangles (if any).
         If there is no intersection, returns self.

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             iter: Iterator for reading the set of rectangles.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (2,2)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(x,z)
         >>> r2.difference(r1)
         >>> [[(1.0,0.0), (2.0,2.0)]]
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        diff_set = set()

        inter = self & other
        if inter == self:
            diff_set.add(inter)
        else:
            ground = self.min_corner
            ceil = self.max_corner

            # The maximum number of sub-cubes is 2*d (2 boxes per coordinate)
            for i in range(self.dim()):
                # new_ground = ground[:i] + (max(ground[i], inter.min_corner[i]),) + ground[i+1:]
                # new_ceil = ceil[:i] + (min(ceil[i], inter.max_corner[i]),) + ceil[i+1:]
                #
                # r1 = Rectangle(ground, new_ground)
                # r2 = Rectangle(new_ceil, ceil)
                #
                # diff_set.add(r1)
                # diff_set.add(r2)
                #
                # ground = new_ground
                # ceil = new_ceil

                inner_ground = ground[:i] + (max(ground[i], inter.max_corner[i]),) + ground[i+1:]
                inner_ceil = ceil[:i] + (min(ceil[i], inter.min_corner[i]),) + ceil[i+1:]

                r1 = Rectangle(ground, inner_ceil)
                r2 = Rectangle(inner_ground, ceil)

                if r1.volume() > 0:
                    diff_set.add(r1)
                if r2.volume() > 0:
                    diff_set.add(r2)

                ground = ground[:i] + (max(ground[i], inter.min_corner[i]),) + ground[i+1:]
                ceil = ceil[:i] + (min(ceil[i], inter.max_corner[i]),) + ceil[i+1:]
        return list(diff_set)

    def difference_func(self, other):
        # type: (Rectangle, Rectangle) -> iter
        """
         Set of rectangles resulting from the difference of two rectangles (if any).
         If there is no intersection, returns self.

         Args:
             self (Rectangle): The Rectangle.
             other (Rectangle): Other Rectangle.

         Returns:
             iter: Iterator for reading the set of rectangles.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (2,2)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(x,z)
         >>> r2.difference(r1)
         >>> {[(1.0,0.0), (2.0,2.0)]}
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        def pairwise(iterable):
            """s -> (s0, s1), (s1, s2), (s2, s3), ..."""
            a, b = tee(iterable)
            next(b, None)
            return zip(a, b)

        inter = self & other
        if inter == self:
            yield self
        else:
            # d is a list with dimension equal to the rectangle dimension.
            dimension = self.dim()

            # For each dimension i, d[i] = {self.min_corner[i], self.max_corner[i]} plus
            # all the points of rectangle 'other' that fall inside of rectangle 'self'
            d = [{self.min_corner[i], self.max_corner[i]} for i in range(dimension)]

            # At maximum:
            # d[i] = {self.min_corner[i], other.min_corner[i], other.max_corner[i], self.max_corner[i]}
            for i in range(dimension):
                if self.min_corner[i] < other.min_corner[i] < self.max_corner[i]:
                    d[i].add(other.min_corner[i])
                if self.min_corner[i] < other.max_corner[i] < self.max_corner[i]:
                    d[i].add(other.max_corner[i])

            # elem[i] = pairwise(d[i])
            # if d[i] = {a, b, c, d} then
            # elem[i] = [(a, b), (b, c), (c, d)]
            elem = (pairwise(sorted(item)) for item in d)

            # Given:
            # elem[i] = [(a, b), (b, c)]
            # elem[j] = [(x, y), (y, z)]
            for vertex in product(*elem):
                # product[0] = ((a, b), (x, y))
                # product[1] = ((a, b), (y, z))
                # product[2] = ((b, c), (x, y))
                # product[3] = ((b, c), (y, z))
                #
                # vertex = ((a, b), (x, y))
                # minc = (a, x)
                # maxc = (b, y)
                minc = tuple(item[0] for item in vertex)
                maxc = tuple(item[1] for item in vertex)
                instance = Rectangle(minc, maxc)
                if instance != inter:
                    yield instance
            # At maximum, len(vertex) = product of len(elem[i]) for i in range(d) = 3**d
            # The maximum number of sub-cubes is 3**d - 1 because the intersection is removed

    def min_set_difference(self, other):
        # type: (Rectangle, Rectangle) -> list
        """
         Equivalent to difference(self, other).
         This function tries to minimize the number of rectangles in the output set
         by concatenating adjacent rectangles.
        """
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        return Rectangle.fusion_rectangles(self.difference(other))

    # __sub__ = difference
    __sub__ = min_set_difference
    """
    Synonym of min_set_difference(self, other).
    """

    # Domination
    def dominates_point(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        """
        Synonym of Point.dominates(self.max_corner, xpoint).
        """
        return less_equal(self.max_corner, xpoint)

    def is_dominated_by_point(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        """
        Synonym of Point.dominates(xpoint, self.min_corner).
        """
        return less_equal(xpoint, self.min_corner)

    def dominates_rect(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
        Synonym of Point.dominates(self.max_corner, other.min_corner).
        """
        return less_equal(self.max_corner, other.min_corner)  # testing. Strict dominance and not overlap
        # return less_equal(self.min_corner, other.min_corner) and less_equal(self.max_corner, other.max_corner) # working

    def is_dominated_by_rect(self, other):
        # type: (Rectangle, Rectangle) -> bool
        """
        Synonym of Rectangle.dominates(other, self).
        """
        return other.dominates_rect(self)

    # Matplot functions
    def plot_2D(self, c='red', xaxe=0, yaxe=1, opacity=1.0):
        # type: (Rectangle, str, int, int, float) -> patches.Rectangle
        """
         Function that creates a graphical representation of the rectangle in 2D.
         In case that the rectangle has dimension higher than 2,
         the user must select which axes wants to print.

         Args:
             self (Rectangle): The Rectangle,
             c (str): The color (look at the colors that are supported by MatplotLib),
             xaxe, yaxe (int): Axes that the user wants to display, between 0..Rectangle.dim()-1
             opacity (float): Opacity of the rectangle, between 0.0..1.0

         Returns:
             patches.Rectangle: 2D representation of the rectangle as a MatplotLib object.

        """
        assert (self.dim() >= 2), 'Dimension required >= 2'
        mc = (self.min_corner[xaxe], self.min_corner[yaxe],)
        width = self.diag_vector()[xaxe]
        height = self.diag_vector()[yaxe]
        return patches.Rectangle(
            mc,  # (x,y)
            width,  # width
            height,  # height
            # color = c, #color
            facecolor=c,  # face color
            edgecolor='black',  # edge color
            alpha=opacity
        )

    def plot_3D(self, c='red', xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (Rectangle, str, int, int, int, float) -> Poly3DCollection
        """
         Function that creates a graphical representation of the rectangle in 3D.
         In case that the rectangle has dimension higher than 3,
         the user must select which axes wants to print.

         Args:
             self (Rectangle): The Rectangle,
             c (str): The color (look at the colors that are supported by MatplotLib),
             xaxe, yaxe, zaxe (int): Axes that the user wants to display, between 0..Rectangle.dim()-1
             opacity (float): Opacity of the rectangle, between 0.0..1.0

         Returns:
             patches.Rectangle: 3D representation of the rectangle as a MatplotLib object.

        """
        assert (self.dim() >= 3), 'Dimension required >= 3'

        minc = (self.min_corner[xaxe], self.min_corner[yaxe], self.min_corner[zaxe],)
        maxc = (self.max_corner[xaxe], self.max_corner[yaxe], self.max_corner[zaxe],)
        rect = Rectangle(minc, maxc)

        # sorted(vertices) =
        # [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
        points = np.array(sorted(rect.vertices()))

        edges = [
            [points[0], points[1], points[3], points[2]],
            [points[2], points[3], points[7], points[6]],
            [points[6], points[4], points[5], points[7]],
            [points[4], points[5], points[1], points[0]],
            [points[0], points[4], points[6], points[2]],
            [points[1], points[5], points[7], points[3]]
        ]

        faces = Poly3DCollection(edges, linewidths=1, edgecolors='k')
        # faces.set_facecolor((0,0,1,0.1))
        # faces.set_facecolor('r')
        faces.set_alpha(opacity)
        faces.set_facecolor(c)
        return faces

    #####################
    # Auxiliary functions
    #####################

    @staticmethod
    def fusion_rectangles(list_rect):
        # type: (iter) -> list
        """
         Concatenation of the rectangles in a list,
         whenever it is possible. If no concatenation is possible,
         returns the original list.

         Args:
             list_rect (list): List of rectangles.

         Returns:
             list: list of rectangles obtained by concatenation.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (1,0)
         >>> t = (2,1)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(z,t)
         >>> Rectangle.fusion_rectangles([r1, r2])
         >>> [[(0.0,0.0), (2.0,1.0)]]
        """

        not_processed = set(list_rect)
        output = []
        while not_processed:
            r1 = not_processed.pop()
            processed = set()
            for r2 in not_processed:
                if r1.is_concatenable(r2):
                    # Concatenate rectangle r1 and r2
                    r1.concatenate_update(r2)
                    processed.add(r2)
            if len(processed) == 0:
                output.append(r1)
            else:
                not_processed = not_processed - processed
                not_processed.add(r1)
        return output

    @staticmethod
    def fusion_rectangles_func(list_rect):
        # type: (iter) -> list
        """
         Concatenation of the rectangles in a list,
         whenever it is possible. If no concatenation is possible,
         returns the original list.

         Args:
             list_rect (list): List of rectangles.

         Returns:
             list: list of rectangles obtained by concatenation.

         Example:
         >>> x = (0,0)
         >>> y = (1,1)
         >>> z = (1,0)
         >>> t = (2,2)
         >>> r1 = Rectangle(x,y)
         >>> r2 = Rectangle(z,t)
         >>> Rectangle.fusion_rectangles([r1, r2])
         >>> [[(0.0,0.0), (2.0,2.0)]]
        """

        # Copy list_rect
        list_out = list(list_rect)
        keep_merging = True
        while keep_merging:
            keep_merging = False
            i = 0
            while i < len(list_out):
                # Check if current rectangle liste_out[i] is concatenable with any successor liste_out[j]
                j = i + 1
                while j < len(list_out):
                    if list_out[i].is_concatenable(list_out[j]):
                        # Concatenate rectangle liste_out[j] to liste_out[j]
                        list_out[i].concatenate_update(list_out[j])
                        # Discard rectangle liste_out[j] from the list
                        list_out.pop(j)
                        keep_merging = True
                    else:
                        # Move to the next element of the list
                        # Index 'j' needs to be updated only if we do not concatenate rectangles
                        j = j + 1
                i = i + 1
        return list_out

    # Difference of cubes in a list
    @staticmethod
    def difference_rectangles(rect, list_rect):
        # type: (Rectangle, iter) -> list
        """
          List of rectangles resulting from the difference of a rectangle
          and a list of rectangles (if any).
          If there is no intersection, returns self.

          Args:
              rect (Rectangle): The Rectangle.
              list_rect (list): List of rectangles.

          Returns:
              list: List of rectangles resulting from applying
              rect = rect - ri for every ri in list_rect.

          Example:
          >>> x = (0,0)
          >>> y = (1,1)
          >>> z = (1,0)
          >>> t = (2,2)
          >>> r1 = Rectangle(x,y)
          >>> r2 = Rectangle(z,t)
          >>> r3 = Rectangle(x,t)
          >>> Rectangle.difference_rectangles(r3, [r1, r2])
          >>> []
         """
        new_rect = {rect}

        for b in list_rect:
            temp = set()
            for a in new_rect:
                # Add 'a' to the temporal set of cubes
                temp.add(a)
                if b.overlaps(a):
                    # Add the set of cubes 'a' - 'b'
                    temp = temp.union(a - b)
                    # temp = temp.union(a.difference(b))
                    # Remove 'a'
                    temp.discard(a)
            new_rect = temp

        # return list(new_rect)
        return Rectangle.fusion_rectangles(new_rect)


##################
# Alpha generators
##################

def comp(d):
    # Set of comparable rectangles
    # Particular cases of alpha
    # zero = (0_1,...,0_d)
    zero = (0,) * d
    # one = (1_1,...,1_d)
    one = (1,) * d
    return [zero, one]


def incomp(d, opt=True):
    # type: (int, bool) -> list
    # # Set of incomparable rectangles
    if opt and d >= 3:
        return incomp_compressed(d)
    else:
        return incomp_expanded(d)


def incomp_expanded(d):
    # type: (int) -> list
    alphaprime = (range(2),) * d
    alpha = product(*alphaprime)

    # Set of comparable and incomparable rectangles
    comparable = comp(d)
    incomparable = list(set(alpha) - set(comparable))
    return incomparable


def incomp_compressed(d):
    # type: (int) -> list
    # Returns E(d) in alpha format
    lin = E(d)
    lout = []
    # Changes:
    # ["0*1", "10*", "*10"]
    # By:
    # ["021", "102", "210"]
    # And finally:
    # [(0, 2, 1), (1, 0, 2), (2, 1, 0)]
    for i in lin:
        lin_temp = i.replace("*", "2")
        alpha = tuple(int(li) for li in lin_temp)
        lout.append(alpha)
    return lout


def E(d):
    # type: (int) -> list
    # Compressed version for a set of alpha indices representing incomparable rectangles
    if d == 3:
        return ["0*1", "10*", "*10"]
    elif d > 3:
        return ["*" + i for i in E(d - 1)] + ["0" + "1" * (d - 1), "1" + "0" * (d - 1)]


#################
# Cube generators
#################

def cpoint(i, alphai, ypoint, xspace):
    # type: (int, int, tuple, Rectangle) -> Rectangle
    result_xspace = Rectangle(xspace.min_corner, xspace.max_corner)
    if alphai == 0:
        # result_xspace.max_corner[i] = ypoint[i]
        result_xspace.max_corner = subt(i, xspace.max_corner, ypoint)
    elif alphai == 1:
        # result_xspace.min_corner[i] = ypoint[i]
        result_xspace.min_corner = subt(i, xspace.min_corner, ypoint)
    return result_xspace


def crect(i, alphai, yrectangle, xspace):
    # type: (int, int, Rectangle, Rectangle) -> Rectangle
    result_xspace = Rectangle(xspace.min_corner, xspace.max_corner)
    if alphai == 0:
        result_xspace = cpoint(i, alphai, yrectangle.max_corner, xspace)
    elif alphai == 1:
        result_xspace = cpoint(i, alphai, yrectangle.min_corner, xspace)
    return result_xspace


def bpoint(alpha, ypoint, xspace):
    # type: (tuple, tuple, Rectangle) -> Rectangle
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(ypoint)), \
        'xspace.min_corner and xpoint do not share the same dimension'
    # assert (dim(ypoint.max_corner) == dim(ypoint)), \
    #    'xspace.max_corner and ypoint do not share the same dimension'
    temp = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp = cpoint(i, alphai, ypoint, temp)
    return temp


def brect(alpha, yrectangle, xspace):
    # type: (tuple, Rectangle, Rectangle) -> Rectangle
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        'xrectangle.min_corner and xrectangle.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    assert (dim(alpha) == dim(yrectangle.min_corner)), \
        'alpha and xrectangle.min_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(yrectangle.min_corner)), \
        'xspace.min_corner and xrectangle.min_corner do not share the same dimension'
    # assert (dim(xspace.max_corner) == dim(yrectangle.max_corner)), \
    #    'xspace.max_corner and yrectangle.max_corner do not share the same dimension'
    temp = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp = crect(i, alphai, yrectangle, temp)
    return temp


def irect(alphaincomp, yrectangle, xspace):
    # type: (list, Rectangle, Rectangle) -> list
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        'xrectangle.min_corner and xrectangle.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    # assert (dim(alphaincomp_list) == dim(yrectangle.min_corner)), \
    #    'alphaincomp_list and yrectangle.min_corner do not share the same dimension'
    # assert (dim(alphaincomp_list) == dim(yrectangle.max_corner)), \
    #    'alphaincomp_list and yrectangle.max_corner do not share the same dimension'
    return [brect(alphaincomp_i, yrectangle, xspace) for alphaincomp_i in alphaincomp]


def idwc(y, z):
    # type: (Rectangle, Rectangle) -> iter
    assert z.dim() == y.dim(), 'Rectangles should have the same dimension'
    # y = [0, y_]
    # assert y.min_corner <= z.min_corner, 'Minimal corner of {0} must be at the origin of the xspace ' \
    #                                      '(i.e., {0} <= {1})'.format(y.min_corner, z.min_corner)
    assert less_equal(y.min_corner, z.min_corner) or incomparables(y.min_corner, z.min_corner),\
        'Minimal corner of {0} must be at the origin of the xspace (i.e., {0} <= {1})'\
            .format(y.min_corner, z.min_corner)
    # assert z.min_corner <= y.max_corner, 'Rectangles {0} and {1} must intersect'.format(y, z)
    assert less_equal(z.min_corner, y.max_corner) or incomparables(z.min_corner, y.max_corner), \
        'Rectangles {0} and {1} must intersect'.format(y, z)

    def w_set(m):
        # type: (int) -> iter
        # { 0^{j-1} 1 *^{m-j} } for j in [1, m]
        return ["0"*(j-1) + "1" + "*"*(m-j) for j in range(1, m+1)]

    def gamma(w, y, z):
        # type: (iter, Rectangle, Rectangle) -> tuple
        d = z.dim()
        j = 0

        alpha = ["*"]*d
        for i in range(d):
            if y.max_corner[i] < z.max_corner[i]:
                alpha[i] = w[j]
                j += 1

        return tuple(int(alphai) if alphai != "*" else 2 for alphai in alpha)

    # Number of coordinates for which y.max_corner[i] < z.max_corner[i]
    d = z.dim()
    m = sum(y.max_corner[i] < z.max_corner[i] for i in range(d))
    # coor = [y.max_corner[i] < z.max_corner[i] for i in range(d)]
    # m = coor.count(True)

    yp = Rectangle(y.max_corner, y.max_corner)
    result = []
    ws = w_set(m)
    for w in ws:
        alpha = gamma(w, y, z)
        result.append(brect(alpha, yp, z))
        # brect(alpha, yrectangle, xspace)

    return result


def iuwc(y, z):
    # type: (Rectangle, Rectangle) -> iter
    assert z.dim() == y.dim(), 'Rectangles should have the same dimension'
    # y = [y^_, 1]
    # assert z.max_corner <= y.max_corner, 'Maximal corner of {1} must be the highest value of the xspace ' \
    #                                      '(i.e., {0} <= {1})'.format(y.min_corner, z.min_corner)
    assert less_equal(z.max_corner, y.max_corner) or incomparables(z.max_corner, y.max_corner), \
        'Maximal corner of {1} must be the highest value of the xspace (i.e., {0} <= {1})'\
            .format(y.min_corner, z.min_corner)
    # assert y.min_corner <= z.max_corner, 'Rectangles {0} and {1} must intersect'.format(y, z)
    assert less_equal(y.min_corner, z.max_corner) or incomparables(y.min_corner, z.max_corner), \
        'Rectangles {0} and {1} must intersect'.format(y, z)

    def w_set(m):
        # type: (int) -> iter
        # { 1^{j-1} 0 *^{m-j} } for j in [1, m]
        return ["1"*(j-1) + "0" + "*"*(m-j) for j in range(1, m+1)]

    def gamma(w, y, z):
        # type: (iter, Rectangle, Rectangle) -> tuple
        d = z.dim()
        j = 0

        alpha = ["*"]*d
        for i in range(d):
            # if y.min_corner[i] < z.max_corner[i]:
            if z.min_corner[i] < y.min_corner[i]:
                alpha[i] = w[j]
                j += 1

        return tuple(int(alphai) if alphai != "*" else 2 for alphai in alpha)

    # Number of coordinates for which y.max_corner[i] < z.max_corner[i]
    d = z.dim()
    m = sum(z.min_corner[i] < y.min_corner[i] for i in range(d))
    # m = sum(y.min_corner[i] < z.max_corner[i] for i in range(d))
    # coor = [z.min_corner[i] < y.min_corner[i] for i in range(d)]
    # m = coor.count(True)

    yp = Rectangle(y.min_corner, y.min_corner)
    result = []
    ws = w_set(m)
    for w in ws:
        alpha = gamma(w, y, z)
        result.append(brect(alpha, yp, z))
        # brect(alpha, yrectangle, xspace)

    return result
