# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Search.

This module encapsulates the complexity of the learning process in
three functions (i.e., Search2D, Search3D and SearchND) depending on
the dimension of the space X. Those functions call to the algorithm
that implements the multidimensional search of the Pareto front.

The learning algorithm is compatible for any dimension N, and for any
Oracle defined according to the template ParetoLib.Oracle.Oracle.

The input parameters of the learning process are the following:
- xspace: the N-dimensional space that contains the upper and lower closures,
represented by a list of minimum and maximum possible values for each dimension
 (i.e., min_cornerx, max_cornerx, etc.).
- oracle: the external knowledge repository that guides the learning process.
- epsilon: a real representing the maximum desired distance between a point x
of the space and a point y of the Pareto front.
- delta: a real representing the maximum area/volume contained in the border
 that separates the upper and lower closures; delta is used as a stopping criterion
 for the learning algorithm (sum(volume(cube) for all cube in border) < delta).
- max_step: the maximum number of cubes in the border that the learning algorithm
will analyze, in case of the stopping condition *delta* is not reached yet.
- sleep: time in seconds that each intermediate 2D/3D graphic must be shown in the screen
(i.e, 0 for not showing intermediate results).
- blocking: boolean that specifies if the intermediate 2D/3D graphics must be explicitly
 closed by the user, or they are automatically closed after *sleep* seconds.
- simplify: boolean that specifies if the number of cubes in the 2D/3D graphics must
be minimized.
- opt_level: an integer specifying which version of the learning algorithm to use
 (i.e., 0, 1 or 2; use 2 for fast convergence).
- parallel: boolean that specifies if the user desire to take advantage of the
multithreading capabilities of the computer.
- logging: boolean that specifies if the algorithm must print traces for
debugging options.


As a result, the function returns an object of the class ResultSet with the distribution
of the space X in three subspaces: a lower closure, an upper closure and a border which
 contains the Pareto front.
"""
import time

from ParetoLib.Geometry.Rectangle import Rectangle

import ParetoLib.Search.SeqSearch as SeqSearch
import ParetoLib.Search.ParSearch as ParSearch
import ParetoLib.Search as RootSearch

from ParetoLib.Search.CommonSearch import EPS, DELTA, STEPS
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Oracle.Oracle import Oracle


# Auxiliar functions used in 2D, 3D and ND
# Creation of Spaces
def create_2D_space(minx, miny, maxx, maxy):
    # type: (float, float, float, float) -> Rectangle
    RootSearch.logger.debug('Creating Space')
    start = time.time()
    minc = (minx, miny)
    maxc = (maxx, maxy)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    RootSearch.logger.debug('Time creating Space: {0}'.format(str(time0)))
    return xyspace


def create_3D_space(minx, miny, minz, maxx, maxy, maxz):
    # type: (float, float, float, float, float, float) -> Rectangle
    RootSearch.logger.debug('Creating Space')
    start = time.time()
    minc = (minx, miny, minz)
    maxc = (maxx, maxy, maxz)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    RootSearch.logger.debug('Time creating Space: {0}'.format(str(time0)))
    return xyspace


#def create_ND_space(*args):
def create_ND_space(args):
    # type: (iter) -> Rectangle
    # args = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
    RootSearch.logger.debug('Creating Space')
    start = time.time()
    minc = tuple(minx for minx, _ in args)
    maxc = tuple(maxx for _, maxx in args)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    RootSearch.logger.debug('Time creating Space: {0}'.format(str(time0)))
    return xyspace

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
             parallel=False,
             logging=True,
             simplify=True):
    # type: (Oracle, float, float, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    xyspace = create_2D_space(min_cornerx, min_cornery, max_cornerx, max_cornery)
    yup = []
    ylow = []
    border = []
    if parallel:
        rs = ParSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    # n = int((max_cornerx - min_cornerx) / 0.1)
    # points = rs.get_points_border(n)

    # print('Points ', points)
    # xs = [point[0] for point in points]
    # ys = [point[1] for point in points]

    if simplify:
        rs.simplify()
        rs.fusion()

    # rs.plot_2D(targetx=xs, targety=ys, blocking=True, var_names=ora.get_var_names())
    # rs.plot_2D_light(targetx=xs, targety=ys, blocking=True, var_names=ora.get_var_names())
    rs.plot_2D_light(blocking=True, var_names=ora.get_var_names())
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
             parallel=False,
             logging=True,
             simplify=True):
    # type: (Oracle, float, float, float, float, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    xyspace = create_3D_space(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)
    yup = []
    ylow = []
    border = []
    if parallel:
        rs = ParSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    # n = int((max_cornerx - min_cornerx) / 0.1)
    # points = rs.get_points_border(n)

    # print('Points ', points)
    # xs = [point[0] for point in points]
    # ys = [point[1] for point in points]
    # zs = [point[2] for point in points]

    if simplify:
        rs.simplify()
        rs.fusion()

    # rs.plot_3D(targetx=xs, targety=ys, targetz=zs, blocking=True, var_names=ora.get_var_names())
    # rs.plot_3D_light(targetx=xs, targety=ys, targetz=zs, blocking=True, var_names=ora.get_var_names())
    rs.plot_3D_light(blocking=True, var_names=ora.get_var_names())
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
             parallel=False,
             logging=True,
             simplify=True):
    # type: (Oracle, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    d = ora.dim()

    minc = (min_corner,) * d
    maxc = (max_corner,) * d
    xyspace = Rectangle(minc, maxc)
    yup = []
    ylow = []
    border = []
    if parallel:
        rs = ParSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    if simplify:
        rs.simplify()
        rs.fusion()
    return rs


def SearchND_2(ora,
               list_intervals,
               epsilon=EPS,
               delta=DELTA,
               max_step=STEPS,
               blocking=False,
               sleep=0.0,
               opt_level=2,
               parallel=False,
               logging=True,
               simplify=True):
    # type: (Oracle, list, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet

    # list_intervals = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
    xyspace = create_ND_space(list_intervals)
    yup = []
    ylow = []
    border = []
    if parallel:
        rs = ParSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    if simplify:
        rs.simplify()
        rs.fusion()
    return rs


def RestartSearch(prev_rs,
               ora,
               epsilon=EPS,
               delta=DELTA,
               max_step=STEPS,
               blocking=False,
               sleep=0.0,
               opt_level=2,
               parallel=False,
               logging=True,
               simplify=True):
    # type: (ResultSet, Oracle, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet

    xyspace = prev_rs.xspace
    yup = prev_rs.yup
    ylow = prev_rs.ylow
    border = prev_rs.border
    if parallel:
        rs = ParSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, yup, ylow, border, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    if simplify:
        rs.simplify()
        rs.fusion()
    return rs