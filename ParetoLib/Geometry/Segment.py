import math

from ParetoLib.Geometry.Point import maximum, minimum, greater_equal, less_equal
import ParetoLib.Geometry.Point as Point


class Segment:
    # l, h are points
    def __init__(self, low, high):
        # type: (Segment, tuple, tuple) -> None
        self.low = minimum(low, high)
        self.high = maximum(low, high)
        assert Point.dim(self.low) == Point.dim(self.high)
        assert greater_equal(self.high, self.low)

    # Membership function
    def __contains__(self, xpoint):
        # type: (Segment, tuple) -> bool
        return (greater_equal(xpoint, self.low) and
                less_equal(xpoint, self.high))

    # Printers
    def to_str(self):
        # type: (Segment) -> str
        # _string = '('
        # for i, data in enumerate(self.l):
        #    _string += str(data)
        #    if i != dim(self.l) - 1:
        #        _string += ', '
        # _string += ')'
        _string = '<'
        _string += str(self.low)
        _string += ', '
        _string += str(self.high)
        _string += '>'
        return _string

    def __repr__(self):
        # type: (Segment) -> str
        return self.to_str()

    def __str__(self):
        # type: (Segment) -> str
        return self.to_str()

    # Equality functions
    def __eq__(self, other):
        # type: (Segment) -> bool
        return (other.low == self.low) and (other.high == self.high)

    def __ne__(self, other):
        # type: (Segment) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Segment) -> float
        return hash((self.low, self.high))

    # Segment properties
    def dim(self):
        # type: (Segment) -> int
        return Point.dim(self.low)

    # def __len__(self):
    def diag(self):
        # type: (Segment) -> tuple
        return Point.subtract(self.high, self.low)

    def norm(self):
        # type: (Segment) -> float
        diagonal = self.diag()
        return Point.norm(diagonal)

    def norm2(self):
        # type: (Segment) -> float
        diagonal = self.diag()
        square_diagonal = tuple(di * di for di in diagonal)
        _sum = sum(square_diagonal)
        return math.sqrt(_sum)
