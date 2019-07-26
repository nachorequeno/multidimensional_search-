import unittest

from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Geometry.Lattice import Lattice


###########
# Lattice #
###########

class LatticeTestCase(unittest.TestCase):

    # def setUp(self):
    # def tearDown(self):

    def test_equality(self):
        # type: (LatticeTestCase) -> None
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        r1 = Rectangle(p1, p2)
        print('Rectangle 1: {0}'.format(r1))

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        r2 = Rectangle(p3, p4)
        print('Rectangle 2: {0}'.format(r2))

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        r3 = Rectangle(p5, p6)
        print('Rectangle 3: {0}'.format(r3))

        l1 = Lattice(dim=r1.dim(), key=lambda x: x.min_corner)
        l2 = Lattice(dim=r1.dim(), key=lambda x: x.max_corner)

        l1.add_list([r1, r2])
        l2.add_list([r1, r2])

        # Equality
        self.assertSetEqual({r1, r2}, l1.less_equal(r3))
        self.assertSetEqual(set(), l1.greater_equal(r3))

        self.assertSetEqual({r1, r2}, l2.less_equal(r3))
        self.assertSetEqual(set(), l2.greater_equal(r3))


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)

