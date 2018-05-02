import itertools
import sys

from sortedcontainers import SortedListWithKey

from ParetoLib.Geometry.Rectangle import *
from ResultSet import *

# EPS = 1e-5
EPS = sys.float_info.min
DELTA = 1e-5


def volumeReport(step, vol_ylow, vol_yup, vol_border, vol_total):
    # type: (ResultSet) -> _

    print ('Volume report (Step, Ylow, Yup, Border, Total): (%s, %s, %s, %s, %s)\n'
           % (step, vol_ylow, vol_yup, vol_border, vol_total))


def search(x,
           member,
           error=EPS):
    # type: (Segment, _, float) -> Segment
    y = x
    dist = subtract(y.h, y.l)
    while any([dist_i >= error for dist_i in dist]):
    # while greater_equal(dist, error):
        yval = div(add(y.l, y.h), 2.0)
        # We need a oracle() for guiding the search
        if member(yval):
            y.h = yval
        else:
            y.l = yval
        dist = subtract(y.h, y.l)
    return y

def search_2(x,
           member,
           error):
    # type: (Segment, _, tuple) -> Segment
    y = x
    dist = subtract(y.h, y.l)
    while greater_equal(dist, error):
        yval = div(add(y.l, y.h), 2.0)
        # We need a oracle() for guiding the search
        if member(yval):
            y.h = yval
        else:
            y.l = yval
        dist = subtract(y.h, y.l)
    return y

def search_opt(x,
               member,
               error=EPS):
    # type: (Segment, _, float) -> Segment
    y = x
    n = dim(x)
    # dist = subtract(y.h, y.l)
    dist = (y.h[0] - y.l[0],) * n

    while dist[0] >= error:
        # yval = div(add(y.l, y.h), 2.0)
        yval = ((y.l[0] + y.h[0]) / 2.0,) * n
        # We need a oracle() for guiding the search
        if member(yval):
            y.h = yval
        else:
            y.l = yval
        dist = (y.h[0] - y.l[0],) * n
    return y


# The search returns a set of Rectangles in Yup, Ylow and Border
def multidim_search(xspace,
                    oracle,
                    epsilon=EPS,
                    delta=DELTA,
                    verbose=False,
                    blocking=False,
                    sleep=0):
    # type: (Rectangle, _, float, float, bool, bool, float) -> ResultSet

    if verbose:
        def vprint(*args):
            # Print each argument separately so caller doesn't need to
            # stuff everything to be printed into a single string
            for arg in args:
                print arg,
            print
    else:
        vprint = lambda *a: None  # do-nothing function

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n
    # Dimension
    n = xspace.dim()

    # Alpha in [0,1]^n
    alphaprime = (range(2),) * n
    alpha = set(itertools.product(*alphaprime))

    # Particular cases of alpha
    # zero = (0_1,...,0_n)    random.uniform(min_corner, max_corner)
    zero = (0,) * n
    # one = (1_1,...,1_n)
    one = (1,) * n

    # Set of comparable and incomparable rectangles
    # comparable = set(filter(lambda x: all(x[i]==x[i+1] for i in range(len(x)-1)), alpha))
    # incomparable = list(filter(lambda x: x[0]!=x[1], alpha))
    comparable = [zero, one]
    ############################################ use list instead of set
    incomparable = alpha.difference(comparable)  # Use list and remove sublist

    # Set of incomparable rectangles
    l = SortedListWithKey(key=Rectangle.volume)
    l.add(xspace)

    ylow = []
    yup = []

    # oracle function
    f = oracle
    #
    error = (epsilon,) * n
    #
    #
    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    prev_vol_border = -1
    step = 0
    #
    # print('incomparable: ', incomparable)
    # print('comparable: ', comparable)
    # while (vol_border <= delta) or (vol_border == prev_vol_border):
    while (vol_border <= delta) or (step >= 100):
        step = step + 1
        vprint('step: ', step)
        vprint('l:', l)
        vprint('set_size(l): ', len(l))

        xrectangle = l.pop()

        vprint('xrectangle: ', xrectangle)
        vprint('xrectangle.volume: ', xrectangle.volume())
        vprint('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        # y = search(xrectangle.diagToSegment(), f, epsilon)
        y = search(xrectangle.diagToSegment(), f, error)
        vprint('y: ', y)

        # b0 = Rectangle(xspace.min_corner, y.l)
        b0 = Rectangle(xrectangle.min_corner, y.l)
        ylow = ylow.append(b0)
        vol_ylow += b0.volume()

        vprint('b0: ', b0)
        vprint('ylow: ', ylow)
        vprint('vol_ylow: ', vol_ylow)

        # b1 = Rectangle(y.h, xspace.max_corner)
        b1 = Rectangle(y.h, xrectangle.max_corner)
        yup = yup.append(b1)
        vol_yup += b1.volume()

        vprint('b1: ', b1)
        vprint('yup: ', yup)
        vprint('vol_yup: ', vol_yup)

        yrectangle = Rectangle(y.l, y.h)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        l = l.extend(i)
        vprint('irect: ', i)

        prev_vol_border = vol_border
        vol_border = vol_total - vol_yup - vol_ylow
        vprint('vol_border: ', vol_border)

        volumeReport(step, vol_ylow, vol_yup, vol_border, vol_total)

        if sleep > 0:
            rs = ResultSet(l, ylow, yup, xspace)
            # for i in range(1, n):
            #    rs.toMatPlot2D(blocking=blocking, sec=sleep, yaxe=i, opacity=0.7)
            if n == 2:
                rs.toMatPlot2D(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.toMatPlot3D(blocking=blocking, sec=sleep, opacity=0.7)

    return ResultSet(l, ylow, yup, xspace)
