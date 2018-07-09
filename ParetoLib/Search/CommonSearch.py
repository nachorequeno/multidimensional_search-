import time

from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *

# from ParetoLib.Search import vprint
from . import vprint

# STEPS = 100
# EPS = sys.float_info.epsilon
# DELTA = sys.float_info.epsilon

EPS = 1e-5
DELTA = 1e-5
STEPS = float('inf')


# Auxiliar functions used in 2D, 3D and ND
# Creation of Spaces
def create_2D_space(minx, miny, maxx, maxy):
    vprint('Creating Space')
    start = time.time()
    minc = (minx, miny)
    maxc = (maxx, maxy)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    vprint('Time creating Space: ', str(time0))
    return xyspace


def create_3D_space(minx, miny, minz, maxx, maxy, maxz):
    vprint('Creating Space')
    start = time.time()
    minc = (minx, miny, minz)
    maxc = (maxx, maxy, maxz)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    vprint('Time creating Space: ', str(time0))
    return xyspace


def create_ND_space(*args):
    # args = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
    vprint('Creating Space')
    start = time.time()
    minc = tuple(minx for minx, _ in args)
    maxc = tuple(maxx for _, maxx in args)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    vprint('Time creating Space: ', str(time0))
    return xyspace


def load_OracleFunction(nfile,
                        human_readable=True):
    # type: (str, bool) -> OracleFunction
    vprint('Creating OracleFunction')
    start = time.time()
    ora = OracleFunction()
    ora.from_file(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    vprint('Time reading OracleFunction: ', str(time0))
    return ora


def load_OraclePoint(nfile,
                     human_readable=True):
    # type: (str, bool) -> OraclePoint
    vprint('Creating OraclePoint')
    start = time.time()
    ora = OraclePoint()
    ora.from_file(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    vprint('Time reading OraclePoint: ', str(time0))
    return ora


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
