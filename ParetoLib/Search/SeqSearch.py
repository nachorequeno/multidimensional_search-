import os
import time
import tempfile

from sortedcontainers import SortedListWithKey, SortedSet

import ParetoLib.Search as RootSearch

from ParetoLib.Search.CommonSearch import EPS, DELTA, STEPS, binary_search
from ParetoLib.Search.ResultSet import ResultSet

from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.Geometry.Rectangle import Rectangle, irect, comp, incomp


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
    # type: (Rectangle, Oracle, float, float, int, bool, float, int, bool) -> ResultSet
    md_search = [multidim_search_opt_0,
                 multidim_search_opt_1,
                 multidim_search_opt_2]

    RootSearch.logger.info('Starting multidimensional search')
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
    RootSearch.logger.info('Time multidim search: ' + str(time0))

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
    # type: (Rectangle, Oracle, float, float, float, bool, float, bool) -> ResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    # border = SortedListWithKey(key=Rectangle.volume)
    border = SortedSet([], key=Rectangle.volume)
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

    RootSearch.logger.debug('xspace: ', xspace)
    RootSearch.logger.debug('vol_border: ', vol_border)
    RootSearch.logger.debug('delta: ', delta)
    RootSearch.logger.debug('step: ', step)
    RootSearch.logger.debug('incomparable: ', incomparable)
    RootSearch.logger.debug('comparable: ', comparable)

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info(
        'Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch, nBorder dominated by Ylow, nBorder dominated by Yup')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        RootSearch.logger.debug('border:', border)
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        RootSearch.logger.debug('xrectangle: ', xrectangle)
        RootSearch.logger.debug('xrectangle.volume: ', xrectangle.volume())
        RootSearch.logger.debug('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        # y = search(xrectangle.diag(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
        RootSearch.logger.debug('y: ', y)

        b0 = Rectangle(xrectangle.min_corner, y.low)
        b1 = Rectangle(y.high, xrectangle.max_corner)

        ylow.append(b0)
        yup.append(b1)

        vol_ylow += b0.volume()
        vol_yup += b1.volume()

        RootSearch.logger.debug('b0: ', b0)
        RootSearch.logger.debug('b1: ', b1)

        RootSearch.logger.debug('ylow: ', ylow)
        RootSearch.logger.debug('yup: ', yup)

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        # Every Border rectangle that is dominated by B1 is included in Yup
        b0_extended = Rectangle(xspace.min_corner, y.low)
        b1_extended = Rectangle(y.high, xspace.max_corner)

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

        yrectangle = Rectangle(y.low, y.high)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        border |= i
        RootSearch.logger.debug('irect: ', i)

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border),
                                       steps_binsearch,
                                       len(border_overlapping_b0), len(border_overlapping_b1)))
        if sleep > 0.0:
            rs = ResultSet(list(border), ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(list(border), ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    return ResultSet(list(border), ylow, yup, xspace)


def multidim_search_opt_1(xspace,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, Oracle, float, float, float, bool, float, bool) -> ResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    border = SortedListWithKey([], key=Rectangle.volume)
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

    RootSearch.logger.debug('xspace: ', xspace)
    RootSearch.logger.debug('vol_border: ', vol_border)
    RootSearch.logger.debug('delta: ', delta)
    RootSearch.logger.debug('step: ', step)
    RootSearch.logger.debug('incomparable: ', incomparable)
    RootSearch.logger.debug('comparable: ', comparable)

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, '
                           'BinSearch, volYlowOpt1, volYlowOpt2, volYupOpt1, volYupOpt2')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        RootSearch.logger.debug('border:', border)
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        RootSearch.logger.debug('xrectangle: ', xrectangle)
        RootSearch.logger.debug('xrectangle.volume: ', xrectangle.volume())
        RootSearch.logger.debug('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        # y = search(xrectangle.diag(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
        RootSearch.logger.debug('y: ', y)

        # b0 = Rectangle(xspace.min_corner, y.low)
        b0 = Rectangle(xrectangle.min_corner, y.low)
        ylow.append(b0)
        vol_ylow += b0.volume()

        RootSearch.logger.debug('b0: ', b0)
        RootSearch.logger.debug('ylow: ', ylow)

        # b1 = Rectangle(y.high, xspace.max_corner)
        b1 = Rectangle(y.high, xrectangle.max_corner)
        yup.append(b1)
        vol_yup += b1.volume()

        RootSearch.logger.debug('b1: ', b1)
        RootSearch.logger.debug('yup: ', yup)

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        ylow_candidates = [rect for rect in border if rect.dominates_rect(b0)]
        ylow.extend(ylow_candidates)
        vol_ylow_opt_1 = sum(b0.volume() for b0 in ylow_candidates)
        vol_ylow += vol_ylow_opt_1
        for rect in ylow_candidates:
            border.remove(rect)

        # Every Border rectangle that is dominated by B1 is included in Yup
        yup_candidates = [rect for rect in border if rect.is_dominated_by_rect(b1)]
        yup.extend(yup_candidates)
        vol_yup_opt_1 = sum(b1.volume() for b1 in yup_candidates)
        vol_yup += vol_yup_opt_1
        for rect in yup_candidates:
            border.remove(rect)
        ################################

        yrectangle = Rectangle(y.low, y.high)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        ################################
        # Every Incomparable rectangle that dominates B0 is included in Ylow
        ylow_candidates = [inc for inc in i if any(inc.dominates_rect(b0) for b0 in ylow)]
        ylow.extend(ylow_candidates)
        vol_ylow_opt_2 = sum(b0.volume() for b0 in ylow_candidates)
        vol_ylow += vol_ylow_opt_2
        for rect in ylow_candidates:
            i.remove(rect)

        # Every Incomparable rectangle that is dominated by B1 is included in Yup
        yup_candidates = [inc for inc in i if any(inc.is_dominated_by_rect(b1) for b1 in yup)]
        yup.extend(yup_candidates)
        vol_yup_opt_2 = sum(b1.volume() for b1 in yup_candidates)
        vol_yup += vol_yup_opt_2
        for rect in yup_candidates:
            i.remove(rect)
        ################################

        border += i
        RootSearch.logger.debug('irect: ', i)

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border),
                                       steps_binsearch,
                                       vol_ylow_opt_1, vol_ylow_opt_2, vol_yup_opt_1, vol_yup_opt_2))
        if sleep > 0.0:
            rs = ResultSet(list(border), ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(list(border), ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    return ResultSet(list(border), ylow, yup, xspace)


def multidim_search_opt_0(xspace,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, Oracle, float, float, float, bool, float, bool) -> ResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

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

    RootSearch.logger.debug('xspace: ', xspace)
    RootSearch.logger.debug('vol_border: ', vol_border)
    RootSearch.logger.debug('delta: ', delta)
    RootSearch.logger.debug('step: ', step)
    RootSearch.logger.debug('incomparable: ', incomparable)
    RootSearch.logger.debug('comparable: ', comparable)

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        RootSearch.logger.debug('border:', border)
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        RootSearch.logger.debug('xrectangle: ', xrectangle)
        RootSearch.logger.debug('xrectangle.volume: ', xrectangle.volume())
        RootSearch.logger.debug('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        # y = search(xrectangle.diag(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
        RootSearch.logger.debug('y: ', y)

        # b0 = Rectangle(xspace.min_corner, y.low)
        b0 = Rectangle(xrectangle.min_corner, y.low)
        ylow.append(b0)
        vol_ylow += b0.volume()

        RootSearch.logger.debug('b0: ', b0)
        RootSearch.logger.debug('ylow: ', ylow)

        # b1 = Rectangle(y.high, xspace.max_corner)
        b1 = Rectangle(y.high, xrectangle.max_corner)
        yup.append(b1)
        vol_yup += b1.volume()

        RootSearch.logger.debug('b1: ', b1)
        RootSearch.logger.debug('yup: ', yup)

        yrectangle = Rectangle(y.low, y.high)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        border += i
        RootSearch.logger.debug('irect: ', i)

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info(
            '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}'.format(step, vol_ylow, vol_yup, vol_border, vol_total,
                                                                 len(ylow), len(yup), len(border),
                                                                 steps_binsearch))
        if sleep > 0.0:
            rs = ResultSet(list(border), ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(list(border), ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    return ResultSet(list(border), ylow, yup, xspace)
