import random
import math

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