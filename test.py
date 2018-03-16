from search import *
import random

EPS = 1e-5
DELTA = 1e-5

def polynomial_function(xpoints, slopes, offset, minc, maxc):
    ypoints = ()
    for i in xpoints:
        str_temp = 'y = '
        # ypoint = min(minc[1], offset)
        ypoint = minc[1]
        if offset >= minc[1]:
            str_temp += str(offset)
            ypoint = offset
        for index, j in enumerate(slopes):
            str_temp += ' + ' + str(slopes[index]) + 'x^' + str(index+1)
            ypoint += math.pow(i,index+1)*slopes[index]
        ypoints += (ypoint % maxc[1], )
        print(str_temp)
        print('(x,y): (' + str(i) + ',' + str(ypoint % maxc[1]) + ')')
    return ypoints

def line_function(xpoints, slope, offset, minc, maxc):
    ypoints = ()
    for i in xpoints:
        str_temp = 'y = '
        #ypoint = min(minc[1], offset)
        ypoint = minc[1]
        if offset >= minc[1]:
            str_temp += str(offset)
            ypoint = offset
        str_temp += ' + ' + str(slope) + 'x'
        ypoint += i*slope
        ypoints += (ypoint % maxc[1], )
        print(str_temp)
        print('(x,y): (' + str(i) + ',' + str(ypoint % maxc[1]) + ')')
    return ypoints

def set_random_points(min_corner, max_corner, num_random_points):
    random.seed()
    xpoints = ()
    for i in range(num_random_points):
        xpoints += (random.uniform(min_corner, max_corner), )
    return xpoints

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

    rs = algorithm_2(xyspace, f)
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

    f = staircase_oracle(x, y)

    rs = algorithm_2(xyspace, f, epsilon, delta, verbose)
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

    rs = algorithm_2(xyspace, f, epsilon, delta, verbose)
    rs.toMatPlot()
    #rs.toFile("/home/requenoj/Desktop/result_main3")
    #rs.toGNUPlot()
    #print("\n")
    return 0

# z = Rectangle(x, y)
# if __name__ == '__main__':
#    test1()
