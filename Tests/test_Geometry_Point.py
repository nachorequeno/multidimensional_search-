import random
import time
import unittest

import numpy as np

import ParetoLib.Geometry.PPoint as pp
import ParetoLib.Geometry.Point as p


class PointTestCase(unittest.TestCase):
    DIM = 2
    REP = 100

    def setUp(self):
        # type: (PointTestCase) -> None
        pass

    def tearDown(self):
        # type: (PointTestCase) -> None
        pass

    def time_for_n_iterations(self, f, l):
        # type: (PointTestCase, callable, iter) -> None
        start = time.time()
        for i in range(l):
            f(i)
        end = time.time()
        print(str(end - start))

    def operation_performance(self,
                              rep=REP,
                              dim=DIM):
        # type: (PointTestCase, int, int) -> None
        xxprime = np.random.rand(2, dim)

        x = tuple(xxprime[0])
        xprime = tuple(xxprime[1])
        r1 = random.randint(0, len(x)-1)
        r2 = random.randint(0, 10)

        print('Point (tuple)')
        self.time_for_n_iterations(lambda z: p.dim(x), rep)
        self.time_for_n_iterations(lambda z: p.norm(x), rep)
        self.time_for_n_iterations(lambda z: p.distance(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.hamming_distance(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.subtract(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.add(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.mult(x, 2), rep)
        self.time_for_n_iterations(lambda z: p.div(x, 2), rep)
        self.time_for_n_iterations(lambda z: p.greater(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.greater(xprime, x), rep)
        self.time_for_n_iterations(lambda z: p.greater_equal(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.greater_equal(xprime, x), rep)
        self.time_for_n_iterations(lambda z: p.less(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.less_equal(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.maximum(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.maximum(xprime, x), rep)
        self.time_for_n_iterations(lambda z: p.minimum(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.minimum(xprime, x), rep)
        self.time_for_n_iterations(lambda z: p.incomparables(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.subt(r1, x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.int_to_bin_list(r2), rep)
        self.time_for_n_iterations(lambda z: p.int_to_bin_tuple(r2), rep)
        self.time_for_n_iterations(lambda z: p.dominates(x, xprime), rep)
        self.time_for_n_iterations(lambda z: p.is_dominated(x, xprime), rep)

        print('Point (numpy)')
        self.time_for_n_iterations(lambda z: pp.dim(x), rep)
        self.time_for_n_iterations(lambda z: pp.norm(x), rep)
        self.time_for_n_iterations(lambda z: pp.distance(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.hamming_distance(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.subtract(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.add(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.mult(x, 2), rep)
        self.time_for_n_iterations(lambda z: pp.div(x, 2), rep)
        self.time_for_n_iterations(lambda z: pp.greater(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.greater(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.greater_equal(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.greater_equal(xprime, x), rep)
        self.time_for_n_iterations(lambda z: pp.less(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.less_equal(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.maximum(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.maximum(xprime, x), rep)
        self.time_for_n_iterations(lambda z: pp.minimum(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.minimum(xprime, x), rep)
        self.time_for_n_iterations(lambda z: pp.incomparables(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.subt(r1, x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.int_to_bin_list(r2), rep)
        self.time_for_n_iterations(lambda z: pp.int_to_bin_tuple(r2), rep)
        self.time_for_n_iterations(lambda z: pp.dominates(x, xprime), rep)
        self.time_for_n_iterations(lambda z: pp.is_dominated(x, xprime), rep)

    def operation_correctness(self, dim=DIM):
        # type: (PointTestCase, int) -> None
        xxprime = np.random.rand(2, dim)

        x = tuple(xxprime[0])
        xprime = tuple(xxprime[1])

        r = random.randint(0, len(x)-1)
        sel = (0,)*(len(x)-1) + (1,)

        self.assertEqual(p.dim(x), pp.dim(x))
        self.assertEqual(p.norm(x), pp.norm(x))
        self.assertEqual(p.distance(x, xprime), pp.distance(x, xprime))
        self.assertEqual(p.hamming_distance(x, xprime), pp.hamming_distance(x, xprime))
        self.assertEqual(p.subtract(x, xprime), pp.subtract(x, xprime))
        self.assertEqual(p.add(x, xprime), pp.add(x, xprime))
        self.assertEqual(p.mult(x, 2), pp.mult(x, 2))
        self.assertEqual(p.div(x, 2), pp.div(x, 2))
        self.assertEqual(p.greater(x, xprime), pp.greater(x, xprime))
        self.assertEqual(p.greater_equal(x, xprime), pp.greater_equal(x, xprime))
        self.assertEqual(p.less(x, xprime), pp.less(x, xprime))
        self.assertEqual(p.less_equal(x, xprime), pp.less_equal(x, xprime))
        self.assertEqual(p.maximum(x, xprime), pp.maximum(x, xprime))
        self.assertEqual(p.minimum(x, xprime), pp.minimum(x, xprime))
        self.assertEqual(p.incomparables(x, xprime), pp.incomparables(x, xprime))
        self.assertEqual(p.subt(r, x, xprime), pp.subt(r, x, xprime))
        self.assertEqual(p.select(x, sel), pp.select(x, sel))
        self.assertEqual(p.int_to_bin_list(r), pp.int_to_bin_list(r))
        self.assertEqual(p.int_to_bin_tuple(r), pp.int_to_bin_tuple(r))
        self.assertEqual(p.dominates(x, xprime), pp.dominates(x, xprime))
        self.assertEqual(p.is_dominated(x, xprime), pp.is_dominated(x, xprime))

    def test_point_operations_performance(self):
        # type: (PointTestCase) -> None
        for dim in range(2, 10):
            self.operation_performance(rep=self.REP, dim=dim)

    def test_point_operations_correctness(self):
        # type: (PointTestCase) -> None
        for dim in range(2, 10):
            self.operation_correctness(dim=dim)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
