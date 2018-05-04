import itertools
import __builtin__

from sortedcontainers import SortedListWithKey

from ParetoLib.Geometry.Rectangle import *
from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *
from ParetoLib.Search.ResultSet import *

# from ParetoLib.Search import vprint
from . import vprint

EPS = 1e-5
DELTA = 1e-5
# STEPS = 100
STEPS = float('inf')


class Search:
    def __init__(self, epsilon=EPS, delta=DELTA, steps=STEPS):
        # EPS = sys.float_info.min
        self.epsilon = epsilon
        self.delta = delta
        self.steps = steps

    # Membership
    def __contains__(self, *args):
        # type: (Search, _) -> bool
        return False

    # Printers
    def toStr(self):
        # type: (Search) -> str
        return "<epsilon %s, delta %s, steps %s>" % (str(self.epsilon), str(self.delta), str(self.steps))

    def __repr__(self):
        # type: (Search) -> str
        return self.toStr()

    def __str__(self):
        # type: (Search) -> str
        return self.toStr()

    # Equality functions
    def __eq__(self, other):
        # type: (Search, Search) -> bool
        sameContent = (other.epsilon == self.epsilon) and \
                      (other.delta == self.delta) and \
                      (other.steps == self.steps)
        return sameContent

    def __ne__(self, other):
        # type: (Search, Search) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Search) -> int
        return hash((self.epsilon, self.delta, self.steps))

    # Loading Oracles
    def loadOracle(self,
                   nfile,
                   human_readable=False):
        None

    # Dimensional tests
    def Search2D(self,
                 nfile,
                 human_readable=False,
                 min_cornerx=0.0,
                 min_cornery=0.0,
                 max_cornerx=1.0,
                 max_cornery=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0.0):
        None

    def Search3D(self,
                 nfile,
                 human_readable=False,
                 min_cornerx=0.0,
                 min_cornery=0.0,
                 min_cornerz=0.0,
                 max_cornerx=1.0,
                 max_cornery=1.0,
                 max_cornerz=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0.0):
        None

    def SearchND(self,
                 nfile,
                 human_readable=True,
                 min_corner=0.0,
                 max_corner=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0.0):
        None

    # Auxiliar functions used in 2D, 3D and ND
    # Creation of Spaces
    def _create2DSpace(self, minx, miny, maxx, maxy):
        vprint('Creating Space')
        start = time.time()
        minc = (minx, miny)
        maxc = (maxx, maxy)
        xyspace = Rectangle(minc, maxc)
        end = time.time()
        time0 = end - start
        vprint('Time creating Space: ', str(time0))
        return xyspace

    def _create3DSpace(self, minx, miny, minz, maxx, maxy, maxz):
        vprint('Creating Space')
        start = time.time()
        minc = (minx, miny, minz)
        maxc = (maxx, maxy, maxz)
        xyspace = Rectangle(minc, maxc)
        end = time.time()
        time0 = end - start
        vprint('Time creating Space: ', str(time0))
        return xyspace

    def _createNDSpace(self, *args):
        # args = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
        vprint('Creating Space')
        start = time.time()
        minc = tuple(minx for minx, _ in args)
        maxc = tuple(maxx for _, maxx in args)
        xyspace = Rectangle(minc, maxc)
        end = time.time()
        time0 = end - start
        vprint('Time creating Space: ', str(time0))
        return xyspace

    def binary_search(self,
                      x,
                      member,
                      error):
        # type: (Search, Segment, _, tuple) -> Segment
        y = x
        dist = subtract(y.h, y.l)
        #while greater_equal(dist, error):
        while not less(dist, error):
            yval = div(add(y.l, y.h), 2.0)
            # We need a oracle() for guiding the search
            if member(yval):
                y.h = yval
            else:
                y.l = yval
            dist = subtract(y.h, y.l)
        return y

    # Multidimensional search
    # The search returns a set of Rectangles in Yup, Ylow and Border
    def multidim_search(self,
                        xspace,
                        oracle,
                        epsilon=EPS,
                        delta=DELTA,
                        max_step=STEPS,
                        blocking=False,
                        sleep=0.0):
        # type: (Search, Rectangle, _, float, float, float, bool, float) -> ResultSet

        vprint('Starting multidimensional search')
        start = time.time()

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
        comparable = [zero, one]
        incomparable = alpha.difference(comparable)  # Use list instead of set. Remove sublist 'comparable'

        # List of incomparable rectangles
        #l = [xspace]
        l = SortedListWithKey(key=Rectangle.volume)
        l.add(xspace)

        ylow = []
        yup = []

        # oracle function
        f = oracle

        error = (epsilon,) * n
        vol_total = xspace.volume()
        vol_yup = 0
        vol_ylow = 0
        vol_border = vol_total
        prev_vol_border = -1
        step = 0

        vprint('xspace: ', xspace)
        vprint('vol_border: ', vol_border)
        vprint('delta: ', delta)
        vprint('step: ', step)
        vprint('incomparable: ', incomparable)
        vprint('comparable: ', comparable)
        while (vol_border >= delta) and (step <= max_step):
            step = step + 1
            vprint('step: ', step)
            vprint('l:', l)
            vprint('set_size(l): ', len(l))

            #l.sort(key=Rectangle.volume)

            xrectangle = l.pop()

            vprint('xrectangle: ', xrectangle)
            vprint('xrectangle.volume: ', xrectangle.volume())
            vprint('xrectangle.norm : ', xrectangle.norm())

            # y, segment
            # y = search(xrectangle.diagToSegment(), f, epsilon)
            y = self.binary_search(xrectangle.diagToSegment(), f, error)
            vprint('y: ', y)

            # b0 = Rectangle(xspace.min_corner, y.l)
            b0 = Rectangle(xrectangle.min_corner, y.l)
            ylow.append(b0)
            vol_ylow += b0.volume()

            vprint('b0: ', b0)
            vprint('ylow: ', ylow)
            vprint('vol_ylow: ', vol_ylow)

            # b1 = Rectangle(y.h, xspace.max_corner)
            b1 = Rectangle(y.h, xrectangle.max_corner)
            yup.append(b1)
            vol_yup += b1.volume()

            vprint('b1: ', b1)
            vprint('yup: ', yup)
            vprint('vol_yup: ', vol_yup)

            yrectangle = Rectangle(y.l, y.h)
            i = irect(incomparable, yrectangle, xrectangle)
            #i = pirect(incomparable, yrectangle, xrectangle)
            #l.extend(i)

            l += i
            vprint('irect: ', i)

            prev_vol_border = vol_border
            vol_border = vol_total - vol_yup - vol_ylow
            vprint('vol_border: ', vol_border)
            vprint('Volume report (Step, Ylow, Yup, Border, Total): (%s, %s, %s, %s, %s)\n'
                   % (step, vol_ylow, vol_yup, vol_border, vol_total))

            if sleep > 0.0:
                rs = ResultSet(list(l), ylow, yup, xspace)
                # for i in range(1, n):
                #    rs.toMatPlot2D(blocking=blocking, sec=sleep, yaxe=i, opacity=0.7)
                if n == 2:
                    rs.toMatPlot2D(blocking=blocking, sec=sleep, opacity=0.7)
                elif n == 3:
                    rs.toMatPlot3D(blocking=blocking, sec=sleep, opacity=0.7)

        end = time.time()
        time0 = end - start
        vprint('Time multidim search: ', str(time0))

        return ResultSet(list(l), ylow, yup, xspace)


class SearchOracleFunction(Search):

#    def __init__(self, epsilon=EPS, delta=DELTA, steps=STEPS):
#        super(SearchOracleFunction, self).__init__(epsilon, delta, steps)

    # Membership
    def __contains__(self, *args):
        super(SearchOracleFunction, self).__contains__()

    # Printers

    def __repr__(self):
        # type: (SearchOracleFunction) -> str
        return super(SearchOracleFunction, self).__repr__()

    def __str__(self):
        # type: (SearchOracleFunction) -> str
        return super(SearchOracleFunction, self).__str__()

    # Equality functions
    def __eq__(self, other):
        # type: (SearchOracleFunction, SearchOracleFunction) -> bool
        return super(SearchOracleFunction, self).__eq__()

    def __ne__(self, other):
        # type: (SearchOracleFunction, SearchOracleFunction) -> bool
        return super(SearchOracleFunction, self).__ne__()

    # Identity function (via hashing)
    def __hash__(self):
        # type: (SearchOracleFunction) -> float
        return super(SearchOracleFunction, self).__hash__()

    # Loading Oracles
    def loadOracle(self,
                   nfile,
                   human_readable=True):
        vprint ('Creating OracleFunction')
        start = time.time()
        ora = OracleFunction()
        ora.fromFile(nfile, human_readable=human_readable)
        end = time.time()
        time0 = end - start
        vprint ('Time reading OracleFunction: ', str(time0))
        return ora

    # Dimensional tests
    def Search2D(self,
                 nfile,
                 human_readable=True,
                 min_cornerx=0.0,
                 min_cornery=0.0,
                 max_cornerx=1.0,
                 max_cornery=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0.0):
        ora = self.loadOracle(nfile, human_readable=human_readable)
        fora = ora.membership()

        xyspace = self._create2DSpace(min_cornerx, min_cornery, max_cornerx, max_cornery)

        rs = self.multidim_search(xyspace, fora, epsilon, delta, max_step, blocking, sleep)

        n = int((max_cornerx - min_cornerx) / 0.1)
        points = rs.getPointsBorder(n)

        vprint("Points ", points)
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True)
        return rs

    def Search3D(self,
                 nfile,
                 human_readable=True,
                 min_cornerx=0.0,
                 min_cornery=0.0,
                 min_cornerz=0.0,
                 max_cornerx=1.0,
                 max_cornery=1.0,
                 max_cornerz=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0.0,
                 ):
        ora = self.loadOracle(nfile, human_readable=human_readable)
        fora = ora.membership()

        xyspace = self._create3DSpace(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

        rs = self.multidim_search(xyspace, fora, epsilon, delta, max_step, blocking, sleep)

        n = int((max_cornerx - min_cornerx) / 0.1)
        points = rs.getPointsBorder(n)

        vprint("Points ", points)
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        zs = [point[2] for point in points]

        rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True)
        return rs

    def SearchND(self,
                 nfile,
                 human_readable=True,
                 min_corner=0.0,
                 max_corner=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0.0):
        ora = self.loadOracle(nfile, human_readable=human_readable)
        fora = ora.membership()
        d = ora.dim()

        minc = (min_corner,) * d
        maxc = (max_corner,) * d
        xyspace = Rectangle(minc, maxc)

        rs = self.multidim_search(xyspace, fora, epsilon, delta, max_step, blocking, sleep)
        return rs


class SearchOraclePoint(Search):

#    def __init__(self, epsilon=EPS, delta=DELTA, steps=STEPS):
#        super(SearchOraclePoint, self).__init__(epsilon, delta, steps)

    # Membership
    def __contains__(self, *args):
        super(SearchOraclePoint, self).__contains__()

    # Printers

    def __repr__(self):
        # type: (SearchOraclePoint) -> str
        return super(SearchOraclePoint, self).__repr__()

    def __str__(self):
        # type: (SearchOraclePoint) -> str
        return super(SearchOraclePoint, self).__str__()

    # Equality functions
    def __eq__(self, other):
        # type: (SearchOraclePoint, SearchOraclePoint) -> bool
        return super(SearchOraclePoint, self).__eq__()

    def __ne__(self, other):
        # type: (SearchOraclePoint, SearchOraclePoint) -> bool
        return super(SearchOraclePoint, self).__ne__()

    # Identity function (via hashing)
    def __hash__(self):
        # type: (SearchOraclePoint) -> float
        return super(SearchOraclePoint, self).__hash__()

    # Loading Oracles
    def loadOracle(self,
                   nfile,
                   human_readable=False):
        vprint ('Creating OraclePoint')
        start = time.time()
        ora = OraclePoint()
        ora.fromFile(nfile, human_readable=human_readable)
        end = time.time()
        time0 = end - start
        vprint ('Time reading OraclePoint: ', str(time0))
        return ora

    # Dimensional tests
    def Search2D(self,
                 nfile,
                 human_readable=False,
                 min_cornerx=0.0,
                 min_cornery=0.0,
                 max_cornerx=1.0,
                 max_cornery=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0):
        ora = self.loadOracle(nfile, human_readable=human_readable)
        fora = ora.membership()

        points = ora.getPoints()

        vprint("Points ", points)
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        minx = __builtin__.min(xs)
        miny = __builtin__.min(ys)

        maxx = __builtin__.max(xs)
        maxy = __builtin__.max(ys)

        xyspace = self._create2DSpace(__builtin__.min(minx, min_cornerx),
                                      __builtin__.min(miny, min_cornery),
                                      __builtin__.min(maxx, max_cornerx),
                                      __builtin__.min(maxy, max_cornery))

        rs = self.multidim_search(xyspace, fora, epsilon, delta, max_step,  blocking, sleep)
        rs.toMatPlot2D(targetx=xs, targety=ys, blocking=True)
        return rs

    def Search3D(self,
                 nfile,
                 human_readable=False,
                 min_cornerx=0.0,
                 min_cornery=0.0,
                 min_cornerz=0.0,
                 max_cornerx=1.0,
                 max_cornery=1.0,
                 max_cornerz=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0):
        ora = self.loadOracle(nfile, human_readable=human_readable)
        fora = ora.membership()

        points = ora.getPoints()

        vprint("Points ", points)
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        zs = [point[2] for point in points]

        minx = __builtin__.min(xs)
        miny = __builtin__.min(ys)
        minz = __builtin__.min(zs)

        maxx = __builtin__.max(xs)
        maxy = __builtin__.max(ys)
        maxz = __builtin__.max(zs)

        xyspace = self._create3DSpace(__builtin__.min(minx, min_cornerx),
                                      __builtin__.min(miny, min_cornery),
                                      __builtin__.min(minz, min_cornerz),
                                      __builtin__.min(maxx, max_cornerx),
                                      __builtin__.min(maxy, max_cornery),
                                      __builtin__.min(maxz, max_cornerz))

        rs = self.multidim_search(xyspace, fora, epsilon, delta, max_step, blocking, sleep)
        rs.toMatPlot3D(targetx=xs, targety=ys, targetz=zs, blocking=True)
        return rs

    def SearchND(self,
                 nfile,
                 human_readable=True,
                 min_corner=0.0,
                 max_corner=1.0,
                 epsilon=EPS,
                 delta=DELTA,
                 max_step=STEPS,
                 blocking=False,
                 sleep=0):
        ora = self.loadOracle(nfile, human_readable=human_readable)
        fora = ora.membership()

        points = ora.getPoints()
        sorted_points = sorted(points)

        vprint("Points ", points)
        minc = sorted_points[0]
        maxc = sorted_points.pop()
        xyspace = Rectangle(minc, maxc)

        rs = self.multidim_search(xyspace, fora, epsilon, delta, max_step, blocking, sleep)
        return rs
