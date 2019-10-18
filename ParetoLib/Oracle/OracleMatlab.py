# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OracleMatlab.

This module instantiate the abstract interface Oracle.
The OracleMatlab interacts with parametrized Matlab models.
"""

import pickle
import io
import os
import sys
import matlab.engine

import ParetoLib.Oracle as RootOracle
from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib._py3k import get_stdout_matlab, get_stderr_matlab


class OracleMatlab(Oracle):
    def __init__(self, matlab_model_file=''):
        # type: (OracleMatlab, str) -> None
        """
        An OracleMatlab is a set of Conditions.
        """
        # super(OracleMatlab, self).__init__()
        Oracle.__init__(self)

        # Initialize the Matlab Engine
        self.out = get_stdout_matlab()
        self.err = get_stderr_matlab()
        self.eng = matlab.engine.start_matlab()

        # Matlab function 'f' not loaded yet.
        # Dimension of the space unknown
        self.f = None
        self.d = None

        self.matlab_model_file = matlab_model_file

    def _lazy_init(self):
        # type: (OracleMatlab) -> None
        assert self.matlab_model_file != ''

        # Lazy initialization of the OracleMatlab
        RootOracle.logger.debug('Initializing OracleMatlab')

        # Include the path of the Matlab model in the Matlab workspace
        self.eng.addpath(os.path.dirname(self.matlab_model_file))

        # Extract the name of the Matlab function.
        # If the Matlab filename is 'matlab_model.m' then:
        #
        # self.eng.matlab_model(*args, **kwargs)
        #
        # will invoke the code

        # matlab_model_file = '/path/to/matlab_model.m'
        # filename, file_extension = ('/path/to/matlab_model', '.m')
        filename, file_extension = os.path.splitext(self.matlab_model_file)
        # func_name = 'matlab_model'
        func_name = os.path.basename(filename)

        # Extract from Matlab the function 'f' that will be used as Oracle
        # self.f = self.eng.__getattr__('matlab_model')
        self.f = self.eng.__getattr__(func_name)

        # Dimension, i.e., equivalent to the number of in arguments of the function 'f'
        self.d = int(self.eng.nargin(func_name))

        RootOracle.logger.debug('Function {0} with {1} parameters'.format(func_name, self.d))

    def __setattr__(self, name, value):
        # type: (OracleMatlab, str, None) -> None
        """
        Assignation of a value to a class attribute.

        Args:
            self (OracleMatlab): The OracleMatlab.
            name (str): The attribute.
            value (None): The value

        Returns:
            None: self.name = value.

        Example:
        >>> matlab_model_file = 'test1.m'
        >>> ora = OracleMatlab()
        >>> ora.matlab_model_file = matlab_model_file
        """

        object.__setattr__(self, name, value)

        str_matlab_file = 'matlab_model_file'
        if (name == str_matlab_file) and (value.strip() != ''):
            self._lazy_init()

    def __repr__(self):
        # type: (OracleMatlab) -> str
        """
        Printer.
        """
        return self.matlab_model_file

    def __str__(self):
        # type: (OracleMatlab) -> str
        """
        Printer.
        """
        return self.matlab_model_file

    def __eq__(self, other):
        # type: (OracleMatlab, OracleMatlab) -> bool
        """
        self == other
        """
        return self.matlab_model_file == other.matlab_model_file

    def __ne__(self, other):
        # type: (OracleMatlab, OracleMatlab) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    def __hash__(self):
        # type: (OracleMatlab) -> int
        """
        Identity function (via hashing).
        """
        return hash(tuple(self.matlab_model_file))

    def __del__(self):
        # type: (OracleMatlab) -> None
        """
        Removes 'self' from the namespace.
        """
        if self.eng is not None:
            self.eng.quit()

    def __copy__(self):
        # type: (OracleMatlab) -> OracleMatlab
        """
        other = copy.copy(self)
        """
        return OracleMatlab(matlab_model_file=self.matlab_model_file)

    def __deepcopy__(self, memo):
        # type: (OracleMatlab, dict) -> OracleMatlab
        """
        other = copy.deepcopy(self)
        """
        # deepcopy function is required for creating multiple instances of the Oracle in ParSearch.
        # deepcopy cannot handle neither regex nor Popen processes
        return OracleMatlab(matlab_model_file=self.matlab_model_file)

    def dim(self):
        # type: (OracleMatlab) -> int
        """
        See Oracle.dim().
        """
        return self.d

    def get_var_names(self):
        # type: (OracleMatlab) -> list
        """
        See Oracle.get_var_names().
        """
        return ['p'+str(i) for i in range(self.d)]

    def __contains__(self, point):
        # type: (OracleMatlab, tuple) -> bool
        """
        Synonym of self.member(point).
        A point belongs to the Oracle if it satisfies all the conditions.
        """
        return self.member(point) is True

    def member(self, point):
        # type: (OracleMatlab, tuple) -> bool
        """
        See Oracle.member().
        """
        return self.f(*point, stdout=self.out, stderr=self.err)

    def membership(self):
        # type: (OracleMatlab) -> callable
        """
        See Oracle.membership().
        """
        return lambda point: self.member(point)

    # Read/Write file functions
    def from_file_binary(self, finput=None):
        # type: (OracleMatlab, io.BinaryIO) -> None
        """
        See Oracle.from_file_binary().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = pickle.load(finput)
            matlab_model_file = os.path.join(current_path, path) if not os.path.isabs(path) else path

            if not os.path.isfile(matlab_model_file):
                RootOracle.logger.info('File {0} does not exists or it is not a file'.format(matlab_model_file))

            self.__init__(matlab_model_file=matlab_model_file)

        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def from_file_text(self, finput=None):
        # type: (OracleMatlab, io.BinaryIO) -> None
        """
        See Oracle.from_file_text().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            # The file contains the path to the Matlab file containing the parametrized model.
            #
            # os.path.join creates absolute path from relative path "./something.txt"
            # os.path.realpath uniforms path "2D/./signal.csv" by "2D/signal.csv"
            #
            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = finput.readline().strip(' \n\t')
            matlab_model_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            matlab_model_file = os.path.realpath(matlab_model_file)

            if not os.path.isfile(matlab_model_file):
                RootOracle.logger.info('File {0} does not exists or it is not a file'.format(matlab_model_file))

            self.__init__(matlab_model_file=matlab_model_file)

        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def to_file_binary(self, foutput=None):
        # type: (OracleMatlab, io.BinaryIO) -> None
        """
        See Oracle.to_file_binary().
        """
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(os.path.abspath(self.matlab_model_file), foutput, pickle.HIGHEST_PROTOCOL)

    def to_file_text(self, foutput=None):
        # type: (OracleMatlab, io.BinaryIO) -> None
        """
        See Oracle.to_file_text().
        """
        assert (foutput is not None), 'File object should not be null'

        foutput.write(os.path.abspath(self.matlab_model_file) + '\n')
