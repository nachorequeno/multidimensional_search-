import unittest
import math

from ParetoLib.Geometry.Segment import Segment


#############
# Segment #
#############

class SegmentTestCase(unittest.TestCase):

    # def setUp(self):
    # def tearDown(self):

    def test_equality(self):
        # type: (SegmentTestCase) -> None
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        s1 = Segment(p1, p2)
        s1p = Segment(p1, p2)
        print('Segment 1: {0}'.format(s1))

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        s2 = Segment(p3, p4)
        print('Segment 2: {0}'.format(s2))

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        s3 = Segment(p5, p6)
        print('Segment 3: {0}'.format(s3))

        # Equality
        self.assertNotEqual(s1, s2)
        self.assertNotEqual(s1, s3)
        self.assertNotEqual(s2, s3)
        self.assertEqual(s1, s1)
        self.assertEqual(s1, s1p)
        self.assertEqual(hash(s1), hash(s1p))

    def test_inclusion(self):
        # type: (SegmentTestCase) -> None
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        s1 = Segment(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        s2 = Segment(p3, p4)

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        s3 = Segment(p5, p6)

        # Inclusion
        self.assertTrue(p1 in s1)
        self.assertTrue(p2 in s1)

        self.assertTrue(p3 in s2)
        self.assertTrue(p4 in s2)

        self.assertTrue(p5 in s3)
        self.assertTrue(p6 in s3)

        self.assertTrue(p5 in s1)
        self.assertFalse(p6 in s1)
        self.assertFalse(p1 in s3)

    def test_diag(self):
        # type: (SegmentTestCase) -> None
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        s1 = Segment(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        s2 = Segment(p3, p4)

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        s3 = Segment(p5, p6)

        # Diagonal
        self.assertEqual(s1.diag(), (1.0, 1.0))
        self.assertEqual(s2.diag(), (1.0, 1.0))
        self.assertEqual(s3.diag(), (1.0, 1.0))

    def test_dim(self):
        # type: (SegmentTestCase) -> None
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        s1 = Segment(p1, p2)

        p3 = (0.5, 0.25, 0.0)
        p4 = (1.5, 1.0, 0.5)
        s2 = Segment(p3, p4)

        p5 = (1.0, )*10
        p6 = (2.0, )*10
        s3 = Segment(p5, p6)

        # Dimension
        self.assertEqual(s1.dim(), 2)
        self.assertEqual(s2.dim(), 3)
        self.assertEqual(s3.dim(), 10)

    def test_norm(self):
        # type: (SegmentTestCase) -> None
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        s1 = Segment(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        s2 = Segment(p3, p4)

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        s3 = Segment(p5, p6)

        # Norm
        self.assertAlmostEqual(s1.norm(), math.sqrt(2))
        self.assertAlmostEqual(s2.norm(), math.sqrt(2))
        self.assertAlmostEqual(s3.norm(), math.sqrt(2))


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
