# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Oracle.

This module defines the abstract interface for Oracles.
It encapsulates the set of minimum operations that every oracle
should provide for guiding the discovery of the Pareto front.
Later on, this oracle can be specialized for multiple application
domains by simply implementing the abstract interface.
"""

import os
import io


# Oracle template

class Oracle:

    def __init__(self):
        pass

    # Printers
    def __repr__(self):
        # type: (Oracle) -> str
        return ''

    def __str__(self):
        # type: (Oracle) -> str
        return ''

    # Equality functions
    def __eq__(self, other):
        # type: (Oracle, Oracle) -> bool
        return False

    def __ne__(self, other):
        # type: (Oracle, Oracle) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Oracle) -> int
        return 0

    def dim(self):
        # type: (Oracle) -> int
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
        # type: (Oracle) -> list
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

    # Membership functions
    def __contains__(self, point):
        # type: (Oracle, tuple) -> bool
        """
        Synonym of self.member(point)
        """
        return self.member(point) is True

    def member(self, point):
        # type: (Oracle, tuple) -> bool
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
        # type: (Oracle) -> callable
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
    def from_file(self, fname='', human_readable=False):
        # type: (Oracle, str, bool) -> None
        """
        Loading an Oracle from a file.

        Args:
            self (Oracle): The Oracle.
            fname (string): The file name where the Oracle is saved.
            human_readable (bool): Boolean indicating if the
                           Oracle will be loaded from a binary or
                           text file.

        Returns:
            None: The Oracle is loaded from fname.

        Example:
        >>> ora = Oracle()
        >>> ora.from_file('filename')
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

    def to_file(self, fname='', append=False, human_readable=False):
        # type: (Oracle, str, bool, bool) -> None
        """
        Writing of an Oracle to a file.

        Args:
            self (Oracle): The Oracle.
            fname (string): The file name where the Oracle will
                            be saved.
            append (bool): Boolean indicating if the Oracle will
                           be appended at the end of the file.
            human_readable (bool): Boolean inficating if the
                           Oracle will be saved in a binary or
                           text file.

        Returns:
            None: The Oracle is saved in fname.

        Example:
        >>> ora = Oracle()
        >>> ora.to_file('filename')
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
