import time

from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *

# from ParetoLib.Search import vprint
from . import vprint

EPS = 1e-5
DELTA = 1e-5
# STEPS = 100
STEPS = float('inf')


# Auxiliar functions used in 2D, 3D and ND
# Creation of Spaces
def create2DSpace(minx, miny, maxx, maxy):
    vprint('Creating Space')
    start = time.time()
    minc = (minx, miny)
    maxc = (maxx, maxy)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    vprint('Time creating Space: ', str(time0))
    return xyspace


def create3DSpace(minx, miny, minz, maxx, maxy, maxz):
    vprint('Creating Space')
    start = time.time()
    minc = (minx, miny, minz)
    maxc = (maxx, maxy, maxz)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    vprint('Time creating Space: ', str(time0))
    return xyspace


def createNDSpace(*args):
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

def loadOracleFunction(nfile,
                       human_readable=True):
    # type: (str, bool) -> OracleFunction
    vprint('Creating OracleFunction')
    start = time.time()
    ora = OracleFunction()
    ora.fromFile(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    vprint('Time reading OracleFunction: ', str(time0))
    return ora


def loadOraclePoint(nfile,
                    human_readable=True):
    # type: (str, bool) -> OraclePoint
    vprint('Creating OraclePoint')
    start = time.time()
    ora = OraclePoint()
    ora.fromFile(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    vprint('Time reading OraclePoint: ', str(time0))
    return ora


def binary_search(x,
                  member,
                  error):
    # type: (Segment, _, tuple) -> (Segment, int)
    y = x
    dist = subtract(y.h, y.l)
    i = 0
    # while greater_equal(dist, error):
    # while any(dist_i > error[0] for dist_i in dist):
    while not less(dist, error):
        i += 1
        yval = div(add(y.l, y.h), 2.0)
        # We need a oracle() for guiding the search
        if member(yval):
            y.h = yval
        else:
            y.l = yval
        dist = subtract(y.h, y.l)
    return y, i