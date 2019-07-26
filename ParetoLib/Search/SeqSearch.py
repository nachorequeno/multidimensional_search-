# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""SeqSearch.

This module implements the sequential version of the learning
algorithms described in [1] for searching the Pareto front.

[1] Learning Monotone Partitions of Partially-Ordered Domains,
Nicolas Basset, Oded Maler, J.I Requeno, in
doc/article.pdf.
"""

import os
import time
import tempfile
import itertools

from sortedcontainers import SortedListWithKey, SortedSet

import ParetoLib.Search as RootSearch

from ParetoLib.Search.CommonSearch import EPS, DELTA, STEPS, binary_search
from ParetoLib.Search.ResultSet import ResultSet

from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.Geometry.Rectangle import Rectangle, irect, idwc, iuwc, comp, incomp
from ParetoLib.Geometry.Lattice import Lattice


# Multidimensional search
# The search returns a set of Rectangles in Yup, Ylow and Border
def multidim_search(xspace,
                    yup,
                    ylow,
                    border,
                    oracle,
                    epsilon=EPS,
                    delta=DELTA,
                    max_step=STEPS,
                    blocking=False,
                    sleep=0.0,
                    opt_level=2,
                    logging=True):
    # type: (Rectangle, list, list, list, Oracle, float, float, int, bool, float, int, bool) -> ResultSet
    md_search = [multidim_search_opt_0,
                 multidim_search_opt_1,
                 multidim_search_opt_2,
                 multidim_search_opt_3]

    RootSearch.logger.info('Starting multidimensional search')
    start = time.time()
    rs = md_search[opt_level](xspace,
                              yup,
                              ylow,
                              border,
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
# opt_3 = Equivalent to opt_2 but using a Lattice for detecting dominated cubes in the boundary
# opt_2 = Equivalent to opt_1 but involving less computations
# opt_1 = Maximum optimisation
# opt_0 = No optimisation
##############################

########################################################################################################################
def multidim_search_opt_3(xspace,
                          yup,
                          ylow,
                          border,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, list, list, list, Oracle, float, float, float, bool, float, bool) -> ResultSet

    # xspace is a particular case of maximal rectangle
    # xspace = [min_corner, max_corner]^n = [0, 1]^n
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
    # border = SortedSet([], key=Rectangle.volume)
    # border.add(xspace)

    border = SortedSet(list(border), key=Rectangle.volume)
    lattice_border_ylow = Lattice(dim=xspace.dim(), key=lambda x: x.min_corner)
    lattice_border_yup = Lattice(dim=xspace.dim(), key=lambda x: x.max_corner)

    if len(border) == 0:
        border.add(xspace)
        lattice_border_ylow.add(xspace)
        lattice_border_yup.add(xspace)
    else:
        lattice_border_ylow.add_list(border)
        lattice_border_yup.add_list(border)

    # ylow = []
    # yup = []

    ylow = list(ylow)
    yup = list(yup)

    # x_minimal = points from 'x' that are strictly incomparable (Pareto optimal)
    # ylow_minimal = []
    # yup_minimal = []

    ylow_minimal = list(ylow)
    yup_minimal = list(yup)

    rs = ResultSet(border, ylow, yup, xspace)

    # oracle function
    f = oracle.membership()

    error = (epsilon,) * n
    vol_total = xspace.volume()
    # vol_yup = 0
    # vol_ylow = 0
    # vol_border = vol_total
    vol_yup = rs.volume_yup()
    vol_ylow = rs.volume_ylow()
    vol_border = vol_total - vol_yup - vol_ylow
    step = 0

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info(
        'Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch, nBorder dominated by Ylow, nBorder dominated by Yup')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        RootSearch.logger.debug('border: {0}'.format(border))
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        lattice_border_ylow.remove(xrectangle)
        lattice_border_yup.remove(xrectangle)

        RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
        RootSearch.logger.debug('xrectangle.volume: {0}'.format(xrectangle.volume()))
        RootSearch.logger.debug('xrectangle.norm: {0}'.format(xrectangle.norm()))

        # y, segment
        # y = search(xrectangle.diag(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
        RootSearch.logger.debug('y: {0}'.format(y))
        # discovered_segments.append(y)

        # b0 = Rectangle(xrectangle.min_corner, y.low)
        # b1 = Rectangle(y.high, xrectangle.max_corner)
        #
        # ylow.append(b0)
        # yup.append(b1)
        #
        # vol_ylow += b0.volume()
        # vol_yup += b1.volume()

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        b0_extended = Rectangle(xspace.min_corner, y.low)
        # border_overlapping_b0 = [rect for rect in border if rect.overlaps(b0_extended)]
        # border_overlapping_b0 = [rect for rect in border_overlapping_b0 if rect.overlaps(b0_extended)]
        ylow_rectangle = Rectangle(y.low, y.low)
        border_overlapping_b0 = lattice_border_ylow.less_equal(ylow_rectangle)
        # border_intersecting_b0 = [b0_extended.intersection(rect) for rect in border_overlapping_b0]

        ## border_nondominatedby_b0 = [rect - b0_extended for rect in border_overlapping_b0]
        # border_nondominatedby_b0 = []
        # for rect in border_overlapping_b0:
        #     border_nondominatedby_b0 += list(rect - b0_extended)

        list_idwc = (idwc(b0_extended, rect) for rect in border_overlapping_b0)
        border_nondominatedby_b0 = set(itertools.chain.from_iterable(list_idwc))
        # border_nondominatedby_b0 = Rectangle.fusion_rectangles(border_nondominatedby_b0)

        # if 'rect' is completely dominated by b0_extended (i.e., rect is strictly inside b0_extended), then
        # set(rect - b0_extended) == {rect}
        # Therefore, 'rect' must be removed from 'non dominated' borders

        border |= border_nondominatedby_b0
        border -= border_overlapping_b0

        lattice_border_ylow.add_list(border_nondominatedby_b0)
        lattice_border_ylow.remove_list(border_overlapping_b0)

        lattice_border_yup.add_list(border_nondominatedby_b0)
        lattice_border_yup.remove_list(border_overlapping_b0)

        # Every Border rectangle that is dominated by B1 is included in Yup
        b1_extended = Rectangle(y.high, xspace.max_corner)
        # border_overlapping_b1 = [rect for rect in border if rect.overlaps(b1_extended)]
        # border_overlapping_b1 = [rect for rect in border_overlapping_b1 if rect.overlaps(b1_extended)]
        yup_rectangle = Rectangle(y.high, y.high)
        border_overlapping_b1 = lattice_border_yup.greater_equal(yup_rectangle)
        # border_intersecting_b1 = [b1_extended.intersection(rect) for rect in border_overlapping_b1]

        ## border_nondominatedby_b1 = [rect - b1_extended for rect in border_overlapping_b1]
        # border_nondominatedby_b1 = []
        # for rect in border_overlapping_b1:
        #     border_nondominatedby_b1 += list(rect - b1_extended)

        list_iuwc = (iuwc(b1_extended, rect) for rect in border_overlapping_b1)
        border_nondominatedby_b1 = set(itertools.chain.from_iterable(list_iuwc))
        # border_nondominatedby_b1 = Rectangle.fusion_rectangles(border_nondominatedby_b1)

        # if 'rect' is completely dominated by b1_extended (i.e., rect is strictly inside b1_extended), then
        # set(rect - b1_extended) == {rect}
        # Therefore, 'rect' must be removed from 'non dominated' borders

        border |= border_nondominatedby_b1
        border -= border_overlapping_b1

        lattice_border_ylow.add_list(border_nondominatedby_b1)
        lattice_border_ylow.remove_list(border_overlapping_b1)

        lattice_border_yup.add_list(border_nondominatedby_b1)
        lattice_border_yup.remove_list(border_overlapping_b1)

        db0 = Rectangle.difference_rectangles(b0_extended, ylow_minimal)
        db1 = Rectangle.difference_rectangles(b1_extended, yup_minimal)

        vol_db0 = sum(b0.volume() for b0 in db0)
        vol_db1 = sum(b1.volume() for b1 in db1)

        # rs = ResultSet([], border_intersecting_b0 + [b0], border_intersecting_b1 + [b1], Rectangle())
        # vol_db0 = rs.volume_ylow() - rs.overlapping_volume_ylow()
        # vol_db1 = rs.volume_yup() - rs.overlapping_volume_yup()

        vol_ylow += vol_db0
        vol_yup += vol_db1

        ylow.extend(db0)
        yup.extend(db1)

        ylow_minimal.append(b0_extended)
        yup_minimal.append(b1_extended)

        RootSearch.logger.debug('b0: {0}'.format(db0))
        RootSearch.logger.debug('b1: {0}'.format(db1))

        RootSearch.logger.debug('ylow: {0}'.format(ylow))
        RootSearch.logger.debug('yup: {0}'.format(yup))

        ################################
        # Every rectangle in 'i' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'i' is incomparable for current B1 and for all B1 included in Yup
        ################################

        yrectangle = Rectangle(y.low, y.high)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        border |= i
        RootSearch.logger.debug('irect: {0}'.format(i))

        lattice_border_ylow.add_list(i)
        lattice_border_yup.add_list(i)

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border),
                                       steps_binsearch,
                                       len(border_overlapping_b0), len(border_overlapping_b1)))
        if sleep > 0.0:
            rs = ResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    return ResultSet(border, ylow, yup, xspace)


def multidim_search_opt_2(xspace,
                          yup,
                          ylow,
                          border,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, list, list, list, Oracle, float, float, float, bool, float, bool) -> ResultSet

    # xspace is a particular case of maximal rectangle
    # xspace = [min_corner, max_corner]^n = [0, 1]^n
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
    # border = SortedSet([], key=Rectangle.volume)
    # border.add(xspace)
    border = SortedSet(list(border), key=Rectangle.volume)
    if len(border) == 0:
        border.add(xspace)

    # ylow = []
    # yup = []

    ylow = list(ylow)
    yup = list(yup)

    # x_minimal = points from 'x' that are strictly incomparable (Pareto optimal)
    # ylow_minimal = []
    # yup_minimal = []

    ylow_minimal = list(ylow)
    yup_minimal = list(yup)

    rs = ResultSet(border, ylow, yup, xspace)

    # oracle function
    f = oracle.membership()

    error = (epsilon,) * n
    vol_total = xspace.volume()
    # vol_yup = 0
    # vol_ylow = 0
    # vol_border = vol_total
    vol_yup = rs.volume_yup()
    vol_ylow = rs.volume_ylow()
    vol_border = vol_total - vol_yup - vol_ylow
    step = 0

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info(
        'Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch, nBorder dominated by Ylow, nBorder dominated by Yup')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        RootSearch.logger.debug('border: {0}'.format(border))
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
        RootSearch.logger.debug('xrectangle.volume: {0}'.format(xrectangle.volume()))
        RootSearch.logger.debug('xrectangle.norm: {0}'.format(xrectangle.norm()))

        # y, segment
        # y = search(xrectangle.diag(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
        RootSearch.logger.debug('y: {0}'.format(y))
        # discovered_segments.append(y)

        # b0 = Rectangle(xrectangle.min_corner, y.low)
        # b1 = Rectangle(y.high, xrectangle.max_corner)
        #
        # ylow.append(b0)
        # yup.append(b1)
        #
        # vol_ylow += b0.volume()
        # vol_yup += b1.volume()

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        b0_extended = Rectangle(xspace.min_corner, y.low)
        border_overlapping_b0 = [rect for rect in border if rect.overlaps(b0_extended)]
        # border_intersecting_b0 = [b0_extended.intersection(rect) for rect in border_overlapping_b0]

        ## border_nondominatedby_b0 = [rect - b0_extended for rect in border_overlapping_b0]
        # border_nondominatedby_b0 = []
        # for rect in border_overlapping_b0:
        #     border_nondominatedby_b0 += list(rect - b0_extended)

        list_idwc = (idwc(b0_extended, rect) for rect in border_overlapping_b0)
        border_nondominatedby_b0 = set(itertools.chain.from_iterable(list_idwc))
        # border_nondominatedby_b0 = Rectangle.fusion_rectangles(border_nondominatedby_b0)

        # if 'rect' is completely dominated by b0_extended (i.e., rect is strictly inside b0_extended), then
        # set(rect - b0_extended) == {rect}
        # Therefore, 'rect' must be removed from 'non dominated' borders

        border |= border_nondominatedby_b0
        border -= border_overlapping_b0

        # Every Border rectangle that is dominated by B1 is included in Yup
        b1_extended = Rectangle(y.high, xspace.max_corner)
        border_overlapping_b1 = [rect for rect in border if rect.overlaps(b1_extended)]
        # border_intersecting_b1 = [b1_extended.intersection(rect) for rect in border_overlapping_b1]

        ## border_nondominatedby_b1 = [rect - b1_extended for rect in border_overlapping_b1]
        # border_nondominatedby_b1 = []
        # for rect in border_overlapping_b1:
        #     border_nondominatedby_b1 += list(rect - b1_extended)

        list_iuwc = (iuwc(b1_extended, rect) for rect in border_overlapping_b1)
        border_nondominatedby_b1 = set(itertools.chain.from_iterable(list_iuwc))
        # border_nondominatedby_b1 = Rectangle.fusion_rectangles(border_nondominatedby_b1)

        # if 'rect' is completely dominated by b1_extended (i.e., rect is strictly inside b1_extended), then
        # set(rect - b1_extended) == {rect}
        # Therefore, 'rect' must be removed from 'non dominated' borders

        border |= border_nondominatedby_b1
        border -= border_overlapping_b1

        db0 = Rectangle.difference_rectangles(b0_extended, ylow_minimal)
        db1 = Rectangle.difference_rectangles(b1_extended, yup_minimal)

        vol_db0 = sum(b0.volume() for b0 in db0)
        vol_db1 = sum(b1.volume() for b1 in db1)

        # rs = ResultSet([], border_intersecting_b0 + [b0], border_intersecting_b1 + [b1], Rectangle())
        # vol_db0 = rs.volume_ylow() - rs.overlapping_volume_ylow()
        # vol_db1 = rs.volume_yup() - rs.overlapping_volume_yup()

        vol_ylow += vol_db0
        vol_yup += vol_db1

        ylow.extend(db0)
        yup.extend(db1)

        ylow_minimal.append(b0_extended)
        yup_minimal.append(b1_extended)

        RootSearch.logger.debug('b0: {0}'.format(db0))
        RootSearch.logger.debug('b1: {0}'.format(db1))

        RootSearch.logger.debug('ylow: {0}'.format(ylow))
        RootSearch.logger.debug('yup: {0}'.format(yup))

        ################################
        # Every rectangle in 'i' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'i' is incomparable for current B1 and for all B1 included in Yup
        ################################

        yrectangle = Rectangle(y.low, y.high)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        border |= i
        RootSearch.logger.debug('irect: {0}'.format(i))

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border),
                                       steps_binsearch,
                                       len(border_overlapping_b0), len(border_overlapping_b1)))
        if sleep > 0.0:
            rs = ResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    return ResultSet(border, ylow, yup, xspace)


def multidim_search_opt_1(xspace,
                          yup,
                          ylow,
                          border,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, list, list, list, Oracle, float, float, float, bool, float, bool) -> ResultSet

    # xspace is a particular case of maximal rectangle
    # xspace = [min_corner, max_corner]^n = [0, 1]^n
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
    #
    # border = SortedSet([], key=Rectangle.volume)
    # border.add(xspace)

    border = SortedSet(list(border), key=Rectangle.volume)
    if len(border) == 0:
        border.add(xspace)

    # ylow = []
    # yup = []

    ylow = list(ylow)
    yup = list(yup)

    rs = ResultSet(border, ylow, yup, xspace)

    # oracle function
    f = oracle.membership()

    error = (epsilon,) * n
    vol_total = xspace.volume()
    # vol_yup = 0
    # vol_ylow = 0
    # vol_border = vol_total
    vol_yup = rs.volume_yup()
    vol_ylow = rs.volume_ylow()
    vol_border = vol_total - vol_yup - vol_ylow
    step = 0

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info(
        'Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch, nBorder dominated by Ylow, nBorder dominated by Yup')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        RootSearch.logger.debug('border: {0}'.format(border))
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
        RootSearch.logger.debug('xrectangle.volume: {0}'.format(xrectangle.volume()))
        RootSearch.logger.debug('xrectangle.norm: {0}'.format(xrectangle.norm()))

        # y, segment
        # y = search(xrectangle.diag(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
        RootSearch.logger.debug('y: {0}'.format(y))
        # discovered_segments.append(y)

        b0 = Rectangle(xrectangle.min_corner, y.low)
        b1 = Rectangle(y.high, xrectangle.max_corner)

        ylow.append(b0)
        yup.append(b1)

        vol_ylow += b0.volume()
        vol_yup += b1.volume()

        RootSearch.logger.debug('b0: {0}'.format(b0))
        RootSearch.logger.debug('b1: {0}'.format(b1))

        RootSearch.logger.debug('ylow: {0}'.format(ylow))
        RootSearch.logger.debug('yup: {0}'.format(yup))

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        # Every Border rectangle that is dominated by B1 is included in Yup
        b0_extended = Rectangle(xspace.min_corner, y.low)
        b1_extended = Rectangle(y.high, xspace.max_corner)

        # Every cube in the boundary overlaps another cube in the boundary
        # When cubes from the boundary are moved to ylow or yup, they may still have a complementary cube
        # remaining in the boundary with a non-empty intersection.
        border_overlapping_ylow = [r for r in ylow if r.overlaps(b0_extended)]
        border_overlapping_yup = [r for r in yup if r.overlaps(b1_extended)]

        border_overlapping_b0 = [rect for rect in border if rect.overlaps(b0_extended)]
        # Warning: Be aware of the overlapping areas of the cubes in the border.
        # If we calculate the intersection of b0_extended with all the cubes in the frontier, and two cubes
        # 'a' and 'b' partially overlaps, then the volume of this overlapping portion will be counted twice
        # border_dominatedby_b0 = [rect.intersection(b0_extended) for rect in border_overlapping_b0]
        # Solution: Project the 'shadow' of the cubes in the border over b0_extended.
        border_dominatedby_b0_shadow = Rectangle.difference_rectangles(b0_extended, border_overlapping_b0)

        # The negative of this image returns a set of cubes in the boundary without overlapping.
        # border_dominatedby_b0 will be appended to ylow.
        # Remove the portion of the negative that overlaps any cube that is already appended to ylow
        border_dominatedby_b0 = Rectangle.difference_rectangles(b0_extended, border_dominatedby_b0_shadow + border_overlapping_ylow)

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

        border_overlapping_b1 = [rect for rect in border if rect.overlaps(b1_extended)]
        # Warning: Be aware of the overlapping areas of the cubes in the border.
        # If we calculate the intersection of b1_extended with all the cubes in the frontier, and two cubes
        # 'a' and 'b' partially overlaps, then the volume of this overlapping portion will be considered twice
        # border_dominatedby_b1 = [rect.intersection(b1_extended) for rect in border_overlapping_b1]
        # Solution: Project the 'shadow' of the cubes in the border over b1_extended.
        border_dominatedby_b1_shadow = Rectangle.difference_rectangles(b1_extended, border_overlapping_b1)

        # The negative of this image returns a set of cubes in the boundary without overlapping.
        # border_dominatedby_b1 will be appended to yup.
        # Remove the portion of the negative that overlaps any cube that is already appended to yup
        border_dominatedby_b1 = Rectangle.difference_rectangles(b1_extended, border_dominatedby_b1_shadow + border_overlapping_yup)

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
        RootSearch.logger.debug('irect: {0}'.format(i))

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border),
                                       steps_binsearch,
                                       len(border_overlapping_b0), len(border_overlapping_b1)))
        if sleep > 0.0:
            rs = ResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    return ResultSet(border, ylow, yup, xspace)


# Opt_inf is not applicable: it does not improve the convergence of opt_0 because it cannot preemptively remove cubes.
# Cubes from the boundary are partially dominated by Pareto points in Ylow/Ylup, while opt_inf searches for
# cubes that are fully dominated.
def multidim_search_opt_inf(xspace,
                          yup,
                          ylow,
                          border,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, list, list, list, Oracle, float, float, float, bool, float, bool) -> ResultSet

    # xspace is a particular case of maximal rectangle
    # xspace = [min_corner, max_corner]^n = [0, 1]^n
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
    #
    # border = SortedListWithKey([], key=Rectangle.volume)
    # border.add(xspace)
    border = SortedListWithKey(list(border), key=Rectangle.volume)
    if len(border) == 0:
        border.add(xspace)

    # ylow = []
    # yup = []

    ylow = list(ylow)
    yup = list(yup)

    rs = ResultSet(border, ylow, yup, xspace)

    # oracle function
    f = oracle.membership()

    error = (epsilon,) * n
    vol_total = xspace.volume()
    # vol_yup = 0
    # vol_ylow = 0
    # vol_border = vol_total
    vol_yup = rs.volume_yup()
    vol_ylow = rs.volume_ylow()
    vol_border = vol_total - vol_yup - vol_ylow
    step = 0

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, '
                           'BinSearch, volYlowOpt1, volYlowOpt2, volYupOpt1, volYupOpt2')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        RootSearch.logger.debug('border: {0}'.format(border))
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
        RootSearch.logger.debug('xrectangle.volume: {0}'.format(xrectangle.volume()))
        RootSearch.logger.debug('xrectangle.norm: {0}'.format(xrectangle.norm()))

        # y, segment
        # y = search(xrectangle.diag(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
        RootSearch.logger.debug('y: {0}'.format(y))

        # b0 = Rectangle(xspace.min_corner, y.low)
        b0 = Rectangle(xrectangle.min_corner, y.low)
        ylow.append(b0)
        vol_ylow += b0.volume()

        RootSearch.logger.debug('b0: {0}'.format(b0))
        RootSearch.logger.debug('ylow: {0}'.format(ylow))

        # b1 = Rectangle(y.high, xspace.max_corner)
        b1 = Rectangle(y.high, xrectangle.max_corner)
        yup.append(b1)
        vol_yup += b1.volume()

        RootSearch.logger.debug('b1: {0}'.format(b1))
        RootSearch.logger.debug('yup: {0}'.format(yup))

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
        RootSearch.logger.debug('irect: {0}'.format(i))

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup), len(border),
                                       steps_binsearch,
                                       vol_ylow_opt_1, vol_ylow_opt_2, vol_yup_opt_1, vol_yup_opt_2))
        if sleep > 0.0:
            rs = ResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    return ResultSet(border, ylow, yup, xspace)


def multidim_search_opt_0(xspace,
                          yup,
                          ylow,
                          border,
                          oracle,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0.0,
                          logging=True):
    # type: (Rectangle, list, list, list, Oracle, float, float, float, bool, float, bool) -> ResultSet

    # xspace is a particular case of maximal rectangle
    # xspace = [min_corner, max_corner]^n = [0, 1]^n
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
    #
    # border = SortedListWithKey(key=Rectangle.volume)
    # border.add(xspace)
    border = SortedListWithKey(list(border), key=Rectangle.volume)
    if len(border) == 0:
        border.add(xspace)

    # ylow = []
    # yup = []

    ylow = list(ylow)
    yup = list(yup)

    rs = ResultSet(border, ylow, yup, xspace)

    # oracle function
    f = oracle.membership()

    error = (epsilon,) * n
    vol_total = xspace.volume()
    # vol_yup = 0
    # vol_ylow = 0
    # vol_border = vol_total
    vol_yup = rs.volume_yup()
    vol_ylow = rs.volume_ylow()
    vol_border = vol_total - vol_yup - vol_ylow
    step = 0

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch')
    while (vol_border >= delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1
        RootSearch.logger.debug('border: {0}'.format(border))
        # l.sort(key=Rectangle.volume)

        xrectangle = border.pop()

        RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
        RootSearch.logger.debug('xrectangle.volume: {0}'.format(xrectangle.volume()))
        RootSearch.logger.debug('xrectangle.norm: {0}'.format(xrectangle.norm()))

        # y, segment
        # y = search(xrectangle.diag(), f, epsilon)
        y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
        RootSearch.logger.debug('y: {0}'.format(y))

        # b0 = Rectangle(xspace.min_corner, y.low)
        b0 = Rectangle(xrectangle.min_corner, y.low)
        ylow.append(b0)
        vol_ylow += b0.volume()

        RootSearch.logger.debug('b0: {0}'.format(b0))
        RootSearch.logger.debug('ylow: {0}'.format(ylow))

        # b1 = Rectangle(y.high, xspace.max_corner)
        b1 = Rectangle(y.high, xrectangle.max_corner)
        yup.append(b1)
        vol_yup += b1.volume()

        RootSearch.logger.debug('b1: {0}'.format(b1))
        RootSearch.logger.debug('yup: {0}'.format(yup))

        yrectangle = Rectangle(y.low, y.high)
        i = irect(incomparable, yrectangle, xrectangle)
        # i = pirect(incomparable, yrectangle, xrectangle)
        # l.extend(i)

        border += i
        RootSearch.logger.debug('irect: {0}'.format(i))

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info(
            '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}'.format(step, vol_ylow, vol_yup, vol_border, vol_total,
                                                                 len(ylow), len(yup), len(border),
                                                                 steps_binsearch))
        if sleep > 0.0:
            rs = ResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    return ResultSet(border, ylow, yup, xspace)
