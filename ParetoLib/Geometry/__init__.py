import sys
from math import log, floor

__version__ = 1.
__name__ = 'Geometry'
__all__ = ['Segment', 'Rectangle', 'ParRectangle', 'Point', 'PPoint']

# Maximum number of decimal digits that should be used in computations.
# This value depends on the accurary (i.e., number of bits) used for float representations.
__numdigits__ = int(floor(abs(log(sys.float_info.epsilon, 10))))
