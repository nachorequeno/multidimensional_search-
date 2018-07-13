import unittest

from ParetoLib.Search.Search import *
from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *
from ParetoLib.Oracle.OracleSTL import *

EPS = 1e-5
DELTA = 1e-5
STEPS = 20
SLEEP_TIME = 0.5


class SearchTestCase(unittest.TestCase):

    def setUp(self):
        # This test only considers Oracles (in *.txt format) that are located in the root
        # of folders Oracle/OracleXXX/[1|2|3|N]D

        self.this_dir = 'Oracle'
        self.oracle = Oracle()

        # By default, use min_corner in 0.0 and max_corner in 1.0
        self.min_c = 0.0
        self.max_c = 1.0
        self.numpoints_verify = 30

    #  Membership testing function used in verify2D, verify3D and verifyND
    def _closureMembershipTest(self, fora, rs, xpoint):
        test1 = fora(xpoint) and (rs.member_yup(xpoint) or rs.member_border(xpoint))
        test2 = (not fora(xpoint)) and (rs.member_ylow(xpoint) or rs.member_border(xpoint))

        print_string = 'Warning!\n'
        print_string += 'Testing ', str(xpoint)
        print_string += '(inYup, inYlow, inBorder): ({0}, {1}, {2})'.format(str(rs.member_yup(xpoint)),
                                                                            str(rs.member_ylow(xpoint)),
                                                                            str(rs.member_border(xpoint)))
        print_string += 'Expecting\n'
        print_string += '(inYup, inYlow): ({0}, {1})'.format(str(fora(xpoint)), str(not fora(xpoint)))

        self.assertTrue(test1 or test2, print_string)

    # Auxiliar function for reporting ND results
    def _verifyND(self,
                  fora,
                  rs,
                  list_test_points):
        # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]

        print('Starting tests\n')
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

        # [self._closureMembershipTest(fora, rs, p) for p in list_test_points]
        if all(self._closureMembershipTest(fora, rs, p) for p in list_test_points):
            print('Ok!\n')
        else:
            print('Not ok!\n')
        end = time.time()
        time0 = end - start

        print(rs.volume_report())
        print('Report Ylow: %s\n'.format(str(nYlow)))
        print('Report Yup: %s\n'.format(str(nYup)))
        print('Report Border: %s\n'.format(str(nBorder)))
        print('Time tests: %s\n'.format(str(time0)))

    def search_verify_ND(self, human_readable, list_test_files):
        # min_corner = 0.0
        # max_corner = 1.0
        min_corner = self.min_c
        max_corner = self.max_c

        for bool_val in (True, False):
            for test in list_test_files:
                print('\nTesting {0}'.format(test))
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
                                  sleep=SLEEP_TIME,
                                  opt_level=opt_level,
                                  parallel=bool_val,
                                  logging=bool_val)

                    # Create numpoints_verify vectors of dimension d
                    # Continuous uniform distribution over the stated interval.
                    # To sample Unif[a, b), b > a
                    # (b - a) * random_sample() + a
                    d = self.oracle.dim()
                    list_test_points = (max_corner - min_corner) * np.random.random_sample((self.numpoints_verify, d)) \
                                       + min_corner
                    self._verifyND(fora, rs, list_test_points)


class SearchOracleFunctionTestCase(SearchTestCase):

    def setUp(self):
        super(SearchOracleFunctionTestCase, self).setUp()
        self.this_dir = 'Oracle/OracleFunction'
        self.oracle = OracleFunction()

    def test_2D(self):
        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_3D(self):
        test_dir = os.path.join(self.this_dir, '3D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_ND(self):
        test_dir = os.path.join(self.this_dir, 'ND')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)


class SearchOraclePointTestCase(SearchTestCase):

    def setUp(self):
        super(SearchOraclePointTestCase, self).setUp()
        self.this_dir = 'Oracle/OraclePoint'
        self.oracle = OraclePoint()

    def test_2D(self):
        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        self.search_verify_ND(human_readable=False, list_test_files=list_test_files)

    def test_3D(self):
        test_dir = os.path.join(self.this_dir, '3D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        self.search_verify_ND(human_readable=False, list_test_files=list_test_files)

    def test_ND(self):
        test_dir = os.path.join(self.this_dir, 'ND')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        self.search_verify_ND(human_readable=False, list_test_files=list_test_files)


class SearchOracleSTLTestCase(SearchTestCase):

    def setUp(self):
        super(SearchOracleSTLTestCase, self).setUp()
        self.this_dir = 'Oracle/OracleSTL'
        self.oracle = OracleSTL()

        # Run tests of the 'sincos' example.
        # The validity of the parametric domain is [-2.0, 2.0] (sin and cos signals has module 1.0)
        self.min_c = -2.0
        self.max_c = 2.0

    def test_1D(self):
        test_dir = os.path.join(self.this_dir, '1D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_2D(self):
        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

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
