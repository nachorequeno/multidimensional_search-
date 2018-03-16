from rectangle import *
import itertools
import matplotlib.pyplot as plt
from resultset import *
import pickle
import time

def metric(lset):
    # lsizes = map(lambda item: item.norm(), lset)
    lsizes = map(lambda item: item.volume(), lset)
    return reduce(lambda x, y: x + y, lsizes)

def staircase_oracle(xs, ys):
    return lambda p: any(p[0] >= x and p[1] >= y for x, y in zip(xs, ys))

def staircase_oracle_2(xs, ys):
    return lambda p: all(p[0] >= x and p[1] >= y for x, y in zip(xs, ys))

EPS = 1e-5
DELTA = 1e-5

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
def algorithm_2(xspace, oracle, epsilon=EPS, delta=DELTA):
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
    # zero = (0_1,...,0_n)
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
        print('step: ', step)

        # print('l:', l)
        # print('set_size(l): ', len(l))
        print('metric(l): ', metric(l))

        lsorted = sorted(l, key=Rectangle.volume)
        # lsorted = sorted(l, key=Rectangle.volume, reverse=True)
        # print('lsorted: ', lsorted)

        xrectangle = lsorted.pop()
        l = set(lsorted)

        print('xrectangle: ', xrectangle)
        print('xrectangle.volume: ', xrectangle.volume())
        # print('xrectangle.norm : ', xrectangle.norm())

        # y, segment
        y = search(xrectangle.diagToSegment(), f, epsilon)
        # print('y: ', y)

        #b0 = Rectangle(xspace.min_corner, y.l)
        b0 = Rectangle(xrectangle.min_corner, y.l)
        b0_set = set()
        b0_set.add(b0)
        ylow = ylow.union(b0_set)
        print('ylow: ', ylow)
        # print('b0: ', b0)

        #b1 = Rectangle(y.h, xspace.max_corner)
        b1 = Rectangle(y.h, xrectangle.max_corner)
        b1_set = set()
        b1_set.add(b1)
        yup = yup.union(b1_set)
        print('yup: ', yup)
        # print('b1: ', b1)

        yrectangle = Rectangle(y.l, y.h)
        i = irect(incomparable, yrectangle, xrectangle)
        l = l.union(i)
        # print('i: ', i)
        # print('l: ', l)
        print('l volumes: ')
        for r in l:
            print(r.volume())
        print ('end volumes')

        prev_met = met
        met = metric(l)
        if (met <= delta) or (met == prev_met):
            break

        #print("\n")
        #time.sleep(1)
    return ResultSet(l, ylow, yup)