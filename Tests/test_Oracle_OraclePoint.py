import os
import tempfile as tf
import copy
import unittest
import numpy as np

from ParetoLib.Oracle.OraclePoint import OraclePoint
from ParetoLib.Oracle.NDTree import NDTree


###############
# OraclePoint #
###############

class OraclePointTestCase(unittest.TestCase):
    def setUp(self):
        self.files_to_clean = set()

    def tearDown(self):
        for filename in self.files_to_clean:
            if os.path.isfile(filename):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        self.files_to_clean.add(filename)

    # Test ND-Tree structure
    def test_NDTree(self,
                    min_corner=0.0,
                    max_corner=1.0):
        # type: (OraclePointTestCase, float, float) -> None

        def f1(x):
            return 1 / x if x > 0.0 else 1000

        def f2(x):
            return 0.1 + 1 / x if x > 0.0 else 1001

        def f3(x):
            return 0.2 + 1 / x if x > 0.0 else 1002

        xs = np.arange(min_corner, max_corner, 0.1)
        y1s = [f1(x) for x in xs]
        y2s = [f2(x) for x in xs]
        y3s = [f3(x) for x in xs]

        ND1 = NDTree()
        ND2 = NDTree()

        self.assertEqual(ND1, ND2)

        for x, y in zip(xs, y3s):
            point = (x, y)
            ND1.update_point(point)
            ND2.update_point(point)

        self.assertEqual(ND1, ND2)

        # ND1 should remain constant when we insert the same point twice
        for x, y in zip(xs, y3s):
            point = (x, y)
            ND1.update_point(point)

        self.assertEqual(ND1, ND2)

        # ND1 should change when we insert new dominanting points
        for x, y in zip(xs, y2s):
            point = (x, y)
            ND1.update_point(point)

        self.assertNotEqual(ND1, ND2)

        # ND1 should change when we insert new dominanting points
        for x, y in zip(xs, y1s):
            point = (x, y)
            ND1.update_point(point)

        self.assertNotEqual(ND1, ND2)

        oldND1 = copy.deepcopy(ND1)

        # ND1 should remain constant when we insert dominated points
        for x, y in zip(xs, y3s):
            point = (x, y)
            ND1.update_point(point)

        self.assertEqual(ND1, oldND1)
        self.assertNotEqual(ND1, ND2)

    # Test OraclePoint
    def test_OraclePoints(self):
        self.read_write_files(human_readable=False)
        self.read_write_files(human_readable=True)

    def read_write_files(self,
                         min_corner=0.0,
                         max_corner=1.0,
                         human_readable=False):
        # type: (OraclePointTestCase, float, float, bool) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Points
        def f1(x):
            return 1 / x if x > 0.0 else 1000

        def f2(x):
            return 0.1 + (1 / x) if x > 0.0 else 1000.1

        def f3(x):
            return -0.1 + (1 / x) if x > 0.0 else 999.9

        xs = np.arange(min_corner, max_corner, 0.1)
        y1s = [f1(x) for x in xs]
        y2s = [f2(x) for x in xs]
        y3s = [f3(x) for x in xs]

        p1 = list(zip(xs, y1s))
        p2 = list(zip(xs, y2s))
        p3 = list(zip(xs, y3s))

        # p1 = [(float(x), float(y)) for x, y in zip(xs, y1s)]
        # p2 = [(float(x), float(y)) for x, y in zip(xs, y2s)]
        # p3 = [(float(x), float(y)) for x, y in zip(xs, y3s)]

        p1 = sorted(p1)
        p2 = sorted(p2)
        p3 = sorted(p3)

        # Oracle
        ora1 = OraclePoint()
        for p in p1:
            ora1.add_point(p)

        ora2 = OraclePoint()
        ora2.add_points(set(p1))

        self.assertEqual(ora1, ora2)

        # Membership test
        fora1 = ora1.membership()

        for p in p1:
            self.assertTrue(fora1(p))

        for p in p2:
            self.assertTrue(fora1(p))

        for p in p3:
            self.assertFalse(fora1(p))

        # Read/Write Oracle from file
        print('Reading from {0}'.format(nfile))
        print('Writing to {0}'.format(nfile))

        ora1.to_file(nfile, append=False, human_readable=human_readable)
        ora2 = OraclePoint()
        ora2.from_file(nfile, human_readable=human_readable)

        self.assertEqual(ora1, ora2)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
