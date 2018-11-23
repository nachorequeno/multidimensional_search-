# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""CommontSearch.

This module instantiate the abstract interface Oracle.
The OraclePoint defines the boundary between the upper and lower
closures based on a discrete cloud of points. The cloud of points is
saved in a NDTree [1], a data structure that is optimised for storing
a Pareto front by removing redundant non-dominating points from the
surface. A point x that dominates every member of the Pareto front
belongs to the lower part of the monotone partition, while a point x
that is dominated by any element of the Pareto front will fall in the
upper part.

[1] Andrzej Jaszkiewicz and Thibaut Lust. ND-Tree-based update: a
fast algorithm for the dynamic non-dominance problem. IEEE Trans-
actions on Evolutionary Computation, 2018.
"""

from ParetoLib.Geometry.Point import add, subtract, less_equal, div
from ParetoLib.Geometry.Segment import Segment

# EPS = sys.float_info.epsilon
# DELTA = sys.float_info.epsilon
# STEPS = 100

EPS = 1e-5
DELTA = 1e-5
STEPS = float('inf')

def binary_search(x,
                  member,
                  error):
    # type: (Segment, callable, tuple) -> (Segment, int)
    i = 0
    y = x

    if member(y.low):
        # All the cube belongs to B1
        y.low = x.low
        y.high = x.low
    elif not member(y.high):
        # All the cube belongs to B0
        y.low = x.high
        y.high = x.high
    else:
        # We don't know. We search for a point in the diagonal
        dist = subtract(y.high, y.low)
        # while greater_equal(dist, error):
        # while any(dist_i > error[0] for dist_i in dist):
        while not less_equal(dist, error):
            i += 1
            yval = div(add(y.low, y.high), 2.0)
            # We need a oracle() for guiding the search
            if member(yval):
                y.high = yval
            else:
                y.low = yval
            dist = subtract(y.high, y.low)
    return y, i
