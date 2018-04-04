# from collections import namedtuple
# Particle = namedtuple('Particle', 'mass position velocity force')
# p = Particle(1, 2, 3, 4)
# print p.velocity

# import numpy
from point import *
from functools import reduce
import math
import time

import matplotlib.pyplot as plt
import matplotlib.lines as lines

# Segment
class Segment:
    # l, h are points
    def __init__(self, low, high):
        self.l = min(low,high)
        self.h = max(low,high)
        assert dim(self.l) == dim(self.h)
        assert greater_equal(self.h, self.l)

    # Membership function
    def __contains__(self, xpoint):
        return (greater_equal(xpoint, self.l) and
                less_equal(xpoint, self.h))

    # Printers
    def toStr(self):
        # _string = "("
        # for i, data in enumerate(self.l):
        #    _string += str(data)
        #    if i != dim(self.l) - 1:
        #        _string += ", "
        # _string += ")"
        _string = "<"
        _string += str(self.l)
        _string += ', '
        _string += str(self.h)
        _string += ">"
        return _string

    def __repr__(self):
        return self.toStr()

    def __str__(self):
        return self.toStr()

    # Equality functions
    def __eq__(self, other):
        return (other.l == self.l) and (other.h == self.h)

    def __ne__(self, other):
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        return hash((self.l, self.h))

    # Segment properties
    def dim(self):
        return dim(self.l)

    #def __len__(self):
    def diag(self):
        return subtract(self.h, self.l)

    def norm(self):
        diagonal = self.diag()
        square_diagonal = map(lambda si: si * si, diagonal)
        _sum = reduce(lambda si, sj: si + sj, square_diagonal)
        return math.sqrt(_sum)
