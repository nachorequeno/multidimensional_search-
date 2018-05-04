import __builtin__
from multiprocessing import Pool, cpu_count, Process, Queue
# from multiprocessing import Process, Queue

import numpy as np
import matplotlib.patches as patches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from ParetoLib.Geometry.Segment import *
from ParetoLib.Geometry.Point import *


# import ParetoLib.Geometry.Point

# Rectangle
# Rectangular Half-Space
# Rectangular Cones

class Rectangle:
    # min_corner, max_corner
    def __init__(self,
                 min_corner=(float("-inf"),) * 2,
                 max_corner=(float("-inf"),) * 2):
        # type: (Rectangle, tuple, tuple) -> None
        assert dim(min_corner) == dim(max_corner)

        self.min_corner = tuple(__builtin__.min(mini, maxi) for mini, maxi in zip(min_corner, max_corner))
        self.max_corner = tuple(__builtin__.max(mini, maxi) for mini, maxi in zip(min_corner, max_corner))

        assert greater_equal(self.max_corner, self.min_corner) or \
               incomparable(self.min_corner, self.max_corner)

    # Membership function
    def __contains__(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        # xpoint is strictly inside the rectangle (i.e., is not along the border)
        return (not incomparable(xpoint, self.min_corner) and
                not incomparable(xpoint, self.max_corner) and
                greater(xpoint, self.min_corner) and
                less(xpoint, self.max_corner))

    def inside(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        # xpoint is inside the rectangle or along the border
        return (not incomparable(xpoint, self.min_corner) and
                not incomparable(xpoint, self.max_corner) and
                greater_equal(xpoint, self.min_corner) and
                less_equal(xpoint, self.max_corner))

    # Printers
    def toStr(self):
        # type: (Rectangle) -> str
        _string = "["
        _string += str(self.min_corner)
        _string += ', '
        _string += str(self.max_corner)
        _string += "]"
        return _string

    def __repr__(self):
        # type: (Rectangle) -> str
        return self.toStr()

    def __str__(self):
        # type: (Rectangle) -> str
        return self.toStr()

    # Equality functions
    def __eq__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        return (other.min_corner == self.min_corner) and (other.max_corner == self.max_corner)

    def __ne__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Rectangle) -> int
        return hash((self.min_corner, self.max_corner))

    # Rectangle properties
    def dim(self):
        # type: (Rectangle) -> int
        return dim(self.min_corner)

    def diag(self):
        # type: (Rectangle) -> tuple
        return subtract(self.max_corner, self.min_corner)

    def norm(self):
        # type: (Rectangle) -> float
        diagonal = self.diag()
        return norm(diagonal)

    def volume(self):
        # type: (Rectangle) -> float
        diagonal = self.diag()
        _prod = reduce(lambda si, sj: si * sj, diagonal)
        return abs(_prod)

    def numVertices(self):
        # type: (Rectangle) -> int
        return int(math.pow(2, self.dim()))

    def vertices(self):
        # type: (Rectangle) -> list
        deltas = self.diag()
        vertex = self.min_corner
        vertices = []
        for i in range(self.numVertices()):
            delta_index = int2bintuple(i, self.dim())
            deltai = select(deltas, delta_index)
            temp_vertex = add(vertex, deltai)
            vertices += [temp_vertex]
        assert (len(vertices) == self.numVertices()), "Error in the number of vertices"
        return vertices

    def diagToSegment(self):
        # type: (Rectangle) -> Segment
        return Segment(self.min_corner, self.max_corner)

    def center(self):
        # type: (Rectangle) -> tuple
        offset = div(self.diag(), 2)
        return add(self.min_corner, offset)

    def distanceToCenter(self, xpoint):
        # type: (Rectangle, tuple) -> float
        middle_point = self.center()
        euclidean_dist = distance(xpoint, middle_point)
        return euclidean_dist

    def getPoints(self, n):
        # type: (Rectangle, int) -> list
        # Return n points along the rectangle diagonal, excluding min/max corners
        # n internal points = n + 1 internal segments
        m = n + 1
        diag_step = div(self.diag(), m)
        min_point = add(self.min_corner, diag_step)
        point_list = [add(min_point, mult(diag_step, i)) for i in range(n)]
        return point_list

    #    def overlapsStrict(self, other):
    #        # type: (Rectangle, Rectangle) -> bool
    #        other_vertices = other.vertices()
    #        other_vertices_inside_self = [other_vertex for other_vertex in other_vertices if other_vertex in self]
    #        other_overlaps_self = any([other_vertex in self for other_vertex in other_vertices])
    #
    #        self_vertices = self.vertices()
    #        self_vertices_inside_other = [self_vertex for self_vertex in self_vertices if self_vertex in other]
    #        self_overlaps_other = any([self_vertex in other for self_vertex in self_vertices])
    #        return len(other_vertices_inside_self) > 0 and \
    #               len(self_vertices_inside_other) > 0 and \
    #               other_overlaps_self and \
    #               self_overlaps_other

    def overlaps(self, other):
        # type: (Rectangle, Rectangle) -> bool
        other_vertices = other.vertices()
        overlap = any([other_vertex in self for other_vertex in other_vertices])
        # overlap = any([self.strictIn(other_vertex) for other_vertex in other_vertices])
        return overlap

    def intersection(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        # Create a default rectangle of area/volume = 0
        # minc = (float("-inf"), ) * self.dim()
        # maxc = (float("-inf"), ) * self.dim()
        minc = (float(0),) * self.dim()
        maxc = (float(0),) * self.dim()

        # if self.overlapsStrict(other):
        if self.overlaps(other):
            # At least, one vertex of each rectangle is inside the other rectangle
            other_vertices = other.vertices()
            # other_vertices_inside_self = [other_vertex for other_vertex in other_vertices if self.strictIn(other_vertex)]
            other_vertices_inside_self = [other_vertex for other_vertex in other_vertices if other_vertex in self]

            self_vertices = self.vertices()
            # self_vertices_inside_other = [self_vertex for self_vertex in self_vertices if other.strictIn(self_vertex)]
            self_vertices_inside_other = [self_vertex for self_vertex in self_vertices if self_vertex in other]
            minc = self_vertices_inside_other[0]
            maxc = other_vertices_inside_self[0]

        r = Rectangle(minc, maxc)
        return r

    # Matplot functions
    def toMatplot2D(self, c='red', xaxe=0, yaxe=1, opacity=1.0):
        # type: (Rectangle, str, int, int, float) -> patches.Rectangle
        assert (self.dim() >= 2), "Dimension required >= 2"
        mc = (self.min_corner[xaxe], self.min_corner[yaxe],)
        width = self.diag()[xaxe]
        height = self.diag()[yaxe]
        return patches.Rectangle(
            mc,  # (x,y)
            width,  # width
            height,  # height
            # color = c, #color
            facecolor=c,  # face color
            edgecolor='black',  # edge color
            alpha=opacity
        )

    def toMatplot3D(self, c='red', xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (Rectangle, str, int, int, int, float) -> Poly3DCollection
        assert (self.dim() >= 3), "Dimension required >= 3"

        minc = (self.min_corner[xaxe], self.min_corner[yaxe], self.min_corner[zaxe],)
        maxc = (self.max_corner[xaxe], self.max_corner[yaxe], self.max_corner[zaxe],)
        r = Rectangle(minc, maxc)

        # sorted(vertices) =
        # [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
        points = np.array(sorted(r.vertices()))

        edges = [
            [points[0], points[1], points[3], points[2]],
            [points[2], points[3], points[7], points[6]],
            [points[6], points[4], points[5], points[7]],
            [points[4], points[5], points[1], points[0]],
            [points[0], points[4], points[6], points[2]],
            [points[1], points[5], points[7], points[3]]
        ]

        faces = Poly3DCollection(edges, linewidths=1, edgecolors='k')
        # faces.set_facecolor((0,0,1,0.1))
        # faces.set_facecolor("r")
        faces.set_facecolor(c)
        faces.set_alpha(opacity)
        return faces


# Auxiliary functions
def cpoint(i, alphai, ypoint, xspace):
    # type: (int, int, tuple, Rectangle) -> Rectangle
    result_xspace = Rectangle(xspace.min_corner, xspace.max_corner)
    if alphai == 0:
        result_xspace.max_corner = subt(i, xspace.max_corner, ypoint)
        # result_xspace.min_corner = xspace.min_corner
    if alphai == 1:
        # result_xspace.max_corner = xspace.max_corner
        result_xspace.min_corner = subt(i, xspace.min_corner, ypoint)
    return result_xspace


def crect(i, alphai, yrectangle, xspace):
    # type: (int, int, Rectangle, Rectangle) -> Rectangle
    if alphai == 0:
        return cpoint(i, alphai, yrectangle.max_corner, xspace)
    if alphai == 1:
        return cpoint(i, alphai, yrectangle.min_corner, xspace)


def bpoint(alpha, ypoint, xspace):
    # type: (tuple, tuple, Rectangle) -> Rectangle
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(ypoint)), \
        "xspace.min_corner and xpoint do not share the same dimension"
    # assert (dim(ypoint.max_corner) == dim(ypoint)), \
    #    "xspace.max_corner and ypoint do not share the same dimension"
    temp1 = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp2 = cpoint(i, alphai, ypoint, temp1)
        temp1 = temp2
    return temp1


def brect(alpha, yrectangle, xspace):
    # type: (tuple, Rectangle, Rectangle) -> Rectangle
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    assert (dim(alpha) == dim(yrectangle.min_corner)), \
        "alpha and xrectangle.min_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(yrectangle.min_corner)), \
        "xspace.min_corner and xrectangle.min_corner do not share the same dimension"
    # assert (dim(xspace.max_corner) == dim(yrectangle.max_corner)), \
    #    "xspace.max_corner and yrectangle.max_corner do not share the same dimension"
    temp1 = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp2 = crect(i, alphai, yrectangle, temp1)
        temp1 = temp2
    return temp1


def irect(alphaincomp, yrectangle, xspace):
    # type: (set, Rectangle, Rectangle) -> list
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(yrectangle.min_corner)), \
    #    "alphaincomp_list and yrectangle.min_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(yrectangle.max_corner)), \
    #    "alphaincomp_list and yrectangle.max_corner do not share the same dimension"
    return [brect(alphaincomp_i, yrectangle, xspace) for alphaincomp_i in alphaincomp]


def pirect(alphaincomp, yrectangle, xspace):
    # type: (set, Rectangle, Rectangle) -> list
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(yrectangle.min_corner)), \
    #    "alphaincomp_list and yrectangle.min_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(yrectangle.max_corner)), \
    #    "alphaincomp_list and yrectangle.max_corner do not share the same dimension"
    nproc = cpu_count()
    pool = Pool(nproc)
    parallel_results = [pool.apply_async(brect, args=(alphaincomp_i, yrectangle, xspace))
                        for alphaincomp_i in alphaincomp]
    pool.close()
    pool.join()
    return [pres.get() for pres in parallel_results]
