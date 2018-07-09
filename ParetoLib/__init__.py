import sys

__version__ = 1.
__name__ = 'ParetoLib'
__all__ = ['Geometry', 'Oracle', 'Search']
__verbose__ = False

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
    # do-nothing function
    def vprint(*args):
        pass


    # do-nothing function
    def eprint(*args):
        pass


# -------------------------------------------------------------------------------

class MissingExtDependencyError(Exception):
    """
    Missing an external dependency. Used for our unit tests to allow skipping
    tests with missing external dependencies, e.g. missing command line tools.
    """
    pass

# -------------------------------------------------------------------------------
