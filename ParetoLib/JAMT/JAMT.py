# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""JAMT package.

This module introduces a set of environment variables and functions
for initializing the AMT 2.0 tool, a tool for monitoring signals and
evaluating properties written in Signal Temporal Logic (STL) over them.
"""

import os


# JAMT requires java to be installed
# -------------------------------------------------------------------------------

def get_java_exec_name():
    return 'java'


def get_java_path():
    java_path = ''
    # java_exec_name = get_java_exec_name()
    # if os.system(java_exec_name) != 0:
    if os.system('java -version') != 0:
        java_path = input('Java not included in PATH. Write the absolute path to Java binary: ')
        if not (java_path and os.path.lexists(java_path)):
            raise RuntimeError('Java not available. Please, install it before running JAMT\n\n'
                               'You can find Java at https://www.java.com/')
    return java_path


def get_java_bin():
    java_path = get_java_path()
    java_exec_name = get_java_exec_name()
    return os.path.join(java_path, java_exec_name)


# -------------------------------------------------------------------------------

def get_jamt_exec_name():
    return [fname for fname in os.listdir(os.path.dirname(__file__)) if fname.endswith('.jar')][0]


def get_jamt_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_jamt_bin():
    jamt_path = get_jamt_path()
    jamt_exec_name = get_jamt_exec_name()
    return os.path.join(jamt_path, jamt_exec_name)


# -------------------------------------------------------------------------------

# JAMT OPTIONS
JAVA_BIN = get_java_bin()
JAVA_OPT_JAR = '-jar'

# JAMT OPTIONS
JAMT_BIN = get_jamt_bin()
JAMT_OPT_STL = '-x'
JAMT_OPT_SIGNAL = '-s'
JAMT_OPT_ALIAS = '-a'
JAMT_OPT_RES = '-v'
