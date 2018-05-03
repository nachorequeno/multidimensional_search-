import os
import random
import __builtin__
import itertools
import unittest

import multiprocessing

from ParetoLib.Search.Search import *
from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *

EPS = 1e-5
DELTA = 1e-5


class SearchTestCase(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    # Multidimensional search
    def msearch(self,
                space,
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

    # Auxiliar functions used in 2D, 3D and ND
    # Creation of Spaces
    def create2DSpace(self, minx, miny, maxx, maxy):
        print ('Creating Space')
        start = time.time()
        minc = (minx, miny)
        maxc = (maxx, maxy)
        xyspace = Rectangle(minc, maxc)
        end = time.time()
        time0 = end - start
        print ('Time creating Space: ', str(time0))
        return xyspace

    def create3DSpace(self, minx, miny, minz, maxx, maxy, maxz):
        print ('Creating Space')
        start = time.time()
        minc = (minx, miny, minz)
        maxc = (maxx, maxy, maxz)
        xyspace = Rectangle(minc, maxc)
        end = time.time()
        time0 = end - start
        print ('Time creating Space: ', str(time0))
        return xyspace

    def createNDSpace(self, *args):
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

    #  Membership testing function used in verify2D, verify3D and verifyND
    def closureMembershipTest(self, fora, rs, xpoint):
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
    def verify2D(self,
                 fora,
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

                    self.closureMembershipTest(fora, rs, xpoint)
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
    def verify3D(self,
                 fora,
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

                        self.closureMembershipTest(fora, rs, xpoint)
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
    def verifyND(self,
                 fora,
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

            [self.closureMembershipTest(fora, rs, p) for p in list_test_points]

        end = time.time()
        time0 = end - start

        vol_total = rs.VolumeYlow() + rs.VolumeYup() + rs.VolumeBorder()
        print ('Volume report (Ylow, Yup, Border, Total): (%s, %s, %s, %s)\n'
               % (str(rs.VolumeYlow()), str(rs.VolumeYup()), str(rs.VolumeBorder()), vol_total)),
        print ('Report Ylow: %s' % (str(nYlow)))
        print ('Report Yup: %s' % (str(nYup)))
        print ('Report Border: %s' % (str(nBorder)))
        print ('Time tests: ', str(time0))


class SearchOracleFunctionTestCase(SearchTestCase):

    def setUp(self):
        super(SearchOracleFunctionTestCase, self).setUp()
        self.this_dir = "Search/OracleFunction"

    # Loading Oracles
    def loadOracleFunction(self,
                           nfile,
                           human_readable=True):
        print ('Creating OracleFunction')
        start = time.time()
        ora = OracleFunction()
        ora.fromFile(nfile, human_readable=human_readable)
        end = time.time()
        time0 = end - start
        print ('Time reading OracleFunction: ', str(time0))
        return ora

    # Dimensional tests
    def OracleFunction2D(self,
                         nfile,
                         human_readable=True,
                         min_cornerx=0.0,
                         min_cornery=0.0,
                         max_cornerx=1.0,
                         max_cornery=1.0,
                         epsilon=EPS,
                         delta=DELTA,
                         verbose=False,
                         blocking=False,
                         test=False,
                         sleep=0):
        ora = self.loadOracleFunction(nfile, human_readable=human_readable)
        fora = ora.membership()

        xyspace = self.create2DSpace(min_cornerx, min_cornery, max_cornerx, max_cornery)

        rs = self.msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

        n = int((max_cornerx - min_cornerx) / 0.1)
        points = rs.getPointsBorder(n)

        print("Points ", points)
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True)
        self.verify2D(fora, rs, test, min_cornerx, min_cornery, max_cornerx, max_cornery)

    def OracleFunction3D(self,
                         nfile,
                         human_readable=True,
                         min_cornerx=0.0,
                         min_cornery=0.0,
                         min_cornerz=0.0,
                         max_cornerx=1.0,
                         max_cornery=1.0,
                         max_cornerz=1.0,
                         epsilon=EPS,
                         delta=DELTA,
                         verbose=False,
                         blocking=False,
                         test=False,
                         sleep=0,
                         ):
        ora = self.loadOracleFunction(nfile, human_readable=human_readable)
        fora = ora.membership()

        xyspace = self.create3DSpace(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

        rs = self.msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

        n = int((max_cornerx - min_cornerx) / 0.1)
        points = rs.getPointsBorder(n)
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        zs = [point[2] for point in points]

        rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True)
        self.verify3D(fora, rs, test, min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

    def OracleFunctionND(self,
                         nfile,
                         human_readable=True,
                         min_corner=0.0,
                         max_corner=1.0,
                         epsilon=EPS,
                         delta=DELTA,
                         verbose=False,
                         blocking=False,
                         test=False,
                         sleep=0,
                         ):
        ora = self.loadOracleFunction(nfile, human_readable=human_readable)
        fora = ora.membership()
        d = ora.dim()

        minc = (min_corner,) * d
        maxc = (max_corner,) * d
        xyspace = Rectangle(minc, maxc)

        rs = self.msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

        t = np.arange(min_corner, max_corner, 0.1)
        # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]
        list_test_points = list(itertools.product(t, repeat=d))

        self.verifyND(fora, rs, list_test_points, test)

    def test_2D(self):
        test_2D_dir = self.this_dir + "/2D/"
        files_path = os.listdir(test_2D_dir)
        test_2D_txt = [test_2D_dir + x for x in files_path if x.endswith(".txt")]

        for test in test_2D_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.OracleFunction2D(min_cornerx=0.0,
                                  min_cornery=0.0,
                                  max_cornerx=1.0,
                                  max_cornery=1.0,
                                  epsilon=EPS,
                                  delta=DELTA,
                                  verbose=False,
                                  blocking=False,
                                  test=False,
                                  sleep=0,
                                  nfile=test,
                                  human_readable=True)

    def test_3D(self):
        test_3D_dir = self.this_dir + "/3D/"
        files_path = os.listdir(test_3D_dir)
        test_3D_txt = [test_3D_dir + x for x in files_path if x.endswith(".txt")]

        for test in test_3D_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.OracleFunction3D(min_cornerx=0.0,
                                  min_cornery=0.0,
                                  min_cornerz=0.0,
                                  max_cornerx=1.0,
                                  max_cornery=1.0,
                                  max_cornerz=1.0,
                                  epsilon=EPS,
                                  delta=DELTA,
                                  verbose=False,
                                  blocking=False,
                                  test=False,
                                  sleep=0,
                                  nfile=test,
                                  human_readable=True)

    def test_ND(self):
        test_ND_dir = self.this_dir + "/ND/"
        files_path = os.listdir(test_ND_dir)
        test_ND_txt = [test_ND_dir + x for x in files_path if x.endswith(".txt")]

        for test in test_ND_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.OracleFunctionND(min_corner=0.0,
                                  max_corner=1.0,
                                  epsilon=EPS,
                                  delta=DELTA,
                                  verbose=False,
                                  blocking=False,
                                  test=False,
                                  sleep=0,
                                  nfile=test,
                                  human_readable=True)


class SearchOraclePointTestCase(SearchTestCase):

    def setUp(self):
        super(SearchOraclePointTestCase, self).setUp()
        self.this_dir = "Search/OraclePoint"

    # Loading Oracles
    def loadOraclePoint(self,
                        nfile,
                        human_readable=False):
        print ('Creating OraclePoint')
        start = time.time()
        ora = OraclePoint()
        ora.fromFile(nfile, human_readable=human_readable)
        end = time.time()
        time0 = end - start
        print ('Time reading OraclePoint: ', str(time0))
        return ora

    # Dimensional tests
    def OraclePoint2D(self,
                      nfile,
                      human_readable=False,
                      min_cornerx=0.0,
                      min_cornery=0.0,
                      max_cornerx=1.0,
                      max_cornery=1.0,
                      epsilon=EPS,
                      delta=DELTA,
                      verbose=False,
                      blocking=False,
                      test=False,
                      sleep=0):
        ora = self.loadOraclePoint(nfile, human_readable=human_readable)
        fora = ora.membership()

        points = ora.getPoints()
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        minx = __builtin__.min(xs)
        miny = __builtin__.min(ys)

        maxx = __builtin__.max(xs)
        maxy = __builtin__.max(ys)

        xyspace = self.create2DSpace(__builtin__.min(minx, min_cornerx),
                                     __builtin__.min(miny, min_cornery),
                                     __builtin__.min(maxx, max_cornerx),
                                     __builtin__.min(maxy, max_cornery))

        rs = self.msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
        rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True)
        self.verify2D(fora, rs, test, min_cornerx, min_cornery, max_cornerx, max_cornery)

    def OraclePoint3D(self,
                      nfile,
                      human_readable=False,
                      min_cornerx=0.0,
                      min_cornery=0.0,
                      min_cornerz=0.0,
                      max_cornerx=1.0,
                      max_cornery=1.0,
                      max_cornerz=1.0,
                      epsilon=EPS,
                      delta=DELTA,
                      verbose=False,
                      blocking=False,
                      test=False,
                      sleep=0):
        ora = self.loadOraclePoint(nfile, human_readable=human_readable)
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

        xyspace = self.create3DSpace(__builtin__.min(minx, min_cornerx),
                                     __builtin__.min(miny, min_cornery),
                                     __builtin__.min(minz, min_cornerz),
                                     __builtin__.min(maxx, max_cornerx),
                                     __builtin__.min(maxy, max_cornery),
                                     __builtin__.min(maxz, max_cornerz))

        rs = self.msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)
        rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True)
        self.verify3D(fora, rs, test, min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

    def OraclePointND(self,
                      nfile,
                      human_readable=False,
                      epsilon=EPS,
                      delta=DELTA,
                      verbose=False,
                      blocking=False,
                      test=False,
                      sleep=0):
        ora = self.loadOraclePoint(nfile, human_readable=human_readable)
        fora = ora.membership()
        d = ora.dim()

        points = ora.getPoints()
        sorted_points = sorted(points)

        minc = sorted_points[0]
        maxc = sorted_points.pop()
        xyspace = Rectangle(minc, maxc)

        rs = self.msearch(xyspace, fora, epsilon, delta, verbose, blocking, sleep)

        t = np.arange(minc, maxc, 0.1)
        # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]
        list_test_points = list(itertools.product(t, repeat=d))

        self.verifyND(fora, rs, list_test_points, test)

    def test_2D(self):
        test_2D_dir = self.this_dir + "/2D/"
        files_path = os.listdir(test_2D_dir)
        test_2D_txt = [test_2D_dir + x for x in files_path if x.endswith(".txt")]

        for test in test_2D_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.OraclePoint2D(min_cornerx=0.0,
                               min_cornery=0.0,
                               max_cornerx=1.0,
                               max_cornery=1.0,
                               epsilon=EPS,
                               delta=DELTA,
                               verbose=False,
                               blocking=False,
                               test=False,
                               sleep=0,
                               nfile=test,
                               human_readable=False)

    def test_3D(self):
        test_3D_dir = self.this_dir + "/3D/"
        files_path = os.listdir(test_3D_dir)
        test_3D_txt = [test_3D_dir + x for x in files_path if x.endswith(".txt")]

        for test in test_3D_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.OraclePoint3D(min_cornerx=0.0,
                               min_cornery=0.0,
                               min_cornerz=0.0,
                               max_cornerx=1.0,
                               max_cornery=1.0,
                               max_cornerz=1.0,
                               epsilon=EPS,
                               delta=DELTA,
                               verbose=False,
                               blocking=False,
                               test=False,
                               sleep=0,
                               nfile=test,
                               human_readable=False)

    def test_ND(self):
        test_ND_dir = self.this_dir + "/ND/"
        files_path = os.listdir(test_ND_dir)
        test_ND_txt = [test_ND_dir + x for x in files_path if x.endswith(".txt")]

        for test in test_ND_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.OraclePointND(epsilon=EPS,
                               delta=DELTA,
                               verbose=False,
                               blocking=False,
                               test=False,
                               sleep=0,
                               nfile=test,
                               human_readable=False)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)

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
