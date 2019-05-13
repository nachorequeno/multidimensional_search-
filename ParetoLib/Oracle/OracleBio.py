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


class OracleBio3D(Oracle):

    def __init__(self, max_k, max_e, max_gamma, N_MF10=10, n_simulations_MF10=100, nthreads=float('inf')):
        # type: (OracleBio3D, float, float, float, int, int, float) -> None
        Oracle.__init__(self)
        self.max_k = max_k
        self.max_e = max_e
        self.max_gamma = max_gamma
        self.N_MF10 = N_MF10
        self.n_simulations_MF10 = n_simulations_MF10
        self.nthreads = nthreads

    def __repr__(self):
        # type: (OracleBio3D) -> str
        """
        Printer.
        """
        return self._to_str()

    def __str__(self):
        # type: (OracleBio3D) -> str
        """
        Printer.
        """
        return self._to_str()

    def _to_str(self):
        # type: (OracleBio3D) -> str
        """
        Printer.
        """
        s = 'Number of nucleosomes: {0}\n'.format(self.N_MF10)
        s += 'Number of simulations: {0}'.format(self.n_simulations_MF10)
        s += 'Number of threads: {0}\n'.format(self.nthreads)
        s += 'Max value of k: {0}\n'.format(self.max_k)
        s += 'Max value of e: {0}\n'.format(self.max_e)
        s += 'Max value of gamma: {0}\n'.format(self.max_gamma)
        return s

    def __eq__(self, other):
        # type: (OracleBio3D, OracleBio3D) -> bool
        """
        self == other
        """
        return (self.max_k == other.max_k) and \
               (self.max_e == other.max_e) and \
               (self.max_gamma == other.max_gamma) and \
               (self.nthreads == other.nthreads) and \
               (self.N_MF10 == other.N_MF10) and\
               (self.n_simulations_MF10 == other.n_simulations_MF10)

    def __hash__(self):
        # type: (OracleBio3D) -> int
        """
        Identity function (via hashing).
        """
        return hash(tuple(self.max_k, self.max_e, self.max_gamma, self.N_MF10, self.n_simulations_MF10, self.nthreads))

    def dim(self):
        # type: (OracleBio3D) -> int
        """
        Dimension of the space where the Oracle is working on.

        Args:
            self (Oracle): The Oracle.

        Returns:
            int: Dimension of the space.

        Example:
        >>> ora = OracleBio3D()
        >>> ora.from_file("3d_space.txt")
        >>> ora.dim()
        >>> 3
        """
        return 3

    def get_var_names(self):
        # type: (OracleBio3D) -> list
        """
        Name of the axes of the space where the Oracle is working on.

        Args:
            self (Oracle): The Oracle.

        Returns:
            list: List of names.

        Example:
        >>> ora = OracleBio3D()
        >>> ora.from_file('3d_space.txt')
        >>> ora.get_var_names()
        >>> ['x', 'y', 'z']
        """
        # If parameter names are not provided, then we use lexicographic characters by default.
        return ['k', 'e', 'gamma']

    def member(self, point):
        # type: (OracleBio3D, tuple) -> bool
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
        >>> ora = OracleBio3D()
        >>> ora.member(x)
        >>> False
        """
        assert dim(point) == self.dim()

        k, e, gamma = point
        m1, _ = sim(k=self.max_k - k, e=e, gamma=self.max_gamma - gamma, N_MF10=self.N_MF10, n_simulations_MF10=self.n_simulations_MF10, nthreads=self.nthreads)

        return bistable_test(m1)

    # Read/Write file functions
    def from_file_binary(self, finput=None):
        # type: (OracleBio3D, io.BinaryIO) -> None
        """
        See Oracle.from_file_binary().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            self.N_MF10 = pickle.load(finput)
            self.n_simulations_MF10 = pickle.load(finput)
            self.nthreads = pickle.load(finput)
            self.max_k = pickle.load(finput)
            self.max_e = pickle.load(finput)
            self.max_gamma = pickle.load(finput)
        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def from_file_text(self, finput=None):
        # type: (OracleBio3D, io.BinaryIO) -> None
        """
        See Oracle.from_file_text().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            self.N_MF10 = int(finput.readline().strip(' \n\t'))
            self.n_simulations_MF10 = int(finput.readline().strip(' \n\t'))
            self.nthreads = float(finput.readline().strip(' \n\t'))
            self.max_k = float(finput.readline().strip(' \n\t'))
            self.max_e = float(finput.readline().strip(' \n\t'))
            self.max_gamma = float(finput.readline().strip(' \n\t'))
        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def to_file_binary(self, foutput=None):
        # type: (OracleBio3D, io.BinaryIO) -> None
        """
        See Oracle.to_file_binary().
        """
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(str(self.N_MF10), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(str(self.n_simulations_MF10), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(str(self.nthreads), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(str(self.max_k), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(str(self.max_e), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(str(self.max_gamma), foutput, pickle.HIGHEST_PROTOCOL)

    def to_file_text(self, foutput=None):
        # type: (OracleBio3D, io.BinaryIO) -> None
        """
        See Oracle.to_file_text().
        """
        assert (foutput is not None), 'File object should not be null'

        foutput.write(str(self.N_MF10) + '\n')
        foutput.write(str(self.n_simulations_MF10) + '\n')
        foutput.write(str(self.nthreads) + '\n')
        foutput.write(str(self.max_k) + '\n')
        foutput.write(str(self.max_e) + '\n')
        foutput.write(str(self.max_gamma) + '\n')


class OracleBio2D(OracleBio3D):

    def __init__(self, max_alpha, max_gamma, N_MF10=10, n_simulations_MF10=100, nthreads=float('inf')):
        # type: (OracleBio2D, float, float, int, int, float) -> None
        super(OracleBio2D, self).__init__(max_k=1, max_e=max_alpha, max_gamma=max_gamma, N_MF10=N_MF10, n_simulations_MF10=n_simulations_MF10, nthreads=nthreads)

    def dim(self):
        # type: (OracleBio2D) -> int
        """
        Dimension of the space where the Oracle is working on.

        Args:
            self (Oracle): The Oracle.

        Returns:
            int: Dimension of the space.

        Example:
        >>> ora = OracleBio2D()
        >>> ora.from_file("2d_space.txt")
        >>> ora.dim()
        >>> 2
        """
        return 2

    def get_var_names(self):
        # type: (OracleBio2D) -> list
        """
        Name of the axes of the space where the Oracle is working on.

        Args:
            self (Oracle): The Oracle.

        Returns:
            list: List of names.

        Example:
        >>> ora = OracleBio2D()
        >>> ora.from_file('2d_space.txt')
        >>> ora.get_var_names()
        >>> ['x', 'y']
        """
        # If parameter names are not provided, then we use lexicographic characters by default.
        return ['alpha', 'gamma']

    def member(self, point):
        # type: (OracleBio2D, tuple) -> bool
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
        >>> ora = OracleBio2D()
        >>> ora.member(x)
        >>> False
        """
        assert dim(point) == self.dim()

        alpha, gamma = point
        m1, _ = sim(k=1.0, e=alpha, gamma=self.max_gamma - gamma, N_MF10=self.N_MF10, n_simulations_MF10=self.n_simulations_MF10, nthreads=self.nthreads)

        return bistable_test(m1)
