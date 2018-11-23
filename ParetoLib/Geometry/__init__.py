# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Geometry package.

This package introduces a set of modules for manipulating Segments,
 Rectangles and Points.

Regarding arithmetic precision, the maximum number of significant
decimal digits is indicated by __numdigits__
"""

import sys
from math import log, floor

__version__ = 1.
__name__ = 'Geometry'
__all__ = ['Segment', 'Rectangle', 'ParRectangle', 'Point', 'PPoint']

# Maximum number of decimal digits that should be used in computations.
# This value depends on the accurary (i.e., number of bits) used for float representations.
__numdigits__ = int(floor(abs(log(sys.float_info.epsilon, 10))))
