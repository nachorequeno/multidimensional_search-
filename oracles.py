import random
import re
import pickle
import sys

import numpy as np
from sympy import Poly, simplify, S, default_sort_key, Intersection, Union
from sympy.solvers.inequalities import solve_poly_inequality, solve_poly_inequalities

from point import *
from data_generator import *

VERBOSE=False

if VERBOSE:
    def vprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        for arg in args:
            print arg,
        print
else:
    vprint = lambda *a: None  # do-nothing function

class Condition:
    # Condition = f op g
    # type(f) = sympy.Expr
    # type(g) = sympy.Expr
    # type(op) = string in {'>', '>=', '<', '<=', '==', '!='}
    #
    # Example
    # inequality = (sympy.Poly(f - g), op)
    comparison = set(['>', '>=', '<', '<=', '==', '!='])

    def __init__(self, f='x', op='==', g='0'):
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
        op_regex = r'(==|>|<|>=|<|<=|<>)'
        f_regex = r'[^%s]+' % op_regex
        g_regex = r'[^%s]+' % op_regex
        regex = r'(?P<f>(%s))(?P<op>(%s))(?P<g>(%s))' % (f_regex, op_regex, g_regex)
        regex_comp = re.compile(regex)
        result = regex_comp.match(poly_function)
        if regex_comp is not None:
            self.op = result.group('op')
            self.f = simplify(result.group('f'))
            self.g = simplify(result.group('g'))

    def get_variables(self):
        # type: (_) -> _
        expr = self.f - self.g
        return sorted(expr.free_symbols, key=default_sort_key)

    def get_expresion(self):
        # type: (_) -> _
        return simplify(self.f - self.g)

    def eval_tuple(self, xpoint):
        # type: (_, tuple, _) -> _
        keys_fv = self.get_variables()
        di = {key: xpoint[i] for i, key in enumerate(keys_fv)}

        vprint('condition ' + str(self) + ' evaluates ' + str(xpoint) + ' to ' + str(self.eval_dict(di)))
        vprint('di ' + str(di))
        return self.eval_dict(di)

    def eval_dict(self, d = None):
        # type: (_, _) -> _
        keys_fv = self.get_variables()
        if d is None:
            #di = dict.fromkeys(expr.free_symbols)
            di = {key: 0 for key in keys_fv}
        else:
            di = d
            keys = set(d.keys())
            assert keys.issuperset(keys_fv), "Keys in dictionary " \
                                             + str(d) \
                                             + " do not match with the variables in the condition"
        expr = self.f - self.g
        res = expr.subs(di)
        ex = str(res) + self.op + '0'
        #vprint('expresion ' + ex)
        return simplify(ex)

    def eval_var_val(self, var=None, val='0'):
        # type: (_, _, int) -> _
        if var is None:
            fvset = self.get_variables()
            fv = fvset.pop()
        else: fv = var
        expr = self.f - self.g
        res = expr.subs(fv, val)
        ex = str(res) + self.op + '0'
        return simplify(ex)

    def eval2(self, x):
        # type: (_, int) -> _
        expr = str(self.f) + self.op + str(self.g)
        _poly = Poly(expr)
        fvset = sorted( _poly.free_symbols, key=default_sort_key)
        # fvset should have only one variable 'x'
        fv = fvset.pop()
        return _poly.subs(fv, x)

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

        self.f = pickle.load(finput)
        self.op = pickle.load(finput)
        self.g = pickle.load(finput)

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

        pickle.dump(self.f, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.op, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.g, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        ## type: (_, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        # str(self.f) + self.op + str(self.g)
        foutput.write(str(self) + '\n')

class ConditionList:
    # List of conditions:
    # [c1, c2,..., cn]

    def __init__(self):
        self.l = []
        self.solution = None

    def __str__(self):
        return self.toStr()

    def toStr(self):
        _string = "["
        for i, item in enumerate(self.l):
            _string += str(item)
            if i < (len(self.l)-1): _string += ', '
        _string += "]"
        return _string

    def add(self, cond):
        # type: (_, Condition) -> None
        self.l.append(cond)

    def get_variables(self):
        # type: (_) -> _
        fv = set()
        for i in self.l:
            fv = fv.union(i.get_variables())
        return list(fv)

    def eval_tuple(self, xpoint):
        # type: (_, tuple) -> _
        _eval = True
        for i in self.l:
            _eval = _eval and i.eval_tuple(xpoint)

        vprint('condition list ' + self.toStr() +' evaluates ' + str(xpoint) + ' to ' + str(_eval))
        return _eval

    def eval_dict(self, d = None):
        # type: (_, _) -> _
        _eval = True
        for i in self.l:
            _eval = _eval and i.eval_dict(d)
        return _eval

    def eval_var_val(self, var=None, val='0'):
        # type: (_, _, int) -> _
        _eval = True
        for i in self.l:
            _eval = _eval and i.eval_var_val(var, val)
        return _eval

    def solve(self):
        # returns set of floats satisfying (c1 and c2 and ... and cn)
        # side-efect: stores the result in a local variable
        #
        # example:
        # ineq1 = (Poly(x ** 2 - 3), ">")
        # ineq2 = (Poly(-x ** 2 + 1), ">")
        # solve_poly((
        #     ineq1,
        #     ineq2,
        # ))
        if self.solution == None:
            _ineq_list = ()
            for poly_ineq in self.l:
                _ineq = (Poly(poly_ineq.f - poly_ineq.g, domain='RR'), poly_ineq.op)
                _ineq_list += (_ineq, )
            vprint(_ineq_list)
            self.solution = self.solve_poly(_ineq_list)
        return self.solution

    def solve_poly(self, polys):
        #return self.solve_poly_inequalities_and(polys)
        return self.solve_poly_inequalities_or(polys)

    def solve_poly_inequalities_and(self, polys):
        return Intersection(*[solve_poly_inequality(*p) for p in polys])

    def solve_poly_inequalities_or(self, polys):
        #return Union(*[solve_poly_inequality(*p) for p in polys])
        return solve_poly_inequalities(polys)

    #TODO
    def list_n_points(self, npoints, min_val, max_val):
        # type: (_, int) -> _
        variables = self.get_variables()
        ndim = variables.count()
        point = (min_val,) * ndim

        #list(Range(0, 10, 1).intersect(self.solution))
        step = float(max_val-min_val)/float(npoints)
        t1 = np.arange(min_val, max_val, step)
        t2 = [i for i in t1 if self.member(i)]
        return t2

    def list_n_points2(self, npoints):
        # type: (_, int) -> _
        self.solve()
        mi = self.solution.inf
        ma = self.solution.sup
        #if isinstance(mi, sympy.core.numbers.NegativeInfinity):
        if isinstance(mi, type(S.NegativeInfinity)):
            mi = -sys.float_info.max
        #if isinstance(mi, core.numbers.Infinity):
        if isinstance(mi, type(S.Infinity)):
            ma = sys.float_info.max

        #list(Range(0, 10, 1).intersect(self.solution))
        step = float(ma-mi)/float(npoints)
        t1 = np.arange(mi, ma, step)
        t2 = [i for i in t1 if self.member(i)]
        return t2

    # Membership functions
    def member(self, xpoint):
        # type: (_, tuple) -> _
        # return self.eval_tuple(xpoint)
        keys = self.get_variables()
        di = {key: xpoint[i] for i, key in enumerate(keys)}
        # di = dict.fromkeys(keys)
        return self.eval_dict(di)

    # TOREMOVE
    def member2(self, x):
        # type: (_, int) -> _
        self.solve()
        return x in self.solution

    def membership(self):
        return lambda xpoint: self.member(xpoint)

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
        # type: (_, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self.l = pickle.load(finput)
        self.solution = pickle.load(finput)

    def fromFileHumRead(self, finput = None):
        # type: (_, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        # init
        self.l = []
        self.solution = None

        # <num_constraints_dimension_i>
        num_constr_dim_i = int(finput.readline())
        for j in range(num_constr_dim_i):
            string_cond = finput.readline()
            cond = Condition()
            cond.initFromString(string_cond)
            self.l.append(cond)

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

        pickle.dump(self.l, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.solution, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        # type: (_, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        # <num_constraints_dimension_i>
        foutput.write(str(len(self.l)) + '\n')

        #foutput.write(str(self.l) + '\n')
        ##for cond_i in range(len(self.l)):
        ##    foutput.write(str(cond_i) + '\n')
        for cond_i in self.l:
            cond_i.toFileHumRead(foutput)

class Oracle:
    # An Oracle is an array of ConditionList, i.e., Oracle[i] contains the ConditionList for ith-dimension
    # For each one of the n-dimensions, we should have a ConditionList

    # Dimension = [0,..,n-1]
    def __init__(self, ndimension=1):
        # type: (_, int) -> None
        # self.oracle = {}
        keys = range(ndimension)
        self.oracle = {key: None for key in keys}

    def __str__(self):
        return self.toStr()

    def toStr(self):
        last_key = self.oracle.keys()[-1]
        _string = "["
        for key in self.oracle.keys():
            _string += str(self.oracle[key])
            if key != last_key: _string += ', '
        _string += "]"
        return _string

    # Addition of ConditionLists.
    # Overwrites previous ConditionLists
    def add(self, condlist, idimension):
        # type: (_, ConditionList, int) -> None
        self.oracle[idimension] = condlist

    # TODO
    def add_set_points(self, setpoints):
        # type: (_, set, int) -> None
        sample = setpoints.pop()
        setpoints.add(sample)

        dimension = dim(sample)
        vs = list_n_variables(dimension)

        for i in range(dimension):
            cl = ConditionList() if i not in self.oracle.keys() else self.oracle[i]
            for point in setpoints:
                c = Condition(vs[i], '==', point[i])
                cl.add(c)
            self.oracle[i] = cl

    def get_variables(self):
        # type: (_) -> _
        # By construction,
        # dimension = number of keys in self.oracle (or, at least, the key with highest value, in case that intermediate dimensions do not have conditions)
        # dimension = number of variables in all the ConditionLists
        highest_key = sorted(self.oracle.keys()).pop()
        fv = set()
        for i in self.oracle:
            fv = fv.union(self.oracle[i].get_variables())
        assert (highest_key == (len(fv) - 1)), \
            "Number of dimensions in Oracle do not match. Got " + str(highest_key) + ". Expected: " + str(len(fv) - 1)
        return list(fv)

    def eval_tuple(self, xpoint):
        # type: (_, tuple) -> _
        _eval = True
        for i in self.oracle:
            _eval = _eval and self.oracle[i].eval_tuple(xpoint)
        vprint('oracle evaluates ' + str(xpoint) + ' to ' + str(_eval))
        return _eval

    def eval_dict(self, d = None):
        # type: (_, _) -> _
        _eval = True
        for i in self.oracle:
            _eval = _eval and self.oracle[i].eval_dict(d)
        return _eval

    def eval_var_val(self, var=None, val='0'):
        # type: (_, _, int) -> _
        _eval = True
        for i in self.oracle:
            _eval = _eval and i.eval_var_val(var, val)
        return _eval

    def solve(self, idimension):
        return self.oracle[idimension].solve()

    #TODO
    def list_n_points(self, npoints, idimension):
        return self.oracle[idimension].list_n_points(npoints)

    # Membership functions
    def member(self, xpoint):
        # type: (_, tuple) -> _
        # return self.eval_tuple(xpoint)
        keys = self.get_variables()
        di = {key: xpoint[i] for i, key in enumerate(keys)}
        # di = dict.fromkeys(keys)
        return self.eval_dict(di)

    #TOREMOVE
    def member2(self, xpoint):
        # type: (dict, tuple) -> _
        assert (len(self.oracle) >= len(xpoint)), "Oracle is not prepared for points of dimension " + str(len(xpoint))
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

        self.oracle = pickle.load(finput)

    def fromFileHumRead(self, finput = None):
        # type: (_, file) -> None
        assert (finput is not None), "File object should not be null"

        # <num_dimensions>
        num_dim = int(finput.readline())
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

        pickle.dump(self.oracle, foutput, pickle.HIGHEST_PROTOCOL)


    def toFileHumRead(self, foutput = None):
        # type: (_, BinaryIO) -> None
        assert (foutput  is not None), "File object should not be null"

        # <num_dimensions>
        foutput.write(str(len(self.oracle)) + '\n')
        for i, condlist_i in self.oracle.iteritems():
             condlist_i.toFileHumRead(foutput)

EPS = 1e-1
def staircase_oracle(xs, ys):
    return lambda p: any(p[0] >= x and p[1] >= y for x, y in zip(xs, ys))

# Point (p0,p1) is closer than a 'epsilon' to point (x,y), which is member point
def membership_oracle(xs, ys, epsilon=EPS):
    return lambda p: any((abs(p[0]-x) <= epsilon) and (abs(p[1]-y) <= epsilon) for x, y in zip(xs, ys))