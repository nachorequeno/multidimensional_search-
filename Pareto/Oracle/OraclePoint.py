import pickle

from _NDTree import *

VERBOSE = True
VERBOSE = False

if VERBOSE:
    # Verbose print (stdout)
    def vprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        for arg in args:
            print arg,
        print


    # Error print (stderr)
    def eprint(*args):
        for arg in args:
            print >> sys.stderr, arg
        print >> sys.stderr

else:
    vprint = lambda *a: None  # do-nothing function
    eprint = lambda *a: None  # do-nothing function


EPS = 1e-1
class OraclePoint:
    # An OraclePoint is an array of ConditionList, i.e., OraclePoint[i] contains the ConditionList for ith-dimension
    # For each one of the n-dimensions, we should have a ConditionList

    # Dimension = [0,..,n-1]
    def __init__(self, MAX_P=2, MIN_CH=2):
        # type: (OraclePoint, int, int) -> None
        self.oracle = NDTree(MAX_P=MAX_P, MIN_CH=MIN_CH)

    def __str__(self):
        # type: (OraclePoint) -> str
        return self.toStr()

    def toStr(self):
        # type: (OraclePoint) -> str
        return str(self.oracle)

    def addPoint(self, point):
        # type: (OraclePoint, tuple) -> None
        self.oracle.update(point)

    def addPoints(self, setpoints):
        # type: (OraclePoint, set) -> None
        for point in setpoints:
            self.addPoint(point)

    def getPoints(self):
        return self.oracle.getPoints()

    # Membership functions
    def member(self, xpoint):
        # type: (OraclePoint, tuple) -> bool
        # Returns 'True' if xpoint belongs to the set of points stored in the Pareto archive
        vprint(xpoint)
        return xpoint in self.getPoints()

    def dominates(self, xpoint):
        # type: (OraclePoint, tuple) -> bool
        # Returns 'True' if xpoint dominates any point of the set of points stored in the Pareto archive
        vprint(xpoint)
        return any(greater_equal(xpoint, point) for point in self.getPoints())

    def membership(self):
        # type: (OraclePoint) -> function
        #return lambda xpoint: self.member(xpoint)
        return lambda xpoint: self.dominates(xpoint)

    # Read/Write file functions
    def fromFile(self, fname='', human_readable=False):
        # type: (OraclePoint, str, bool) -> None
        assert (fname != ''), "Filename should not be null"

        mode = 'rb'
        finput = open(fname, mode)
        if human_readable:
            self.fromFileHumRead(finput)
        else:
            self.fromFileNonHumRead(finput)
        finput.close()

    def fromFileNonHumRead(self, finput=None):
        # type: (OraclePoint, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

        self.oracle = pickle.load(finput)

    def fromFileHumRead(self, finput=None):
        # type: (OraclePoint, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self.oracle = NDTree()
        #for line in finput.readlines():
        for i, line in enumerate(finput):
            line = line.replace('(', '')
            line = line.replace(')', '')
            line = line.split(',')
            point = tuple(float(pi) for pi in line)
            vprint("Adding: ", i, point)
            self.oracle.update(point)
        vprint("numPoints: ", i)

    def toFile(self, fname='', append=False, human_readable=False):
        # type: (OraclePoint, str, bool, bool) -> None
        assert (fname != ''), "Filename should not be null"

        if append:
            mode = 'ab'
        else:
            mode = 'wb'

        foutput = open(fname, mode)
        if human_readable:
            self.toFileHumRead(foutput)
        else:
            self.toFileNonHumRead(foutput)
        foutput.close()

    def toFileNonHumRead(self, foutput=None):
        # type: (OraclePoint, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

        pickle.dump(self.oracle, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        # type: (OraclePoint, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        setPoints = self.getPoints()
        vprint("Set of points ")
        vprint(setPoints)
        for point in setPoints:
            foutput.write(str(point))
            foutput.write('\n')