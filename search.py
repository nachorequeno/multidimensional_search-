from segment import *
from rectangle import *
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def metric(lset):
    # lsizes = map(lambda item: item.norm(), lset)
    lsizes = map(lambda item: item.volume(), lset)
    return reduce(lambda x, y: x + y, lsizes)

def staircase_oracle(xs, ys):
    return lambda p: any(p[0] >= x and p[1] >= y for x, y in zip(xs, ys))

def line_oracle():
    return lambda point: all(point(0) >= x for x in point)

    #def line_oracle(point1, point2):
    #minim = min(point1, point2)
    #maxi = max(point1, point2)
    #diagonal = subtract(maxi, minim)
    #return lambda p: any(p[0] >= x for x in diagonal)

def line_oracle2(xyz, abc):
    #x = x0 + a*t
    #y = y0 + b*t
    #z = z0 + c*t
    #...
    return lambda point: all(x >= x0 + a*point(0) for x, x0, a in zip(point, xyz, abc))


class ResulSet(object):
  def __init__(self, border, ylow, yup):
     self.border = border
     self.ylow = ylow
     self.yup = yup

  def toGNUPlotYup(self):
    print('set title \'Yup\'')
    for i, rect in enumerate(self.yup):
        print('set object ' + str(i+1) + ' ' + rect.toGnuPlot() + ' ' + rect.toGnuPlotColor("green"))

    #print('set ' + xspace.toGnuPlotXrange())
    #print('set ' + xspace.toGnuPlotYrange())
    print('set xzeroaxis')
    print('set yzeroaxis')

    print('plot x')


  def toGNUPlotYlow(self):
    print('set title \'Ylow\'')
    for i, rect in enumerate(self.ylow):
        print('set object ' + str(i+1) + ' ' + rect.toGnuPlot() + ' ' + rect.toGnuPlotColor("red"))

    #print('set ' + xspace.toGnuPlotXrange())
    #print('set ' + xspace.toGnuPlotYrange())
    print('set xzeroaxis')
    print('set yzeroaxis')

    print('plot x')

  def toGNUPlotBorder(self):
    print('set title \'Border\'')
    for i, rect in enumerate(self.border):
        print('set object ' + str(i+1) + ' ' + rect.toGnuPlot() + ' ' + rect.toGnuPlotColor("blu"))

    #print('set ' + xspace.toGnuPlotXrange())
    #print('set ' + xspace.toGnuPlotYrange())
    print('set xzeroaxis')
    print('set yzeroaxis')

    print('plot x')


  def toGNUPlot(self):
      print('set title \'Xspace\'')
      i = 0
      for rect in self.ylow:
          print('set object ' + str(i + 1) + ' ' + rect.toGnuPlot() + ' ' + rect.toGnuPlotColor("red"))
          i += 1

      for rect in self.yup:
          print('set object ' + str(i + 1) + ' ' + rect.toGnuPlot() + ' ' + rect.toGnuPlotColor("green"))
          i += 1

      for rect in self.border:
          print('set object ' + str(i + 1) + ' ' + rect.toGnuPlot() + ' ' + rect.toGnuPlotColor("blu"))
          i += 1

      #print('set ' + xspace.toGnuPlotXrange())
      #print('set ' + xspace.toGnuPlotYrange())
      print('set xzeroaxis')
      print('set yzeroaxis')

      print('plot x')

  def toMatPlotYup(self):
    patches = []
    for rect in self.yup:
        patches += [rect.toMatplot('green')]
    return patches

  def toMatPlotYlow(self):
    patches = []
    for rect in self.ylow:
        patches += [rect.toMatplot('red')]
    return patches

  def toMatPlotBorder(self):
    patches = []
    for rect in self.border:
        patches += [rect.toMatplot('blue')]
    return patches

  def toMatPlot(self):
      fig1 = plt.figure()
      ax1 = fig1.add_subplot(111, aspect='equal')

      pathpatch_yup = self.toMatPlotYup()
      pathpatch_ylow = self.toMatPlotYlow()
      pathpatch_border = self.toMatPlotBorder()

      pathpatch = pathpatch_yup
      pathpatch += pathpatch_ylow
      pathpatch += pathpatch_border

      #print('Pathpatch: ')
      #print(pathpatch)
      for pathpatch_i in pathpatch:
          ax1.add_patch(pathpatch_i)
      ax1.set_title('Approximation of the Pareto front')
      ax1.autoscale_view()

      plt.show()
      #fig1.savefig('rect1.png', dpi=90, bbox_inches='tight')


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
        # lsorted = sorted(l, key=Rectangle.norm, reverse=True)
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

        #TO SOLVE: Can the metric increase at the end of every step?
        prev_met = met
        met = metric(l)
        if (met <= delta) or (met == prev_met):
            break

        #print("\n")
        #time.sleep(1)
    return ResulSet(l, ylow, yup)