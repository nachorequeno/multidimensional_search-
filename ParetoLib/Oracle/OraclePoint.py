import sys
import resource
import io
import pickle

from ParetoLib.Oracle.NDTree import NDTree
from ParetoLib.Oracle.Oracle import Oracle


class OraclePoint(Oracle):
    # class OraclePoint:
    # OraclePoint defines membership function based on a cloud of points that belongs to the closure.
    # OraclePoint saves a set of points in a NDTree
    def __init__(self, max_points=2, min_children=2):
        # type: (OraclePoint, int, int) -> None
        # super(OraclePoint, self).__init__()
        Oracle.__init__(self)
        self.oracle = NDTree(max_points=max_points, min_children=min_children)

    # Printers
    def __repr__(self):
        # type: (OraclePoint) -> str
        return self.to_str()

    def __str__(self):
        # type: (OraclePoint) -> str
        return self.to_str()

    def to_str(self):
        # type: (OraclePoint) -> str
        return str(self.oracle)

    # Equality functions
    def __eq__(self, other):
        # type: (OraclePoint, OraclePoint) -> bool
        return self.oracle == other.oracle

    def __ne__(self, other):
        # type: (OraclePoint, OraclePoint) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (OraclePoint) -> int
        return hash(self.oracle)

    # Oracle operations
    def add_point(self, p):
        # type: (OraclePoint, tuple) -> None
        self.oracle.update_point(p)

    def add_points(self, setpoints):
        # type: (OraclePoint, set) -> None
        for point in setpoints:
            self.add_point(point)

    def get_points(self):
        # type: (OraclePoint) -> set
        return self.oracle.get_points()

    def dim(self):
        # type: (OraclePoint) -> int
        return self.oracle.dim()

    def get_var_names(self):
        # type: (OraclePoint) -> list
        # super(OraclePoint, self).get_var_names()
        return Oracle.get_var_names(self)

    # Membership functions
    def __contains__(self, p):
        # type: (OraclePoint, tuple) -> bool
        # set_points = self.get_points()
        # return p in set_points
        return self.member(p)

    def member(self, p):
        # type: (OraclePoint, tuple) -> bool
        # Returns 'True' if p belongs to the set of points stored in the Pareto archive
        return p in self.get_points()

    def membership(self):
        # type: (OraclePoint) -> callable
        # Returns 'True' if p is dominated by any point stored in the Pareto archive
        return lambda p: self.oracle.dominates(p)

    # Read/Write file functions
    def from_file_binary(self, finput=None):
        # type: (OraclePoint, io.BinaryIO) -> None
        assert (finput is not None), 'File object should not be null'

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

        self.oracle = pickle.load(finput)

    def from_file_text(self, finput=None):
        # type: (OraclePoint, io.BinaryIO) -> None
        assert (finput is not None), 'File object should not be null'

        def _line2tuple(inline):
            line = inline
            line = line.replace('(', '')
            line = line.replace(')', '')
            line = line.split(',')
            return tuple(float(pi) for pi in line)

        self.oracle = NDTree()

        point_list = (_line2tuple(line) for line in finput)
        for point in point_list:
            self.oracle.update_point(point)

    def to_file_binary(self, foutput=None):
        # type: (OraclePoint, io.BinaryIO) -> None
        assert (foutput is not None), 'File object should not be null'

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

        pickle.dump(self.oracle, foutput, pickle.HIGHEST_PROTOCOL)

    def to_file_text(self, foutput=None):
        # type: (OraclePoint, io.BinaryIO) -> None
        assert (foutput is not None), 'File object should not be null'

        setPoints = self.get_points()
        for point in setPoints:
            foutput.write(str(point))
            foutput.write('\n')