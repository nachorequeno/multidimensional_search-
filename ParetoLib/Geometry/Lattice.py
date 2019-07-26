# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Lattice.

This module introduces the Lattice class. It includes a set of
operations for creating and handling partial ordered sets.
"""

from sortedcontainers import SortedKeyList
from operator import getitem


class Lattice(object):
    def __init__(self,
                 dim,
                 key=lambda x: x):
        # type: (Lattice, int, callable) -> None
        assert dim > 0
        self.key = key
        # self.list_of_lists = [SortedKeyList([], key=lambda x, j=i: self.key(x)[j]) for i in range(dim)]
        self.list_of_lists = [SortedKeyList([], key=lambda x, j=i: getitem(self.key(x), j)) for i in range(dim)]
        # TODO: Change SortedList by SortedSet?

    def _to_str(self):
        # type: (Lattice) -> str
        """
        Printer.
        """
        return str(self.list_of_lists)

    def __repr__(self):
        # type: (Lattice) -> str
        """
        Printer.
        """
        return self._to_str()

    def __str__(self):
        # type: (Lattice) -> str
        """
        Printer.
        """
        return self._to_str()

    def __eq__(self, other):
        # type: (Lattice, Lattice) -> bool
        """
        self == other
        """
        return (other.list_of_lists == self.list_of_lists) and (other.key == self.key)

    def __ne__(self, other):
        # type: (Lattice, Lattice) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    def __hash__(self):
        # type: (Lattice) -> int
        """
        Identity function (via hashing).
        """
        return hash((tuple(self.list_of_lists), self.key))

    def __len__(self):
        # type: (Lattice) -> int
        """
        len(self)
        """
        s = self.get_elements()
        return len(s)

    # Lattice properties
    def dim(self):
        # type: (Lattice) -> int
        """
        Dimension of the Lattice.

        Args:
            self (Lattice): The Lattice.

        Returns:
            int: Dimension of the Lattice.

        Example:
        >>> x = (0,0,0)
        >>> l = Lattice(len(x))
        >>> l.dim()
        >>> 3
        """
        return len(self.list_of_lists)

    def get_elements(self):
        # type: (Lattice) -> set
        return set(self.list_of_lists[0])

    def add(self, elem):
        # type: (Lattice, object) -> None
        for l in self.list_of_lists:
            l.add(elem)

    def add_list(self, lst):
        # type: (Lattice, iter) -> None
        for elem in lst:
            self.add(elem)

    def remove(self, elem):
        # type: (Lattice, object) -> None
        for l in self.list_of_lists:
            l.discard(elem)

    def remove_list(self, lst):
        # type: (Lattice, iter) -> None
        for elem in lst:
            self.remove(elem)

    def less(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i < elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_lists:
            index = l.bisect_left(elem)
            s = s.intersection(l[:index])
        return s

    def less_equal(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i <= elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_lists:
            index = l.bisect_right(elem)
            s = s.intersection(l[:index])
        return s

    def greater(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i > elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_lists:
            index = l.bisect_right(elem)
            s = s.intersection(l[index:])
        return s

    def greater_equal(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i >= elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_lists:
            index = l.bisect_left(elem)
            s = s.intersection(l[index:])
        return s

    def equal(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i == elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_lists:
            index1 = l.bisect_left(elem)
            index2 = l.bisect_right(elem)
            s = s.intersection(l[index1:index2])
        return s
