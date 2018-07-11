from ParetoLib.Search.SeqSearch import *
from ParetoLib.Search.ParSearch import *

from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *
from ParetoLib.Oracle.OracleSTL import *


# from ParetoLib.Search.CommonSearch import *
# import ParetoLib.Search.SeqSearch as SeqSearch
# import ParetoLib.Search.ParSearch as ParSearch

# Auxiliar functions used in 2D, 3D and ND
# Creation of Spaces
def create_2D_space(minx, miny, maxx, maxy):
    print('Creating Space')
    start = time.time()
    minc = (minx, miny)
    maxc = (maxx, maxy)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    print('Time creating Space: {0}'.format(str(time0)))
    return xyspace


def create_3D_space(minx, miny, minz, maxx, maxy, maxz):
    print('Creating Space')
    start = time.time()
    minc = (minx, miny, minz)
    maxc = (maxx, maxy, maxz)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    print('Time creating Space: {0}'.format(str(time0)))
    return xyspace


def create_ND_space(*args):
    # args = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
    print('Creating Space')
    start = time.time()
    minc = tuple(minx for minx, _ in args)
    maxc = tuple(maxx for _, maxx in args)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    print('Time creating Space: {0}'.format(str(time0)))
    return xyspace


def load_OracleFunction(nfile,
                        human_readable=True):
    # type: (str, bool) -> OracleFunction
    print('Creating OracleFunction')
    start = time.time()
    ora = OracleFunction()
    ora.from_file(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    print('Time reading OracleFunction: {0}'.format(str(time0)))
    return ora


def load_OraclePoint(nfile,
                     human_readable=True):
    # type: (str, bool) -> OraclePoint
    print('Creating OraclePoint')
    start = time.time()
    ora = OraclePoint()
    ora.from_file(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    print('Time reading OraclePoint: {0}'.format(str(time0)))
    return ora


def load_OracleSTL(nfile,
                   human_readable=True):
    # type: (str, bool) -> OracleSTL
    print('Creating OracleSTL')
    start = time.time()
    ora = OracleSTL()
    ora.from_file(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    print('Time reading OracleSTL: {0}'.format(str(time0)))
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
             sleep=0.0,
             opt_level=2,
             parallel=False,
             logging=True):
    # type: (Oracle, float, float, float, float, float, float, int, bool, float, int, bool, bool) -> ResultSet
    xyspace = create_2D_space(min_cornerx, min_cornery, max_cornerx, max_cornery)
    if parallel:
        rs = ParetoLib.Search.ParSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                                        blocking, sleep, opt_level, logging)
    else:
        rs = ParetoLib.Search.SeqSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                                        blocking, sleep, opt_level, logging)
    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    # n = int((max_cornerx - min_cornerx) / 0.1)
    # points = rs.get_points_border(n)

    # print('Points ', points)
    # xs = [point[0] for point in points]
    # ys = [point[1] for point in points]

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
             parallel=False,
             logging=True):
    # type: (Oracle, float, float, float, float, float, float, float, float, int, bool, float, int, bool, bool) -> ResultSet
    xyspace = create_3D_space(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

    if parallel:
        rs = ParetoLib.Search.ParSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                                        blocking, sleep, opt_level, logging)
    else:
        rs = ParetoLib.Search.SeqSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                                        blocking, sleep, opt_level, logging)
    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    # n = int((max_cornerx - min_cornerx) / 0.1)
    # points = rs.get_points_border(n)

    # print('Points ', points)
    # xs = [point[0] for point in points]
    # ys = [point[1] for point in points]
    # zs = [point[2] for point in points]

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
             parallel=False,
             logging=True):
    # type: (Oracle, float, float, float, float, int, bool, float, int, bool, bool) -> ResultSet
    d = ora.dim()

    minc = (min_corner,) * d
    maxc = (max_corner,) * d
    xyspace = Rectangle(minc, maxc)

    if parallel:
        rs = ParetoLib.Search.ParSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                                        blocking, sleep, opt_level, logging)
    else:
        rs = ParetoLib.Search.SeqSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                                        blocking, sleep, opt_level, logging)
    rs.simplify()
    return rs
