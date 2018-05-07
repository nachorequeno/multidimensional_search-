import time
import unittest

import numpy as np

import ParetoLib.Geometry.PPoint as pp
import ParetoLib.Geometry.Point as p


class PointTestCase(unittest.TestCase):
    DIM = 2
    REP = 100

    def setUp(self):
        None

    def tearDown(self):
        None

    def time_for_n_iterations(self, f, l):
        start = time.time()
        for i in range(l):
            f(i)
        end = time.time()
        print(str(end - start))

    def operation_performance(self,
                              rep=REP,
                              dim=DIM):
        xxprime = np.random.rand(2, dim)

        x = tuple(xxprime[0])
        xprime = tuple(xxprime[1])

        print("Point (tuple)")
        self.time_for_n_iterations(lambda z: p.norm(x), rep)
        self.time_for_n_iterations(lambda z: p.distance(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.distanceHamming(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.subtract(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.add(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.mult(x, 2), rep)
        self.time_for_n_iterations(lambda z: p.div(x, 2), rep)
        self.time_for_n_iterations(lambda z: p.greater(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.greater_equal(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.less(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.less_equal(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.max(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.min(x, xprime), rep)

        print("Point (numpy)")
        self.time_for_n_iterations(lambda z: pp.norm(x), rep)
        self.time_for_n_iterations(lambda z: pp.distance(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.distanceHamming(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.subtract(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.add(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.mult(x, 2), rep)
        self.time_for_n_iterations(lambda z: pp.div(x, 2), rep)
        self.time_for_n_iterations(lambda z: pp.greater(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.greater_equal(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.less(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.less_equal(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.max(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.min(x, xprime), rep)

    def operation_correctness(self, dim=DIM):
        xxprime = np.random.rand(2, dim)

        x = tuple(xxprime[0])
        xprime = tuple(xxprime[1])

        self.assertEqual(p.norm(x), pp.norm(x))
        self.assertEqual(p.distance(x, xprime), pp.distance(x, xprime))
        self.assertEqual(p.distanceHamming(x, xprime), pp.distanceHamming(x, xprime))
        self.assertEqual(p.subtract(x, xprime), pp.subtract(x, xprime))
        self.assertEqual(p.add(x, xprime), pp.add(x, xprime))
        self.assertEqual(p.mult(x, 2), pp.mult(x, 2))
        self.assertEqual(p.div(x, 2), pp.div(x, 2))
        self.assertEqual(p.greater(x, xprime), pp.greater(x, xprime))
        self.assertEqual(p.greater_equal(x, xprime), pp.greater_equal(x, xprime))
        self.assertEqual(p.less(x, xprime), pp.less(x, xprime))
        self.assertEqual(p.less_equal(x, xprime), pp.less_equal(x, xprime))
        self.assertEqual(p.max(x, xprime), pp.max(x, xprime))
        self.assertEqual(p.min(x, xprime), pp.min(x, xprime))

    def test_point_operations_performance(self):
        for dim in range(2, 10):
            self.operation_performance(rep=self.REP, dim=dim)

    def test_point_operations_correctness(self):
        for dim in range(2, 10):
            self.operation_correctness(dim=dim)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
