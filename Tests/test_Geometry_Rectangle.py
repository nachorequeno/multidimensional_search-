import unittest

from ParetoLib.Geometry.Rectangle import *

#############
# Rectangle #
#############

class RectangleTestCase(unittest.TestCase):

    #def setUp(self):
    #def tearDown(self):

    def test_equality(self):
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        r1 = Rectangle(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        r2 = Rectangle(p3, p4)

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        r3 = Rectangle(p5, p6)

        r4 = Rectangle()
        r5 = Rectangle()

        # Equality
        self.assertNotEqual(r1, r2)
        self.assertNotEqual(r1, r3)
        self.assertNotEqual(r2, r3)
        self.assertEqual(r4, r5)

    def test_distance_to_center(self):

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        r3 = Rectangle(p5, p6)

        dist_p5 = r3.distanceToCenter(p5)
        dist_p6 = r3.distanceToCenter(p6)

        # Distance to center
        self.assertEqual(dist_p5, dist_p6)

    def test_volumes(self):
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        r1 = Rectangle(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        r2 = Rectangle(p3, p4)

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        r3 = Rectangle(p5, p6)

        r_intersect = r1.intersection(r2)

        # Volumes
        self.assertEqual(r1.volume(), r2.volume())
        self.assertEqual(r3.volume(), r1.volume())
        self.assertEqual(r3.volume(), r2.volume())

        self.assertGreater(r1.volume(), r_intersect.volume())
        self.assertGreater(r2.volume(), r_intersect.volume())

    def test_vertices(self):
        p1 = (0.0, 0.0)
        p2 = (1.0, 1.0)
        r = Rectangle(p1, p2)
        vertices = r.vertices()
        expected_vertices = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]

        # Vertices
        self.assertEqual(vertices, expected_vertices),

        num_vertices = r.numVertices()
        num_vertices_expected = len(expected_vertices)
        self.assertEqual(num_vertices, num_vertices_expected)

    def test_intersection(self):

        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        r1 = Rectangle(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        r2 = Rectangle(p3, p4)

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        r3 = Rectangle(p5, p6)

        p7 = (1.5, 0.0)
        p8 = (2.0, 1.0)
        r4 = Rectangle(p7, p8)

        p9 = (0.5, 1.0)
        r5 = Rectangle(p9, p2)

        p10 = (0.5, 1.75)
        r6 = Rectangle(p1, p10)

        p1_intersect = (0.5, 0.75)
        p2_intersect = (1.0, 1.0)
        r_intersect_expected = Rectangle(p1_intersect, p2_intersect)
        r_intersect = r1.intersection(r2)

        # Intersection of Rectangles
        self.assertTrue(r1.overlaps(r2))
        self.assertTrue(not r1.overlaps(r3))
        self.assertTrue(not r1.overlaps(r4))
        self.assertTrue(r1.overlaps(r5))
        self.assertTrue(r1.overlaps(r6))
        self.assertTrue(r2.overlaps(r1))
        self.assertTrue(not r2.overlaps(r3))
        self.assertTrue(not r2.overlaps(r4))
        self.assertTrue(not r3.overlaps(r1))
        self.assertTrue(not r3.overlaps(r2))
        self.assertTrue(not r3.overlaps(r4))
        self.assertTrue(not r4.overlaps(r1))
        self.assertTrue(not r4.overlaps(r2))
        self.assertTrue(not r4.overlaps(r3))

        #####
        self.assertEqual(r_intersect, r_intersect_expected)
        self.assertEqual(r1.intersection(r5), r5)
        self.assertEqual(r1.intersection(r6), r6)
        self.assertEqual(r5.intersection(r1), r5)
        self.assertEqual(r6.intersection(r1), r6)
        ####

    def test_concatenation(self):

        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        r1 = Rectangle(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        r2 = Rectangle(p3, p4)

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        r3 = Rectangle(p5, p6)

        p7 = (1.5, 0.0)
        p8 = (2.0, 1.0)
        r4 = Rectangle(p7, p8)

        p9 = (0.5, 1.0)
        r5 = Rectangle(p9, p2)

        p10 = (0.5, 1.75)
        r6 = Rectangle(p1, p10)

        r_intersect = r1.intersection(r2)

        # Concatenation of Rectangles
        self.assertTrue(not r1.isconcatenable(r2))
        self.assertTrue(not r1.isconcatenable(r3))
        self.assertTrue(not r1.isconcatenable(r4))
        self.assertTrue(not r1.isconcatenable(r5))
        self.assertTrue(not r1.isconcatenable(r6))
        self.assertTrue(not r2.isconcatenable(r1))
        self.assertTrue(not r2.isconcatenable(r3))
        self.assertTrue(r2.isconcatenable(r4))
        self.assertTrue(not r2.isconcatenable(r5))
        self.assertTrue(not r2.isconcatenable(r6))
        self.assertTrue(not r3.isconcatenable(r1))
        self.assertTrue(not r3.isconcatenable(r2))
        self.assertTrue(not r4.isconcatenable(r1))
        self.assertTrue(r4.isconcatenable(r2))
        self.assertTrue(not r5.isconcatenable(r1))
        self.assertTrue(not r5.isconcatenable(r2))
        self.assertTrue(not r5.isconcatenable(r6))
        self.assertTrue(not r6.isconcatenable(r1))
        self.assertTrue(not r6.isconcatenable(r2))
        self.assertTrue(not r6.isconcatenable(r5))

        self.assertEqual(r1, r_intersect.concatenate(r5).concatenate(r6))
        self.assertEqual(r4, r2.concatenate(r4).intersection(r4))

    def test_difference(self):
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        r1 = Rectangle(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        r2 = Rectangle(p3, p4)

        p5 = (0.5, 1.0)
        r3 = Rectangle(p1, p5)
        r4 = Rectangle(p5, p2)

        p6 = (0.0, 1.0)
        p7 = (0.5, 1.75)
        r5 = Rectangle(p6, p7)

        diff_result = set(r1 - r2)

        # Difference
        self.assertTrue(r3 in diff_result)
        self.assertTrue(r4 in diff_result)
        self.assertTrue(r5 in diff_result)
        self.assertTrue(len(diff_result) == 3)

        diff_result21 = set(r3 - r4)
        diff_result22 = set(r4 - r3)
        diff_result31 = set(r4 - r5)
        diff_result32 = set(r5 - r4)

        # r1 - r2 returns r1 in the case that r1 and r2 do not intersect
        self.assertTrue(len(diff_result21) == 1)
        self.assertTrue(len(diff_result22) == 1)
        self.assertTrue(len(diff_result31) == 1)
        self.assertTrue(len(diff_result32) == 1)

        self.assertTrue(r3 in diff_result21)
        self.assertTrue(r4 in diff_result22)
        self.assertTrue(r4 in diff_result31)
        self.assertTrue(r5 in diff_result32)

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)

