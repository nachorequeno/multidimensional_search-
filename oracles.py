import random
import math
import re
import pickle

from ast import literal_eval
from sympy import Poly, simplify
from sympy.solvers.inequalities import solve_poly_inequalities


# seek(offset, from)
# from =
# 0: means your reference point is the beginning of the file
# 1: means your reference point is the current file position
# 2: means your reference point is the end of the file
# if append:
#    output.seek(0, 2)


def fromFiletest(finput):
    if finput is None:
        finput = open("/home/requenoj/Desktop/oracle.txt", 'rb')


class Condition:
    # Condition = f op g
    # type(f) = sympy.Expr
    # type(g) = sympy.Expr
    # type(op) = string in {'>', '>=', '<', '<=', '==', '!='}
    #
    # Example
    # inequality = (sympy.Poly(f - g), op)
    comparison = set(['>', '>=', '<', '<=', '==', '!='])

    def __init__(self, f, op, g):
        # type: (_, str, str, str) -> None
        assert (op in self.comparison), "Operator " + op + " must be any of: {'>', '>=', '<', '<=', '==', '!='}"
        assert (not f.isdigit() or not g.isdigit()), \
            "At least '" + f + "' or '" + g + "' must be a polynomial expression (i.e., not a single number)"
        self.op = op
        self.f = simplify(f)
        self.g = simplify(g)

    def __str__(self):
        return str(self.f) + self.op + str(self.g)

    def initFromString(self, poly_function):
        #op_exp = (=|>|<|>=|<|<=|<>)\s\d+
        #f_regex = r'(\s*\w\s*)+'
        #g_regex = r'(\s*\w\s*)+'
        op_regex = r'(=|>|<|>=|<|<=|<>)'
        f_regex = r'[^%s]+' % op_regex
        g_regex = r'[^%s]+' % op_regex
        regex = r'(?P<f>(%s))(?P<op>(%s))(?P<g>(%s))' % (f_regex, op_regex, g_regex)
        regex_comp = re.compile(regex)
        result = regex_comp.match(poly_function)
        if regex_comp is not None:
            self.op = result.group('op')
            self.f = simplify(result.group('f'))
            self.g = simplify(result.group('g'))

    # Read/Write file functions
    def fromFile(self, fname='', human_readable=False):
        # type: (_, str, bool) -> None
        assert (fname != ''), "Filename should not be null"

        mode = 'rb'
        finput = open(fname, mode)
        if human_readable:
            self.fromFileHumRead(finput)
        else:
            self.fromFileNonHumRead(finput)
        finput.close()

    def fromFileNonHumRead(self, finput = None):
        ## type: (_, file) -> None
        assert (finput is not None), "File object should not be null"

        _temp = pickle.load(finput)
        print('temp')
        self = _temp

    def fromFileHumRead(self, finput = None):
        ## type: (_, file) -> None
        assert (finput is not None), "File object should not be null"

        poly_function = finput.readline()
        self.initFromString(poly_function)


    def toFile(self, fname='', append=False, human_readable=False):
        # type: (_, str, bool, bool) -> None
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
        ## type: (_, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        pickle.dump(self, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        ## type: (_, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        # str(self.f) + self.op + str(self.g)
        print(str(self))
        print(self.str())
        foutput.write(str(self))

class ConditionList:
    # List of conditions:
    # [c1, c2,..., cn]

    def __init__(self):
        self.l = []
        self.solution = None

    def add(self, cond):
        # type: (_, Condition) -> None
        self.l.append(cond)

    def solve(self):
        # returns set of floats satisfying (c1 and c2 and ... and cn)
        # side-efect: stores the result in a local variable
        #
        # example:
        # ineq1 = (Poly(x ** 2 - 3), ">")
        # ineq2 = (Poly(-x ** 2 + 1), ">")
        # solve_poly_inequalities((
        #     ineq1,
        #     ineq2,
        # ))
        if self.solution == None:
            _ineq_list = ()
            for poly_ineq in self.l:
                _ineq = (Poly(poly_ineq.f - poly_ineq.g), poly_ineq.op)
                _ineq_list += (_ineq, )
            self.solution = solve_poly_inequalities(_ineq_list)
        return self.solution


    def member(self, x):
        # type: (_, int) -> _
        self.solve()
        return x in self.solution

    def membership(self):
        return lambda x: self.member(x)

    # Read/Write file functions
    def fromFile(self, fname='', human_readable=False):
        # type: (_, str, _, bool) -> None
        assert (fname != ''), "Filename should not be null"

        mode = 'rb'
        finput = open(fname, mode)
        if human_readable:
            self.fromFileHumRead(finput)
        else:
            self.fromFileNonHumRead(finput)
        finput.close()

    def fromFileNonHumRead(self, finput = None):
        # type: (_, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self = pickle.load(finput)

    def fromFileHumRead(self, finput = None):
        # type: (_, file) -> None
        assert (finput is not None), "File object should not be null"

        # <num_constraints_dimension_i>
        num_constr_dim_i = finput.readline()
        for j in range(num_constr_dim_i):
            num_constr_dim_i = finput.readline()
            literal_eval()

    def toFile(self, fname='', append=False, human_readable=False):
        # type: (_, str, bool, bool) -> None
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
        # type: (_, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        pickle.dump(self, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        # type: (_, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        # <num_constraints_dimension_i>
        foutput.write(str(len(self.l)))
        for cond_i in range(len(self.l)):
            foutput.write(str(cond_i))

class Oracle:
    # An Oracle is an array of ConditionList, i.e., Oracle[i] contains the ConditionList for i-dimension
    # For each one of the n-dimensions, we should have a ConditionList
    # Dimension = [0,..,n-1]
    def __init__(self):
        self.oracle = {}

    def add(self, condlist, idimension):
        # type: (_, ConditionList, int) -> None
        self.oracle[idimension] = condlist

    def member(self, xpoint):
        # type: (dict, tuple) -> _
        assert (len(self.oracle) >= xpoint.dim()), "Oracle is not prepared for points of dimension " + str(xpoint.dim())
        ismember = True
        #for i, condlist in enumerate(self.oracle):
        for i, condlist in self.oracle.iteritems():
            ismember = ismember and condlist.member(xpoint[i])
        return ismember

    def membership(self):
        return lambda xpoint: self.member(xpoint)

    # Read/Write file functions
    def fromFile(self, fname='', human_readable=False):
        # type: (_, str, _, bool) -> None
        assert (fname != ''), "Filename should not be null"

        mode = 'rb'
        finput = open(fname, mode)
        if human_readable:
            self.fromFileHumRead(finput)
        else:
            self.fromFileNonHumRead(finput)
        finput.close()

    def fromFileNonHumRead(self, finput = None):
        # type: (_, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self = pickle.load(finput)

    def fromFileHumRead(self, finput = None):
        # type: (_, file) -> None
        assert (finput is not None), "File object should not be null"

        # <num_dimensions>
        num_dim = finput.readline()
        self.oracle = dict.fromkeys(range(num_dim))
        for i in range(num_dim):
            self.oracle[i] = ConditionList()
            self.oracle[i].fromFileHumRead(finput)

    def toFile(self, fname='', append=False, human_readable=False):
        # type: (_, str, bool, bool) -> None
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

    def toFileNonHumRead(self, foutput = None):
        # type: (_, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        pickle.dump(self, foutput, pickle.HIGHEST_PROTOCOL)


    def toFileHumRead(self, foutput = None):
        # type: (_, BinaryIO) -> None
        assert (foutput  is not None), "File object should not be null"

        # <num_dimensions>
        foutput.write(str(len(self.oracle)))
        for i, condlist_i in self.oracle.iteritems():
             condlist_i.toFileHumRead(foutput)


#############################################################

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
            str_temp += ' + ' + str(slopes[index]) + 'x^' + str(index + 1)
            ypoint += math.pow(i, index + 1) * slopes[index]
        ypoints += (ypoint % maxc[1],)
        print(str_temp)
        print('(x,y): (' + str(i) + ',' + str(ypoint % maxc[1]) + ')')
    return ypoints


def line_function(xpoints, slope, offset, minc, maxc):
    ypoints = ()
    for i in xpoints:
        str_temp = 'y = '
        # ypoint = min(minc[1], offset)
        ypoint = minc[1]
        if offset >= minc[1]:
            str_temp += str(offset)
            ypoint = offset
        str_temp += ' + ' + str(slope) + 'x'
        ypoint += i * slope
        ypoints += (ypoint % maxc[1],)
        print(str_temp)
        print('(x,y): (' + str(i) + ',' + str(ypoint % maxc[1]) + ')')
    return ypoints


def set_random_points(min_corner, max_corner, num_random_points):
    random.seed()
    xpoints = ()
    for i in range(num_random_points):
        xpoints += (random.uniform(min_corner, max_corner),)
    return xpoints