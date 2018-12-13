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
requenoj@argentiere:~/Dropbo
"""

import os
import platform
from ctypes import CDLL, c_double, c_int, c_void_p, c_char_p


# STLe requires to be compiled for the OS
# -------------------------------------------------------------------------------
def get_stle_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_stle_exec_name():
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
    return os.path.join(stle_path, stle_exec_name)


def get_stle_lib_name():
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
    return os.path.join(stle_path, stle_lib_name)

# -------------------------------------------------------------------------------
# Options of the STLe executable file
########################
### Offline commands ###
########################
STLE_BIN = get_stle_bin()
STLE_OPT_CSV = '-db'
STLE_OPT_IN_MEM_CSV = '1'
STLE_OPT_IN_FILE_CSV = '0'
STLE_OPT_IN_MEM_STL = '-f'
STLE_OPT_IN_FILE_STL = '-ff'
STLE_OPT_TIMESTAMP = '-os'
STLE_OPT_TIME = '0'
STLE_OPT_HELP = '-h'
#####################
## Online commands ##
#####################
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
# cdll.LoadLibrary(STLE_LIB)
stle = CDLL(STLE_LIB)

# Version of STLe
# const char *stl_version(void)
stl_version = stle.stl_version
stl_version.argtypes = [c_void_p]
stl_version.restype = c_char_p

# Read a signal from a csv file
# struct stl_pcsignal *stl_read_pcsignal_csv_fname(const char *fileName, int flags)
# 'flags': specify the way to interpret signals (i.e., 0 default)
# Return 0 if it fails to read the file
stl_read_pcsignal_csv_fname = stle.stl_read_pcsignal_csv_fname
stl_read_pcsignal_csv_fname.argtypes = [c_char_p, c_int]
stl_read_pcsignal_csv_fname.restype = c_void_p

# Delete signal
# void stl_delete_pcsignal(struct stl_pcsignal *signal)
stl_delete_pcsignal = stle.stl_delete_pcsignal
stl_delete_pcsignal.argtypes = [c_void_p]
stl_delete_pcsignal.restypes = c_void_p

# Create an expression set (it will contain the formula)
# struct stl_exprset *stl_make_exprset(void);
stl_make_exprset = stle.stl_make_exprset
stl_make_exprset.argtypes = [c_void_p]
stl_make_exprset.restype = c_void_p

# Delete expression set
# void stl_delete_exprset(struct stl_exprset *exprset)
stl_delete_exprset = stle.stl_delete_exprset
stl_delete_exprset.argtypes = [c_void_p]

# Parse a formula from a string
# const struct stl_expr *stl_parse_sexpr_str(struct stl_exprset *exprset, const char *str, int *pos)
# 'pos': pointer to an integer that will receive the position of the first character after the formula
# (i.e. how many character the parser read). Pass 0 if you don't care.
# Return 0 if it fails to read the file
stl_parse_sexpr_str = stle.stl_parse_sexpr_str
stl_parse_sexpr_str.argtypes = [c_void_p, c_char_p, c_void_p] # c_int
stl_parse_sexpr_str.restype = c_void_p

# Get the number of parameters (n) of the signal
# int stl_pcsignal_size(const struct stl_pcsignal *signal)
stl_pcsignal_size = stle.stl_pcsignal_size
stl_pcsignal_size.argtypes = [c_void_p]
stl_pcsignal_size.restype = c_int

# Define the number of parameters (n) of the formula
# struct stl_signalvars *stl_make_signalvars_xn(int n)
stl_make_signalvars_xn = stle.stl_make_signalvars_xn
stl_make_signalvars_xn.argtypes = [c_int]
stl_make_signalvars_xn.restype = c_void_p

# Delete the mapping between signal and variables
# void stl_delete_signalvars(struct stl_signalvars *signalvars)
stl_delete_signalvars = stle.stl_delete_signalvars
stl_delete_signalvars.argtypes = [c_void_p]
stl_delete_signalvars.restype = c_void_p

# Create a monitor
# struct stl_offlinepcmonitor *stl_make_offlinepcmonitor(struct stl_pcsignal *signal, const struct stl_signalvars *signalvars, struct stl_exprset *exprset)
stl_make_offlinepcmonitor = stle.stl_make_offlinepcmonitor
stl_make_offlinepcmonitor.argtypes = [c_void_p, c_void_p, c_void_p]
stl_make_offlinepcmonitor.restype = c_void_p

# Running the monitor
# const struct stl_pcseries *stl_offlinepcmonitor_make_output(struct stl_offlinepcmonitor *monitor, const stl_expr *expr, int rewrite, const stl_expr **rewritten)
# rewrite = 1
# rewritten = 0
stl_offlinepcmonitor_make_output = stle.stl_offlinepcmonitor_make_output
stl_offlinepcmonitor_make_output.argtypes = [c_void_p, c_void_p, c_int, c_void_p]
stl_offlinepcmonitor_make_output.restype = c_void_p


# Delete the monitor
# void stl_offlinepcmonitor_delete(struct stl_offlinepcmonitor *monitor)
stl_offlinepcmonitor_delete = stle.stl_offlinepcmonitor_delete
stl_offlinepcmonitor_delete.argtypes = [c_void_p]
stl_offlinepcmonitor_delete.restype = c_void_p

# Get the value of the output at time 0
# double stl_pcseries_value0(const struct stl_pcseries *series)
stl_pcseries_value0 = stle.stl_pcseries_value0
stl_pcseries_value0.argtypes = [c_void_p]
stl_pcseries_value0.restype = c_double
