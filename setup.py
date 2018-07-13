# -------------------------------------------------------------------------------
#
#   ParetoLib  Copyright (C) 2018  J. Ignacio Requeno
#
#   This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
#   This is free software, and you are welcome to redistribute it under certain
#   conditions; type `show c' for details.
#
# -------------------------------------------------------------------------------
# File :  setup.py
# Last version :  v1.0 ( 23/Apr/2018 )
# Description :  Distutils based setup script for ParetoLib.
# -------------------------------------------------------------------------------
# Historical report :
#
#   DATE :  23/Apr/2018
#   VERSION :  v1.0
#   AUTHOR(s) :  J. Ignacio Requeno
#
# -------------------------------------------------------------------------------
# Note :  The content of this file has been created using "setup.py" from
#   Biopython (http://www.biopython.org) as template.
# -------------------------------------------------------------------------------

from __future__ import print_function

import sys
import os
from distutils.core import setup
from distutils.core import Command
from distutils.command.install import install
from distutils.command.build_py import build_py

# -------------------------------------------------------------------------------

_CHECKED = None


# -------------------------------------------------------------------------------

def can_import(module_name):
    """
    Check whether the 'module_name' can be imported or not.
    
    Arguments :
        module_name  ( string )
            Name of the module to be imported.

    Returns :
        bool
            True if 'module_name' can be imported, False otherwise.
    """
    try:
        __import__(module_name)
    except ImportError:
        return (False)
    else:
        return (True)


def check_dependencies():
    """
    Return whether the installation should continue.

    Returns :
        bool
            True if it can continue, False otherwise.
    """
    # Check if NumPy, Sympy, SortedContainers or matplotlib are missing, as they are required for
    # ParetoLib to work properly
    if (not can_import('numpy')):
        print('Numerical Python (NumPy) is not installed.\nThis package is required for' \
              'ParetoLib.\n\nYou can find NumPy at http://www.numpy.org')
        return (False)
    if (not can_import('sympy')):
        print('Symbolic Python (SymPy) is not installed.\nThis package is required for' \
              'ParetoLib.\n\nYou can find SymPy at http://www.sympy.org')
        return (False)
    if (not can_import('sortedcontainers')):
        print('SortedContainers is not installed.\nThis package is required for' \
              'ParetoLib.\n\nYou can find SortedContainers at https://pypi.org/project/sortedcontainers/')
        return (False)
    if (not can_import('matplotlib')):
        print('Matplotlib is not installed.\nThis package is required for' \
              'ParetoLib.\n\nYou can find Matplotlib at https://matplotlib.org/')
        return (False)
    # Exit automatically if running as part of some script
    if (not sys.stdout.isatty()):
        sys.exit(-1)
    return (True)


def check_dependencies_once():
    """
    Call 'check_dependencies', caching the result to avoid subsequent calls.

    Returns :
        bool
            True if all the dependencies have been satisfied, False otherwise.
    """
    global _CHECKED
    if (_CHECKED is None):
        _CHECKED = check_dependencies()
    return (_CHECKED)


class install_paretolib(install):
    """
    Override the standard install to check for dependencies.
    """

    def run(self):
        if (check_dependencies_once()):
            # Run the normal install
            install.run(self)


class build_py_paretolib(build_py):
    """
    Override the standard build to check for dependencies.
    """

    def run(self):
        if (not check_dependencies_once()):
            return
        build_py.run(self)


class test_paretolib(Command):
    """
    Run all of the tests for ParetoLib. This is a automatic test run class to make
    distutils kind of act like perl. With this you can do:

        python setup.py build
        python setup.py install
        python setup.py test

    """
    description = "Automatically run the test suite for ParetoLib."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        this_dir = os.getcwd()
        # Change to the test dir and run the tests
        os.chdir('Tests')
        sys.path.insert(0, '')
        import run_tests
        run_tests.main([])
        # Change back to the current directory
        os.chdir(this_dir)


# -------------------------------------------------------------------------------

# Check that we have the right Python version
if (sys.version_info[:2] < (2, 7)):
    print('ParetoLib requires Python 2.7.9 (or Python 3.4 or later). Python {0}.{1} detected'.format(
        sys.version_info[:2]))
    #          'Python %d.%d detected'.format(sys.version_info[:2]))
    sys.exit(1)
elif ((sys.version_info[0] == 3) and (sys.version_info[:2] < (3, 4))):
    print(
        'ParetoLib requires Python 3.4 or later (or Python 2.7). Python {0}.{1} detected'.format(sys.version_info[:2]))
    #          'Python %d.%d detected' % sys.version_info[:2])
    sys.exit(1)

# We now define the ParetoLib version number in ParetoLib/__init__.py
__version__ = 'unknown'
for line in open('ParetoLib/__init__.py'):
    if (line.startswith('__version__')):
        exec (line.strip())

old_path = os.getcwd()
src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(src_path)
sys.path.insert(0, src_path)

setup_args = {'name': 'ParetoLib',
              'version': '1.0',
              'author': 'J. Ignacio Requeno',
              'author_email': 'jose-ignacio.requeno-jarabo@univ-grenoble-alpes.fr',
              'url': 'https://gricad-gitlab.univ-grenoble-alpes.fr/requenoj/multidimensional_search/',
              'description': 'ParetoLib is a free multidimensional boundary learning library for ' \
                             'tools for Python 2.7.9 and Python 3.4 or newer',
              'download_url': 'https://gricad-gitlab.univ-grenoble-alpes.fr/requenoj/multidimensional_search/repository/master/' \
                              'archive.tar.gz',
              'cmdclass': {'install': install_paretolib,
                           'build_py': build_py_paretolib,
                           'test': test_paretolib, },
              'packages': ['ParetoLib',
                           'ParetoLib.Geometry',
                           'ParetoLib.JAMT',
                           'ParetoLib.Oracle',
                           'ParetoLib.Search',
                           'ParetoLib._py3k'],
              'package_data': {'ParetoLib.JAMT': ['*.jar']},
              }

try:
    setup(**setup_args)
finally:
    del sys.path[0]
    os.chdir(old_path)
