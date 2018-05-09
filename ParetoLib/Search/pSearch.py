import itertools
from multiprocessing import Manager, Pool, cpu_count
import multiprocessing as mp
import copy

from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *
from ParetoLib.Search.ResultSet import *

# from ParetoLib.Search import vprint
from . import vprint

EPS = 1e-5
DELTA = 1e-5
# STEPS = 100
STEPS = float('inf')


# Auxiliar functions used in 2D, 3D and ND
# Creation of Spaces
def _create2DSpace(minx, miny, maxx, maxy):
    vprint('Creating Space')
    start = time.time()
    minc = (minx, miny)
    maxc = (maxx, maxy)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    vprint('Time creating Space: ', str(time0))
    return xyspace


def _create3DSpace(minx, miny, minz, maxx, maxy, maxz):
    vprint('Creating Space')
    start = time.time()
    minc = (minx, miny, minz)
    maxc = (maxx, maxy, maxz)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    vprint('Time creating Space: ', str(time0))
    return xyspace


def _createNDSpace(*args):
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


def binary_search(x,
                  member,
                  error):
    # type: (Segment, _, tuple) -> Segment
    y = x
    dist = subtract(y.h, y.l)
    # while greater_equal(dist, error):
    # while any(dist_i > error[0] for dist_i in dist):
    while not less(dist, error):
        yval = div(add(y.l, y.h), 2.0)
        # We need a oracle() for guiding the search
        if member(yval):
            y.h = yval
        else:
            y.l = yval
        dist = subtract(y.h, y.l)
    return y


def pbin_search_ser(args):
    xrectangle, f, epsilon, n = args
    error = (epsilon,) * n
    return binary_search(xrectangle.diagToSegment(), f, error)


def pbin_search(args):
    xrectangle, ora, epsilon, n = args
    f = ora.membership()
    error = (epsilon,) * n
    return binary_search(xrectangle.diagToSegment(), f, error)

def pbin_search_dict(args):
    xrectangle, dict_man, epsilon, n = args
    ora = dict_man[mp.current_process().name]
    f = ora.membership()
    error = (epsilon,) * n
    return binary_search(xrectangle.diagToSegment(), f, error)


def pb0(args):
    # b0 = Rectangle(xspace.min_corner, y.l)
    xrectangle, y = args
    return Rectangle(xrectangle.min_corner, y.l)


def pb1(args):
    # b1 = Rectangle(y.h, xspace.max_corner)
    xrectangle, y = args
    return Rectangle(y.h, xrectangle.max_corner)


def pborder(args):
    # border = irect(incomparable, yrectangle, xrectangle)
    incomparable, y, xrectangle = args
    yrectangle = Rectangle(y.l, y.h)
    return irect(incomparable, yrectangle, xrectangle)


def pvol(rect):
    return rect.volume()


# Multidimensional search
# The search returns a set of Rectangles in Yup, Ylow and Border
def multidim_search(xspace,
                    oracle,
                    epsilon=EPS,
                    delta=DELTA,
                    max_step=STEPS,
                    blocking=False,
                    sleep=0.0):
    # type: (Rectangle, Oracle, float, float, float, bool, float) -> ResultSet

    vprint('Starting multidimensional search')
    start = time.time()

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Alpha in [0,1]^n
    alphaprime = (range(2),) * n
    alpha = itertools.product(*alphaprime)

    # Particular cases of alpha
    # zero = (0_1,...,0_n)    random.uniform(min_corner, max_corner)
    zero = (0,) * n
    # one = (1_1,...,1_n)
    one = (1,) * n

    # Set of comparable and incomparable rectangles
    comparable = [zero, one]
    incomparable = list(set(alpha) - set(comparable))

    # List of incomparable rectangles
    border = [xspace]

    # Upper and lower clausure
    ylow = []
    yup = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    #oracle_dict = {proc: copy.deepcopy(oracle) for proc in mp.active_children()}
    man = Manager()
    dict_man = man.dict()

    for proc in mp.active_children():
        dict_man[proc.name] = copy.deepcopy(oracle)

    vprint('xspace: ', xspace)
    vprint('vol_border: ', vol_border)
    vprint('delta: ', delta)
    vprint('step: ', step)
    vprint('incomparable: ', incomparable)
    vprint('comparable: ', comparable)

    print('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (step <= max_step):
        # 'f = oracle.membership()' is not thread safe!
        # Create a copy of 'oracle' for each concurrent process
        # args_pbin_search = [(xrectangle, copy.deepcopy(oracle), epsilon, n) for xrectangle in border]
        # y_list = p.map(pbin_search, args_pbin_search)
        args_pbin_search_dict = [(xrectangle, dict_man, epsilon, n) for xrectangle in border]
        y_list = p.map(pbin_search_dict, args_pbin_search_dict)
        # args_pbin_search_ser = ((xrectangle, f, epsilon, n) for xrectangle in border)
        # y_list = map(pbin_search_ser, args_pbin_search)

        b0_list = p.map(pb0, zip(border, y_list))
        b1_list = p.map(pb1, zip(border, y_list))

        ylow.extend(b0_list)
        yup.extend(b1_list)

        vol_b0_list = p.map(pvol, b0_list)
        vol_b1_list = p.map(pvol, b1_list)

        vol_ylow += sum(vol_b0_list)
        vol_yup += sum(vol_b1_list)

        args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(border, y_list))
        border2 = p.map(pborder, args_pborder)
        # Flatten list
        border = list(chain.from_iterable(border2))

        vol_border = vol_total - vol_yup - vol_ylow
        # vprint('Volume report (Step, Ylow, Yup, Border, Total, nYlow, nYup, nBorder): (%s, %s, %s, %s, %s, %d, %d, %d)'
        #      % (step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border)))

        print('%s, %s, %s, %s, %s, %d, %d, %d'
               % (step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border)))

        step = step + len(border)

        if sleep > 0.0:
            rs = ResultSet(list(border), ylow, yup, xspace)
            if n == 2:
                rs.toMatPlot2D(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.toMatPlot3D(blocking=blocking, sec=sleep, opacity=0.7)

    end = time.time()
    time0 = end - start
    vprint('Time multidim search: ', str(time0))

    return ResultSet(border, ylow, yup, xspace)


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


# Dimensional tests
def Search2D(ora,
             min_cornerx=0.0,
             min_cornery=0.0,
             max_cornerx=1.0,
             max_cornery=1.0,
             epsilon=EPS,
             delta=DELTA,
             max_step=STEPS,
             blocking=False,
             sleep=0.0):
    # type: (Oracle, float, float, float, float, float, float, float, bool, float) -> ResultSet
    xyspace = _create2DSpace(min_cornerx, min_cornery, max_cornerx, max_cornery)
    rs = multidim_search(xyspace, ora, epsilon, delta, max_step, blocking, sleep)

    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    n = int((max_cornerx - min_cornerx) / 0.1)
    points = rs.getPointsBorder(n)

    vprint("Points ", points)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True)
    return rs


def Search3D(ora,
             min_cornerx=0.0,
             min_cornery=0.0,
             min_cornerz=0.0,
             max_cornerx=1.0,
             max_cornery=1.0,
             max_cornerz=1.0,
             epsilon=EPS,
             delta=DELTA,
             max_step=STEPS,
             blocking=False,
             sleep=0.0):
    # type: (Oracle, float, float, float, float, float, float, float, bool, float) -> ResultSet
    xyspace = _create3DSpace(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

    rs = multidim_search(xyspace, ora, epsilon, delta, max_step, blocking, sleep)

    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    n = int((max_cornerx - min_cornerx) / 0.1)
    points = rs.getPointsBorder(n)

    vprint("Points ", points)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]

    rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True)
    return rs


def SearchND(ora,
             min_corner=0.0,
             max_corner=1.0,
             epsilon=EPS,
             delta=DELTA,
             max_step=STEPS,
             blocking=False,
             sleep=0.0):
    # type: (Oracle, float, float, float, float, float, bool, float) -> ResultSet
    d = ora.dim()

    minc = (min_corner,) * d
    maxc = (max_corner,) * d
    xyspace = Rectangle(minc, maxc)

    rs = multidim_search(xyspace, ora, epsilon, delta, max_step, blocking, sleep)
    return rs
