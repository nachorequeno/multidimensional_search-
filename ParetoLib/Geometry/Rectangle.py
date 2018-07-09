import __builtin__

import numpy as np
import matplotlib.patches as patches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from itertools import product, tee

from ParetoLib.Geometry.Segment import *
from ParetoLib.Geometry.Point import *


# Rectangle
# Rectangular Half-Space
# Rectangular Cones

class Rectangle:
    # min_corner, max_corner
    def __init__(self,
                 min_corner=(float('-inf'),) * 2,
                 max_corner=(float('-inf'),) * 2):
        # type: (Rectangle, tuple, tuple) -> None
        assert dim(min_corner) == dim(max_corner)

        # self.min_corner = tuple(__builtin__.min(mini, maxi) for mini, maxi in zip(min_corner, max_corner))
        # self.max_corner = tuple(__builtin__.max(mini, maxi) for mini, maxi in zip(min_corner, max_corner))

        self.min_corner = tuple(r(__builtin__.min(mini, maxi)) for mini, maxi in zip(min_corner, max_corner))
        self.max_corner = tuple(r(__builtin__.max(mini, maxi)) for mini, maxi in zip(min_corner, max_corner))

        assert greater_equal(self.max_corner, self.min_corner) or incomparables(self.min_corner, self.max_corner)

    # Membership function
    def __contains__(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        # xpoint is strictly inside the rectangle (i.e., is not along the border)
        return (greater(xpoint, self.min_corner) and
                less(xpoint, self.max_corner))

    def inside(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        # xpoint is inside the rectangle or along the border
        return (greater_equal(xpoint, self.min_corner) and
                less_equal(xpoint, self.max_corner))

    # Printers
    def to_str(self):
        # type: (Rectangle) -> str
        _string = '['
        _string += str(self.min_corner)
        _string += ', '
        _string += str(self.max_corner)
        _string += ']'
        return _string

    def __repr__(self):
        # type: (Rectangle) -> str
        return self.to_str()

    def __str__(self):
        # type: (Rectangle) -> str
        return self.to_str()

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

    def num_vertices(self):
        # type: (Rectangle) -> int
        return int(math.pow(2, self.dim()))

    def vertices(self):
        # type: (Rectangle) -> list
        deltas = self.diag()
        vertex = self.min_corner
        vertices = []
        for i in range(self.num_vertices()):
            delta_index = int_to_bin_tuple(i, self.dim())
            deltai = select(deltas, delta_index)
            temp_vertex = add(vertex, deltai)
            vertices += [temp_vertex]
        assert (len(vertices) == self.num_vertices()), 'Error in the number of vertices'
        return vertices

    def diag_to_segment(self):
        # type: (Rectangle) -> Segment
        return Segment(self.min_corner, self.max_corner)

    def center(self):
        # type: (Rectangle) -> tuple
        offset = div(self.diag(), 2)
        return add(self.min_corner, offset)

    def distance_to_center(self, xpoint):
        # type: (Rectangle, tuple) -> float
        middle_point = self.center()
        euclidean_dist = distance(xpoint, middle_point)
        return euclidean_dist

    def get_points(self, n):
        # type: (Rectangle, int) -> list
        # Return n points along the rectangle diagonal, excluding min/max corners
        # n internal points = n + 1 internal segments
        m = n + 1
        diag_step = div(self.diag(), m)
        min_point = add(self.min_corner, diag_step)
        point_list = [add(min_point, mult(diag_step, i)) for i in range(n)]
        return point_list

    # Geometric operations between two rectangles
    def is_concatenable(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        d = self.dim()
        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)
        # (self != other)
        return (not self.overlaps(other)) \
               and len(vert_self) == len(vert_other) \
               and len(vert_self) == pow(2, d) \
               and len(inter) == pow(2, d - 1)

    def concatenate(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        assert (not self.overlaps(other)), 'Rectangles should not overlap'

        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)
        rect = Rectangle(self.min_corner, self.max_corner)

        # if len(vert_1) == len(vert_2) and \
        #    len(vert_1) == pow(2, d) and \
        #    len(inter) == pow(2, d - 1):
        # if 'self' and 'other' are concatenable
        if self.is_concatenable(other):
            new_union_vertices = (vert_self.union(vert_other)) - inter
            assert len(new_union_vertices) > 0, \
                'Error in computing vertices for the concatenation of "' + str(self) + '" and "' + str(other) + '"'
            rect.min_corner = __builtin__.min(new_union_vertices)
            rect.max_corner = __builtin__.max(new_union_vertices)
        return rect

    def concatenate_update(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        assert (not self.overlaps(other)), 'Rectangles should not overlap'

        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)

        # if 'self' and 'other' are concatenable
        if self.is_concatenable(other):
            new_union_vertices = (vert_self.union(vert_other)) - inter
            assert len(new_union_vertices) > 0, \
                'Error in computing vertices for the concatenation of "' + str(self) + '" and "' + str(other) + '"'
            self.min_corner = __builtin__.min(new_union_vertices)
            self.max_corner = __builtin__.max(new_union_vertices)
        return self

    def overlaps(self, other):
        # type: (Rectangle, Rectangle) -> bool
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        minc = tuple(__builtin__.max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
        maxc = tuple(__builtin__.min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))
        return less(minc, maxc)

    def intersection(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        if self.overlaps(other):
            minc = tuple(__builtin__.max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
            maxc = tuple(__builtin__.min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))
            return Rectangle(minc, maxc)
        else:
            return Rectangle(self.min_corner, self.max_corner)

    def intersection_update(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        if self.overlaps(other):
            self.min_corner = tuple(
                __builtin__.max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
            self.max_corner = tuple(
                __builtin__.min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))

        return self

    __and__ = intersection

    def difference(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        def pairwise(iterable):
            """s -> (s0, s1), (s1, s2), (s2, s3), ..."""
            a, b = tee(iterable)
            next(b, None)
            return zip(a, b)

        inter = self & other
        if inter == self:
            yield self
        else:
            dimension = self.dim()
            d = [None] * dimension
            for i in range(dimension):
                d[i] = {self.min_corner[i], self.max_corner[i]}

            for i in range(dimension):
                if self.min_corner[i] < other.min_corner[i] < self.max_corner[i]:
                    d[i].add(other.min_corner[i])
                if self.min_corner[i] < other.max_corner[i] < self.max_corner[i]:
                    d[i].add(other.max_corner[i])

            elem = (pairwise(sorted(item)) for item in d)
            for vertex in product(*elem):
                # vertex = ((x1, x2), (y1, y2), ...)
                # x1 = min value for coord x
                # x2 = max value for coord x
                minc = tuple(item[0] for item in vertex)
                maxc = tuple(item[1] for item in vertex)
                instance = Rectangle(minc, maxc)
                if instance != inter:
                    yield instance

    __sub__ = difference

    # Domination
    def dominates_point(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        return less_equal(self.max_corner, xpoint)

    def is_dominated_by_point(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        return less_equal(xpoint, self.min_corner)

    def dominates_rect(self, other):
        # type: (Rectangle, Rectangle) -> bool
        # return less_equal(self.max_corner, other.min_corner)
        return less_equal(self.min_corner, other.min_corner) and less_equal(self.max_corner, other.max_corner)

    def is_dominated_by_rect(self, other):
        # type: (Rectangle, Rectangle) -> bool
        return other.dominates_rect(self)

    # Matplot functions
    def toMatplot2D(self, c='red', xaxe=0, yaxe=1, opacity=1.0):
        # type: (Rectangle, str, int, int, float) -> patches.Rectangle
        assert (self.dim() >= 2), 'Dimension required >= 2'
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
        assert (self.dim() >= 3), 'Dimension required >= 3'

        minc = (self.min_corner[xaxe], self.min_corner[yaxe], self.min_corner[zaxe],)
        maxc = (self.max_corner[xaxe], self.max_corner[yaxe], self.max_corner[zaxe],)
        rect = Rectangle(minc, maxc)

        # sorted(vertices) =
        # [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
        points = np.array(sorted(rect.vertices()))

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
        # faces.set_facecolor('r')
        faces.set_facecolor(c)
        faces.set_alpha(opacity)
        return faces


# Auxiliary functions
def cpoint(i, alphai, ypoint, xspace):
    # type: (int, int, tuple, Rectangle) -> Rectangle
    result_xspace = Rectangle(xspace.min_corner, xspace.max_corner)
    if alphai == 0:
        # result_xspace.max_corner[i] = ypoint[i]
        result_xspace.max_corner = subt(i, xspace.max_corner, ypoint)
    if alphai == 1:
        # result_xspace.min_corner[i] = ypoint[i]
        result_xspace.min_corner = subt(i, xspace.min_corner, ypoint)
    return result_xspace


def crect(i, alphai, yrectangle, xspace):
    # type: (int, int, Rectangle, Rectangle) -> Rectangle
    if alphai == 0:
        return cpoint(i, alphai, yrectangle.max_corner, xspace)
    if alphai == 1:
        return cpoint(i, alphai, yrectangle.min_corner, xspace)


#########################################################################################
def bpoint(alpha, ypoint, xspace):
    # type: (tuple, tuple, Rectangle) -> Rectangle
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(ypoint)), \
        'xspace.min_corner and xpoint do not share the same dimension'
    # assert (dim(ypoint.max_corner) == dim(ypoint)), \
    #    'xspace.max_corner and ypoint do not share the same dimension'
    temp = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp = cpoint(i, alphai, ypoint, temp)
    return temp


def brect(alpha, yrectangle, xspace):
    # type: (tuple, Rectangle, Rectangle) -> Rectangle
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        'xrectangle.min_corner and xrectangle.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    assert (dim(alpha) == dim(yrectangle.min_corner)), \
        'alpha and xrectangle.min_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(yrectangle.min_corner)), \
        'xspace.min_corner and xrectangle.min_corner do not share the same dimension'
    # assert (dim(xspace.max_corner) == dim(yrectangle.max_corner)), \
    #    'xspace.max_corner and yrectangle.max_corner do not share the same dimension'
    temp = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp = crect(i, alphai, yrectangle, temp)
    return temp


#########################################################################################
def bpoint2(alpha, ypoint, xspace):
    # type: (tuple, tuple, Rectangle) -> Rectangle
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(ypoint)), \
        'xspace.min_corner and xpoint do not share the same dimension'
    # assert (dim(ypoint.max_corner) == dim(ypoint)), \
    #    'xspace.max_corner and ypoint do not share the same dimension'
    partial_rect = (cpoint(i, alphai, ypoint, xspace) for i, alphai in enumerate(alpha))
    temp = Rectangle(xspace.min_corner, xspace.max_corner)
    for part_rect in partial_rect:
        temp = temp.intersection(part_rect) if temp.overlaps(part_rect) else temp
    return temp


def brect2(alpha, yrectangle, xspace):
    # type: (tuple, Rectangle, Rectangle) -> Rectangle
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        'xrectangle.min_corner and xrectangle.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    assert (dim(alpha) == dim(yrectangle.min_corner)), \
        'alpha and xrectangle.min_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(yrectangle.min_corner)), \
        'xspace.min_corner and xrectangle.min_corner do not share the same dimension'
    # assert (dim(xspace.max_corner) == dim(yrectangle.max_corner)), \
    #    'xspace.max_corner and yrectangle.max_corner do not share the same dimension'

    partial_rect = (crect(i, alphai, yrectangle, xspace) for i, alphai in enumerate(alpha))
    temp = Rectangle(xspace.min_corner, xspace.max_corner)
    for part_rect in partial_rect:
        temp = temp.intersection(part_rect) if temp.overlaps(part_rect) else temp
    return temp


#########################################################################################

def irect(alphaincomp, yrectangle, xspace):
    # type: (list, Rectangle, Rectangle) -> list
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        'xrectangle.min_corner and xrectangle.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    # assert (dim(alphaincomp_list) == dim(yrectangle.min_corner)), \
    #    'alphaincomp_list and yrectangle.min_corner do not share the same dimension'
    # assert (dim(alphaincomp_list) == dim(yrectangle.max_corner)), \
    #    'alphaincomp_list and yrectangle.max_corner do not share the same dimension'
    return [brect(alphaincomp_i, yrectangle, xspace) for alphaincomp_i in alphaincomp]
