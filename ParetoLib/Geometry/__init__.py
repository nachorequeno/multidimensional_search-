import sys
from math import log, floor

__version__ = 1.
__name__ = "Geometry"
__all__ = ["Segment", "Rectangle", "pRectangle", "Point", "PPoint"]
__verbose__ = False

# Maximum number of decimal digits that should be used in computations.
# This value depends on the accurary (i.e., number of bits) used for float representations.
__numdigits__ = int(floor(abs(log(sys.float_info.epsilon, 10))))

if __verbose__:
    # Verbose print (stdout)
    def vprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        for arg in args:
            print arg,
        print


    # Error print (stderr)
    def eprint(*args):
        for arg in args:
            print >> sys.stderr, arg
        print >> sys.stderr

else:
    vprint = lambda *a: None  # do-nothing function
    eprint = lambda *a: None  # do-nothing function
