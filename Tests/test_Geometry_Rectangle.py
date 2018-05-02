from ParetoLib.Geometry.Segment import *
from ParetoLib.Geometry.Rectangle import *

#def testSegment():
#    x = (1.0,) * 2
#    y = (2.0,) * 2
#    xy = Segment(x, y)


def testRectangle():
    r1 = Rectangle()
    r2 = Rectangle()

    assert (r1 == r2), \
        "Comparison of Rectangle failed. Expected to be equal:\n(r1, r2) = (%s, %s)" % (str(r1), str(r2))

    p1 = (0.0, 0.75)
    p2 = (1.0, 1.75)
    r1 = Rectangle(p1, p2)

    p3 = (0.5, 0.0)
    p4 = (1.5, 1.0)
    r2 = Rectangle(p3, p4)

    p5 = (1.0, 1.0)
    p6 = (2.0, 2.0)
    r3 = Rectangle(p5, p6)

    # Equality
    assert (r1 != r2), \
        "Comparison of Rectangle failed. Expected to be different:\n(r1, r2) = (%s, %s)" % (str(r1), str(r2))

    assert (r1 != r3), \
        "Comparison of Rectangle failed. Expected to be different:\n(r1, r3) = (%s, %s)" % (str(r1), str(r3))

    assert (r2 != r3), \
        "Comparison of Rectangle failed. Expected to be different:\n(r2, r3) = (%s, %s)" % (str(r2), str(r3))

    dist_p5 = r3.distanceToCenter(p5)
    dist_p6 = r3.distanceToCenter(p6)

    # Distance to center
    assert (dist_p5 == dist_p6), \
        "Distance to center failed. Expected to be equal:\n(p5, p6) = (%s, %s)\nr3 = %s\ndist(p5)=%s\ndist(p6) = (%s)" \
        % (str(p5), str(p6), str(r3), str(dist_p5), str(dist_p6))

    p1_intersect = (0.5, 0.75)
    p2_intersect = (1.0, 1.0)
    r_intersect_expected = Rectangle(p1_intersect, p2_intersect)
    r_intersect = r1.intersection(r2)

    # Intersection of Rectangles
    assert (r1.overlaps(r2)), \
        "Overlapping of Rectangle failed. Expected to be true:\n(r1, r2) = (%s, %s)" % (str(r1), str(r2))

    assert (r_intersect == r_intersect_expected), \
        "Intersection of Rectangle failed. Expected to be equal:\n(r1, r2) = (%s, %s)" \
        % (str(r_intersect), str(r_intersect_expected))

    # Volumes
    assert (r1.volume() == r2.volume()), \
        "Comparison of volume failed. Expected r1.volume == r2.volume = (%s, %s)" % (str(r1.volume()), str(r2.volume()))

    assert (r3.volume() == r1.volume()), \
        "Comparison of volume failed. Expected r3.volume == r1.volume = (%s, %s)" % (str(r3.volume()), str(r1.volume()))

    assert (r3.volume() == r2.volume()), \
        "Comparison of volume failed. Expected r3.volume == r2.volume = (%s, %s)" % (str(r3.volume()), str(r2.volume()))

    assert (r1.volume() > r_intersect.volume()), \
        "Comparison of volume failed. Expected r1.volume > r_intersect.volume = (%s, %s)"\
        % (str(r1.volume()), str(r2.volume()))

    assert (r2.volume() > r_intersect.volume()), \
        "Comparison of volume failed. Expected r2.volume > r_intersect.volume = (%s, %s)"\
        % (str(r2.volume()), str(r_intersect.volume()))

    p1 = (0.0, 0.0)
    p2 = (1.0, 1.0)
    r = Rectangle(p1, p2)
    vertices = r.vertices()
    expected_vertices = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]

    # Vertices
    assert (vertices == expected_vertices), \
        "Comparison of vertices failed. Expected to be equal:\nVertices_1 = %s\nVertices_2 = %s)" \
        % (str(vertices), str(expected_vertices))

    num_vertices = r.numVertices()
    num_vertices_expected = len(expected_vertices)
    assert (num_vertices == num_vertices_expected), \
        "Comparison of num_vertices failed. Expected to be equal:\nnVertices_1 = %s\nnVertices_2 = %s)" \
        % (str(num_vertices), str(num_vertices_expected))

if __name__ == '__main__':
    #testSegment()
    testRectangle()
