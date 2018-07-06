import itertools

from sortedcontainers import SortedListWithKey, SortedSet

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
                    sleep=0.0,
                    opt_level=2,
                    logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float) -> ResultSet
    md_search = [multidim_search_opt_0,
                 multidim_search_opt_1,
                 multidim_search_opt_2]

    # vprint('Starting multidimensional search')
    start = time.time()
    rs = md_search[opt_level](xspace,
                              oracle,
                              epsilon=epsilon,
                              delta=delta,
                              max_step=max_step,
                              blocking=blocking,
                              sleep=sleep,
                              logging=logging)
    end = time.time()
    time0 = end - start
    # vprint('Time multidim search: ', str(time0))

    return rs


##############################
# opt_2 = Maximum optimisation
# opt_1 = Medium optimisation
# opt_0 = No optimisation
##############################

########################################################################################################################
def multidim_search_opt_2(xspace,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, Oracle, float, float, float, bool, float) -> ResultSet

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
    # border = SortedListWithKey(key=Rectangle.volume)
    border = SortedSet(key=Rectangle.volume)
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

    # vprint('xspace: ', xspace)
    # vprint('vol_border: ', vol_border)
    # vprint('delta: ', delta)
    # vprint('step: ', step)
    # vprint('incomparable: ', incomparable)
    # vprint('comparable: ', comparable)

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    print(
        'Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch, nBorder dominated by Ylow, nBorder dominated by Yup')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        # vprint('border:', border)
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        # vprint('xrectangle: ', xrectangle)
        # vprint('xrectangle.volume: ', xrectangle.volume())
        # vprint('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        # y = search(xrectangle.diagToSegment(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diagToSegment(), f, error)
        # vprint('y: ', y)

        b0 = Rectangle(xrectangle.min_corner, y.l)
        b1 = Rectangle(y.h, xrectangle.max_corner)

        ylow.append(b0)
        yup.append(b1)

        vol_ylow += b0.volume()
        vol_yup += b1.volume()

        # vprint('b0: ', b0)
        # vprint('b1: ', b1)

        # vprint('ylow: ', ylow)
        # vprint('yup: ', yup)

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        # Every Border rectangle that is dominated by B1 is included in Yup
        b0_extended = Rectangle(xspace.min_corner, y.l)
        b1_extended = Rectangle(y.h, xspace.max_corner)

        # border_overlapping_b0 = [rect for rect in border if b0_extended.overlaps(rect)]
        # border_dominatedby_b0 = [b0_extended.intersection(rect) for rect in border_overlapping_b0]
        border_overlapping_b0 = [rect for rect in border if rect.overlaps(b0_extended)]
        border_dominatedby_b0 = [rect.intersection(b0_extended) for rect in border_overlapping_b0]

        # border_nondominatedby_b0 = [rect - b0_extended for rect in border_overlapping_b0]

        border_nondominatedby_b0 = []
        for rect in border_overlapping_b0:
            border_nondominatedby_b0 += list(rect - b0_extended)

        # border_nondominatedby_b0 = set()
        # for rect in border_overlapping_b0:
        #    border_nondominatedby_b0 |= set(rect - b0_extended)
        # border_nondominatedby_b0 -= set(border_overlapping_b0)

        # if 'rect' is completely dominated by b0_extended (i.e., rect is strictly inside b0_extended), then
        # set(rect - b0_extended) == {rect}
        # Therefore, 'rect' must be removed from 'non dominated' borders

        # border -= border_overlapping_b0
        border |= border_nondominatedby_b0
        border -= border_overlapping_b0

        # border_overlapping_b1 = [rect for rect in border if b1_extended.overlaps(rect)]
        # border_dominatedby_b1 = [b1_extended.intersection(rect) for rect in border_overlapping_b1]

        border_overlapping_b1 = [rect for rect in border if rect.overlaps(b1_extended)]
        border_dominatedby_b1 = [rect.intersection(b1_extended) for rect in border_overlapping_b1]

        # border_nondominatedby_b1 = [rect - b1_extended for rect in border_overlapping_b1]

        border_nondominatedby_b1 = []
        for rect in border_overlapping_b1:
            border_nondominatedby_b1 += list(rect - b1_extended)

        # border_nondominatedby_b1 = set()
        # for rect in border_overlapping_b1:
        #    border_nondominatedby_b1 |= set(rect - b1_extended)
        # border_nondominatedby_b1 -= set(border_overlapping_b1)

        # if 'rect' is completely dominated by b1_extended (i.e., rect is strictly inside b1_extended), then
        # set(rect - b1_extended) == {rect}
        # Therefore, 'rect' must be removed from 'non dominated' borders

        # border -= border_overlapping_b1
        border |= border_nondominatedby_b1
        border -= border_overlapping_b1

        ylow.extend(border_dominatedby_b0)
        yup.extend(border_dominatedby_b1)

        vol_ylow += sum(b0.volume() for b0 in border_dominatedby_b0)
        vol_yup += sum(b1.volume() for b1 in border_dominatedby_b1)

        ################################
        # Every rectangle in 'i' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'i' is incomparable for current B1 and for all B1 included in Yup
        ################################

        yrectangle = Rectangle(y.l, y.h)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        border |= i
        # vprint('irect: ', i)

        vol_border = vol_total - vol_yup - vol_ylow

        print('%s, %s, %s, %s, %s, %d, %d, %d, %d, %d, %d'
              % (step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border), steps_binsearch,
                 len(border_overlapping_b0), len(border_overlapping_b1)))
        if sleep > 0.0:
            rs = ResultSet(list(border), ylow, yup, xspace)
            if n == 2:
                rs.toMatPlot2D(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.toMatPlot3D(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(list(border), ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.toFile(name)

    return ResultSet(list(border), ylow, yup, xspace)


def multidim_search_opt_1(xspace,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, Oracle, float, float, float, bool, float) -> ResultSet

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
    # border = SortedSet(key=Rectangle.volume)
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

    # vprint('xspace: ', xspace)
    # vprint('vol_border: ', vol_border)
    # vprint('delta: ', delta)
    # vprint('step: ', step)
    # vprint('incomparable: ', incomparable)
    # vprint('comparable: ', comparable)

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    print(
        'Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch, volYlowOpt1, volYlowOpt2, volYupOpt1, volYupOpt2')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        # vprint('border:', border)
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        # vprint('xrectangle: ', xrectangle)
        # vprint('xrectangle.volume: ', xrectangle.volume())
        # vprint('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        # y = search(xrectangle.diagToSegment(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diagToSegment(), f, error)
        # vprint('y: ', y)

        # b0 = Rectangle(xspace.min_corner, y.l)
        b0 = Rectangle(xrectangle.min_corner, y.l)
        ylow.append(b0)
        vol_ylow += b0.volume()

        # vprint('b0: ', b0)
        # vprint('ylow: ', ylow)

        # b1 = Rectangle(y.h, xspace.max_corner)
        b1 = Rectangle(y.h, xrectangle.max_corner)
        yup.append(b1)
        vol_yup += b1.volume()

        # vprint('b1: ', b1)
        # vprint('yup: ', yup)

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        ylow_candidates = [rect for rect in border if rect.dominatesRect(b0)]
        ylow.extend(ylow_candidates)
        vol_ylow_opt_1 = sum(b0.volume() for b0 in ylow_candidates)  ##
        vol_ylow += vol_ylow_opt_1
        for rect in ylow_candidates:
            border.remove(rect)

        # Every Border rectangle that is dominated by B1 is included in Yup
        yup_candidates = [rect for rect in border if rect.isDominatedByRect(b1)]
        yup.extend(yup_candidates)
        vol_yup_opt_1 = sum(b1.volume() for b1 in yup_candidates)  ##
        vol_yup += vol_yup_opt_1
        for rect in yup_candidates:
            border.remove(rect)
        ################################

        yrectangle = Rectangle(y.l, y.h)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        ################################
        # Every Incomparable rectangle that dominates B0 is included in Ylow
        ylow_candidates = [inc for inc in i if any(inc.dominatesRect(b0) for b0 in ylow)]
        ylow.extend(ylow_candidates)
        vol_ylow_opt_2 = sum(b0.volume() for b0 in ylow_candidates)  ##
        vol_ylow += vol_ylow_opt_2
        for rect in ylow_candidates:
            i.remove(rect)

        # Every Incomparable rectangle that is dominated by B1 is included in Yup
        yup_candidates = [inc for inc in i if any(inc.isDominatedByRect(b1) for b1 in yup)]
        yup.extend(yup_candidates)
        vol_yup_opt_2 = sum(b1.volume() for b1 in yup_candidates)  ##
        vol_yup += vol_yup_opt_2
        for rect in yup_candidates:
            i.remove(rect)
        ################################

        border += i
        # vprint('irect: ', i)

        vol_border = vol_total - vol_yup - vol_ylow

        print('%s, %s, %s, %s, %s, %d, %d, %d, %d, %s, %s, %s, %s'
              % (step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border), steps_binsearch,
                 vol_ylow_opt_1, vol_ylow_opt_2, vol_yup_opt_1, vol_yup_opt_2))
        if sleep > 0.0:
            rs = ResultSet(list(border), ylow, yup, xspace)
            if n == 2:
                rs.toMatPlot2D(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.toMatPlot3D(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(list(border), ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.toFile(name)

    return ResultSet(list(border), ylow, yup, xspace)


def multidim_search_opt_0(xspace,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, Oracle, float, float, float, bool, float) -> ResultSet

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
    # border = SortedSet(key=Rectangle.volume)
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

    # vprint('xspace: ', xspace)
    # vprint('vol_border: ', vol_border)
    # vprint('delta: ', delta)
    # vprint('step: ', step)
    # vprint('incomparable: ', incomparable)
    # vprint('comparable: ', comparable)

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    print('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        # vprint('border:', border)
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        # vprint('xrectangle: ', xrectangle)
        # vprint('xrectangle.volume: ', xrectangle.volume())
        # vprint('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        # y = search(xrectangle.diagToSegment(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diagToSegment(), f, error)
        # vprint('y: ', y)

        # b0 = Rectangle(xspace.min_corner, y.l)
        b0 = Rectangle(xrectangle.min_corner, y.l)
        ylow.append(b0)
        vol_ylow += b0.volume()

        # vprint('b0: ', b0)
        # vprint('ylow: ', ylow)

        # b1 = Rectangle(y.h, xspace.max_corner)
        b1 = Rectangle(y.h, xrectangle.max_corner)
        yup.append(b1)
        vol_yup += b1.volume()

        # vprint('b1: ', b1)
        # vprint('yup: ', yup)

        yrectangle = Rectangle(y.l, y.h)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        border += i
        # vprint('irect: ', i)

        vol_border = vol_total - vol_yup - vol_ylow

        print('%s, %s, %s, %s, %s, %d, %d, %d, %d'
              % (step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border), steps_binsearch))
        if sleep > 0.0:
            rs = ResultSet(list(border), ylow, yup, xspace)
            if n == 2:
                rs.toMatPlot2D(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.toMatPlot3D(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(list(border), ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.toFile(name)

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
             sleep=0.0,
             opt_level=2,
             logging=True):
    # type: (Oracle, float, float, float, float, float, float, int, bool, float, int, bool) -> ResultSet
    xyspace = create2DSpace(min_cornerx, min_cornery, max_cornerx, max_cornery)
    rs = multidim_search(xyspace, ora, epsilon, delta, max_step, blocking, sleep, opt_level, logging)

    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    n = int((max_cornerx - min_cornerx) / 0.1)
    points = rs.getPointsBorder(n)

    # vprint("Points ", points)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    # rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True, var_names=ora.get_var_names())
    # rs.toMatPlot2DLight(targetx=xs, targety=ys, blocking=True, var_names=ora.get_var_names())
    rs.simplify()
    rs.toMatPlot2DLight(blocking=True, var_names=ora.get_var_names())
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
             sleep=0.0,
             opt_level=2,
             logging=True):
    # type: (Oracle, float, float, float, float, float, float, float, float, int, bool, float, int, bool) -> ResultSet
    xyspace = create3DSpace(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

    rs = multidim_search(xyspace, ora, epsilon, delta, max_step, blocking, sleep, opt_level, logging)

    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    n = int((max_cornerx - min_cornerx) / 0.1)
    points = rs.getPointsBorder(n)

    # vprint("Points ", points)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]

    # rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True, var_names=ora.get_var_names())
    # rs.toMatPlot3DLight(targetx=xs, targety=ys, targetz=zs, blocking=True, var_names=ora.get_var_names())
    rs.simplify()
    rs.toMatPlot3DLight(blocking=True, var_names=ora.get_var_names())
    return rs


def SearchND(ora,
             min_corner=0.0,
             max_corner=1.0,
             epsilon=EPS,
             delta=DELTA,
             max_step=STEPS,
             blocking=False,
             sleep=0.0,
             opt_level=2,
             logging=True):
    # type: (Oracle, float, float, float, float, int, bool, float, int, bool) -> ResultSet
    d = ora.dim()

    minc = (min_corner,) * d
    maxc = (max_corner,) * d
    xyspace = Rectangle(minc, maxc)

    rs = multidim_search(xyspace, ora, epsilon, delta, max_step, blocking, sleep, opt_level, logging)
    rs.simplify()
    return rs
