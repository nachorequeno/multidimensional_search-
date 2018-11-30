# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Segment.

This module introduces the Segment class. It includes a set of
operations for creating and handling segments, i.e., intervals
between two Cartesian points. For instance, the diagonal of a
Rectangle is considered as a Segment object.

This class is used for storing the result of a binary search
over the diagonal of a Rectangle, i.e., the interval where a
Pareto point is located.
"""

import math

from ParetoLib.Geometry.Point import maximum, minimum, greater_equal, less_equal, r
import ParetoLib.Geometry.Point as Point


class Segment:
    def __init__(self, low, high):
        # type: (Segment, tuple, tuple) -> None
        """
        A Segment is represented by a couple of Points (i.e., tuples)
        named self.low and self.high.

        Given two input Points, the attribute self.low contains
        the smallest one and self.high the greatest one.

        Points are stored as tuples of float numbers, which are
        automatically rounded to the maximal decimal precision
        specified by ParetoLib.Geometry.__numdigits__

        By using Segments as intermediate elements for initializing
        Rectangles, we guarantee that arithmetic issues caused by
        decimal precision are removed.

        Args:
            self (Segment): A Segment.
            low (tuple): A point.
            high (tuple): Another point.

        Returns:
            None

        Example:
        >>> x = (2, 4, 6)
        >>> y = (2, 4, 7)
        >>> s = Segment(x, y)
        """

        self.low = minimum(low, high)
        self.high = maximum(low, high)
        assert Point.dim(self.low) == Point.dim(self.high)
        assert greater_equal(self.high, self.low)

    # Membership function
    def __contains__(self, xpoint):
        # type: (Segment, tuple) -> bool
        """
        Membership function that checks if a Point is located
        inside a Segment.

        Args:
            self (Segment): A Segment.
            xpoint (tuple): A point.

        Returns:
            bool: True if xpoint is inside the interval
            [self.low, self.high].

        Example:
        >>> p = (2, 4, 7)
        >>> x = (2, 4, 6)
        >>> y = (2, 4, 8)
        >>> s = Segment(x, y)
        >>> p in s
        >>> True
        """
        return (greater_equal(xpoint, self.low) and
                less_equal(xpoint, self.high))

    def __setattr__(self, name, value):
        # type: (Segment, str, iter) -> None
        """
        Assignation of a value to a class attribute.

        Args:
            self (Segment): The Segment.
            name (str): The attribute.
            value (None): The value

        Returns:
            None: self.name = value.

        Example:
        >>> x = (2, 4, 6)
        >>> y = (2, 4, 7)
        >>> s = Segment(x, y)
        >>> s.high = y
        """
        # Round the elements of 'value' when assigning them to self.low or self.high
        val = tuple(r(vi) for vi in value)
        self.__dict__[name] = val
        # object.__setattr__(self, name, val)

    def _to_str(self):
        # type: (Segment) -> str
        """
        Printer.
        """
        _string = '<'
        _string += str(self.low)
        _string += ', '
        _string += str(self.high)
        _string += '>'
        return _string

    def __repr__(self):
        # type: (Segment) -> str
        """
        Printer.
        """
        return self._to_str()

    def __str__(self):
        # type: (Segment) -> str
        """
        Printer.
        """
        return self._to_str()

    def __eq__(self, other):
        # type: (Segment) -> bool
        """
        self == other
        """
        return (other.low == self.low) and (other.high == self.high)

    def __ne__(self, other):
        # type: (Segment) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    def __hash__(self):
        # type: (Segment) -> float
        """
        Identity function (via hashing).
        """
        return hash((self.low, self.high))

    # Segment properties
    def dim(self):
        # type: (Segment) -> int
        """
        Dimension of the points stored in a Segment.

        Args:
            self (Segment): A Segment.

        Returns:
            int: len(self.low).

        Example:
        >>> x = (2, 4, 6)
        >>> y = (2, 4, 7)
        >>> s = Segment(x, y)
        >>> s.dim()
        >>> 3
        """
        return Point.dim(self.low)

    def diag(self):
        # type: (Segment) -> tuple
        """
        Diagonal of the Segment, i.e., vector going from the
        lower corner to the higher corner.

        Args:
            self (Segment): A Segment.

        Returns:
            tuple: substract(self.high, self.low).

        Example:
        >>> x = (0, 1, 2)
        >>> y = (3, 4, 5)
        >>> s = Segment(x, y)
        >>> s.diag()
        >>> (3.0, 3.0, 3.0)
        """

        return Point.subtract(self.high, self.low)

    def norm(self):
        # type: (Segment) -> float
        """
        Norm of the Segment.diag().

        Args:
            self (Segment): A Segment.

        Returns:
            float: norm(self.diag()).

        Example:
        >>> x = (0, 1, 2)
        >>> y = (3, 4, 5)
        >>> s = Segment(x, y)
        >>> s.norm()
        >>> 5.196
        """

        diagonal = self.diag()
        return Point.norm(diagonal)
