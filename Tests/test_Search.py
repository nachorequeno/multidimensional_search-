import os
import random
import __builtin__
import itertools

import multiprocessing

# import ParetoLib.Search
# import ParetoLib.Oracle

from ParetoLib.Search.Search import *
from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *

EPS = 1e-5
DELTA = 1e-5


################
# Simple tests #
################

def testBinSearch(nfile=os.path.abspath("./Tests/Search/2D/test4.txt")):
    x = (0.0,) * 2
    y = (1.0,) * 2
    xy = Rectangle(x, y)

    ora = loadOracleFunction(nfile=nfile, human_readable=True)
    f = ora.membership()

    return search(xy.diagToSegment(), f)


def testMultiDimSearch(nfile=os.path.abspath("./Tests/Search/2D/test4.txt")):
    x = (0.0,) * 2
    y = (1.0,) * 2
    xyspace = Rectangle(x, y)

    ora = loadOracleFunction(nfile=nfile, human_readable=True)
    f = ora.membership()

    rs = multidim_search(xyspace, f)
    rs.toMatPlot2D()


#################
# Complex tests #
#################

# Auxiliar functions used in 2D, 3D and ND

# Loading Oracles
def loadOracleFunction(nfile, human_readable):
    print ('Creating OracleFunction')
    start = time.time()
    ora = OracleFunction()
    ora.fromFile(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    print ('Time reading OracleFunction: ', str(time0))
    return ora


def loadOraclePoint(nfile, human_readable):
    print ('Creating OraclePoint')
    start = time.time()
    ora = OraclePoint()
    ora.fromFile(nfile, human_readable=human_readable)
    end = time.time()
    time0 = end - start
    print ('Time reading OraclePoint: ', str(time0))
    return ora


# Creation of Spaces
def create2DSpace(minx, miny, maxx, maxy):
    print ('Creating Space')
    start = time.time()
    minc = (minx, miny)
    maxc = (maxx, maxy)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    print ('Time creating Space: ', str(time0))
    return xyspace


def create3DSpace(minx, miny, minz, maxx, maxy, maxz):
    print ('Creating Space')
    start = time.time()
    minc = (minx, miny, minz)
    maxc = (maxx, maxy, maxz)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    print ('Time creating Space: ', str(time0))
    return xyspace


def createNDSpace(*args):
    # args = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
    print ('Creating Space')
    start = time.time()
    minc = tuple(minx for minx, _ in args)
    maxc = tuple(maxx for _, maxx in args)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    print ('Time creating Space: ', str(time0))
    return xyspace


# Multidimensional search
def msearch(space,
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


#  Membership testing function used in verify2D, verify3D and verifyND
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


# Auxiliar function for reporting ND results
def verifyND(fora,
             rs,
             list_test_points,
             test=False):
    # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]
    nYup = 0
    nYlow = 0
    nBorder = 0

    print ('Starting tests\n')
    start = time.time()
    if test:
        f1 = lambda p: 1 if rs.MemberYup(p) else 0
        f2 = lambda p: 1 if rs.MemberYlow(p) else 0
        f3 = lambda p: 1 if rs.MemberBorder(p) else 0

        list_nYup = map(f1, list_test_points)
        list_nYlow = map(f2, list_test_points)
        list_nBorder = map(f3, list_test_points)

        nYup = sum(list_nYup)
        nYlow = sum(list_nYlow)
        nBorder = sum(list_nBorder)

        [closureMembershipTest(fora, rs, p) for p in list_test_points]

    end = time.time()
    time0 = end - start

    vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
    print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
           % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total)),
    print ('Report Ylow: %s' % (str(nYlow)))
    print ('Report Yup: %s' % (str(nYup)))
    print ('Report Border: %s' % (str(nBorder)))
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
    ora = loadOracleFunction(nfile, human_readable=True)
    fora = ora.membership()

    xyspace = create2DSpace(min_cornerx, min_cornery, max_cornerx, max_cornery)

    rs = msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

    n = int((max_cornerx - min_cornerx) / 0.1)
    points = rs.getPointsBorder(n)

    print("Points ", points)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True)
    verify2D(fora, rs, test, min_cornerx, min_cornery, max_cornerx, max_cornery)


def test3DOracleFunction(min_cornerx=0.0,
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
    ora = loadOracleFunction(nfile, human_readable=True)
    fora = ora.membership()

    xyspace = create3DSpace(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

    rs = msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

    n = int((max_cornerx - min_cornerx) / 0.1)
    points = rs.getPointsBorder(n)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]

    rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True)
    verify3D(fora, rs, test, min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)


def testNDOracleFunction(min_corner=0.0,
                         max_corner=1.0,
                         nfile=os.path.abspath("tests/3D/test4.txt"),
                         epsilon=EPS,
                         delta=DELTA,
                         verbose=False,
                         blocking=False,
                         test=False,
                         sleep=0):
    ora = loadOracleFunction(nfile, human_readable=True)
    fora = ora.membership()
    dim = ora.dim()

    minc = (min_corner,) * dim
    maxc = (max_corner,) * dim
    xyspace = Rectangle(minc, maxc)

    rs = msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

    t = np.arange(min_corner, max_corner, 0.1)
    # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]
    list_test_points = list(itertools.product(t, repeat=dim))

    verifyND(fora, rs, list_test_points, test)


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
    ora = loadOraclePoint(nfile, human_readable=False)
    fora = ora.membership()

    points = ora.getPoints()
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    minx = __builtin__.min(xs)
    miny = __builtin__.min(ys)

    maxx = __builtin__.max(xs)
    maxy = __builtin__.max(ys)

    xyspace = create2DSpace(__builtin__.min(minx, min_cornerx),
                            __builtin__.min(miny, min_cornery),
                            __builtin__.min(maxx, max_cornerx),
                            __builtin__.min(maxy, max_cornery))

    rs = msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True)
    verify2D(fora, rs, test, min_cornerx, min_cornery, max_cornerx, max_cornery)


def test3DOraclePoint(min_cornerx=0.0,
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
    ora = loadOraclePoint(nfile, human_readable=False)
    fora = ora.membership()

    points = ora.getPoints()
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]

    minx = __builtin__.min(xs)
    miny = __builtin__.min(ys)
    minz = __builtin__.min(zs)

    maxx = __builtin__.max(xs)
    maxy = __builtin__.max(ys)
    maxz = __builtin__.max(zs)

    xyspace = create3DSpace(__builtin__.min(minx, min_cornerx),
                            __builtin__.min(miny, min_cornery),
                            __builtin__.min(minz, min_cornerz),
                            __builtin__.min(maxx, max_cornerx),
                            __builtin__.min(maxy, max_cornery),
                            __builtin__.min(maxz, max_cornerz))

    rs = msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True)
    verify3D(fora, rs, test, min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)


def testNDOraclePoint(nfile=os.path.abspath("tests/3D/test4.txt"),
                      epsilon=EPS,
                      delta=DELTA,
                      verbose=False,
                      blocking=False,
                      test=False,
                      sleep=0):
    ora = loadOraclePoint(nfile, human_readable=False)
    fora = ora.membership()
    dim = ora.dim()

    points = ora.getPoints()
    sorted_points = sorted(points)

    minc = sorted_points[0]
    maxc = sorted_points.pop()
    xyspace = Rectangle(minc, maxc)

    rs = msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

    t = np.arange(minc, maxc, 0.1)
    # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]
    list_test_points = list(itertools.product(t, repeat=dim))

    verifyND(fora, rs, list_test_points, test)


# Test OraclePoint
def test2DOraclePoint_1X(min_cornerx=0.0,
                         min_cornery=0.0,
                         max_cornerx=1.0,
                         max_cornery=1.0,
                         epsilon=EPS,
                         delta=DELTA,
                         verbose=False,
                         blocking=False,
                         test=False,
                         sleep=0):
    minc = (min_cornerx, min_cornery)
    maxc = (max_cornerx, max_cornery)
    xyspace = Rectangle(minc, maxc)

    def f1(x):
        return 1 / x if x > 0.0 else 110

    def f2(x):
        return 0.1 + 1 / x if x > 0.0 else 110

    def f3(x):
        return 0.2 + 1 / x if x > 0.0 else 110

    xs = np.arange(min_cornerx, max_cornerx, 0.01)
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
    rs = msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    rs.toMatPlot2D(targetx=list(xs), targety=y1s, blocking=True)
    verify2D(fora, rs, test, min_cornerx, min_cornery, max_cornerx, max_cornery)


if __name__ == '__main__':
    # local_path = './Search'
    # test_2D = local_path + "/2D/test%s.txt"
    ##nfile=os.path.abspath()
    # arr_txt = [x for x in os.listdir('.') if x.endswith(".txt")]

    this_dir = os.getcwd()
    test_2D_dir = this_dir + '/Search/2D'
    test_3D_dir = this_dir + '/Search/3D'
    test_ND_dir = this_dir + '/Search/ND'

    files_path = [os.path.abspath(x) for x in os.listdir(test_2D_dir)]
    test_2D_txt = [x for x in files_path if x.endswith(".txt")]

    for test in test_2D_txt:
        test2DOracleFunction(min_cornerx=0.0,
                             min_cornery=0.0,
                             max_cornerx=1.0,
                             max_cornery=1.0,
                             epsilon=EPS,
                             delta=DELTA,
                             verbose=False,
                             blocking=False,
                             test=False,
                             sleep=0,
                             nfile=test)

    files_path = [os.path.abspath(x) for x in os.listdir(test_3D_dir)]
    test_3D_txt = [x for x in files_path if x.endswith(".txt")]

    for test in test_3D_txt:
        test2DOracleFunction(min_cornerx=0.0,
                             min_cornery=0.0,
                             max_cornerx=1.0,
                             max_cornery=1.0,
                             epsilon=EPS,
                             delta=DELTA,
                             verbose=False,
                             blocking=False,
                             test=False,
                             sleep=0,
                             nfile=test)

    files_path = [os.path.abspath(x) for x in os.listdir(test_ND_dir)]
    test_ND_txt = [x for x in files_path if x.endswith(".txt")]

    for test in test_ND_txt:
        testNDOracleFunction(min_corner=0.0,
                             max_corner=1.0,
                             epsilon=EPS,
                             delta=DELTA,
                             verbose=False,
                             blocking=False,
                             test=False,
                             sleep=0,
                             nfile=test)

    # filename_list = ["./Tests/Search/ND/test-%sd.txt" % i for i in range(2, 11)]
    # filename_list = ["./Tests/Search/ND/test-%sd.txt" % i for i in range(2, 3)]
    # [testNDOracleFunction(min_corner=0.0,
    #                     max_corner=1.0,
    #                     epsilon=0.01,
    #                     delta=0.01,
    #                     verbose=False,
    #                     blocking=False,
    #                     test=False,
    #                     sleep=0,
    #                     nfile=os.path.abspath(filename)) for filename in filename_list]
