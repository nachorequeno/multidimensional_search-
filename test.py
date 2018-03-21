from search import *
from oracles import *
import random

import matplotlib.pyplot as plt

EPS = 1e-5
DELTA = 1e-5

def main1():
    x = (0.0,) * 2
    y = (1.0,) * 2

    f = staircase_oracle(x, y)
    xy = Segment(x, y)
    print(xy.dim())

    return search(xy, f)

def main2():
    x = (0.0,) * 2
    y = (1.0,) * 2
    xyspace = Rectangle(x, y)

    t1 = (0.2, 0.8)
    t2 = (0.8, 0.2)

    f = staircase_oracle(t1, t2)
    #f = membership_oracle(t1, t2)

    rs = multidim_search(xyspace, f)
    rs.toMatPlot()
    #rs.toGNUPlot()
    #print("\n")
    return 0

def main3(min_corner = 0.0,
          max_corner = 1.0,
          num_random_points = 50,
          epsilon = EPS,
          delta = DELTA,
          verbose=False):

    minc = (min_corner,) * 2
    maxc = (max_corner,) * 2
    xyspace = Rectangle(minc, maxc)

    random.seed()
    offset = random.uniform(min_corner, max_corner)
    slope = -random.uniform(min_corner, max_corner)
    x = set_random_points(min_corner, max_corner, num_random_points)
    y = line_function(x, slope, offset, minc, maxc)

    #f = staircase_oracle(x, y)
    f = membership_oracle(x, y)

    rs = multidim_search(xyspace, f, epsilon, delta, verbose)
    rs.toMatPlot()
    #rs.toFile("/home/requenoj/Desktop/result_main3")
    #rs.toGNUPlot()
    #print("\n")
    return 0

def main4(min_corner = 0.0,
          max_corner = 1.0,
          num_random_points = 50,
          epsilon = EPS,
          delta = DELTA,
          dimension = 2,
          verbose=False):

    minc = (min_corner,) * 2
    maxc = (max_corner,) * 2
    xyspace = Rectangle(minc, maxc)

    random.seed()
    offset = random.uniform(min_corner, max_corner)
    slopes = set_random_points(min_corner, max_corner, dimension)
    x = set_random_points(min_corner, max_corner, num_random_points)
    y = polynomial_function(x, slopes, offset, minc, maxc)

    #f = staircase_oracle(x, y)
    f = membership_oracle(x, y)

    rs = multidim_search(xyspace, f, epsilon, delta, verbose)
    rs.toMatPlot(targetx=list(x), targety=list(y), blocking=True)
    #rs.toGNUPlot()
    #rs.toFile("/home/requenoj/Desktop/result_main3")
    return 0

# z = Rectangle(x, y)
# if __name__ == '__main__':
#    test1()
