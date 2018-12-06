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


# STLe requires to be compiled for the OS
# -------------------------------------------------------------------------------

def get_stle_exec_name():
    ext = ''
    if platform.system() == 'Linux':
        ext = '.bin'
    elif platform.system() == 'Windows':
        ext = '.exe'
    else:
        raise RuntimeError('OS Platform \'{0}\' not compatible for STLe.\n'.format(platform.system()))
    return [fname for fname in os.listdir(os.path.dirname(__file__)) if fname.endswith(ext)][0]


def get_stle_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_stle_bin():
    stle_path = get_stle_path()
    stle_exec_name = get_stle_exec_name()
    return os.path.join(stle_path, stle_exec_name)


# -------------------------------------------------------------------------------
# STLE OPTIONS
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
