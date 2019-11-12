import unittest

from ParetoLib.Geometry.Rectangle import Rectangle, iuwc, idwc


#############
# Rectangle #
#############

class RectangleTestCase(unittest.TestCase):

    # def setUp(self):
    # def tearDown(self):

    def test_equality(self):
        # type: (RectangleTestCase) -> None
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

        r4 = Rectangle()
        r5 = Rectangle()

        # Equality
        self.assertNotEqual(r1, r2)
        self.assertNotEqual(r1, r3)
        self.assertNotEqual(r2, r3)
        self.assertEqual(r4, r5)

        self.assertGreater(r3, r1)
        self.assertGreaterEqual(r3, r1)
        self.assertGreaterEqual(r1, r1)
        self.assertLess(r1, r3)
        self.assertLessEqual(r1, r3)
        self.assertLessEqual(r1, r1)

    def test_inclusion(self):
        # type: (RectangleTestCase) -> None
        p1 = (0.0, 0.75)
        p2 = (1.0, 1.75)
        r1 = Rectangle(p1, p2)

        p3 = (0.5, 0.0)
        p4 = (1.5, 1.0)
        r2 = Rectangle(p3, p4)

        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        r3 = Rectangle(p5, p6)

        # Inclusion
        self.assertTrue(r1.inside(p1))
        self.assertTrue(r1.inside(p2))

        self.assertTrue(r2.inside(p3))
        self.assertTrue(r2.inside(p4))

        self.assertTrue(r3.inside(p5))
        self.assertTrue(r3.inside(p6))

        self.assertFalse(p1 in r1)
        self.assertFalse(p2 in r1)

        self.assertFalse(p3 in r2)
        self.assertFalse(p4 in r2)

        self.assertFalse(p5 in r3)
        self.assertFalse(p6 in r3)

        # p5 is in the edge of r1, so no strictly inside r1
        self.assertFalse(p5 in r1)
        self.assertFalse(p6 in r1)
        self.assertFalse(p1 in r3)

    def test_distance_to_center(self):
        # type: (RectangleTestCase) -> None
        p5 = (1.0, 1.0)
        p6 = (2.0, 2.0)
        r3 = Rectangle(p5, p6)

        dist_p5 = r3.distance_to_center(p5)
        dist_p6 = r3.distance_to_center(p6)

        # Distance to center
        self.assertEqual(dist_p5, dist_p6)

    def test_volumes(self):
        # type: (RectangleTestCase) -> None
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
        # type: (RectangleTestCase) -> None
        p1 = (0.0, 0.0)
        p2 = (1.0, 1.0)
        rect = Rectangle(p1, p2)
        vertices = rect.vertices()
        expected_vertices = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]

        # Vertices
        self.assertEqual(vertices, expected_vertices),

        num_vertices = rect.num_vertices()
        num_vertices_expected = len(expected_vertices)
        self.assertEqual(num_vertices, num_vertices_expected)

    def test_intersection(self):
        # type: (RectangleTestCase) -> None
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
        # type: (RectangleTestCase) -> None
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
        self.assertTrue(not r1.is_concatenable(r2))
        self.assertTrue(not r1.is_concatenable(r3))
        self.assertTrue(not r1.is_concatenable(r4))
        self.assertTrue(not r1.is_concatenable(r5))
        self.assertTrue(not r1.is_concatenable(r6))
        self.assertTrue(not r2.is_concatenable(r1))
        self.assertTrue(not r2.is_concatenable(r3))
        self.assertTrue(r2.is_concatenable(r4))
        self.assertTrue(not r2.is_concatenable(r5))
        self.assertTrue(not r2.is_concatenable(r6))
        self.assertTrue(not r3.is_concatenable(r1))
        self.assertTrue(not r3.is_concatenable(r2))
        self.assertTrue(not r4.is_concatenable(r1))
        self.assertTrue(r4.is_concatenable(r2))
        self.assertTrue(not r5.is_concatenable(r1))
        self.assertTrue(not r5.is_concatenable(r2))
        self.assertTrue(not r5.is_concatenable(r6))
        self.assertTrue(not r6.is_concatenable(r1))
        self.assertTrue(not r6.is_concatenable(r2))
        self.assertTrue(not r6.is_concatenable(r5))

        self.assertEqual(r1, r_intersect.concatenate(r5).concatenate(r6))
        self.assertEqual(r4, r2.concatenate(r4).intersection(r4))

    def test_difference(self):
        # type: (RectangleTestCase) -> None
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
        r6 = Rectangle(p1, p7)

        diff_result = set(r1.difference(r2))

        # Difference
        self.assertTrue(r6 in diff_result)
        # self.assertTrue(r3 in diff_result)
        self.assertTrue(r4 in diff_result)
        # self.assertTrue(r5 in diff_result)
        # self.assertTrue(len(diff_result) == 3)
        self.assertTrue(len(diff_result) == 2)

        diff_result21 = set(r3.difference(r4))
        diff_result22 = set(r4.difference(r3))
        diff_result31 = set(r4.difference(r5))
        diff_result32 = set(r5.difference(r4))

        # r1.difference(r2) returns r1 in the
        # case that r1 and r2 do not intersect
        self.assertTrue(len(diff_result21) == 1)
        self.assertTrue(len(diff_result22) == 1)
        self.assertTrue(len(diff_result31) == 1)
        self.assertTrue(len(diff_result32) == 1)

        self.assertTrue(r3 in diff_result21)
        self.assertTrue(r4 in diff_result22)
        self.assertTrue(r4 in diff_result31)
        self.assertTrue(r5 in diff_result32)

        # r1 - r2 is a synonym for r1.difference(r2)
        # '-' tries to minimize the number of cubes generated by
        # self.difference(other) by concatenating adjacent boxes
        self.assertLessEqual(len(r1 - r2), len(diff_result))
        self.assertLessEqual(len(r3 - r4), len(diff_result21))
        self.assertLessEqual(len(r4 - r3), len(diff_result22))
        self.assertLessEqual(len(r4 - r5), len(diff_result31))
        self.assertLessEqual(len(r5 - r4), len(diff_result32))

    def test_idwc_iuwc(self):
        # type: (RectangleTestCase) -> None
        p1 = (0.0,)*4
        p2 = (0.5,)*4
        p3 = (0.2, 0.6, 0.2, 0.2)

        z = Rectangle(p1, p2)
        y = Rectangle(p1, p3)

        r = [Rectangle((0.2, 0.0, 0.0, 0.0), p2), Rectangle((0.0, 0.0, 0.2, 0.0), (0.2, 0.5, 0.5, 0.5)),
             Rectangle((0.0, 0.0, 0.0, 0.2), (0.2, 0.5, 0.2, 0.5))]

        self.assertSetEqual(set(r), set(idwc(y, z)))

        p1 = (0.0,) * 3
        p2 = (0.5,) * 3
        p3 = (0.2, 0.6, 0.2)
        p4 = (0.2, ) * 3
        p5 = (1.0,) * 3

        z = Rectangle(p1, p2)
        y1 = Rectangle(p1, p3)
        y2 = Rectangle(p4, p5)
        # y_interval = Rectangle
        p6 = (0.2, 0.0, 0.0)
        p7 = (0.2, 0.5, 0.5)

        r1 = [Rectangle(p6, p2), Rectangle((0.0, 0.0, 0.2), p7)]
        r2 = [Rectangle(p1, p7), Rectangle(p6, (0.5, 0.2, 0.5)),
              Rectangle((0.2, 0.2, 0.0), (0.5, 0.5, 0.2))]

        self.assertSetEqual(set(r1), set(idwc(y1, z)))
        self.assertSetEqual(set(r2), set(iuwc(y2, z)))

        self.assertSetEqual(set(), set(idwc(y1, z)) & set(y1 - z))
        self.assertSetEqual(set(), set(iuwc(y2, z)) & set(y2 - z))


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
