import math
from multiprocessing import Pool, cpu_count, Process, Queue

from functools import reduce
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D

from segment import *
from point import *

# Rectangle
# Rectangular Half-Space
# Rectangular Cones

class Rectangle:
    # min_corner, max_corner
    def __init__(self, min_corner, max_corner):
        # type: (Rectangle, tuple, tuple) -> None
        assert dim(min_corner) == dim(max_corner)
        if incomparable(min_corner, max_corner):
            min_c = min_corner if min_corner[0] <= max_corner[0] else max_corner
            max_c = max_corner if min_corner[0] <= max_corner[0] else min_corner
            self.min_corner = min_c
            self.max_corner = max_c
            # self.min_corner = min_corner
            # self.max_corner = max_corner
        else:
            self.min_corner = min(min_corner, max_corner)
            self.max_corner = max(min_corner, max_corner)
            assert greater_equal(self.max_corner, self.min_corner)

    # Membership function
    def __contains__(self, xpoint):
        # type: (Rectangle, tuple) -> bool
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

    # Matplot functions
    def toMatplot(self, c='red', xaxe=0, yaxe=1, opacity=1.0):
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

        minc = (self.min_corner[xaxe], self.min_corner[yaxe], self.min_corner[zaxe], )
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
def cpoint(i, alphai, xpoint, xspace):
    # type: (int, int, tuple, Rectangle) -> Rectangle
    result_xspace = Rectangle(xspace.min_corner, xspace.max_corner)
    if alphai == 0:
        result_xspace.max_corner = subt(i, xspace.max_corner, xpoint)
        # result_xspace.min_corner = xspace.min_corner
    if alphai == 1:
        # result_xspace.max_corner = xspace.max_corner
        result_xspace.min_corner = subt(i, xspace.min_corner, xpoint)
    return result_xspace


def crect(i, alphai, xrectangle, xspace):
    # type: (int, int, Rectangle, Rectangle) -> Rectangle
    if alphai == 0:
        return cpoint(i, alphai, xrectangle.max_corner, xspace)
    if alphai == 1:
        return cpoint(i, alphai, xrectangle.min_corner, xspace)


def bpoint(alpha, xpoint, xspace):
    # type: (tuple, tuple, Rectangle) -> Rectangle
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xpoint)), \
        "xspace.min_corner and xpoint do not share the same dimension"
    # assert (dim(xspace.max_corner) == dim(xpoint)), \
    #    "xspace.max_corner and xpoint do not share the same dimension"
    temp1 = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp2 = cpoint(i, alphai, xpoint, temp1)
        temp1 = temp2
    return temp1


def brect(alpha, xrectangle, xspace):
    # type: (tuple, Rectangle, Rectangle) -> Rectangle
    assert (dim(xrectangle.min_corner) == dim(xrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    assert (dim(alpha) == dim(xrectangle.min_corner)), \
        "alpha and xrectangle.min_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xrectangle.min_corner)), \
        "xspace.min_corner and xrectangle.min_corner do not share the same dimension"
    # assert (dim(xspace.max_corner) == dim(xrectangle.max_corner)), \
    #    "xspace.max_corner and xrectangle.max_corner do not share the same dimension"
    temp1 = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp2 = crect(i, alphai, xrectangle, temp1)
        temp1 = temp2
    return temp1


def pbrect(queue, alpha, xrectangle, xspace):
    # type: (Queue, tuple, Rectangle, Rectangle) -> None
    queue.put(brect(alpha, xrectangle, xspace))


def irect(alphaincomp, xrectangle, xspace):
    # type: (set, Rectangle, Rectangle) -> set
    assert (dim(xrectangle.min_corner) == dim(xrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(xrectangle.min_corner)), \
    #    "alphaincomp_list and xrectangle.min_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(xrectangle.max_corner)), \
    #    "alphaincomp_list and xrectangle.max_corner do not share the same dimension"
    return set(brect(alphaincomp_i, xrectangle, xspace) for alphaincomp_i in alphaincomp)

nproc = cpu_count()
pool = Pool(nproc)

def pirect(alphaincomp, xrectangle, xspace):
    # type: (set, Rectangle, Rectangle) -> set
    assert (dim(xrectangle.min_corner) == dim(xrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(xrectangle.min_corner)), \
    #    "alphaincomp_list and xrectangle.min_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(xrectangle.max_corner)), \
    #    "alphaincomp_list and xrectangle.max_corner do not share the same dimension"
    #nproc = cpu_count()
    #pool = Pool(nproc)
    processes = []
    rets = []
    q = Queue()

    for alphaincomp_i in alphaincomp:
        p = Process(target=pbrect, args=(q, alphaincomp_i, xrectangle, xspace))
        processes.append(p)
        p.start()
        if len(processes) > nproc:
            for p in processes:
                ret = q.get()  # will block
                rets.append(ret)
            for p in processes:
                p.join()

    for p in processes:
        ret = q.get()  # will block
        rets.append(ret)
    for p in processes:
        p.join()
    return set(rets)


def pirect2(alphaincomp, xrectangle, xspace):
    # type: (set, Rectangle, Rectangle) -> set
    assert (dim(xrectangle.min_corner) == dim(xrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(xrectangle.min_corner)), \
    #    "alphaincomp_list and xrectangle.min_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(xrectangle.max_corner)), \
    #    "alphaincomp_list and xrectangle.max_corner do not share the same dimension"
    #nproc = cpu_count()
    #pool = Pool(nproc)
    parallel_results = [pool.apply_async(brect, args=(alphaincomp_i, xrectangle, xspace)) for alphaincomp_i in
                        alphaincomp]
    pool.close()
    pool.join()
    res = set()
    for pres in parallel_results:
        res.add(pres.get())
    return res
