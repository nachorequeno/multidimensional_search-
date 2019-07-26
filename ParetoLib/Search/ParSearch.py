# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""ParSearch.

This module implements a multithreading version of the learning
algorithms described in [1] for searching the Pareto front.

[1] Learning Monotone Partitions of Partially-Ordered Domains,
Nicolas Basset, Oded Maler, J.I Requeno, in
doc/article.pdf.
"""

import os
import copy
import time
import tempfile
import itertools
import multiprocessing as mp

from multiprocessing import Manager, Pool, cpu_count
from sortedcontainers import SortedSet

import ParetoLib.Search as RootSearch

from ParetoLib.Search.CommonSearch import EPS, DELTA, STEPS, binary_search
from ParetoLib.Search.ParResultSet import ParResultSet

from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.Geometry.Rectangle import Rectangle, irect, idwc, iuwc, comp, incomp
from ParetoLib.Geometry.ParRectangle import pvol
from ParetoLib.Geometry.Lattice import Lattice


def pbin_search_ser(args):
    xrectangle, f, epsilon, n = args
    RootSearch.logger.debug('Executing serial binary search')
    RootSearch.logger.debug('xrectangle, epsilon, n: {0}, {1}, {2}'.format(xrectangle, epsilon, n))
    error = (epsilon,) * n
    y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
    RootSearch.logger.debug('End serial binary search')
    RootSearch.logger.debug('y, steps_binsearch: {0}, {1}'.format(y, steps_binsearch))
    return y


def pbin_search(args):
    xrectangle, dict_man, epsilon, n = args
    RootSearch.logger.debug('Executing parallel binary search')
    RootSearch.logger.debug('xrectangle, epsilon, n: {0}, {1}, {2}'.format(xrectangle, epsilon, n))
    RootSearch.logger.debug('dict_man[{0}]: {1}'.format(mp.current_process().name, dict_man[mp.current_process().name]))
    ora = dict_man[mp.current_process().name]
    f = ora.membership()
    RootSearch.logger.debug('f = {0}'.format(f))
    error = (epsilon,) * n
    y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
    RootSearch.logger.debug('End parallel binary search')
    RootSearch.logger.debug('y, steps_binsearch: {0}, {1}'.format(y, steps_binsearch))
    return y


def pb0(args):
    # b0 = Rectangle(xspace.min_corner, y.low)
    xrectangle, y = args
    return Rectangle(xrectangle.min_corner, y.low)


def pb1(args):
    # b1 = Rectangle(y.high, xspace.max_corner)
    xrectangle, y = args
    return Rectangle(y.high, xrectangle.max_corner)


def pborder(args):
    # border = irect(incomparable, yrectangle, xrectangle)
    incomparable, y, xrectangle = args
    yrectangle = Rectangle(y.low, y.high)
    return irect(incomparable, yrectangle, xrectangle)


def pborder_dominatedby_bi(args):
    bi_extended, rect = args
    return rect.intersection(bi_extended)


def pborder_nondominatedby_bi(args):
    rect, bi_extended = args
    return rect - bi_extended


def pborder_nondominatedby_b0(args):
    b0_extended, rect = args
    return idwc(b0_extended, rect)


def pborder_nondominatedby_b1(args):
    b1_extended, rect = args
    return iuwc(b1_extended, rect)

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
    # type: (Rectangle, Oracle, float, float, int, bool, float, int, bool) -> ParResultSet
    md_search = [multidim_search_deep_first_opt_0,
                 multidim_search_deep_first_opt_1,
                 multidim_search_deep_first_opt_2,
                 multidim_search_deep_first_opt_3]

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
# opt_3 = Equivalent to opt_2 but using a Lattice for detecting dominated cubes in the boundary
# opt_2 = Equivalent to opt_1 but involving less computations
# opt_1 = Maximum optimisation
# opt_0 = No optimisation
##############################

########################################################################################################################
# Multidimensional search prioritizing the analysis of rectangles with highest volume
def multidim_search_deep_first_opt_3(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

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

    border = SortedSet([], key=Rectangle.volume)
    border.add(xspace)

    lattice_border_ylow = Lattice(dim=xspace.dim(), key=lambda x: x.min_corner)
    lattice_border_yup = Lattice(dim=xspace.dim(), key=lambda x: x.max_corner)

    lattice_border_ylow.add(xspace)
    lattice_border_yup.add(xspace)

    # Upper and lower clausure
    ylow = []
    yup = []

    # x_minimal = points from 'x' that are strictly incomparable (Pareto optimal)
    ylow_minimal = []
    yup_minimal = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        border -= slice_border

        lattice_border_ylow.remove_list(slice_border)
        lattice_border_yup.remove_list(slice_border)

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        # b0_list = p.map(pb0, zip(slice_border, y_list))
        # b1_list = p.map(pb1, zip(slice_border, y_list))
        #
        # ylow.extend(b0_list)
        # yup.extend(b1_list)
        #
        # vol_b0_list = p.imap_unordered(pvol, b0_list)
        # vol_b1_list = p.imap_unordered(pvol, b1_list)
        #
        # vol_ylow += sum(vol_b0_list)
        # vol_yup += sum(vol_b1_list)

        ################################
        for y_segment in y_list:
            yl, yh = y_segment.low, y_segment.high
            # Every Border rectangle that dominates B0 is included in Ylow
            # Every Border rectangle that is dominated by B1 is included in Yup
            b0_extended = Rectangle(xspace.min_corner, yl)
            b1_extended = Rectangle(yh, xspace.max_corner)

            # Warning: Be aware of the overlapping areas of the cubes in the border.
            ylow_rectangle = Rectangle(yl, yl)
            border_overlapping_b0 = lattice_border_ylow.less_equal(ylow_rectangle)
            # border_overlapping_b0 = [rect for rect in border if b0_extended.overlaps(rect)]

            # for rect in border_overlapping_b0:
            #     border |= list(rect - b0_extended)
            # border -= border_overlapping_b0

            # Use [] (list, static) instead of () (iterator, dynamic) for preventing interleaving and racing conditions
            # of copy.deepcopy when running in parallel
            # args_pborder_nondominatedby_b0 = [(rect, copy.deepcopy(b0_extended)) for rect in border_overlapping_b0]
            # border_nondominatedby_b0_list = p.imap_unordered(pborder_nondominatedby_bi, args_pborder_nondominatedby_b0)
            args_pborder_nondominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            border_nondominatedby_b0_list = p.imap_unordered(pborder_nondominatedby_b0, args_pborder_nondominatedby_b0)

            # Flatten list
            border_nondominatedby_b0 = set(itertools.chain.from_iterable(border_nondominatedby_b0_list))

            # args_pborder_dominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            # border_dominatedby_b0 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b0)
            # border_dominatedby_b0 = [rect.intersection(b0_extended) for rect in border_overlapping_b0]

            border |= border_nondominatedby_b0
            border -= border_overlapping_b0

            lattice_border_ylow.add_list(border_nondominatedby_b0)
            lattice_border_ylow.remove_list(border_overlapping_b0)

            lattice_border_yup.add_list(border_nondominatedby_b0)
            lattice_border_yup.remove_list(border_overlapping_b0)

            yup_rectangle = Rectangle(yh, yh)
            border_overlapping_b1 = lattice_border_yup.greater_equal(yup_rectangle)
            # border_overlapping_b1 = [rect for rect in border if b1_extended.overlaps(rect)]
            # for rect in border_overlapping_b1:
            #     border |= list(rect - b1_extended)
            # border -= border_overlapping_b1

            # args_pborder_nondominatedby_b1 = [(rect, copy.deepcopy(b1_extended)) for rect in border_overlapping_b1]
            # border_nondominatedby_b1_list = p.imap_unordered(pborder_nondominatedby_bi, args_pborder_nondominatedby_b1)
            args_pborder_nondominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]
            border_nondominatedby_b1_list = p.imap_unordered(pborder_nondominatedby_b1, args_pborder_nondominatedby_b1)

            # Flatten list
            border_nondominatedby_b1 = set(itertools.chain.from_iterable(border_nondominatedby_b1_list))

            # args_pborder_dominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]
            # border_dominatedby_b1 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b1)
            # border_dominatedby_b1 = [rect.intersection(b1_extended) for rect in border_overlapping_b1]

            border |= border_nondominatedby_b1
            border -= border_overlapping_b1

            lattice_border_ylow.add_list(border_nondominatedby_b1)
            lattice_border_ylow.remove_list(border_overlapping_b1)

            lattice_border_yup.add_list(border_nondominatedby_b1)
            lattice_border_yup.remove_list(border_overlapping_b1)

            db0 = Rectangle.difference_rectangles(b0_extended, ylow_minimal)
            db1 = Rectangle.difference_rectangles(b1_extended, yup_minimal)

            ylow.extend(db0)
            yup.extend(db1)

            ylow_minimal.append(b0_extended)
            yup_minimal.append(b1_extended)

            vol_b0_list = p.imap_unordered(pvol, db0)
            vol_b1_list = p.imap_unordered(pvol, db1)

            vol_ylow += sum(vol_b0_list)
            vol_yup += sum(vol_b1_list)

        ################################

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        lattice_border_ylow.add_list(list(new_incomp_rects))
        lattice_border_yup.add_list(list(new_incomp_rects))

        ################################
        # Every rectangle in 'new_incomp_rects' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'new_incomp_rects' is incomparable for current B1 and for all B1 included in Yup
        ################################

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


def multidim_search_deep_first_opt_2(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

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

    border = SortedSet([], key=Rectangle.volume)
    border.add(xspace)

    # Upper and lower clausure
    ylow = []
    yup = []

    # x_minimal = points from 'x' that are strictly incomparable (Pareto optimal)
    ylow_minimal = []
    yup_minimal = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        # b0_list = p.map(pb0, zip(slice_border, y_list))
        # b1_list = p.map(pb1, zip(slice_border, y_list))
        #
        # ylow.extend(b0_list)
        # yup.extend(b1_list)
        #
        # vol_b0_list = p.imap_unordered(pvol, b0_list)
        # vol_b1_list = p.imap_unordered(pvol, b1_list)
        #
        # vol_ylow += sum(vol_b0_list)
        # vol_yup += sum(vol_b1_list)

        ################################
        for y_segment in y_list:
            yl, yh = y_segment.low, y_segment.high
            # Every Border rectangle that dominates B0 is included in Ylow
            # Every Border rectangle that is dominated by B1 is included in Yup
            b0_extended = Rectangle(xspace.min_corner, yl)
            b1_extended = Rectangle(yh, xspace.max_corner)

            # Warning: Be aware of the overlapping areas of the cubes in the border.
            border_overlapping_b0 = [rect for rect in border if b0_extended.overlaps(rect)]
            # for rect in border_overlapping_b0:
            #     border |= list(rect - b0_extended)
            # border -= border_overlapping_b0

            # Use [] (list, static) instead of () (iterator, dynamic) for preventing interleaving and racing conditions
            # of copy.deepcopy when running in parallel
            # args_pborder_nondominatedby_b0 = [(rect, copy.deepcopy(b0_extended)) for rect in border_overlapping_b0]
            # border_nondominatedby_b0_list = p.imap_unordered(pborder_nondominatedby_bi, args_pborder_nondominatedby_b0)
            args_pborder_nondominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            border_nondominatedby_b0_list = p.imap_unordered(pborder_nondominatedby_b0, args_pborder_nondominatedby_b0)

            # Flatten list
            border_nondominatedby_b0 = set(itertools.chain.from_iterable(border_nondominatedby_b0_list))

            # args_pborder_dominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            # border_dominatedby_b0 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b0)
            # border_dominatedby_b0 = [rect.intersection(b0_extended) for rect in border_overlapping_b0]

            border |= border_nondominatedby_b0
            border -= border_overlapping_b0

            border_overlapping_b1 = [rect for rect in border if b1_extended.overlaps(rect)]
            # for rect in border_overlapping_b1:
            #     border |= list(rect - b1_extended)
            # border -= border_overlapping_b1

            # args_pborder_nondominatedby_b1 = [(rect, copy.deepcopy(b1_extended)) for rect in border_overlapping_b1]
            # border_nondominatedby_b1_list = p.imap_unordered(pborder_nondominatedby_bi, args_pborder_nondominatedby_b1)
            args_pborder_nondominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]
            border_nondominatedby_b1_list = p.imap_unordered(pborder_nondominatedby_b1, args_pborder_nondominatedby_b1)

            # Flatten list
            border_nondominatedby_b1 = set(itertools.chain.from_iterable(border_nondominatedby_b1_list))

            # args_pborder_dominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]
            # border_dominatedby_b1 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b1)
            # border_dominatedby_b1 = [rect.intersection(b1_extended) for rect in border_overlapping_b1]

            border |= border_nondominatedby_b1
            border -= border_overlapping_b1

            db0 = Rectangle.difference_rectangles(b0_extended, ylow_minimal)
            db1 = Rectangle.difference_rectangles(b1_extended, yup_minimal)

            ylow.extend(db0)
            yup.extend(db1)

            ylow_minimal.append(b0_extended)
            yup_minimal.append(b1_extended)

            vol_b0_list = p.imap_unordered(pvol, db0)
            vol_b1_list = p.imap_unordered(pvol, db1)

            vol_ylow += sum(vol_b0_list)
            vol_yup += sum(vol_b1_list)

        ################################

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        ################################
        # Every rectangle in 'new_incomp_rects' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'new_incomp_rects' is incomparable for current B1 and for all B1 included in Yup
        ################################

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


def multidim_search_deep_first_opt_1(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

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

    # Upper and lower clausure
    ylow = []
    yup = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        b0_list = p.map(pb0, zip(slice_border, y_list))
        b1_list = p.map(pb1, zip(slice_border, y_list))

        ylow.extend(b0_list)
        yup.extend(b1_list)

        vol_b0_list = p.imap_unordered(pvol, b0_list)
        vol_b1_list = p.imap_unordered(pvol, b1_list)

        vol_ylow += sum(vol_b0_list)
        vol_yup += sum(vol_b1_list)

        ################################
        for y_segment in y_list:
            yl, yh = y_segment.low, y_segment.high
            # Every Border rectangle that dominates B0 is included in Ylow
            # Every Border rectangle that is dominated by B1 is included in Yup
            b0_extended = Rectangle(xspace.min_corner, yl)
            b1_extended = Rectangle(yh, xspace.max_corner)

            # Every cube in the boundary overlaps another cube in the boundary
            # When cubes from the boundary are moved to ylow or yup, they may still have a complementary cube
            # remaining in the boundary with a non-empty intersection.
            border_overlapping_ylow = [r for r in ylow if r.overlaps(b0_extended)]
            border_overlapping_yup = [r for r in yup if r.overlaps(b1_extended)]

            border_overlapping_b0 = [rect for rect in border if b0_extended.overlaps(rect)]
            for rect in border_overlapping_b0:
                border |= list(rect - b0_extended)
            border -= border_overlapping_b0

            border_overlapping_b1 = [rect for rect in border if b1_extended.overlaps(rect)]
            for rect in border_overlapping_b1:
                border |= list(rect - b1_extended)
            border -= border_overlapping_b1

            # border_dominatedby_b0 = [rect.intersection(b0_extended) for rect in border_overlapping_b0]
            # border_dominatedby_b1 = [rect.intersection(b1_extended) for rect in border_overlapping_b1]

            # Use [] (list, static) instead of () (iterator, dynamic) for preventing interleaving and racing conditions
            # of copy.deepcopy when running in parallel
            # args_pborder_dominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            # args_pborder_dominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]

            # border_dominatedby_b0 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b0)
            # border_dominatedby_b1 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b1)

            # Warning: Be aware of the overlapping areas of the cubes in the border.
            # If we calculate the intersection of b{0|1}_extended with all the cubes in the frontier, and two cubes
            # 'a' and 'b' partially overlaps, then the volume of this overlapping portion will be considered twice
            # Solution: Project the 'shadow' of the cubes in the border over b{0|1}_extended.

            border_dominatedby_b0_shadow = Rectangle.difference_rectangles(b0_extended, border_overlapping_b0)
            border_dominatedby_b1_shadow = Rectangle.difference_rectangles(b1_extended, border_overlapping_b1)

            # The negative of this image returns a set of cubes in the boundary without overlapping.
            # border_dominatedby_b{0|1} will be appended to yup/ylow.
            # Remove the portion of the negative that overlaps any cube is already appended to yup/ylow

            border_dominatedby_b0 = Rectangle.difference_rectangles(b0_extended,
                                                                    border_dominatedby_b0_shadow + border_overlapping_ylow)  # ylow
            border_dominatedby_b1 = Rectangle.difference_rectangles(b1_extended,
                                                                    border_dominatedby_b1_shadow + border_overlapping_yup)  # yup

            ylow.extend(border_dominatedby_b0)
            yup.extend(border_dominatedby_b1)

            vol_b0_list = p.imap_unordered(pvol, border_dominatedby_b0)
            vol_b1_list = p.imap_unordered(pvol, border_dominatedby_b1)

            vol_ylow += sum(vol_b0_list)
            vol_yup += sum(vol_b1_list)
        ################################

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        ################################
        # Every rectangle in 'new_incomp_rects' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'new_incomp_rects' is incomparable for current B1 and for all B1 included in Yup
        ################################

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


# Opt_inf is not applicable: it does not improve the convergence of opt_0 because it cannot preemptively remove cubes.
# Cubes from the boundary are partially dominated by Pareto points in Ylow/Ylup, while opt_inf searches for
# cubes that are fully dominated.
def multidim_search_deep_first_opt_inf(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

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

    # Upper and lower clausure
    ylow = []
    yup = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step - step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        # border = list(set(border).difference(set(slice_border)))
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        b0_list = p.map(pb0, zip(slice_border, y_list))
        b1_list = p.map(pb1, zip(slice_border, y_list))

        ylow.extend(b0_list)
        yup.extend(b1_list)

        vol_b0_list = p.imap_unordered(pvol, b0_list)
        vol_b1_list = p.imap_unordered(pvol, b1_list)

        vol_ylow += sum(vol_b0_list)
        vol_yup += sum(vol_b1_list)

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        # Every Border rectangle that is dominated by B1 is included in Yup
        ylow_candidates = [rect for rect in border if any(rect.dominates_rect(b0) for b0 in b0_list)]
        yup_candidates = [rect for rect in border if any(rect.is_dominated_by_rect(b1) for b1 in b1_list)]

        ylow.extend(ylow_candidates)
        yup.extend(yup_candidates)

        vol_ylow_opt_list = p.imap_unordered(pvol, ylow_candidates)
        vol_yup_opt_list = p.imap_unordered(pvol, yup_candidates)

        vol_ylow += sum(vol_ylow_opt_list)
        vol_yup += sum(vol_yup_opt_list)

        border -= ylow_candidates
        border -= yup_candidates
        ################################

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        ################################
        # Every Incomparable rectangle that dominates B0 is included in Ylow
        # Every Incomparable rectangle that is dominated by B1 is included in Yup
        ylow_candidates = [inc for inc in new_incomp_rects if any(inc.dominates_rect(b0) for b0 in ylow)]
        yup_candidates = [inc for inc in new_incomp_rects if any(inc.is_dominated_by_rect(b1) for b1 in yup)]

        ylow.extend(ylow_candidates)
        yup.extend(yup_candidates)

        vol_ylow_opt_list = p.imap_unordered(pvol, ylow_candidates)
        vol_yup_opt_list = p.imap_unordered(pvol, yup_candidates)

        vol_ylow += sum(vol_ylow_opt_list)
        vol_yup += sum(vol_yup_opt_list)

        new_incomp_rects = new_incomp_rects.difference(ylow_candidates)
        new_incomp_rects = new_incomp_rects.difference(yup_candidates)
        ################################

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


def multidim_search_deep_first_opt_0(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

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

    # Upper and lower clausure
    ylow = []
    yup = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        # border = list(set(border).difference(set(slice_border)))
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        b0_list = p.map(pb0, zip(slice_border, y_list))
        b1_list = p.map(pb1, zip(slice_border, y_list))

        ylow.extend(b0_list)
        yup.extend(b1_list)

        vol_b0_list = p.imap_unordered(pvol, b0_list)
        vol_b1_list = p.imap_unordered(pvol, b1_list)

        vol_ylow += sum(vol_b0_list)
        vol_yup += sum(vol_b1_list)

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)
