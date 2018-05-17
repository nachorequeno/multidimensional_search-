from multiprocessing import Pool, cpu_count

from ParetoLib.Geometry.Rectangle import *

############################################################################
# Parallel version for the computation of incomparable rectangles in a space
############################################################################

def pbrect(args):
    alpha, yrectangle, xspace = args
    return brect(alpha, yrectangle, xspace)


def pirect(alphaincomp, yrectangle, xspace):
    # type: (list, Rectangle, Rectangle) -> list
    ## type: (set, Rectangle, Rectangle) -> list
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        "xrectangle.min_corner and xrectangle.max_corner do not share the same dimension"
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        "xspace.min_corner and xspace.max_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(yrectangle.min_corner)), \
    #    "alphaincomp_list and yrectangle.min_corner do not share the same dimension"
    # assert (dim(alphaincomp_list) == dim(yrectangle.max_corner)), \
    #    "alphaincomp_list and yrectangle.max_corner do not share the same dimension"

    nproc = cpu_count()
    pool = Pool(nproc)

    args_i = ((alphaincomp_i, yrectangle, xspace) for alphaincomp_i in alphaincomp)
    #parallel_results = pool.map(pbrect, args_i)
    parallel_results = pool.imap_unordered(pbrect, args_i)

    # Stop multiprocessing
    pool.close()
    pool.join()

    return parallel_results

#############################################################################################
# Wrappers for methods of the Rectangle class.
# The "multiprocessing" library requires "pickable" methods for the parallelization of tasks;
# i.e., these wrappers.
#############################################################################################

def pvol(rect):
    # type: (Rectangle) -> float
    return rect.volume()

def pvertices(rect):
    # type: (Rectangle) -> list
    return rect.vertices()

def pinside(args):
    rect, xpoint = args
    return rect.inside(xpoint)
