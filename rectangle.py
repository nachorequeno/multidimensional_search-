from segment import *
from functools import reduce
import math

import matplotlib.patches as patches

# Rectangle
# Rectangular Half-Space
# Rectangular Cones

class Rectangle:
    # min_corner, max_corner
    def __init__(self, min_corner, max_corner):
        assert dim(min_corner) == dim(max_corner)
        if incomparable(min_corner, max_corner):
            self.min_corner = min_corner
            self.max_corner = max_corner
        else:
            self.min_corner = min(min_corner, max_corner)
            self.max_corner = max(min_corner, max_corner)
            assert greater_equal(self.max_corner, self.min_corner)

    # Membership function
    def __contains__(self, xpoint):
        return (greater_equal(xpoint, self.min_corner) and
                less_equal(xpoint, self.max_corner))

    # Printers
    def toStr(self):
        _string = "["
        _string += str(self.min_corner)
        _string += ', '
        _string += str(self.max_corner)
        _string += "]"
        return _string

    def __repr__(self):
        return self.toStr()

    def __str__(self):
        return self.toStr()

    # Equality functions
    def __eq__(self, other):
        return (other.min_corner == self.min_corner) and (other.max_corner == self.max_corner)

    def __ne__(self, other):
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        return hash((self.min_corner, self.max_corner))

    # Rectangle properties
    def dim(self):
        return dim(self.min_corner)

    def diag(self):
        return subtract(self.max_corner, self.min_corner)

    def norm(self):
        diagonal = self.diag()
        square_diagonal = map(lambda si: si * si, diagonal)
        _sum = reduce(lambda si, sj: si + sj, square_diagonal)
        return math.sqrt(_sum)

    def volume(self):
        diagonal = self.diag()
        _prod = reduce(lambda si, sj: si * sj, diagonal)
        return abs(_prod)

    def numVertices(self):
        return int(math.pow(2, self.dim()))

    def vertices(self):
        deltas = self.diag()
        vertex = self.min_corner
        vertices = [] * self.numVertices()
        for i in range(self.numVertices()):
            delta_index = int2bintuple(i, self.dim())
            deltai = select(delta_index, deltas)
            temp_vertex = add(vertex, deltai)
            vertices += [temp_vertex]
        assert (len(vertices) == self.numVertices()), "Error in the number of vertices"
        return vertices

    def diagToSegment(self):
        return Segment(self.min_corner, self.max_corner)

    # GnuPlot functions
    def toGnuPlot(self, xaxe=0, yaxe=1):
        #string1 = 'rect from ' + str(self.min_corner) + ' to ' + str(self.max_corner) + ' fs empty border 1'
        #string1 = 'rect from ' + str(self.min_corner) + ' to ' + str(self.max_corner) + ' fc lt 1'
        #string1 = 'rect from ' + str(self.min_corner) + ' to ' + str(self.max_corner)
        minc = (self.min_corner[xaxe], self.min_corner[yaxe],)
        maxc = (self.max_corner[xaxe], self.max_corner[yaxe],)
        string1 = 'rect from ' + str(minc) + ' to ' + str(maxc)
        string2 = string1.replace("(", "")
        string = string2.replace(")", "")
        return string

    def toGnuPlotColor(self, color):
        return 'fc rgb \"' + color + '\"'
        #return 'fc lt 1 rgb \"' + color + '\"'

    def toGnuPlotXrange(self, index=0):
        return 'xrange[' + str(self.min_corner[index]) + ':' + str(self.max_corner[index]) + ']'

    def toGnuPlotYrange(self, index=1):
        return 'yrange[' + str(self.min_corner[index]) + ':' + str(self.max_corner[index]) + ']'

    # Matplot functions
    def toMatplot(self, c='red', xaxe=0, yaxe=1):
        assert (self.dim() >= 2), "Dimension required >= 2"
        mc = (self.min_corner[xaxe], self.min_corner[yaxe], )
        width = self.diag()[xaxe]
        height = self.diag()[yaxe]
        return patches.Rectangle(
            mc,  # (x,y)
            width,  # width
            height,  # height
            #color = c, #color
            facecolor = c,  # face color
            edgecolor = 'black'  # edge color
        )
# Auxiliary functions
def cpoint(i, alphai, xpoint, xspace):
    result_xspace = Rectangle(xspace.min_corner, xspace.max_corner)
    if alphai == 0:
        result_xspace.max_corner = subt(i, xspace.max_corner, xpoint)
        #result_xspace.min_corner = xspace.min_corner
    if alphai == 1:
        #result_xspace.max_corner = xspace.max_corner
        result_xspace.min_corner = subt(i, xspace.min_corner, xpoint)
    return result_xspace


def crect(i, alphai, xrectangle, xspace):
    if alphai == 0:
        return cpoint(i, alphai, xrectangle.max_corner, xspace)
    if alphai == 1:
        return cpoint(i, alphai, xrectangle.min_corner, xspace)


def bpoint(alpha, xpoint, xspace):
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xpoint)), \
        "xspace.min_corner and xpoint do not share the same dimension"
    #assert (dim(xspace.max_corner) == dim(xpoint)), \
    #    "xspace.max_corner and xpoint do not share the same dimension"
    temp1 = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp2 = cpoint(i, alphai, xpoint, temp1)
        temp1 = temp2
    return temp1


def brect(alpha, xrectangle, xspace):
    assert (dim(xrectangle.min_corner) == dim(xrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    assert (dim(alpha) == dim(xrectangle.min_corner)), \
        "alpha and xrectangle.min_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xrectangle.min_corner)), \
        "xspace.min_corner and xrectangle.min_corner do not share the same dimension"
    #assert (dim(xspace.max_corner) == dim(xrectangle.max_corner)), \
    #    "xspace.max_corner and xrectangle.max_corner do not share the same dimension"
    temp1 = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp2 = crect(i, alphai, xrectangle, temp1)
        temp1 = temp2
    return temp1


def irect(alphaincomp_list, xrectangle, xspace):
    assert (dim(xrectangle.min_corner) == dim(xrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    #assert (dim(alphaincomp_list) == dim(xrectangle.min_corner)), \
    #    "alphaincomp_list and xrectangle.min_corner do not share the same dimension"
    #assert (dim(alphaincomp_list) == dim(xrectangle.max_corner)), \
    #    "alphaincomp_list and xrectangle.max_corner do not share the same dimension"
    return set(brect(alphaincomp_i, xrectangle, xspace) for alphaincomp_i in alphaincomp_list)
