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

def main5():
    nfile = '/home/requenoj/Desktop/oracle.txt'
    nfile2 = '/home/requenoj/Desktop/oracle2.txt'
    nfile3 = '/home/requenoj/Desktop/oracle3.txt'
    # ftemp = open(nfile, 'wb')
    c1 = Condition('x', '>', '2')
    c2 = Condition('x', '>', '5')
    cl = ConditionList()
    cl.add(c1)
    cl.add(c2)
    # Condition
    c1.toFile(nfile, append=False, human_readable=True)
    c3 = Condition()
    c3.fromFile(nfile, human_readable=True)
    print('c3 ' + str(c3))

    # ConditionList
    cl.toFile(nfile2, append=False, human_readable=True)
    cl2 = ConditionList()
    cl2.fromFile(nfile2, human_readable=True)
    print('cl2 ' + str(cl2))

    # Oracle
    ora = Oracle()
    ora.add(cl, 1)
    ora.add(cl, 2)
    ora.toFile(nfile3, append=False, human_readable=True)
    ora2 = Oracle()
    ora2.fromFile(nfile3, human_readable=True)
    print('ora2 ' + str(ora2))

    # Condition
    print('c1 ' + str(c1))
    c1.toFile(nfile, append=False, human_readable=False)
    c3 = Condition()
    c3.fromFile(nfile, human_readable=False)
    print('c3 ' + str(c3))

    # ConditionList
    print('cl ' + str(cl))
    cl.toFile(nfile2, append=False, human_readable=False)
    cl2 = ConditionList()
    cl2.fromFile(nfile2, human_readable=False)
    print('cl2 ' + str(cl2))

    #Oracle
    ora = Oracle()
    ora.add(cl, 1)
    ora.add(cl, 2)
    ora.toFile(nfile3, append=False, human_readable=False)
    ora2 = Oracle()
    ora2.fromFile(nfile3, human_readable=False)
    print('ora2 ' + str(ora2))

def main6():
    c1 = Condition('x', '>', '2')
    c2 = Condition('x', '>', '5')
    cl1 = ConditionList()
    cl1.add(c1)
    f1 = cl1.membership()
    f1(0)
    f1(3)

    cl2 = ConditionList()
    cl2.add(c2)
    f2 = cl2.membership()
    f2(3)
    f2(6)

    # Oracle
    ora = Oracle()
    ora.add(cl1, 0)
    ora.add(cl2, 1)
    fora = ora.membership()
    fora((2,5))
    fora((3,5))
    fora((3,6))
# z = Rectangle(x, y)
# if __name__ == '__main__':
#    test1()
