__version__ = 1.
__name__ = 'ParetoLib'
__all__ = ['Geometry', 'Oracle', 'Search']


# -------------------------------------------------------------------------------

class MissingExtDependencyError(Exception):
    """
    Missing an external dependency. Used for our unit tests to allow skipping
    tests with missing external dependencies, e.g. missing command line tools.
    """
    pass

# -------------------------------------------------------------------------------
