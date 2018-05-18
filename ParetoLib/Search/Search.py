import itertools

from sortedcontainers import SortedListWithKey

from ParetoLib.Search.CommonSearch import *
from ParetoLib.Search.ResultSet import *

# from ParetoLib.Search import vprint
from . import vprint

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
    # border = [xspace]
    border = SortedListWithKey(key=Rectangle.volume)
    border.add(xspace)

    ylow = []
    yup = []

    # oracle function
    f = oracle.membership()

    error = (epsilon,) * n
    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0

    vprint('xspace: ', xspace)
    vprint('vol_border: ', vol_border)
    vprint('delta: ', delta)
    vprint('step: ', step)
    vprint('incomparable: ', incomparable)
    vprint('comparable: ', comparable)

    print('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch')
    while (vol_border >= delta) and (step <= max_step):
        step = step + 1
        vprint('border:', border)
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        vprint('xrectangle: ', xrectangle)
        vprint('xrectangle.volume: ', xrectangle.volume())
        vprint('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        # y = search(xrectangle.diagToSegment(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diagToSegment(), f, error)
        vprint('y: ', y)

        # b0 = Rectangle(xspace.min_corner, y.l)
        b0 = Rectangle(xrectangle.min_corner, y.l)
        ylow.append(b0)
        vol_ylow += b0.volume()

        vprint('b0: ', b0)
        vprint('ylow: ', ylow)

        # b1 = Rectangle(y.h, xspace.max_corner)
        b1 = Rectangle(y.h, xrectangle.max_corner)
        yup.append(b1)
        vol_yup += b1.volume()

        vprint('b1: ', b1)
        vprint('yup: ', yup)

        yrectangle = Rectangle(y.l, y.h)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        border += i
        vprint('irect: ', i)

        vol_border = vol_total - vol_yup - vol_ylow

        # vprint('Volume report (Step, Ylow, Yup, Border, Total, nYlow, nYup, nBorder): (%s, %s, %s, %s, %s, %d, %d, %d)'
        #      % (step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border)))

        print('%s, %s, %s, %s, %s, %d, %d, %d, %d'
              % (step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border), steps_binsearch))
        if sleep > 0.0:
            rs = ResultSet(list(border), ylow, yup, xspace)
            if n == 2:
                rs.toMatPlot2D(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.toMatPlot3D(blocking=blocking, sec=sleep, opacity=0.7)

    end = time.time()
    time0 = end - start
    vprint('Time multidim search: ', str(time0))

    return ResultSet(list(border), ylow, yup, xspace)


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
    xyspace = create2DSpace(min_cornerx, min_cornery, max_cornerx, max_cornery)
    rs = multidim_search(xyspace, ora, epsilon, delta, max_step, blocking, sleep)

    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    n = int((max_cornerx - min_cornerx) / 0.1)
    points = rs.getPointsBorder(n)

    vprint("Points ", points)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    # rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True)
    # rs.toMatPlot2DLight(targetx=xs, targety=ys, blocking=True)
    rs.toMatPlot2DLight(blocking=True)
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
    xyspace = create3DSpace(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

    rs = multidim_search(xyspace, ora, epsilon, delta, max_step, blocking, sleep)

    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    n = int((max_cornerx - min_cornerx) / 0.1)
    points = rs.getPointsBorder(n)

    vprint("Points ", points)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]

    # rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True)
    # rs.toMatPlot3DLight(targetx=xs, targety=ys, targetz=zs, blocking=True)
    rs.toMatPlot3DLight(blocking=True)
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
