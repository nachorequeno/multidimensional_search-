import os
import tempfile as tf
import copy
import unittest

from ParetoLib.Oracle.OraclePoint import *
from ParetoLib.Oracle._NDTree import *


###############
# OraclePoint #
###############

class OraclePointTestCase (unittest.TestCase):
    def setUp(self):
        self.files_to_clean = set()


    def tearDown(self):
        for filename in self.files_to_clean:
            if (os.path.isfile(filename)):
                os.remove(filename)


    def add_file_to_clean(self, filename):
        """
        Adds a file for deferred removal by the tearDown() routine.

        Arguments :
            filename  ( string )
                File name to remove by the tearDown() routine.
        """
        self.files_to_clean.add(filename)

    # Test ND-Tree structure
    def test_NDTree(self,
                   min_corner=0.0,
                   max_corner=1.0):
        # type: (_, float, float) -> _

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
            ND1.updatePoint(point)
            ND2.updatePoint(point)

        self.assertEqual(ND1, ND2)

        # ND1 should remain constant when we insert the same point twice
        for x, y in zip(xs, y3s):
            point = (x, y)
            ND1.updatePoint(point)

        self.assertEqual(ND1, ND2)

        # ND1 should change when we insert new dominanting points
        for x, y in zip(xs, y2s):
            point = (x, y)
            ND1.updatePoint(point)

        self.assertNotEqual(ND1, ND2)

        # ND1 should change when we insert new dominanting points
        for x, y in zip(xs, y1s):
            point = (x, y)
            ND1.updatePoint(point)

        self.assertNotEqual(ND1, ND2)

        oldND1 = copy.deepcopy(ND1)

        # ND1 should remain constant when we insert dominated points
        for x, y in zip(xs, y3s):
            point = (x, y)
            ND1.updatePoint(point)

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
        # type: (_, float, float, bool) -> _
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Points
        def f1(x):
            return 1 / x if x > 0.0 else 1000

        def f2(x):
            return 0.1 + 1 / x if x > 0.0 else 1001

        def f3(x):
            return -0.1 + 1 / x if x > 0.0 else 999

        xs = np.arange(min_corner, max_corner, 0.1)
        y1s = [f1(x) for x in xs]
        y2s = [f2(x) for x in xs]
        y3s = [f3(x) for x in xs]

        p1 = [(x, y) for x, y in zip(xs, y1s)]
        p2 = [(x, y) for x, y in zip(xs, y2s)]
        p3 = [(x, y) for x, y in zip(xs, y3s)]

        # Oracle
        ora1 = OraclePoint()
        for x, y in zip(xs, y1s):
            point = (x, y)
            ora1.addPoint(point)

        ora2 = OraclePoint()
        ora2.addPoints(set(p1))

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
        ora1.toFile(nfile, append=False, human_readable=human_readable)
        ora2 = OraclePoint()
        ora2.fromFile(nfile, human_readable=human_readable)

        self.assertEqual(ora1, ora2)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
