__version__=1.

#-------------------------------------------------------------------------------

class MissingExtDependencyError ( Exception ) :
    """
    Missing an external dependency. Used for our unit tests to allow skipping
    tests with missing external dependencies, e.g. missing command line tools.
    """
    pass


#-------------------------------------------------------------------------------