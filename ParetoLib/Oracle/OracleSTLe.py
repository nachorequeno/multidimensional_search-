# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OracleSTLe.

This module instantiate the abstract interface Oracle.
It encapsulates the interaction with STLe [1].

[1] Bakhirkin, A., and Basset, N. (2019, April).
"Specification and Efficient Monitoring Beyond STL".
In Proceedings of the 25th International Conference on Tools and
Algorithms for the Construction and Analysis of Systems (TACAS)
"""

import re
import pickle
import subprocess
import tempfile
import ast
import io
import sys
import os
import filecmp

import ParetoLib.Oracle as RootOracle
from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.STLe.STLe import STLE_BIN, STLE_OPT_IN_MEM_STL, STLE_OPT_IN_FILE_STL, STLE_OPT_TIME, STLE_OPT_TIMESTAMP, \
    STLE_OPT_CSV, STLE_OPT_IN_MEM_CSV, STLE_OPT_IN_FILE_CSV


class OracleSTLe(Oracle):
    def __init__(self, stl_prop_file='', csv_signal_file='', stl_param_file=''):
        # type: (OracleSTLe, str, str, str) -> None
        # assert stl_prop_file != ''
        # assert csv_signal_file != ''
        # assert stl_param_file != ''

        Oracle.__init__(self)

        self.stl_prop_file = stl_prop_file.strip(' \n\t')
        self.csv_signal_file = csv_signal_file.strip(' \n\t')

        stl_param_file_trim = stl_param_file.strip(' \n\t')
        self.stl_parameters = OracleSTLe.get_parameters_stl(stl_param_file_trim)

    def __repr__(self):
        # type: (OracleSTLe) -> str
        """
        Printer.
        """
        return self._to_str()

    def __str__(self):
        # type: (OracleSTLe) -> str
        """
        Printer.
        """
        return self._to_str()

    def _to_str(self):
        # type: (OracleSTLe) -> str
        s = 'STL property file: {0}\n'.format(self.stl_prop_file)
        s += 'STL parameters file: {0}\n'.format(self.stl_parameters)
        s += 'CSV signal file: {0}\n'.format(self.csv_signal_file)
        return s

    def __eq__(self, other):
        # type: (OracleSTLe, OracleSTLe) -> bool
        """
        self == other
        """
        # return hash(self) == hash(other)
        res = False
        try:
            res = (self.stl_prop_file == other.stl_prop_file) \
                  or filecmp.cmp(self.stl_prop_file, other.stl_prop_file)
            res = res or ((self.csv_signal_file == other.csv_signal_file)
                          or filecmp.cmp(self.csv_signal_file, other.vcd_signal_file))
            res = res or (self.stl_parameters == other.stl_parameters)
        except OSError:
            RootOracle.logger.error(
                'Unexpected error when comparing: {0}\n{1}\n{2}'.format(sys.exc_info()[0], str(self), str(other)))
        return res

    def __ne__(self, other):
        # type: (OracleSTLe, OracleSTLe) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    def __hash__(self):
        # type: (OracleSTLe) -> int
        """
        Identity function (via hashing).
        """
        return hash((self.stl_prop_file, self.csv_signal_file, self.stl_parameters))

    def dim(self):
        # type: (OracleSTLe) -> int
        """
        See Oracle.dim().
        """
        return len(self.stl_parameters)

    def get_var_names(self):
        # type: (OracleSTLe) -> list
        """
        See Oracle.get_var_names().
        """
        return [str(i) for i in self.stl_parameters]

    @staticmethod
    def get_parameters_stl(stl_param_file):
        # type: (str) -> list
        res = []

        # Each line of the stl_param_file contains the name of a parameter in the STL formula
        try:
            f = open(stl_param_file, 'rb')
            res = [line.replace(' ', '') for line in f]
            f.close()
        except IOError:
            RootOracle.logger.warning('Parameter STL file does not appear to exist.')
        finally:
            return res

    def replace_par_val_stl_formula(self, xpoint):
        # type: (OracleSTLe, tuple) -> str
        # The number of parameters in the STL formula should be less or equal than
        # the number of coordinates in the tuple
        assert self.dim() <= len(xpoint)

        def eval_expr(match):
            # Evaluate the arithmetic expression detected by 'match'
            res = 0
            try:
                res = str(eval(match.group(0)))
            except SyntaxError:
                RootOracle.logger.error('Syntax error: {0}'.format(str(match)))
            finally:
                return res

        ####
        # Regex for detecting an arithmetic expression inside a STL formula
        # number = '([+-]?(\d+(\.\d*)?)|(\.\d+))'
        number = '([+-]?(\d+(\.\d*)?)|(\.\d+))([eE][-+]?\d+)?'
        op = '(\*|\/|\+|\-)+'
        math_regex = r'(\b{0}\b({1}\b{2}\b)*)'.format(number, op, number)
        # math_regex = r'(\b%s\b(%s\b%s\b)*)' % (number, op, number)
        # math_regex = r'(?P<expr>\b%s\b(%s\b%s\b)*)' % (number, op, number)
        pattern = re.compile(math_regex)
        ####

        f = open(self.stl_prop_file, 'r')
        stl_prop_file_subst = tempfile.NamedTemporaryFile(mode='w', delete=False)
        stl_prop_file_subst_name = stl_prop_file_subst.name

        for line in f:
            for i, par in enumerate(self.stl_parameters):
                line = re.sub(r'\b{0}\b'.format(par), str(xpoint[i]), line)

            line = pattern.sub(eval_expr, line)
            stl_prop_file_subst.write(line)

        f.close()
        stl_prop_file_subst.close()

        return stl_prop_file_subst_name

    def eval_stl_formula(self, stl_prop_file):
        # type: (OracleSTLe, str) -> bool

        result = "0"
        try:
            # Invoke example of the monitoring tool (STLe).
            # STLe evaluates a STL formula (.stl) over a signal (.csv)
            # returns the result by the standard output (stdout).
            #
            # command means: "Given the signal in csv format,
            # evaluate the formula stl_prop_file at time 0"
            # command = ['STLe', csv_signal_file, '-db', '1', '-ff', stl_prop_file, '-os', '0']
            command = [STLE_BIN, self.csv_signal_file,
                       STLE_OPT_CSV, STLE_OPT_IN_MEM_CSV,
                       STLE_OPT_IN_FILE_STL, stl_prop_file,
                       STLE_OPT_TIMESTAMP, STLE_OPT_TIME]

            DEVNULL = open(os.path.devnull, 'w')
            RootOracle.logger.debug('Command: {0}'.format(command))
            # subprocess.call(command)
            result = subprocess.check_output(command, stderr=DEVNULL, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            message = 'Running "{0}" raised an exception'.format(' '.join(e.cmd))
            raise RuntimeError(message)
        finally:
            # Return the result of evaluating the STL formula.
            return OracleSTLe.parse_stle_result(result)

    @staticmethod
    def parse_stle_result(result):
        # type: (str) -> bool
        #
        # STLe may return:
        # - a boolean value (i.e, "0" for False and "1" for True),
        # - a boolean signal,
        # - a real value (i.e., min/max of a real value signal).
        # We assume that the output is a boolean value.
        RootOracle.logger.debug('Result: {0}'.format(result))
        return int(result) == 1

    # Membership functions
    def __contains__(self, p):
        # type: (OracleSTLe, tuple) -> bool
        return self.member(p) is True

    def member(self, xpoint):
        # type: (OracleSTLe, tuple) -> bool
        """
        See Oracle.member().
        """
        assert self.stl_prop_file != ''
        assert self.csv_signal_file != ''
        assert self.stl_parameters != []

        # Replace parameters of the STL formula with current values in xpoint tuple
        stl_prop_file_subst_name = self.replace_par_val_stl_formula(xpoint)

        # Invoke STLe for solving the STL formula for the current values for the parameters
        result = False
        try:
            result = self.eval_stl_formula(stl_prop_file_subst_name)
            with open(stl_prop_file_subst_name, 'r') as fin:
                RootOracle.logger.debug(
                    'Result of evaluating file {0}: {1}\n{2}.'.format(stl_prop_file_subst_name, result, fin.read()))
            # Remove temporal files
            os.remove(stl_prop_file_subst_name)
        except RuntimeError:
            RootOracle.logger.warning('Error when evaluating formula in file {0}.'.format(stl_prop_file_subst_name))
        finally:
            return result

    def membership(self):
        # type: (OracleSTLe) -> callable
        """
        See Oracle.membership().
        """
        return lambda xpoint: self.member(xpoint)

    # Read/Write file functions
    def from_file_binary(self, finput=None):
        # type: (OracleSTLe, io.BinaryIO) -> None
        """
        See Oracle.from_file_binary().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = pickle.load(finput)
            self.stl_prop_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            path = pickle.load(finput)
            self.csv_signal_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            self.stl_parameters = pickle.load(finput)

            fname_list = (self.stl_prop_file, self.csv_signal_file)
            for fname in fname_list:
                if not os.path.isfile(fname):
                    RootOracle.logger.info('File {0} does not exists or it is not a file'.format(fname))

        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def from_file_text(self, finput=None):
        # type: (OracleSTLe, io.BinaryIO) -> None
        """
        See Oracle.from_file_text().
        """
        assert (finput is not None), 'File object should not be null'

        try:
            # Each file line contains the path to a configuration file required by STLe.
            # If it is a relative path, we calculate the absolute path.
            # If it is a absolute path, we do nothing.

            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = finput.readline().strip(' \n\t')
            self.stl_prop_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            path = finput.readline().strip(' \n\t')
            self.csv_signal_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            self.stl_parameters = ast.literal_eval(finput.readline().strip(' \n\t'))

            fname_list = (self.stl_prop_file, self.csv_signal_file)
            for fname in fname_list:
                if not os.path.isfile(fname):
                    RootOracle.logger.info('File {0} does not exists or it is not a file'.format(fname))

        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def to_file_binary(self, foutput=None):
        # type: (OracleSTLe, io.BinaryIO) -> None
        """
        See Oracle.to_file_binary().
        """
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(os.path.abspath(self.csv_signal_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(os.path.abspath(self.stl_prop_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.stl_parameters, foutput, pickle.HIGHEST_PROTOCOL)

    def to_file_text(self, foutput=None):
        # type: (OracleSTLe, io.BinaryIO) -> None
        """
        See Oracle.to_file_text().
        """
        assert (foutput is not None), 'File object should not be null'

        foutput.write(os.path.abspath(self.csv_signal_file) + '\n')
        foutput.write(os.path.abspath(self.stl_prop_file) + '\n')
        foutput.write(str(self.stl_parameters) + '\n')
