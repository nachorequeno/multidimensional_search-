# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""
ParetoLib package.
"""
__version__ = "2.0.0"
__name__ = 'ParetoLib'
__all__ = ['Geometry', 'JAMT', 'Oracle', 'Search', 'STLe', '_py3k']


# -------------------------------------------------------------------------------

class MissingExtDependencyError(Exception):
    """
    Missing an external dependency. Used for our unit tests to allow skipping
    tests with missing external dependencies, e.g. missing command line tools.
    """
    pass

# -------------------------------------------------------------------------------
