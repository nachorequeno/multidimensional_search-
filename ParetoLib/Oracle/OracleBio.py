# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OracleBio.

This module instantiate the abstract interface Oracle.
It encapsulates the simulation of biological models.*****
"""

import os
import io

import ParetoLib.Oracle as RootOracle
from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.Bio.Bio import *


class OracleBio(Oracle):

    def __init__(self):
        pass

    def __repr__(self):
        # type: (OracleBio) -> str
        """
        Printer.
        """
        return ''

    def __str__(self):
        # type: (OracleBio) -> str
        """
        Printer.
        """
        return ''

    def __eq__(self, other):
        # type: (OracleBio, OracleBio) -> bool
        """
        self == other
        """
        return False

    def __ne__(self, other):
        # type: (OracleBio, OracleBio) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    def __hash__(self):
        # type: (OracleBio) -> int
        """
        Identity function (via hashing).
        """
        return 0

    def dim(self):
        # type: (OracleBio) -> int
        """
        Dimension of the space where the Oracle is working on.

        Args:
            self (Oracle): The Oracle.

        Returns:
            int: Dimension of the space.

        Example:
        >>> ora = Oracle()
        >>> ora.from_file("3d_space.txt")
        >>> ora.dim()
        >>> 3
        """
        return 0

    def get_var_names(self):
        # type: (OracleBio) -> list
        """
        Name of the axes of the space where the Oracle is working on.

        Args:
            self (Oracle): The Oracle.

        Returns:
            list: List of names.

        Example:
        >>> ora = Oracle()
        >>> ora.from_file('3d_space.txt')
        >>> ora.get_var_names()
        >>> ['x', 'y', 'z']
        """
        # If parameter names are not provided, then we use lexicographic characters by default.
        return [chr(i) for i in range(ord('a'), ord('z') + 1)]

    def __contains__(self, point):
        # type: (OracleBio, tuple) -> bool
        """
        Synonym of self.member(point)
        """
        return self.member(point) is True

    def member(self, point):
        # type: (OracleBio, tuple) -> bool
        """
        Function answering whether a point belongs to the upward
        closure or not.

        Args:
            self (Oracle): The Oracle.
            point (tuple): The point of the space that we inspect.

        Returns:
            bool: True if the point belongs to the upward closure.

        Example:
        >>> x = (0.0, 0.0)
        >>> ora = Oracle()
        >>> ora.member(x)
        >>> False
        """
        return False

    def membership(self):
        # type: (OracleBio) -> callable
        """
        Returns a function that answers membership queries.
        Later on, this function is used as input parameter of
        ParetoLib.Search algorithms for guiding the discovery of the
        Pareto front.

        Args:
            self (Oracle): The Oracle.

        Returns:
            callable: Function that answers whether a point belongs
                      to the upward closure or not.

        Example:
        >>> x = (0.0, 0.0)
        >>> ora = Oracle()
        >>> f = ora.membership()
        >>> f(x)
        >>> False
        """
        return lambda point: self.member(point)

    # Read/Write file functions
     def from_file_binary(self, finput=None):
        # type: (Oracle, io.BinaryIO) -> None
        """
        Loading an Oracle from a binary file.

        Args:
            self (Oracle): The Oracle.
            finput (io.BinaryIO): The file where the Oracle is saved.

        Returns:
            None: The Oracle is loaded from finput.

        Example:
        >>> ora = Oracle()
        >>> infile = open('filename', 'rb')
        >>> ora.from_file_binary(infile)
        >>> infile.close()
        """
        pass

    def from_file_text(self, finput=None):
        # type: (Oracle, io.BinaryIO) -> None
        """
        Loading an Oracle from a text file.

        Args:
            self (Oracle): The Oracle.
            finput (io.BinaryIO): The file where the Oracle is saved.

        Returns:
            None: The Oracle is loaded from finput.

        Example:
        >>> ora = Oracle()
        >>> infile = open('filename', 'r')
        >>> ora.from_file_text(infile)
        >>> infile.close()
        """
        pass

    def to_file_binary(self, foutput=None):
        # type: (Oracle, io.BinaryIO) -> None
        """
        Writing of an Oracle to a binary file.

        Args:
            self (Oracle): The Oracle.
            foutput (io.BinaryIO): The file where the Oracle will
                                   be saved.

        Returns:
            None: The Oracle is saved in foutput.

        Example:
        >>> ora = Oracle()
        >>> outfile = open('filename', 'wb')
        >>> ora.to_file_binary(outfile)
        >>> outfile.close()
        """
        pass

    def to_file_text(self, foutput=None):
        # type: (Oracle, io.BinaryIO) -> None
        """
        Writing of an Oracle to a text file.

        Args:
            self (Oracle): The Oracle.
            foutput (io.BinaryIO): The file where the Oracle will
                                   be saved.

        Returns:
            None: The Oracle is saved in foutput.

        Example:
        >>> ora = Oracle()
        >>> outfile = open('filename', 'w')
        >>> ora.to_file_text(outfile)
        >>> outfile.close()
        """
        pass
