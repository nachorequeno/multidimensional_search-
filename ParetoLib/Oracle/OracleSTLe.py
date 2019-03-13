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
import io
import sys
import os
import filecmp
from ctypes import c_double

import ParetoLib.Oracle as RootOracle
from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.STLe.STLe import STLeLibInterface, STLE_BIN, STLE_INTERACTIVE, STLE_READ_SIGNAL, STLE_EVAL, STLE_RESET, STLE_OK, MAX_STLE_CALLS


class OracleSTLe(Oracle):
    # OracleSTLe interacts with the binary executable STLe via PIPEs and string passing.
    def __init__(self, stl_prop_file='', csv_signal_file='', stl_param_file=''):
        # type: (OracleSTLe, str, str, str) -> None
        Oracle.__init__(self)

        # Load STLe formula
        self.stl_prop_file = stl_prop_file.strip(' \n\t')
        self.stl_formula = None

        # Load parameters of the STLe formula
        self.stl_param_file = stl_param_file.strip(' \n\t')
        self.stl_parameters = None

        # Load the signal
        self.csv_signal_file = csv_signal_file.strip(' \n\t')

        # Load the pattern for evaluating arithmetic expressions in STLe
        self.pattern = OracleSTLe._regex_arithm_expr_stl_eval()

        # Number of calls to the STLe oracle
        self.num_oracle_calls = 0

        # STLe oracle
        self.stle_oracle = None

        # Flag for indicating that Oracle is not initialized yet
        self.initialized = False

    def _lazy_init(self):
        # type: (OracleSTLe) -> None
        # Lazy initialization of the OracleSTLe

        assert self.stl_prop_file != ''
        assert self.stl_param_file != ''
        assert self.csv_signal_file != ''

        RootOracle.logger.info('Initializing OracleSTLe')

        self.stl_formula = OracleSTLe.load_stl_formula(self.stl_prop_file)
        self.stl_parameters = OracleSTLe.get_parameters_stl(self.stl_param_file)

        # Start STLe oracle in interactive mode (i.e., more efficient)
        args = [STLE_BIN, STLE_INTERACTIVE]
        RootOracle.logger.debug('Starting: {0}'.format(args))
        self.stle_oracle = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, bufsize=0)

        # Loading the signal in memory
        self._load_signal_in_mem()

        # Marking the Oracle as initialized
        self.initialized = True

    def _load_signal_in_mem(self):
        # type: (OracleSTLe) -> None
        # Load the signal in memory
        # (read-signal-csv "file_name")
        expression = '({0} "{1}")'.format(STLE_READ_SIGNAL, self.csv_signal_file)
        RootOracle.logger.debug('Running: {0}'.format(expression))
        self.stle_oracle.stdin.write(expression)
        self.stle_oracle.stdin.flush()
        #
        ok = self.stle_oracle.stdout.readline()
        ok = ok.strip(' \n\t')
        #
        RootOracle.logger.debug('ok: {0}'.format(ok))
        if ok != STLE_OK:
            message = 'Unexpected error when loading {0}: {1}'.format(self.csv_signal_file, ok)
            RootOracle.logger.error(message)
            raise RuntimeError(message)

    def _clean_cache(self):
        # type: (OracleSTLe) -> None
        assert self.stle_oracle is not None
        assert not self.stle_oracle.stdin.closed
        assert not self.stle_oracle.stdout.closed

        # Cleaning cache
        # (clear-monitor)
        expression = '({0})'.format(STLE_RESET)
        RootOracle.logger.debug('Running: {0}'.format(expression))
        self.stle_oracle.stdin.write(expression)
        self.stle_oracle.stdin.flush()
        res2 = self.stle_oracle.stdout.readline()
        RootOracle.logger.debug('result: {0}'.format(res2))

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
        s += 'STL parameters file: {0}\n'.format(self.stl_param_file)
        # s += 'STL parameters: {0}\n'.format(self.stl_parameters)
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
                          or filecmp.cmp(self.csv_signal_file, other.csv_signal_file))
            res = res or ((self.stl_param_file == other.stl_param_file)
                          or (self.stl_parameters == other.stl_parameters))
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
        return hash((self.stl_prop_file, self.csv_signal_file, self.stl_param_file))

    def __del__(self):
        # type: (OracleSTLe) -> None
        if self.initialized and self.stle_oracle is not None:
            self.stle_oracle.terminate()

    def __copy__(self):
        # type: (OracleSTLe) -> OracleSTLe
        return OracleSTLe(stl_prop_file=self.stl_prop_file, csv_signal_file=self.csv_signal_file, stl_param_file=self.stl_param_file)

    def __deepcopy__(self, memo):
        # type: (OracleSTLe, dict) -> OracleSTLe
        # deepcopy function is required for creating multiple instances of the Oracle in ParSearch.
        # deepcopy cannot handle regex
        return OracleSTLe(stl_prop_file=self.stl_prop_file, csv_signal_file=self.csv_signal_file, stl_param_file=self.stl_param_file)

    def __getattr__(self, name):
        # type: (OracleSTLe, str) -> _
        elem = object.__getattribute__(self, name)
        if elem is None:
            RootOracle.logger.debug('Initializating OracleSTLe')
            self._lazy_init()
            elem = object.__getattribute__(self, name)
            RootOracle.logger.debug('Initialized Oracle')
        RootOracle.logger.debug('__getattr__: {0}, {1}'.format(name, elem))
        # s = input()
        return elem

    def __getattribute__(self, name):
        # type: (OracleSTLe, str) -> _
        elem = object.__getattribute__(self, name)
        RootOracle.logger.debug('__getattribute__: {0}'.format(name))
        if elem is None:
            raise AttributeError
        return elem

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
            # res = [line.replace(' ', '') for line in f]
            res = [line.strip(' \n\t') for line in f]
            f.close()
        except IOError:
            RootOracle.logger.warning('Parameter STL file does not appear to exist.')
        finally:
            return res

    @staticmethod
    def load_stl_formula(stl_file):
        # type: (str) -> str
        formula = ''
        try:
            f = open(stl_file, 'r')
            formula = f.read()
            f.close()

        except IOError:
            RootOracle.logger.warning('STL file does not appear to exist.')
        finally:
            return formula

    @staticmethod
    def _regex_arithm_expr_stl_eval():
        # type: () -> re.Pattern
        # Regex for detecting an arithmetic expression inside a STL formula
        number = '([+-]?(\d+(\.\d*)?)|(\.\d+))([eE][-+]?\d+)?'
        op = '(\*|\/|\+|\-)+'
        math_regex = r'(\b{0}\b({1}\b{2}\b)*)'.format(number, op, number)
        return re.compile(math_regex)

    def replace_val_stl_formula(self, xpoint):
        # type: (OracleSTLe, tuple) -> str
        # The number of parameters in the STL formula should be less or equal than
        # the number of coordinates in the tuple
        assert self.dim() <= len(xpoint)
        assert self.stl_formula != ''
        assert self.stl_parameters != []

        def eval_expr(match):
            # type: (re.SRE_Pattern) -> str
            # Evaluate the arithmetic expression detected by 'match'
            result = '0'
            #'{:.15f}'
            # float_format = '{:.' + str(ParetoLib.Geometry.__numdigits__) + 'f}'
            try:
                result = str(eval(match.group(0)))
                # result = float_format.format(eval(match.group(0)))
            except SyntaxError:
                RootOracle.logger.error('Syntax error: {0}'.format(str(match)))
            finally:
                return result

        RootOracle.logger.debug('Evaluating STL formula')
        val_formula = self.stl_formula
        for i, par in enumerate(self.stl_parameters):
            val_formula = re.sub(r'\b{0}\b'.format(par), str(xpoint[i]), val_formula)
        val_formula = self.pattern.sub(eval_expr, val_formula)

        return val_formula

    def eval_stl_formula(self, stl_formula):
        # type: (OracleSTLe, str) -> bool
        assert self.stle_oracle is not None
        assert not self.stle_oracle.stdin.closed
        assert not self.stle_oracle.stdout.closed

        res1 = '0'
        # Evaluating formula
        # (eval formula)
        expression = '({0} {1})'.format(STLE_EVAL, stl_formula)
        RootOracle.logger.debug('Running: {0}'.format(expression))
        self.stle_oracle.stdin.write(expression)
        self.stle_oracle.stdin.flush()
        res1 = self.stle_oracle.stdout.readline()
        RootOracle.logger.debug('result: {0}'.format(res1))

        # Return the result of evaluating the STL formula.
        return OracleSTLe.parse_stle_result(res1)

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

        RootOracle.logger.debug('Running membership function')
        # Cleaning the cache of STLe after MAX_ORACLE_CALLS (i.e., 'gargage collector')
        if self.num_oracle_calls > MAX_STLE_CALLS:
            self.num_oracle_calls = 0
            self._clean_cache()

        # Replace parameters of the STL formula with current values in xpoint tuple
        val_stl_formula = self.replace_val_stl_formula(xpoint)

        # Invoke STLe for solving the STL formula for the current values for the parameters
        result = False
        try:
            self.num_oracle_calls = self.num_oracle_calls + 1
            result = self.eval_stl_formula(val_stl_formula)
        except RuntimeError:
            RootOracle.logger.warning('Error when evaluating formula {0}.'.format(val_stl_formula))
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
            stl_prop_file = os.path.join(current_path, path) if not os.path.isabs(path) else path

            path = pickle.load(finput)
            csv_signal_file = os.path.join(current_path, path) if not os.path.isabs(path) else path

            path = pickle.load(finput)
            stl_param_file = os.path.join(current_path, path) if not os.path.isabs(path) else path

            fname_list = (stl_prop_file, csv_signal_file, stl_param_file)
            for fname in fname_list:
                if not os.path.isfile(fname):
                    RootOracle.logger.info('File {0} does not exists or it is not a file'.format(fname))

            self.__init__(stl_prop_file=stl_prop_file, stl_param_file=stl_param_file, csv_signal_file=csv_signal_file)

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
            #
            # os.path.join creates absolute path from relative path "./something.txt"
            # os.path.realpath uniforms path "2D/./signal.csv" by "2D/signal.csv"
            #
            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = finput.readline().strip(' \n\t')
            stl_prop_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            stl_prop_file = os.path.realpath(stl_prop_file)

            path = finput.readline().strip(' \n\t')
            csv_signal_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            csv_signal_file = os.path.realpath(csv_signal_file)

            path = finput.readline().strip(' \n\t')
            stl_param_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            stl_param_file = os.path.realpath(stl_param_file)

            fname_list = (stl_prop_file, csv_signal_file, stl_param_file)
            for fname in fname_list:
                if not os.path.isfile(fname):
                    RootOracle.logger.info('File {0} does not exists or it is not a file'.format(fname))

            self.__init__(stl_prop_file=stl_prop_file, stl_param_file=stl_param_file, csv_signal_file=csv_signal_file)

        except EOFError:
            RootOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def to_file_binary(self, foutput=None):
        # type: (OracleSTLe, io.BinaryIO) -> None
        """
        See Oracle.to_file_binary().
        """
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(os.path.abspath(self.stl_prop_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(os.path.abspath(self.csv_signal_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(os.path.abspath(self.stl_param_file), foutput, pickle.HIGHEST_PROTOCOL)

    def to_file_text(self, foutput=None):
        # type: (OracleSTLe, io.BinaryIO) -> None
        """
        See Oracle.to_file_text().
        """
        assert (foutput is not None), 'File object should not be null'

        foutput.write(os.path.abspath(self.stl_prop_file) + '\n')
        foutput.write(os.path.abspath(self.csv_signal_file) + '\n')
        foutput.write(os.path.abspath(self.stl_param_file) + '\n')


class OracleSTLeLib(OracleSTLe):
    # OracleSTLeLib interacts directly with the C library of STLe via the C API that STLe exports.
    def __init__(self, stl_prop_file='', csv_signal_file='', stl_param_file=''):
        # type: (OracleSTLeLib, str, str, str) -> None
        Oracle.__init__(self)

        # Load STLe formula
        self.stl_prop_file = stl_prop_file.strip(' \n\t')
        self.stl_formula = None

        # Load parameters of the STLe formula
        self.stl_param_file = stl_param_file.strip(' \n\t')
        self.stl_parameters = None

        # Load the signal
        self.csv_signal_file = csv_signal_file.strip(' \n\t')

        # Load the pattern for evaluating arithmetic expressions in STLe
        self.pattern = OracleSTLe._regex_arithm_expr_stl_eval()

        # Number of calls to the STLe oracle
        self.num_oracle_calls = 0

        # Load interface with STLeLib (C)
        # STLeLibInterface()
        self.stle = None

        # signalvars are the parameters of STLe formula in C API format
        self.signalvars = None
        self.signal = None

        # exprset is a set of STLe formulas in C API format
        self.exprset = None
        self.monitor = None

        # Flag for indicating that Oracle is not initialized yet
        self.initialized = False

    def _lazy_init(self):
        # type: (OracleSTLe) -> None
        # Lazy initialization of the OracleSTLe

        assert self.stl_prop_file != ''
        assert self.stl_param_file != ''
        assert self.csv_signal_file != ''

        RootOracle.logger.info('Initializing OracleSTLeLib')

        self.stl_formula = OracleSTLe.load_stl_formula(self.stl_prop_file)
        self.stl_parameters = OracleSTLe.get_parameters_stl(self.stl_param_file)
        self.stle = STLeLibInterface()

        RootOracle.logger.debug('Starting: {0}'.format(self.csv_signal_file))

        # Loading the signal in memory
        self._load_signal_in_mem()

        # Creating signal monitor and expression set
        self._create_monitor_exprset()

        # Marking the Oracle as initialized
        self.initialized = True

    def _load_signal_in_mem(self):
        # type: (OracleSTLeLib) -> None
        assert self.stle is not None
        
        # Load the signal in memory
        RootOracle.logger.debug('Loading signal "{0}" into memory'.format(self.csv_signal_file))
        self.signal = self.stle.stl_read_pcsignal_csv_fname(self.csv_signal_file)

        if self.signal is None:
            message = 'Unexpected error when loading {0}'.format(self.csv_signal_file)
            RootOracle.logger.error(message)
            raise RuntimeError(message)

        n = self.stle.stl_pcsignal_size(self.signal)
        # self.signalvars = stl_make_signalvars_xn(c_int(n))
        self.signalvars = self.stle.stl_make_signalvars_xn(n)
        RootOracle.logger.debug('Signalvars created: {0}'.format(self.signalvars))

    def _clean_cache(self):
        # type: (OracleSTLeLib) -> None
        assert self.stle is not None
        assert self.signalvars is not None
        
        # Remove signal monitor and expression set
        self._remove_monitor_exprset()

        # Create a new signal monitor and expression set
        self._create_monitor_exprset()

    def _remove_monitor_exprset(self):
        # type: (OracleSTLeLib) -> None
        assert self.stle is not None
        assert self.signalvars is not None

        RootOracle.logger.debug('Cleaning cache of exprsets')

        # Remove exprset
        if self.exprset is not None:
            self.stle.stl_delete_exprset(self.exprset)

        # Remove monitor
        if self.monitor is not None:
            self.stle.stl_delete_offlinepcmonitor(self.monitor)

    def _create_monitor_exprset(self):
        # type: (OracleSTLeLib) -> None
        assert self.stle is not None
        assert self.signalvars is not None

        # Create a new exprset
        self.exprset = self.stle.stl_make_exprset()
        RootOracle.logger.debug('Exprset created: {0}'.format(self.exprset))

        # Create a monitor for analyzing the signal
        self.monitor = self.stle.stl_make_offlinepcmonitor(self.signal, self.signalvars, self.exprset)
        RootOracle.logger.debug('Monitor created: {0}'.format(self.monitor))

    def _to_str(self):
        # type: (OracleSTLe) -> str
        s = 'STL property file: {0}\n'.format(self.stl_prop_file)
        s += 'STL parameters file: {0}\n'.format(self.stl_param_file)
        # s += 'STL parameters: {0}\n'.format(self.stl_parameters)
        s += 'CSV signal file: {0}\n'.format(self.csv_signal_file)
        return s

    def __copy__(self):
        # type: (OracleSTLeLib) -> OracleSTLeLib
        return OracleSTLeLib(stl_prop_file=self.stl_prop_file, csv_signal_file=self.csv_signal_file,
                             stl_param_file=self.stl_param_file)

    def __deepcopy__(self, memo):
        # type: (OracleSTLeLib) -> OracleSTLeLib
        # deepcopy function is required for creating multiple instances of the Oracle in ParSearch.
        # deepcopy cannot handle regex
        return OracleSTLeLib(stl_prop_file=self.stl_prop_file, csv_signal_file=self.csv_signal_file,
                             stl_param_file=self.stl_param_file)

    def __getattr__(self, name):
        # type: (OracleSTLeLib, str) -> _
        return super(OracleSTLeLib, self).__getattr__(name)

    def __getattribute__(self, name):
        # type: (OracleSTLeLib, str) -> _
        return super(OracleSTLeLib, self).__getattribute__(name)

    def __del__(self):
        # type: (OracleSTLeLib) -> None

        if self.initialized and self.stle is not None:
            if self.signal is not None:
                self.stle.stl_delete_pcsignal(self.signal)
            if self.signalvars is not None:
                self.stle.stl_delete_signalvars(self.signalvars)
            if self.exprset is not None:
                self.stle.stl_delete_exprset(self.exprset)
            if self.monitor is not None:
                self.stle.stl_delete_offlinepcmonitor(self.monitor)

    @staticmethod
    def parse_stle_result(result):
        # type: (c_double) -> bool
        #
        # STLe may return:
        # - a boolean value (i.e, "0" for False and "1" for True),
        # - a boolean signal,
        # - a real value (i.e., min/max of a real value signal).
        # We assume that the output is a boolean value.
        RootOracle.logger.debug('Result: {0}'.format(result))
        return int(result) == 1

    def eval_stl_formula(self, stl_formula):
        # type: (OracleSTLeLib, str) -> bool
        assert self.stle is not None
        assert self.monitor is not None
        assert self.signal is not None
        assert self.signalvars is not None
        assert self.exprset is not None

        RootOracle.logger.debug('Evaluating: {0}'.format(stl_formula))

        # Add STLe formula to the expression set
        expr = self.stle.stl_parse_sexpr_str(self.exprset, stl_formula)

        RootOracle.logger.debug('STLe formula parsed: {0}'.format(expr))

        # Evaluating formula
        stl_series = self.stle.stl_offlinepcmonitor_make_output(self.monitor, expr)
        RootOracle.logger.debug('STLe series: {0}'.format(stl_series))

        res = self.stle.stl_pcseries_value0(stl_series)
        RootOracle.logger.debug('Result: {0}'.format(res))

        # Remove STLe formula from the expression set
        self.stle.stl_unref_expr(expr)

        # Return the result of evaluating the STL formula.
        return OracleSTLeLib.parse_stle_result(res)

