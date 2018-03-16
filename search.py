from rectangle import *
import itertools
from resultset import *

EPS = 1e-5
DELTA = 1e-5

def metric(lset):
    # lsizes = map(lambda item: item.norm(), lset)
    lsizes = map(lambda item: item.volume(), lset)
    return reduce(lambda x, y: x + y, lsizes)

def staircase_oracle(xs, ys):
    return lambda p: any(p[0] >= x and p[1] >= y for x, y in zip(xs, ys))

#TODO: Consider that (x,y) is inside rectangle rect
#TODO: Consider that (p0,p1) is close to (x,y): for instance, less than a 'delta'
def membership_oracle(xs, ys, rect):
    return lambda p: any(p[0] == x and p[1] == y for x, y in zip(xs, ys))

def search(x, member, epsilon=EPS):
    # x, y = segments
    y = x
    error = (epsilon,) * x.dim()
    while greater_equal(y.diag(), error):
        yval = div(add(y.l, y.h), 2)
        # We need a oracle() for guiding the search
        if member(yval):
            y.h = yval
        else:
            y.l = yval
    return y


# The search returns a set of Rectangles in Yup, Ylow and Border
def algorithm_2(xspace,
                oracle,
                epsilon=EPS,
                delta=DELTA,
                verbose=False):
    if verbose:
        def vprint(*args):
            # Print each argument separately so caller doesn't need to
            # stuff everything to be printed into a single string
            for arg in args:
                print arg,
    #        print
    else:
        vprint = lambda *a: None  # do-nothing function

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n
    # Dimension
    n = xspace.dim()

    # Alpha in [0,1]^n
    alphaprime = (range(2),) * n
    alpha = set(itertools.product(*alphaprime))

    # Particular cases of alpha
    # zero = (0_1,...,0_n)    random.uniform(min_corner, max_corner)
    zero = (0,) * n
    # one = (1_1,...,1_n)
    one = (1,) * n

    # Set of comparable and incomparable rectangles
    # comparable = set(filter(lambda x: all(x[i]==x[i+1] for i in range(len(x)-1)), alpha))
    # incomparable = list(filter(lambda x: x[0]!=x[1], alpha))
    comparable = set()
    comparable.add(zero)
    comparable.add(one)
    incomparable = alpha.difference(comparable)

    # Set of diagonals (i.e., segments) from all the rectangles
    l = set()
    l.add(xspace)

    ylow = set()
    yup = set()

    # oracle function
    f = oracle
    step = 0

    met = -1

    # print('incomparable: ', incomparable)
    # print('comparable: ', comparable)
    while True:
        step = step + 1
        vprint('step: ', step)

        vprint('l:', l)
        vprint('set_size(l): ', len(l))
        vprint('metric(l): ', metric(l))
        vprint('l volumes: ')
        for r in l:
            vprint(r.volume())
        vprint ('end volumes')

        lsorted = sorted(l, key=Rectangle.volume)
        # lsorted = sorted(l, key=Rectangle.volume, reverse=True)
        vprint('lsorted: ', lsorted)

        xrectangle = lsorted.pop()
        l = set(lsorted)

        vprint('xrectangle: ', xrectangle)
        vprint('xrectangle.volume: ', xrectangle.volume())
        vprint('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        y = search(xrectangle.diagToSegment(), f, epsilon)
        vprint('y: ', y)

        #b0 = Rectangle(xspace.min_corner, y.l)
        b0 = Rectangle(xrectangle.min_corner, y.l)
        b0_set = set()
        b0_set.add(b0)
        ylow = ylow.union(b0_set)
        vprint('ylow: ', ylow)
        vprint('b0: ', b0)

        #b1 = Rectangle(y.h, xspace.max_corner)
        b1 = Rectangle(y.h, xrectangle.max_corner)
        b1_set = set()
        b1_set.add(b1)
        yup = yup.union(b1_set)
        vprint('yup: ', yup)
        vprint('b1: ', b1)

        yrectangle = Rectangle(y.l, y.h)
        i = irect(incomparable, yrectangle, xrectangle)
        l = l.union(i)
        vprint('i: ', i)

        prev_met = met
        met = metric(l)
        if (met <= delta) or (met == prev_met):
            break

        vprint('\n')
        #time.sleep(1)
    return ResultSet(l, ylow, yup)