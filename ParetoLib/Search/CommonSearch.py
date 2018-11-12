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
