from search import *
import random

def main1():
    x = (0.0,) * 2
    y = (1.0,) * 2
    t = (0.75,) * 2

    f = staircase_oracle(t, t)
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

    rs = algorithm_2(xyspace, f)
    rs.toMatPlot()
    #rs.toGNUPlot()
    #print("\n")
    return 0

def main3():
    min_corner = 0.0
    max_corner = 3.0

    x = (min_corner,) * 2
    y = (max_corner,) * 2
    xyspace = Rectangle(x, y)


    num_random_points = 50
    t1 = (random.uniform(min_corner, max_corner), ) * num_random_points
    t2 = (random.uniform(min_corner, max_corner), ) * num_random_points

    EPS = 1e-3
    DELTA = 1e-3
    f = staircase_oracle_2(t1, t2)

    rs = algorithm_2(xyspace, f, epsilon=EPS, delta=DELTA)
    rs.toMatPlot()
    rs.toFile("/home/requenoj/Desktop/result_main3")
    #rs.toGNUPlot()
    #print("\n")
    return 0

# z = Rectangle(x, y)
# if __name__ == '__main__':
#    test1()
