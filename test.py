from segment import *
from point import *
from rectangle import *
from search import *

# Graphics
#from graphics import *

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
    xy = Rectangle(x, y)

    #t = (0.75,) * 2
    #t1 = (0.3, 0.8)
    #t2 = (0.4, 0.9)

    t1 = (0.2, 0.8)
    t2 = (0.8, 0.2)
    #t1 = (0.25,)
    #t2 = (0.25,)

    f = staircase_oracle(t1, t2)

    rs = algorithm_2(xy, f)
    #rs.toGNUPlot()
    rs.toMatPlot()
    print("\n")
    return 0



# z = Rectangle(x, y)
# if __name__ == '__main__':
#    test1()
