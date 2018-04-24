import os
import random
import __builtin__

import multiprocessing

# import Pareto.Search
# import Pareto.Oracle

from Pareto.Search.Search import *
from Pareto.Oracle.OracleFunction import *
from Pareto.Oracle.OraclePoint import *

EPS = 1e-5
DELTA = 1e-5


# Simple tests
def testBinSearch():
    x = (0.0,) * 2
    y = (1.0,) * 2
    xy = Segment(x, y)

    t1 = (0.2, 0.8)
    t2 = (0.8, 0.2)
    f = staircase_oracle(t1, t2)

    return search(xy, f)


def testMultiDimSearch():
    x = (0.0,) * 2
    y = (1.0,) * 2
    xyspace = Rectangle(x, y)

    t1 = (0.2, 0.8)
    t2 = (0.8, 0.2)
    f = staircase_oracle(t1, t2)

    rs = multidim_search(xyspace, f)
    rs.toMatPlot()
    return 0

# Auxiliar functions used in 2D and 3D
# Multidimensional search
def search(space,
           fora,
           epsilon=EPS,
           delta=DELTA,
           verbose=False,
           blocking=False,
           sleep=0):
    print ('Starting multidimensional search')
    start = time.time()
    rs = multidim_search(space, fora, epsilon, delta, verbose, blocking, sleep)
    end = time.time()
    time0 = end - start
    print ('Time multidim search: ', str(time0))
    return rs

#  Membership testing function used in verify2D and verify3D
def closureMembershipTest(fora, rs, xpoint):
    test1 = fora(xpoint) and (rs.MemberYup(xpoint) or rs.MemberBorder(xpoint))
    test2 = (not fora(xpoint)) and (rs.MemberYlow(xpoint) or rs.MemberBorder(xpoint))
    if (test1 or test2):
        None
    else:
        print ('Warning! ')
        print ('Testing ', str(xpoint))
        print ('(inYup, inYlow, inBorder): (%s, %s, %s)'
               % (str(rs.MemberYup(xpoint)), str(rs.MemberYlow(xpoint)), str(rs.MemberBorder(xpoint))))
        print ('Expecting ')
        print ('(inYup, inYlow): (%s, %s)'
               % (str(fora(xpoint)), str(not fora(xpoint))))

# Test 2D
# Auxiliar function for reporting 2D results
def verify2D(fora,
           rs,
           test=False,
           min_cornerx=0.0,
           min_cornery=0.0,
           max_cornerx=1.0,
           max_cornery=1.0):
    t1 = np.arange(min_cornerx, max_cornerx, 0.1)
    t2 = np.arange(min_cornery, max_cornery, 0.1)

    testYup = False
    testYlow = False
    testBorder = False

    nYup = 0
    nYlow = 0
    nBorder = 0

    print ('Starting tests')
    start = time.time()
    if test:
        for t1p in t1:
            for t2p in t2:
                xpoint = (t1p, t2p)
                testYup = testYup or rs.MemberYup(xpoint)
                testYlow = testYlow or rs.MemberYlow(xpoint)
                testBorder = testBorder or rs.MemberBorder(xpoint)

                nYup = nYup + 1 if rs.MemberYup(xpoint) else nYup
                nYlow = nYlow + 1 if rs.MemberYlow(xpoint) else nYlow
                nBorder = nBorder + 1 if rs.MemberBorder(xpoint) else nBorder

                closureMembershipTest(fora, rs, xpoint)
    end = time.time()
    time0 = end - start

    vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
    print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
           % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total))
    print ('Report Ylow: %s, %s' % (str(testYlow), str(nYlow)))
    print ('Report Yup: %s, %s' % (str(testYup), str(nYup)))
    print ('Report Border: %s, %s' % (str(testBorder), str(nBorder)))
    print ('Time tests: ', str(time0))


# OracleFunction
def test2DOracleFunction(min_cornerx=0.0,
           min_cornery=0.0,
           max_cornerx=1.0,
           max_cornery=1.0,
           nfile=os.path.abspath("tests/2D/test0.txt"),
           epsilon=EPS,
           delta=DELTA,
           verbose=False,
           blocking=False,
           test=False,
           sleep=0):
    minc = (min_cornerx, min_cornery)
    maxc = (max_cornerx, max_cornery)
    xyspace = Rectangle(minc, maxc)

    ora = OracleFunction()
    ora.fromFile(nfile, human_readable=True)
    fora = ora.membership()

    rs = multidim_search(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    rs.toMatPlot(blocking=True)
    # list_x = ora.list_n_points(npoints, 0)
    # list_y = ora.list_n_points(npoints, 1)
    # rs.toMatPlot(targetx=list_x, targety=list_y, blocking=True)
    verify2D(fora, rs, test, min_cornerx, min_cornery, max_cornerx, max_cornery)

# OraclePoint
def test2DOraclePoint(min_cornerx=0.0,
           min_cornery=0.0,
           max_cornerx=1.0,
           max_cornery=1.0,
           nfile=os.path.abspath("tests/OraclePoint/oracle4_xy_bin.txt"),
           epsilon=EPS,
           delta=DELTA,
           verbose=False,
           blocking=False,
           test=False,
           sleep=0):

    print ('Creating OraclePoint')
    start = time.time()
    ora = OraclePoint()
    ora.fromFile(nfile, human_readable=False)
    end = time.time()
    time0 = end - start
    print ('Time reading OraclePoint: ', str(time0))

    points = ora.getPoints()
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    minx = __builtin__.min(xs)
    miny = __builtin__.min(ys)

    maxx = __builtin__.max(xs)
    maxy = __builtin__.max(ys)

    print ('Creating Space')
    start = time.time()
    minc = (__builtin__.min(minx, min_cornerx), __builtin__.min(miny, min_cornery))
    maxc = (__builtin__.max(maxx, max_cornerx), __builtin__.max(maxy, max_cornery))
    xyspace = Rectangle(minc, maxc)
    time0 = end - start
    print ('Time creating Space: ', str(time0))

    fora = ora.membership()
    rs = search(xyspace, fora, epsilon, delta, verbose, blocking, test, sleep) *****

    rs.toMatPlot(targetx=xs, targety=ys, blocking=True)
    verify2D(fora, rs, test, min_cornerx, min_cornery, max_cornerx, max_cornery)


# Test 3D
# Auxiliar function for reporting 3D results
def verify3D(fora,
             rs,
             test=False,
             min_cornerx=0.0,
             min_cornery=0.0,
             min_cornerz=0.0,
             max_cornerx=1.0,
             max_cornery=1.0,
             max_cornerz=1.0):
    t1 = np.arange(min_cornerx, max_cornerx, 0.1)
    t2 = np.arange(min_cornery, max_cornery, 0.1)
    t3 = np.arange(min_cornerz, max_cornerz, 0.1)

    testYup = False
    testYlow = False
    testBorder = False

    nYup = 0
    nYlow = 0
    nBorder = 0

    print ('Starting tests')
    start = time.time()
    if test:
        for t1p in t1:
            for t2p in t2:
                for t3p in t3:
                    xpoint = (t1p, t2p, t3p)
                    testYup = testYup or rs.MemberYup(xpoint)
                    testYlow = testYlow or rs.MemberYlow(xpoint)
                    testBorder = testBorder or rs.MemberBorder(xpoint)

                    nYup = nYup + 1 if rs.MemberYup(xpoint) else nYup
                    nYlow = nYlow + 1 if rs.MemberYlow(xpoint) else nYlow
                    nBorder = nBorder + 1 if rs.MemberBorder(xpoint) else nBorder

                    closureMembershipTest(fora, rs, xpoint)
    end = time.time()
    time0 = end - start

    vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
    print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
           % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total))
    print ('Report Ylow: %s, %s' % (str(testYlow), str(nYlow)))
    print ('Report Yup: %s, %s' % (str(testYup), str(nYup)))
    print ('Report Border: %s, %s' % (str(testBorder), str(nBorder)))
    print ('Time tests: ', str(time0))


def test3D(min_cornerx=0.0,
           min_cornery=0.0,
           min_cornerz=0.0,
           max_cornerx=1.0,
           max_cornery=1.0,
           max_cornerz=1.0,
           nfile=os.path.abspath("tests/3D/test4.txt"),
           epsilon=EPS,
           delta=DELTA,
           verbose=False,
           blocking=False,
           test=False,
           sleep=0):
    minc = (min_cornerx, min_cornery, min_cornerz)
    maxc = (max_cornerx, max_cornery, max_cornerz)
    xyspace = Rectangle(minc, maxc)

    ora = OracleFunction()
    ora.fromFile(nfile, human_readable=True)
    fora = ora.membership()

    start = time.time()
    rs = multidim_search(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    end = time.time()
    time1 = end - start
    print ('Time multidim search: ', str(time1))

    #
    rs.toMatPlot3D(blocking=True)
    #
    verify3D(fora, rs, test, min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)


def test3D_map(min_cornerx=0.0,
               min_cornery=0.0,
               min_cornerz=0.0,
               max_cornerx=1.0,
               max_cornery=1.0,
               max_cornerz=1.0,
               nfile=os.path.abspath("tests/3D/test4.txt"),
               epsilon=EPS,
               delta=DELTA,
               verbose=False,
               blocking=False,
               test=False,
               sleep=0):
    minc = (min_cornerx, min_cornery, min_cornerz)
    maxc = (max_cornerx, max_cornery, max_cornerz)
    xyspace = Rectangle(minc, maxc)

    ora = OracleFunction()
    ora.fromFile(nfile, human_readable=True)
    fora = ora.membership()

    start = time.time()
    rs = multidim_search(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    end = time.time()
    time1 = end - start

    t1 = np.arange(min_cornerx, max_cornerx, 0.1)
    t2 = np.arange(min_cornery, max_cornery, 0.1)
    t3 = np.arange(min_cornerz, max_cornerz, 0.1)

    # testYup = False
    # testYlow = False
    # testBorder = False

    nYup = 0
    nYlow = 0
    nBorder = 0

    print ('Starting tests\n')
    start = time.time()
    if test:
        list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]

        ##############
        # list_test_Yup = map(rs.MemberYup, list_test_points)
        # list_test_Ylow = map(rs.MemberYlow, list_test_points)
        # list_test_Border = map(rs.MemberBorder, list_test_points)

        # testYup = reduce(lambda i, j: i or j, list_test_Yup)
        # testYlow = reduce(lambda i, j: i or j, list_test_Ylow)
        # testBorder = reduce(lambda i, j: i or j, list_test_Border)
        ##############

        ##############
        print ('Phase 1\n', time.time())
        f1 = lambda point: 1 if rs.MemberYup(point) else 0
        f2 = lambda point: 1 if rs.MemberYlow(point) else 0
        f3 = lambda point: 1 if rs.MemberBorder(point) else 0

        list_nYup = map(f1, list_test_points)
        list_nYlow = map(f2, list_test_points)
        list_nBorder = map(f3, list_test_points)

        nYup = reduce(lambda i, j: i + j, list_nYup)
        nYlow = reduce(lambda i, j: i + j, list_nYlow)
        nBorder = reduce(lambda i, j: i + j, list_nBorder)
        ##############

        ##############
        print ('Phase 2\n', time.time())
        [closureMembershipTest(fora, rs, point) for point in list_test_points]
        ##############
    end = time.time()
    time2 = end - start

    vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
    print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
           % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total)),
    print ( 'Report Ylow: %s' % (str(nYlow)) )
    print ( 'Report Yup: %s' % (str(nYup)) )
    print ( 'Report Border: %s' % (str(nBorder)) )
    print ( 'Time multidim search: ', str(time1) )
    print ( 'Time tests: ', str(time2) )
    return 0


# Test N-Dimensional Oracles
def testNdim(min_corner=0.0,
             max_corner=1.0,
             nfile=os.path.abspath("tests/2D/test0.txt"),
             npoints=50,
             dim=2,
             epsilon=EPS,
             delta=DELTA,
             verbose=False,
             blocking=False,
             sleep=0):
    minc = (min_corner,) * dim
    maxc = (max_corner,) * dim
    xyspace = Rectangle(minc, maxc)

    ora = Oracle()
    ora.fromFile(nfile, human_readable=True)
    fora = ora.membership()

    rs = multidim_search(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

    # list_x = ora.list_n_points(npoints, 0)
    # list_y = ora.list_n_points(npoints, 1)
    # print(list_x)
    # print(list_y)
    # rs.toMatPlot(targetx=list_x, targety=list_y, blocking=True)
    # rs.toMatPlot(blocking=blocking, sec=sleep)

    def f(t):
        return [x * x for x in t]

    # t1 = np.arange(min_corner, max_corner, 0.1)
    t1 = np.arange(0, 2, 0.1)

    rs.toMatPlot(targetx=list(t1), targety=f(t1), blocking=True)
    return 0


# Test OraclePoint
def test2DOraclePoint_1X(min_corner=0.0,
           max_corner=1.0,
           epsilon=EPS,
           delta=DELTA,
           verbose=False,
           blocking=False,
           test=False,
           sleep=0):
    minc = (min_corner, min_corner)
    maxc = (max_corner, max_corner)
    xyspace = Rectangle(minc, maxc)

    def f1(x):
        return 1 / x if x > 0.0 else 1000

    def f2(x):
        return 0.1 + 1 / x if x > 0.0 else 1000

    def f3(x):
        return 0.2 + 1 / x if x > 0.0 else 1000

    xs = np.arange(min_corner, max_corner, 0.01)
    y1s = [f1(x) for x in xs]
    y2s = [f2(x) for x in xs]
    y3s = [f3(x) for x in xs]

    print ('Creating OraclePoint\n')
    ora = OraclePoint()
    for x, y in zip(xs, y3s):
        point = (x, y)
        print('Adding ', point)
        ora.addPoint(point)

    print ('End step 1\n')

    for x, y in zip(xs, y2s):
        point = (x, y)
        print('Adding ', point)
        ora.addPoint(point)

    print ('End step 2\n')

    for x, y in zip(xs, y1s):
        point = (x, y)
        print('Adding ', point)
        ora.addPoint(point)

    print ('End step 3\n')
    print ('OraclePoint \n')
    print(str(ora))

    fora = ora.membership()
    print ('Starting multidimensional search\n')
    start = time.time()
    rs = multidim_search(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    end = time.time()
    time1 = end - start

    rs.toMatPlot(targetx=list(xs), targety=y1s, blocking=True)
    verify3D(fora, rs, test, min_cornerx, min_cornery, max_cornerx, max_cornery)



if __name__ == '__main__':
    test2DOracleFunction(min_cornerx=0.0,
                         min_cornery=0.0,
                         max_cornerx=1.0,
                         max_cornery=1.0,
                         nfile=os.path.abspath("tests/2D/test0.txt"),
                         epsilon=EPS,
                         delta=DELTA,
                         verbose=False,
                         blocking=False,
                         test=False,
                         sleep=0)
