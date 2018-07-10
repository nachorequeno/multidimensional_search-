from ParetoLib.Geometry.Point import *
from ParetoLib.Geometry.Segment import *

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
    y = x
    dist = subtract(y.high, y.low)
    i = 0
    # while greater_equal(dist, error):
    # while any(dist_i > error[0] for dist_i in dist):
    while not less(dist, error):
        i += 1
        yval = div(add(y.low, y.high), 2.0)
        # We need a oracle() for guiding the search
        if member(yval):
            y.high = yval
        else:
            y.low = yval
        dist = subtract(y.high, y.low)
    return y, i
