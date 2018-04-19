from ndtree import *
from search import *
from oracles import *
from oraclepoint import *
import __builtin__

import random
import os

import matplotlib.pyplot as plt

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


# Oracles and polynomial conditions
def testFileOracleRead():
    nfile = os.path.abspath("tests/Oracle/oracle.txt")
    nfile2 = os.path.abspath("tests/Oracle/oracle2.txt")
    nfile3 = os.path.abspath("tests/Oracle/oracle3.txt")

    # ftemp = open(nfile, 'wb')
    c1 = Condition('x', '>', '2')
    c2 = Condition('x', '>', '5')
    cl = ConditionList()
    cl.add(c1)
    cl.add(c2)
    # Condition
    c1.toFile(nfile, append=False, human_readable=True)
    c3 = Condition()
    c3.fromFile(nfile, human_readable=True)
    print('c3 ' + str(c3))

    # ConditionList
    cl.toFile(nfile2, append=False, human_readable=True)
    cl2 = ConditionList()
    cl2.fromFile(nfile2, human_readable=True)
    print('cl2 ' + str(cl2))

    # Oracle
    ora = Oracle()
    ora.add(cl, 1)
    ora.add(cl, 2)
    ora.toFile(nfile3, append=False, human_readable=True)
    ora2 = Oracle()
    ora2.fromFile(nfile3, human_readable=True)
    print('ora2 ' + str(ora2))


def testFileOracleNoRead():
    nfile = os.path.abspath("tests/Oracle/oracle.txt")
    nfile2 = os.path.abspath("tests/Oracle/oracle2.txt")
    nfile3 = os.path.abspath("tests/Oracle/oracle3.txt")

    # ftemp = open(nfile, 'wb')
    c1 = Condition('x', '>', '2')
    c2 = Condition('x', '>', '5')
    cl = ConditionList()
    cl.add(c1)
    cl.add(c2)

    # Condition
    print('c1 ' + str(c1))
    c1.toFile(nfile, append=False, human_readable=False)
    c3 = Condition()
    c3.fromFile(nfile, human_readable=False)
    print('c3 ' + str(c3))

    # ConditionList
    print('cl ' + str(cl))
    cl.toFile(nfile2, append=False, human_readable=False)
    cl2 = ConditionList()
    cl2.fromFile(nfile2, human_readable=False)
    print('cl2 ' + str(cl2))

    # Oracle
    ora = Oracle()
    ora.add(cl, 1)
    ora.add(cl, 2)
    ora.toFile(nfile3, append=False, human_readable=False)
    ora2 = Oracle()
    ora2.fromFile(nfile3, human_readable=False)
    print('ora2 ' + str(ora2))


def testFileOracle():
    nfile = os.path.abspath("tests/Oracle/oracle.txt")
    nfile2 = os.path.abspath("tests/Oracle/oracle2.txt")
    nfile3 = os.path.abspath("tests/Oracle/oracle3.txt")
    # ftemp = open(nfile, 'wb')

    c1 = Condition('x', '>', '2')
    c2 = Condition('x', '>', '5')
    cl = ConditionList()
    cl.add(c1)
    cl.add(c2)

    # Condition
    c1.toFile(nfile, append=False, human_readable=True)
    c3 = Condition()
    c3.fromFile(nfile, human_readable=True)
    print('c3 ' + str(c3))

    # ConditionList
    cl.toFile(nfile2, append=False, human_readable=True)
    cl2 = ConditionList()
    cl2.fromFile(nfile2, human_readable=True)
    print('cl2 ' + str(cl2))

    # Oracle
    ora = Oracle()
    ora.add(cl, 1)
    ora.add(cl, 2)
    ora.toFile(nfile3, append=False, human_readable=True)
    ora2 = Oracle()
    ora2.fromFile(nfile3, human_readable=True)
    print('ora2 ' + str(ora2))

    # Condition
    print('c1 ' + str(c1))
    c1.toFile(nfile, append=False, human_readable=False)
    c3 = Condition()
    c3.fromFile(nfile, human_readable=False)
    print('c3 ' + str(c3))

    # ConditionList
    print('cl ' + str(cl))
    cl.toFile(nfile2, append=False, human_readable=False)
    cl2 = ConditionList()
    cl2.fromFile(nfile2, human_readable=False)
    print('cl2 ' + str(cl2))

    # Oracle
    ora = Oracle()
    ora.add(cl, 1)
    ora.add(cl, 2)
    ora.toFile(nfile3, append=False, human_readable=False)
    ora2 = Oracle()
    ora2.fromFile(nfile3, human_readable=False)
    print('ora2 ' + str(ora2))


def testFileOraclePointRead(min_corner=0.0,
                            max_corner=1.0):
    nfile = os.path.abspath("tests/OraclePoint/oracle.txt")

    # Points
    def f(x):
        return 1 / x if x > 0.0 else 1000

    xs = np.arange(min_corner, max_corner, 0.1)
    ys = [f(x) for x in xs]

    # Oracle
    ora = OraclePoint()
    for x, y in zip(xs, ys):
        point = (x, y)
        ora.addPoint(point)
    print('ora ' + str(ora))
    print('ora rect' + str(ora.oracle.root.rect))
    ora.toFile(nfile, append=False, human_readable=True)

    ora2 = OraclePoint()
    ora2.fromFile(nfile, human_readable=True)
    print('ora2 ' + str(ora2))
    print('ora2 rect' + str(ora2.oracle.root.rect))


def testFileOraclePointNoRead(min_corner=0.0,
                              max_corner=1.0):
    nfile = os.path.abspath("tests/OraclePoint/oracle.txt")

    # Points
    def f(x):
        return 1 / x if x > 0.0 else 1000

    xs = np.arange(min_corner, max_corner, 0.1)
    ys = [f(x) for x in xs]

    # Oracle
    ora = OraclePoint()
    for x, y in zip(xs, ys):
        point = (x, y)
        ora.addPoint(point)
    print('ora ' + str(ora))
    ora.toFile(nfile, append=False, human_readable=False)

    ora2 = OraclePoint()
    ora2.fromFile(nfile, human_readable=False)
    print('ora2 ' + str(ora2))


def testInOutFileOraclePoint(infile=os.path.abspath("tests/OraclePoint/oracle2.txt"),
                                    outfile=os.path.abspath("tests/OraclePoint/oracle2_bin.txt")):

    def readTupleFile(nfile):
        mode = 'rb'
        finput = open(nfile, mode)

        setpoints = set()
        for i, line in enumerate(finput):
            line = line.replace('(', '')
            line = line.replace(')', '')
            line = line.split(',')
            point = tuple(float(pi) for pi in line)
            setpoints.add(point)
        return setpoints

    #ora2 = OraclePoint()
    ora2 = OraclePoint(5, 4)
    ora2.fromFile(infile, human_readable=True)
    ora2.toFile(outfile, human_readable=False)
    points = ora2.getPoints()

    #print('ora2 ' + str(ora2))
    print('ora2 rect' + str(ora2.oracle.root.rect))
    print('numPoints: ' + str(len(points)))

    x = [point[0] for point in points]
    y = [point[1] for point in points]

    rs = ResultSet()
    rs.toMatPlot(targetx=x, targety=y, blocking=True)

    originalPoints = readTupleFile(infile)

    x = [point[0] for point in originalPoints]
    y = [point[1] for point in originalPoints]

    rs.toMatPlot(targetx=x, targety=y, blocking=True)



def testMembershipCondition():
    c1 = Condition('x', '>', '2')
    c2 = Condition('x', '>', '5')
    cl1 = ConditionList()
    cl1.add(c1)
    f1 = cl1.membership()
    f1(0)
    f1(3)

    cl2 = ConditionList()
    cl2.add(c2)
    f2 = cl2.membership()
    f2(3)
    f2(6)

    # Oracle
    ora = Oracle()
    ora.add(cl1, 0)
    ora.add(cl2, 1)
    fora = ora.membership()
    fora((2, 5))
    fora((3, 5))
    fora((3, 6))


# Test 2-Dimensional Oracles
def test2D(min_cornerx=0.0,
           min_cornery=0.0,
           max_cornerx=1.0,
           max_cornery=1.0,
           nfile=os.path.abspath("tests/2D/test0.txt"),
           epsilon=EPS,
           delta=DELTA,
           verbose=False,
           blocking=False,
           sleep=0):
    minc = (min_cornerx, min_cornery)
    maxc = (max_cornerx, max_cornery)
    xyspace = Rectangle(minc, maxc)

    ora = Oracle()
    ora.fromFile(nfile, human_readable=True)
    fora = ora.membership()

    rs = multidim_search(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    rs.toMatPlot(blocking=True)
    # list_x = ora.list_n_points(npoints, 0)
    # list_y = ora.list_n_points(npoints, 1)
    # print(list_x)
    # print(list_y)
    # rs.toMatPlot(targetx=list_x, targety=list_y, blocking=True)
    return 0


# Auxiliar function for 3-Dimensional testing
def OracleTest(fora, rs, xpoint):
    test1 = fora(xpoint) and (rs.MemberYup(xpoint) or rs.MemberBorder(xpoint))
    test2 = (not fora(xpoint)) and (rs.MemberYlow(xpoint) or rs.MemberBorder(xpoint))
    if (test1 or test2):
        None
    else:
        print 'Warning! '
        print 'Testing ', str(xpoint)
        print ('(inYup, inYlow, inBorder): (%s, %s, %s)'
               % (str(rs.MemberYup(xpoint)), str(rs.MemberYlow(xpoint)), str(rs.MemberBorder(xpoint))))
        print 'Expecting '
        print ('(inYup, inYlow): (%s, %s)'
               % (str(fora(xpoint)), str(not fora(xpoint))))


# Test 3-Dimensional Oracles
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

    ora = Oracle()
    ora.fromFile(nfile, human_readable=True)
    fora = ora.membership()

    start = time.time()
    rs = multidim_search(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    end = time.time()
    time1 = end - start

    t1 = np.arange(min_cornerx, max_cornerx, 0.1)
    t2 = np.arange(min_cornery, max_cornery, 0.1)
    t3 = np.arange(min_cornerz, max_cornerz, 0.1)

    testYup = False
    testYlow = False
    testBorder = False

    nYup = 0
    nYlow = 0
    nBorder = 0

    print ('Starting tests\n')
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

                    OracleTest(fora, rs, xpoint)
    end = time.time()
    time2 = end - start

    vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
    print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
           % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total)),
    print 'Report Ylow: %s, %s' % (str(testYlow), str(nYlow))
    print 'Report Yup: %s, %s' % (str(testYup), str(nYup))
    print 'Report Border: %s, %s' % (str(testBorder), str(nBorder))
    print 'Time multidim search: ', str(time1)
    print 'Time tests: ', str(time2)
    return 0


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

    ora = Oracle()
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
        [OracleTest(fora, rs, point) for point in list_test_points]
        ##############
    end = time.time()
    time2 = end - start

    vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
    print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
           % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total)),
    print 'Report Ylow: %s' % (str(nYlow))
    print 'Report Yup: %s' % (str(nYup))
    print 'Report Border: %s' % (str(nBorder))
    print 'Time multidim search: ', str(time1)
    print 'Time tests: ', str(time2)
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

    rs.toMatPlot(targetx=t1, targety=f(t1), blocking=True)
    return 0


# Test ND-Tree structure
def testNDTree(min_corner=0.0,
               max_corner=1.0):
    def f1(x):
        return 1 / x if x > 0.0 else 1000

    def f2(x):
        return 0.1 + 1 / x if x > 0.0 else 1000

    def f3(x):
        return 0.2 + 1 / x if x > 0.0 else 1000

    xs = np.arange(min_corner, max_corner, 0.1)
    y1s = [f1(x) for x in xs]
    y2s = [f2(x) for x in xs]
    y3s = [f3(x) for x in xs]

    ndtree = NDTree()

    print('Round 0')
    for x, y in zip(xs, y3s):
        point = (x, y)
        # print ('Inserting %s into NDTree' % (str(point)))
        ndtree.update(point)
    print ('NDTree')
    print (str(ndtree))
    print ('Rectangle')
    print (ndtree.root.rect)
    # print ('NDTree %s' % (str(ndtree)))

    print('Round 1')
    for x, y in zip(xs, y3s):
        point = (x, y)
        # print ('Inserting %s into NDTree' % (str(point)))
        ndtree.update(point)
    print ('NDTree')
    print (str(ndtree))
    print ('Rectangle')
    print (ndtree.root.rect)
    # print ('NDTree %s' % (str(ndtree)))

    ndtree.report()

    # print('Round 2')
    # point = (xs[0],y1s[0])
    # ndtree.update(point)
    # print ('NDTree')
    # print (str(ndtree))

    # ndtree.report()

    print('Round 2')
    for x, y in zip(xs, y2s):
        point = (x, y)
        # print ('Inserting %s into NDTree' % (str(point)))
        ndtree.update(point)
    print ('NDTree')
    print (str(ndtree))
    print ('Rectangle')
    print (ndtree.root.rect)
    ##print ('NDTree %s' % (str(ndtree)))

    ndtree.report()

    print('Round 3')
    for x, y in zip(xs, y1s):
        point = (x, y)
        # print ('Inserting %s into NDTree' % (str(point)))
        ndtree.update(point)
    print ('NDTree')
    print (str(ndtree))
    print ('Rectangle')
    print (ndtree.root.rect)
    ##print ('NDTree %s' % (str(ndtree)))

    ndtree.report()


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

    t1 = np.arange(min_corner, max_corner, 0.1)
    t2 = np.arange(min_corner, max_corner, 0.1)

    testYup = False
    testYlow = False
    testBorder = False

    nYup = 0
    nYlow = 0
    nBorder = 0

    print ('Starting tests\n')
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

                OracleTest(fora, rs, xpoint)
    end = time.time()
    time2 = end - start

    vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
    print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
           % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total)),
    print 'Report Ylow: %s, %s' % (str(testYlow), str(nYlow))
    print 'Report Yup: %s, %s' % (str(testYup), str(nYup))
    print 'Report Border: %s, %s' % (str(testBorder), str(nBorder))
    print 'Time multidim search: ', str(time1)
    print 'Time tests: ', str(time2)
    return 0

def test2DOraclePoint(min_corner=0.0,
           max_corner=1.0,
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
    print 'Time reading Oracle: ', str(time0)

    points = ora.getPoints()
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    minx = __builtin__.min(xs)
    miny = __builtin__.min(ys)

    maxx = __builtin__.max(xs)
    maxy = __builtin__.max(ys)

    minc = (__builtin__.min(minx, min_corner), __builtin__.min(miny, min_corner))
    maxc = (__builtin__.max(maxx, max_corner), __builtin__.max(maxy, max_corner))
    xyspace = Rectangle(minc, maxc)

    fora = ora.membership()
    print ('Starting multidimensional search')
    start = time.time()
    rs = multidim_search(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
    end = time.time()
    time1 = end - start
    print 'Time multidim search: ', str(time1)

    rs.toMatPlot(targetx=xs, targety=ys, blocking=True)

    t1 = np.arange(min_corner, max_corner, 0.1)
    t2 = np.arange(min_corner, max_corner, 0.1)

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

                OracleTest(fora, rs, xpoint)
    end = time.time()
    time2 = end - start

    vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
    print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
           % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total)),
    print 'Report Ylow: %s, %s' % (str(testYlow), str(nYlow))
    print 'Report Yup: %s, %s' % (str(testYup), str(nYup))
    print 'Report Border: %s, %s' % (str(testBorder), str(nBorder))
    print 'Time tests: ', str(time2)
    return 0

# if __name__ == '__main__':
#    test1()
