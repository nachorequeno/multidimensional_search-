import sys

__version__ = 1.
__name__ = "Oracle"
__all__ = ["NDTree", "Oracle", "OracleFunction", "OraclePoint", "OracleSTL"]
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
    vprint = lambda *a: None  # do-nothing function
    eprint = lambda *a: None  # do-nothing function
