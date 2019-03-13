# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""STLe package.

This module introduces a set of environment variables and functions
for initializing the STLe tool, a tool for monitoring signals and
evaluating properties written in Signal Temporal Logic (STL) over them.

Usage:
stle ([OPTIONS] SIGNAL_FILE)+
stle cmd [OPTIONS]
Options:
-f FORMULA      Evaluate the FORMULA.
-ff FILE        Read a formula from the file.
-isf FORMAT     Specifies how to translate samples in the following csv files to a sequence of intervals.
        FORMAT is a string of characters:
        f       Default. Sample time is in the first column.
        l       Sample time is in the last column.
        s       Default. A sample denotes start time of an interval. First sample should have time 0.
        e       A sample denotes end time of an interval.
        o       Default. Intervals except the last are right-open.
        c       Intervals are right-closed.
        Format 'eo' is special: the sample at time 0 (if it exists) and the last sample are inclusive.
        Different formats can be specified for different files, e.g., '-isf feo file1 -isf lso file2'.
-os 0|1 Default 0. Print whole output signal instead of only value at time 0 (this may print a lot).
-osf FORMAT     Print singnals in specified format.
        FORMAT can be:
        c       Default. Csv format that can be read with '-rf feo'.
        g       Format for visualizing with Gnuplot.
        d       Human-readable format for debugging.
-osn TITLE      Title of the output signal (Gnuplot format only).
-pf     Print formula to stderr.
-pi     Print input signal to stderr in debug format (this may print a lot).
-pc     Print performance counters to stderr.
-pm     Print some extra messages for readability.
-de 0|1 Default 1. Evaluate the formula.
-db 0|1 Default 0. Read whole signal file into memory before (speeds up reading a bit).
-v      Print vesion and exit.
-h      Print this message.
"""

import os, stat
import platform

from ctypes import CDLL, c_int, c_double, c_char_p, c_void_p, pointer

def get_stle_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_stle_exec_name():
    # Selecting STLe binary file depending on the OS
    ext = ''
    if platform.system() == 'Linux':
        ext = '.bin'
    elif platform.system() == 'Windows':
        ext = '.exe'
    else:
        raise RuntimeError('OS Platform \'{0}\' not compatible for STLe.\n'.format(platform.system()))
    return [fname for fname in os.listdir(os.path.dirname(__file__)) if fname.endswith(ext)][0]


def get_stle_bin():
    stle_path = get_stle_path()
    stle_exec_name = get_stle_exec_name()
    path = os.path.join(stle_path, stle_exec_name)
    # Making binary file executable for owner, group and others
    os.chmod(path, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def get_stle_lib_name():
    # Selecting STLe binary file depending on the OS
    ext = ''
    if platform.system() == 'Linux':
        # ext = '.so'
        ext = '.so.1'
    elif platform.system() == 'Windows':
        ext = '.dll'
    else:
        raise RuntimeError('OS Platform \'{0}\' not compatible for STLe.\n'.format(platform.system()))
    return [fname for fname in os.listdir(os.path.dirname(__file__)) if fname.endswith(ext)][0]


def get_stle_lib():
    stle_path = get_stle_path()
    stle_lib_name = get_stle_lib_name()
    path = os.path.join(stle_path, stle_lib_name)
    # Making binary file executable for owner, group and others
    os.chmod(path, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return path


# -------------------------------------------------------------------------------
# Options of the STLe executable file
####################
# Offline commands #
####################
STLE_BIN = get_stle_bin()
STLE_OPT_CSV = '-db'
STLE_OPT_IN_MEM_CSV = '1'
STLE_OPT_IN_FILE_CSV = '0'
STLE_OPT_IN_MEM_STL = '-f'
STLE_OPT_IN_FILE_STL = '-ff'
STLE_OPT_TIMESTAMP = '-os'
STLE_OPT_TIME = '0'
STLE_OPT_HELP = '-h'

###################
# Online commands #
###################
# (read-signal-csv "file_name")
# (eval formula)
# (clear-monitor)
STLE_INTERACTIVE = 'cmd'
STLE_READ_SIGNAL = 'read-signal-csv'
STLE_EVAL = 'eval'
STLE_RESET = 'clear-monitor'
STLE_OK = 'ok'
MAX_STLE_CALLS = 50

# -------------------------------------------------------------------------------
# API for interacting with STLe via C functions
STLE_LIB = get_stle_lib()


class STLeLibInterface:
    def __init__(self):
        # type: (STLeLibInterface) -> None

        # cdll.LoadLibrary(STLE_LIB)
        self._stle = CDLL(STLE_LIB)

        # List of STLe functions
        self._stl_version = None
        self._stl_read_pcsignal_csv_fname = None
        self._stl_delete_pcsignal = None
        self._stl_make_exprset = None
        self._stl_delete_exprset = None
        self._stl_unref_expr = None
        self._stl_parse_sexpr_str = None
        self._stl_pcsignal_size = None
        self._stl_make_signalvars_xn = None
        self._stl_delete_signalvars = None
        self._stl_make_offlinepcmonitor = None
        self._stl_offlinepcmonitor_make_output = None
        self._stl_delete_offlinepcmonitor = None
        self._stl_pcseries_value0 = None

        # Initialize C interfaze with STLe
        self._initialize_c_interfaze()

    def _initialize_c_interfaze(self):
        # type: (STLeLibInterface) -> None

        # Version of STLe
        # const char *stl_version(void)
        self._stl_version = self._stle.stle_version
        self._stl_version.argtypes = [c_void_p]
        self._stl_version.restype = c_char_p

        # Read a signal from a csv file
        # struct stle_pcsignal *stle_read_pcsignal_csv_fname(const char *fileName, int flags)
        # 'flags': specify the way to interpret signals (i.e., 0 default)
        # Return 0 if it fails to read the file
        self._stl_read_pcsignal_csv_fname = self._stle.stle_read_pcsignal_csv_fname
        self._stl_read_pcsignal_csv_fname.argtypes = [c_char_p, c_int]
        self._stl_read_pcsignal_csv_fname.restype = c_void_p

        # Delete signal
        # void stle_delete_pcsignal(struct stle_pcsignal *signal)
        self._stl_delete_pcsignal = self._stle.stle_delete_pcsignal
        self._stl_delete_pcsignal.argtypes = [c_void_p]
        self._stl_delete_pcsignal.restypes = None

        # Create an expression set (it will contain the formula)
        # struct stle_exprset *stle_make_exprset(void)
        self._stl_make_exprset = self._stle.stle_make_exprset
        self._stl_make_exprset.argtypes = [c_void_p]
        self._stl_make_exprset.restype = c_void_p

        # Delete expression set
        # void stle_delete_exprset(struct stle_exprset *exprset)
        self._stl_delete_exprset = self._stle.stle_delete_exprset
        self._stl_delete_exprset.argtypes = [c_void_p]
        self._stl_delete_exprset.restype = None

        # Delete expression
        # void stle_unref_expr(const struct stle_expr *expr)
        self._stl_unref_expr = self._stle.stle_unref_expr
        self._stl_unref_expr.argtypes = [c_void_p]
        self._stl_unref_expr.restype = None

        # Comparison of expressions (via equality of struct stle_expr_impl *)
        # const struct stle_expr_impl *stle_get_expr_impl(const struct stle_expr *expr)
        self._stl_get_expr_impl = self._stle.stle_get_expr_impl
        self._stl_get_expr_impl.argtypes = [c_void_p]
        self._stl_get_expr_impl.restype = c_void_p

        # Parse a formula from a string
        # const struct stle_expr *stle_parse_sexpr_str(struct stle_exprset *exprset, const char *str, int *pos)
        # 'pos': pointer to an integer that will receive the position of the first character after the formula
        # (i.e. how many character the parser read). Pass 0 if you don't care.
        # Return 0 if it fails to read the file
        self._stl_parse_sexpr_str = self._stle.stle_parse_sexpr_str
        self._stl_parse_sexpr_str.argtypes = [c_void_p, c_char_p, c_void_p]  # c_int
        self._stl_parse_sexpr_str.restype = c_void_p

        # Get the number of parameters (n) of the signal
        # int stle_pcsignal_size(const struct stle_pcsignal *signal)
        self._stl_pcsignal_size = self._stle.stle_pcsignal_size
        self._stl_pcsignal_size.argtypes = [c_void_p]
        self._stl_pcsignal_size.restype = c_int

        # Define the number of parameters (n) of the formula
        # struct stle_signalvars *stle_make_signalvars_xn(int n)
        self._stl_make_signalvars_xn = self._stle.stle_make_signalvars_xn
        self._stl_make_signalvars_xn.argtypes = [c_int]
        self._stl_make_signalvars_xn.restype = c_void_p

        # Delete the mapping between signal and variables
        # void stle_delete_signalvars(struct stle_signalvars *signalvars)
        self._stl_delete_signalvars = self._stle.stle_delete_signalvars
        self._stl_delete_signalvars.argtypes = [c_void_p]
        self._stl_delete_signalvars.restype = None

        # Create a monitor
        # struct stle_offlinepcmonitor *stle_make_offlinepcmonitor(struct stle_pcsignal *signal, const struct stle_signalvars *signalvars, struct stle_exprset *exprset)
        self._stl_make_offlinepcmonitor = self._stle.stle_make_offlinepcmonitor
        self._stl_make_offlinepcmonitor.argtypes = [c_void_p, c_void_p, c_void_p]
        self._stl_make_offlinepcmonitor.restype = c_void_p

        # Running the monitor
        # const struct stle_pcseries *stle_offlinepcmonitor_make_output(struct stle_offlinepcmonitor *monitor, const stle_expr *expr, int rewrite, const stle_expr **rewritten)
        # rewrite = 1
        # rewritten = 0
        self._stl_offlinepcmonitor_make_output = self._stle.stle_offlinepcmonitor_make_output
        self._stl_offlinepcmonitor_make_output.argtypes = [c_void_p, c_void_p, c_int, c_void_p]
        self._stl_offlinepcmonitor_make_output.restype = c_void_p

        # Delete the monitor
        # void stle_delete_offlinepcmonitor(struct stle_offlinepcmonitor *monitor)
        self._stl_delete_offlinepcmonitor = self._stle.stle_delete_offlinepcmonitor
        self._stl_delete_offlinepcmonitor.argtypes = [c_void_p]
        self._stl_delete_offlinepcmonitor.restype = None

        # Get the value of the output at time 0
        # double stle_pcseries_value0(const struct stle_pcseries *series)
        self._stl_pcseries_value0 = self._stle.stle_pcseries_value0
        self._stl_pcseries_value0.argtypes = [c_void_p]
        self._stl_pcseries_value0.restype = c_double

    def __copy__(self):
        # type: (STLeLibInterface) -> STLeLibInterface
        return STLeLibInterface()

    def __deepcopy__(self, memo):
        # type: (STLeLibInterface, dict) -> STLeLibInterface
        # deepcopy function is required for creating multiple instances of the Oracle in ParSearch.
        # deepcopy cannot handle regex
        return STLeLibInterface()

    def stl_version(self):
        # type: (STLeLibInterface) -> c_char_p
        return self._stl_version(None)

    def stl_read_pcsignal_csv_fname(self, csv_signal_file, val=0):
        # type: (STLeLibInterface, str, int) -> c_void_p
        return self._stl_read_pcsignal_csv_fname(c_char_p(csv_signal_file), c_int(val))

    def stl_delete_pcsignal(self, signal):
        # type: (STLeLibInterface, c_void_p) -> None
        return self._stl_delete_pcsignal(signal)

    def stl_make_exprset(self):
        # type: (STLeLibInterface) -> c_void_p
        return self._stl_make_exprset(None)

    def stl_delete_exprset(self, exprset):
        # type: (STLeLibInterface, c_void_p) -> None
        return self._stl_delete_exprset(exprset)

    def stl_unref_expr(self, expr):
        # type: (STLeLibInterface, c_void_p) -> None
        return self._stl_unref_expr(expr)

    def stl_get_expr_impl(self, expr):
        # type: (STLeLibInterface, c_void_p) -> c_void_p
        return self._stl_get_expr_impl(expr)

    def stl_parse_sexpr_str(self, exprset, stl_formula, val=0):
        # type: (STLeLibInterface, c_void_p, str, int) -> c_void_p
        pos = c_int(val)
        # expr = stl_parse_sexpr_str(self.exprset, stl_formula, c_void_p(pos))
        return self._stl_parse_sexpr_str(exprset, c_char_p(stl_formula), pointer(pos))

    def stl_pcsignal_size(self, signal):
        # type: (STLeLibInterface, c_void_p) -> c_int
        return self._stl_pcsignal_size(signal)

    def stl_make_signalvars_xn(self, n):
        # type: (STLeLibInterface, c_int) -> c_void_p
        return self._stl_make_signalvars_xn(n)

    def stl_delete_signalvars(self, delete_signalvars):
        # type: (STLeLibInterface, c_void_p) -> None
        return self._stl_delete_signalvars(delete_signalvars)

    def stl_make_offlinepcmonitor(self, signal, signalvars, exprset):
        # type: (STLeLibInterface, c_void_p, c_void_p, c_void_p) -> c_void_p
        return self._stl_make_offlinepcmonitor(signal, signalvars, exprset)

    def stl_offlinepcmonitor_make_output(self, monitor, expr, val_rewrite=1, val_rewritten=0):
        # type: (STLeLibInterface, c_void_p, c_void_p, int, int) -> c_void_p
        rewrite = c_int(val_rewrite)
        rewritten = c_void_p(val_rewritten)
        return self._stl_offlinepcmonitor_make_output(monitor, expr, rewrite, rewritten)

    def stl_delete_offlinepcmonitor(self, monitor):
        # type: (STLeLibInterface, c_void_p) -> None
        return self._stl_delete_offlinepcmonitor(monitor)

    def stl_pcseries_value0(self, stle_series):
        # type: (STLeLibInterface, c_void_p) -> c_double
        return self._stl_pcseries_value0(stle_series)