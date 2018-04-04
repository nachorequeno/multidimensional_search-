from search import *
from oracles import *
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

    #Oracle
    ora = Oracle()
    ora.add(cl, 1)
    ora.add(cl, 2)
    ora.toFile(nfile3, append=False, human_readable=False)
    ora2 = Oracle()
    ora2.fromFile(nfile3, human_readable=False)
    print('ora2 ' + str(ora2))


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
    fora((2,5))
    fora((3,5))
    fora((3,6))

# Test 2-Dimensional Oracles
def test2D(min_cornerx = 0.0,
          min_cornery = 0.0,
          max_cornerx = 1.0,
          max_cornery = 1.0,
          nfile=os.path.abspath("tests/2D/test0.txt"),
          npoints=50,
          epsilon = EPS,
          delta = DELTA,
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
    #list_x = ora.list_n_points(npoints, 0)
    #list_y = ora.list_n_points(npoints, 1)
    #print(list_x)
    #print(list_y)
    #rs.toMatPlot(targetx=list_x, targety=list_y, blocking=True)
    return 0

# Test 3-Dimensional Oracles
def test3D(min_cornerx=0.0,
           min_cornery=0.0,
           min_cornerz=0.0,
           max_cornerx=1.0,
           max_cornery=1.0,
           max_cornerz=1.0,
           nfile=os.path.abspath("tests/3D/test4.txt"),
           npoints=50,
           epsilon=EPS,
           delta=DELTA,
           verbose=False,
           blocking=False,
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

    start = time.time()
    for t1p in t1:
        for t2p in t2:
            for t3p in t3:
                xpoint = (t1p, t2p, t3p)
                testYup = testYup or rs.MemberYup(xpoint)
                testYlow = testYlow or rs.MemberYlow(xpoint)
                testBorder = testBorder or rs.MemberBorder(xpoint)

                test1 = fora(xpoint) and (rs.MemberYup(xpoint) or rs.MemberBorder(xpoint))
                test2 = (not fora(xpoint)) and (rs.MemberYlow(xpoint) or rs.MemberBorder(xpoint))

                nYup = nYup + 1 if rs.MemberYup(xpoint) else nYup
                nYlow = nYlow + 1 if rs.MemberYlow(xpoint) else nYlow
                nBorder = nBorder + 1 if rs.MemberBorder(xpoint) else nBorder

                if (test1 or test2):
                    None
                else:
                    print 'Warning! '
                    print 'Testing ', str(xpoint)
                    print ('(inYup, inYlow, inBorder): (%s, %s, %s)'
                                % (str(rs.MemberYup(xpoint)), str(rs.MemberYlow(xpoint)), str(rs.MemberBorder(xpoint))) )
                    print 'Expecting '
                    print ('(inYup, inYlow): (%s, %s)'
                                % (str(fora(xpoint)), str(not fora(xpoint))))
    end = time.time()
    time2 = end - start

    print ('Volume report : (%s, %s, %s)\n'
                    % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder())) ),
    print 'Report Ylow: %s, %s' % (str(testYlow), str(nYlow))
    print 'Report Yup: %s, %s' % (str(testYup), str(nYup))
    print 'Report Border: %s, %s' % (str(testBorder), str(nBorder))
    print 'Time multidim search: ', str(time1)
    print 'Time tests: ', str(time2)
    return 0


# Test N-Dimensional Oracles
def testNdim(min_corner = 0.0,
          max_corner = 1.0,
          nfile=os.path.abspath("tests/2D/test0.txt"),
          npoints=50,
          dim = 2,
          epsilon = EPS,
          delta = DELTA,
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
    #list_x = ora.list_n_points(npoints, 0)
    #list_y = ora.list_n_points(npoints, 1)
    #print(list_x)
    #print(list_y)
    #rs.toMatPlot(targetx=list_x, targety=list_y, blocking=True)
    #rs.toMatPlot(blocking=blocking, sec=sleep)

    def f(t):
        return [x*x for x in t]

    #t1 = np.arange(min_corner, max_corner, 0.1)
    t1 = np.arange(0, 2, 0.1)

    rs.toMatPlot(targetx=t1, targety=f(t1), blocking=True)
    return 0

# if __name__ == '__main__':
#    test1()
