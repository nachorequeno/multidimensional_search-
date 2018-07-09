import unittest

from ParetoLib.Search.ParSearch import *
from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *
from ParetoLib.Oracle.OracleSTL import *

EPS = 1e-5
DELTA = 1e-5
STEPS = 20


class SearchTestCase(unittest.TestCase):

    def setUp(self):
        # This test only considers Oracles (in *.txt format) that are located in the root
        # of folders Oracle/OracleXXX/[1|2|3|N]D

        self.this_dir = "Oracle"
        self.oracle = Oracle()

        # By default, use min_corner in 0.0 and max_corner in 1.0
        self.min_c = 0.0
        self.max_c = 1.0

    #  Membership testing function used in verify2D, verify3D and verifyND
    def _closureMembershipTest(self, fora, rs, xpoint):
        test1 = fora(xpoint) and (rs.member_yup(xpoint) or rs.member_border(xpoint))
        test2 = (not fora(xpoint)) and (rs.member_ylow(xpoint) or rs.member_border(xpoint))

        vprint_string = 'Warning!\n'
        vprint_string += 'Testing ', str(xpoint)
        vprint_string += '(inYup, inYlow, inBorder): (%s, %s, %s)' \
                         % (str(rs.member_yup(xpoint)), str(rs.member_ylow(xpoint)),
                            str(rs.member_border(xpoint)))
        vprint_string += 'Expecting\n'
        vprint_string += '(inYup, inYlow): (%s, %s)' \
                         % (str(fora(xpoint)), str(not fora(xpoint)))

        self.assertTrue(test1 or test2, vprint_string)

    # Auxiliar function for reporting 2D results
    def _verify2D(self,
                  fora,
                  rs,
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

        vprint('Starting tests')
        start = time.time()
        for t1p in t1:
            for t2p in t2:
                xpoint = (t1p, t2p)
                testYup = testYup or rs.member_yup(xpoint)
                testYlow = testYlow or rs.member_ylow(xpoint)
                testBorder = testBorder or rs.member_border(xpoint)

                nYup = nYup + 1 if rs.member_yup(xpoint) else nYup
                nYlow = nYlow + 1 if rs.member_ylow(xpoint) else nYlow
                nBorder = nBorder + 1 if rs.member_border(xpoint) else nBorder

                self._closureMembershipTest(fora, rs, xpoint)
        end = time.time()
        time0 = end - start

        print (rs.volume_report())
        print ('Report Ylow: %s, %s' % (str(testYlow), str(nYlow)))
        print ('Report Yup: %s, %s' % (str(testYup), str(nYup)))
        print ('Report Border: %s, %s' % (str(testBorder), str(nBorder)))
        print ('Time tests: ', str(time0))

    # Auxiliar function for reporting 3D results
    def _verify3D(self,
                  fora,
                  rs,
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
        for t1p in t1:
            for t2p in t2:
                for t3p in t3:
                    xpoint = (t1p, t2p, t3p)
                    testYup = testYup or rs.member_yup(xpoint)
                    testYlow = testYlow or rs.member_ylow(xpoint)
                    testBorder = testBorder or rs.member_border(xpoint)

                    nYup = nYup + 1 if rs.member_yup(xpoint) else nYup
                    nYlow = nYlow + 1 if rs.member_ylow(xpoint) else nYlow
                    nBorder = nBorder + 1 if rs.member_border(xpoint) else nBorder

                    self._closureMembershipTest(fora, rs, xpoint)
        end = time.time()
        time0 = end - start

        print (rs.volume_report())
        print ('Report Ylow: %s, %s' % (str(testYlow), str(nYlow)))
        print ('Report Yup: %s, %s' % (str(testYup), str(nYup)))
        print ('Report Border: %s, %s' % (str(testBorder), str(nBorder)))
        print ('Time tests: ', str(time0))

    # Auxiliar function for reporting ND results
    def _verifyND(self,
                  fora,
                  rs,
                  list_test_points):
        # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]

        print ('Starting tests\n')
        start = time.time()
        f1 = lambda p: 1 if rs.member_yup(p) else 0
        f2 = lambda p: 1 if rs.member_ylow(p) else 0
        f3 = lambda p: 1 if rs.member_border(p) else 0

        list_nYup = map(f1, list_test_points)
        list_nYlow = map(f2, list_test_points)
        list_nBorder = map(f3, list_test_points)

        nYup = sum(list_nYup)
        nYlow = sum(list_nYlow)
        nBorder = sum(list_nBorder)

        [self._closureMembershipTest(fora, rs, p) for p in list_test_points]

        end = time.time()
        time0 = end - start

        print (rs.volume_report())
        print ('Report Ylow: %s' % (str(nYlow)))
        print ('Report Yup: %s' % (str(nYup)))
        print ('Report Border: %s' % (str(nBorder)))
        print ('Time tests: ', str(time0))

    def search_verify_1D(self, human_readable):
        # test_1D_dir = self.this_dir + "/1D/"
        test_1D_dir = os.path.join(self.this_dir, "1D")
        files_path = os.listdir(test_1D_dir)
        # test_1D_txt = [test_1D_dir + x for x in files_path if x.endswith(".txt")]
        test_1D_txt = [os.path.join(test_1D_dir, x) for x in files_path if x.endswith(".txt")]

        # min_corner = 0.0
        # max_corner = 1.0
        min_corner = self.min_c
        max_corner = self.max_c

        for test in test_1D_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.oracle.from_file(test, human_readable)
            fora = self.oracle.membership()
            for opt_level in range(3):
                rs = SearchND(ora=self.oracle,
                              min_corner=min_corner,
                              max_corner=max_corner,
                              epsilon=EPS,
                              delta=DELTA,
                              max_step=STEPS,
                              blocking=False,
                              sleep=0,
                              opt_level=opt_level,
                              logging=False)

                d = self.oracle.dim()
                t = np.arange(min_corner, max_corner, 0.1)
                # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]
                list_test_points = list(itertools.product(t, repeat=d))

                self._verifyND(fora, rs, list_test_points)

    def search_verify_2D(self, human_readable):
        # test_2D_dir = self.this_dir + "/2D/"
        test_2D_dir = os.path.join(self.this_dir, "2D")
        files_path = os.listdir(test_2D_dir)
        # test_2D_txt = [test_2D_dir + x for x in files_path if x.endswith(".txt")]
        test_2D_txt = [os.path.join(test_2D_dir, x) for x in files_path if x.endswith(".txt")]

        # min_x, min_y = (0.0, 0.0)
        # max_x, max_y = (1.0, 1.0)

        min_x, min_y = (self.min_c, self.min_c)
        max_x, max_y = (self.max_c, self.max_c)

        for test in test_2D_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.oracle.from_file(test, human_readable)
            fora = self.oracle.membership()
            for opt_level in range(3):
                rs = Search2D(ora=self.oracle,
                              min_cornerx=min_x,
                              min_cornery=min_y,
                              max_cornerx=max_x,
                              max_cornery=max_y,
                              epsilon=EPS,
                              delta=DELTA,
                              max_step=STEPS,
                              blocking=False,
                              sleep=0,
                              opt_level=opt_level,
                              logging=False)
                self._verify2D(fora,
                               rs,
                               min_cornerx=min_x,
                               min_cornery=min_y,
                               max_cornerx=max_x,
                               max_cornery=max_y)

    def search_verify_3D(self, human_readable):
        # test_3D_dir = self.this_dir + "/3D/"
        test_3D_dir = os.path.join(self.this_dir, "3D")
        files_path = os.listdir(test_3D_dir)
        # test_3D_txt = [test_3D_dir + x for x in files_path if x.endswith(".txt")]
        test_3D_txt = [os.path.join(test_3D_dir, x) for x in files_path if x.endswith(".txt")]

        # min_x, min_y, min_z = (0.0, 0.0, 0.0)
        # max_x, max_y, max_z = (1.0, 1.0, 1.0)

        min_x, min_y, min_z = (self.min_c, self.min_c, self.min_c)
        max_x, max_y, max_z = (self.max_c, self.max_c, self.max_c)

        for test in test_3D_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.oracle.from_file(test, human_readable)
            fora = self.oracle.membership()
            for opt_level in range(3):
                rs = Search3D(ora=self.oracle,
                              min_cornerx=min_x,
                              min_cornery=min_y,
                              min_cornerz=min_z,
                              max_cornerx=max_x,
                              max_cornery=max_y,
                              max_cornerz=max_z,
                              epsilon=EPS,
                              delta=DELTA,
                              max_step=STEPS,
                              blocking=False,
                              sleep=0,
                              opt_level=opt_level,
                              logging=False)
                self._verify3D(fora,
                               rs,
                               min_cornerx=min_x,
                               min_cornery=min_y,
                               min_cornerz=min_z,
                               max_cornerx=max_x,
                               max_cornery=max_y,
                               max_cornerz=max_z)

    def search_verify_ND(self, human_readable):
        # test_ND_dir = self.this_dir + "/ND/"
        test_ND_dir = os.path.join(self.this_dir, "ND")
        files_path = os.listdir(test_ND_dir)
        # test_ND_txt = [test_ND_dir + x for x in files_path if x.endswith(".txt")]
        test_ND_txt = [os.path.join(test_ND_dir, x) for x in files_path if x.endswith(".txt")]

        # min_corner = 0.0
        # max_corner = 1.0

        min_corner = self.min_c
        max_corner = self.max_c

        for test in test_ND_txt:
            self.assertTrue(os.path.isfile(test), test)
            self.oracle.from_file(test, human_readable)
            fora = self.oracle.membership()
            for opt_level in range(3):
                rs = SearchND(ora=self.oracle,
                              min_corner=min_corner,
                              max_corner=max_corner,
                              epsilon=EPS,
                              delta=DELTA,
                              max_step=STEPS,
                              blocking=False,
                              sleep=0,
                              opt_level=opt_level,
                              logging=False)

                d = self.oracle.dim()
                t = np.arange(min_corner, max_corner, 0.1)
                # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]
                list_test_points = list(itertools.product(t, repeat=d))

                self._verifyND(fora, rs, list_test_points)


class SearchOracleFunctionTestCase(SearchTestCase):

    def setUp(self):
        super(SearchOracleFunctionTestCase, self).setUp()
        self.this_dir = "Oracle/OracleFunction"
        self.oracle = OracleFunction()

    def test_2D(self):
        self.search_verify_2D(True)

    def test_3D(self):
        self.search_verify_3D(True)

    def test_ND(self):
        self.search_verify_ND(True)


class SearchOraclePointTestCase(SearchTestCase):

    def setUp(self):
        super(SearchOraclePointTestCase, self).setUp()
        self.this_dir = "Oracle/OraclePoint"
        self.oracle = OraclePoint()

    def test_2D(self):
        self.search_verify_2D(False)

    def test_3D(self):
        self.search_verify_3D(False)

    def test_ND(self):
        self.search_verify_ND(False)


class SearchOracleSTLTestCase(SearchTestCase):

    def setUp(self):
        super(SearchOracleSTLTestCase, self).setUp()
        self.this_dir = "Oracle/OracleSTL"
        self.oracle = OracleSTL()

        # Run tests of the 'sincos' example.
        # The validity of the parametric domain is [-2.0, 2.0] (sin and cos signals has module 1.0)
        self.min_c = -2.0
        self.max_c = 2.0

    def test_1D(self):
        self.search_verify_1D(False)

    def test_2D(self):
        self.search_verify_2D(False)

    # Currently, we only run OracleSTL tests for 1D and 2D because of the
    # complexity in verifying the results and the computational cost of
    # evaluating STL properties in the Test folder.

    # def test_3D(self):
    #     self.search_verify_3D(False)

    # def test_ND(self):
    #     self.search_verify_ND(False)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
