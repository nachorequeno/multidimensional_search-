# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OracleBio.

This module instantiate the abstract interface Oracle.
It encapsulates the simulation of biological model SSA_LRI_MFPT1.
"""

import sys
import io
import pickle

import ParetoLib.Oracle as RootOracle
from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.Bio.SSA_LRI_MFPT1 import sim, bistable_test
from ParetoLib.Geometry.Point import dim


class OracleBio(Oracle):

    def __init__(self, N_MF10=10, n_simulations_MF10=100, nthreads=float('inf')):
        # type: (OracleBio, int, int) -> None
        Oracle.__init__(self)
        self.N_MF10 = N_MF10
        self.n_simulations_MF10 = n_simulations_MF10
        self.nthreads = nthreads

    def __repr__(self):
        # type: (OracleBio) -> str
        """
        Printer.
        """
        return self._to_str()

    def __str__(self):
        # type: (OracleBio) -> str
        """
        Printer.
        """
        return self._to_str()

    def _to_str(self):
        # type: (OracleBio) -> str
        """
        Printer.
        """
        s = 'Number of nucleosomes: {0}\n'.format(self.N_MF10)
        s += 'Number of simulations: {0}'.format(self.n_simulations_MF10)
        s += 'Number of threads: {0}\n'.format(self.nthreads)
        return s

    def __eq__(self, other):
        # type: (OracleBio, OracleBio) -> bool
        """
        self == other
        """
        return (self.nthreads == other.nthreads) and (self.N_MF10 == other.N_MF10) and (self.n_simulations_MF10 == other.n_simulations_MF10)

    def __hash__(self):
        # type: (OracleBio) -> int
        """
        Identity function (via hashing).
        """
        return hash(tuple(self.N_MF10, self.n_simulations_MF10, self.nthreads))

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
        return 3

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
        return ['k', 'e', 'gamma']

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
        >>> x = (0.0, 0.0, 0.0)
        >>> ora = OracleBio()
        >>> ora.member(x)
        >>> False
        """
        assert dim(point) == self.dim()

        k, e, gamma = point
        m1, _ = sim(k=k, e=e, gamma=gamma, N_MF10=self.N_MF10, n_simulations_MF10=self.n_simulations_MF10, nthreads=self.nthreads)

        return bistable_test(m1)

    # Read/Write file functions
    def from_file_binary(self, finput=None):
        # type: (OracleBio, io.BinaryIO) -> None
        """
        See Oracle.from_file_binary().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            self.N_MF10 = pickle.load(finput)
            self.n_simulations_MF10 = pickle.load(finput)

        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def from_file_text(self, finput=None):
        # type: (OracleBio, io.BinaryIO) -> None
        """
        See Oracle.from_file_text().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            self.N_MF10 = finput.readline().strip(' \n\t')
            self.n_simulations_MF10 = finput.readline().strip(' \n\t')
        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def to_file_binary(self, foutput=None):
        # type: (OracleBio, io.BinaryIO) -> None
        """
        See Oracle.to_file_binary().
        """
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(str(self.N_MF10), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(str(self.n_simulations_MF10), foutput, pickle.HIGHEST_PROTOCOL)

    def to_file_text(self, foutput=None):
        # type: (OracleBio, io.BinaryIO) -> None
        """
        See Oracle.to_file_text().
        """
        assert (foutput is not None), 'File object should not be null'

        foutput.write(str(self.N_MF10) + '\n')
        foutput.write(str(self.n_simulations_MF10) + '\n')

