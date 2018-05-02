import re
import sys
import pickle

from sympy import Poly, simplify, expand, S, default_sort_key, Intersection, Interval, Expr, Symbol
from sympy.solvers.inequalities import solve_poly_inequality, solve_poly_inequalities

from ParetoLib.Geometry.Point import *

# from data_generator import *

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


class Condition:
    # Condition = f op g
    # type(f) = sympy.Expr
    # type(g) = sympy.Expr
    # type(op) = string in {'>', '>=', '<', '<=', '==', '!='}
    #
    # Example
    # inequality = (sympy.Poly(f - g), op)
    comparison = ['==', '>', '<', '>=', '<=', '<>']

    def __init__(self, f='x', op='==', g='0'):
        # type: (_, str, str, str) -> None
        assert (op in self.comparison), "Operator " + op + " must be any of: {'>', '>=', '<', '<=', '==', '!='}"
        assert (not f.isdigit() or not g.isdigit()), \
            "At least '" + f + "' or '" + g + "' must be a polynomial expression (i.e., not a single number)"
        self.op = op
        self.f = simplify(f)
        self.g = simplify(g)

        if not self.all_coeff_are_positive():
            eprint("WARNING! Expression '%s' contains negative coefficients: %s"
                   % (str(self.get_expression()), str(self.get_expression_with_negative_coeff())))

    def initFromString(self, poly_function):
        # op_exp = (=|>|<|>=|<|<=|<>)\s\d+
        # f_regex = r'(\s*\w\s*)+'
        # g_regex = r'(\s*\w\s*)+'
        vprint('Polynomial string ', poly_function)

        op_comp = "|".join(self.comparison)
        op_regex = r'(%s)' % op_comp
        f_regex = r'[^%s]+' % op_comp
        g_regex = r'[^%s]+' % op_comp
        regex = r'(?P<f>(%s))(?P<op>(%s))(?P<g>(%s))' % (f_regex, op_regex, g_regex)
        regex_comp = re.compile(regex)
        result = regex_comp.match(poly_function)
        vprint('Parsing result ', str(result))
        # if regex_comp is not None:
        if result is not None:
            self.op = result.group('op')
            self.f = simplify(result.group('f'))
            self.g = simplify(result.group('g'))
            vprint('(op, f, g): (%s, %s, %s) ' % (self.op, self.f, self.g))

            if not self.all_coeff_are_positive():
                eprint("WARNING! Expression '%s' contains negative coefficients: %s"
                       % (str(self.get_expression()), str(self.get_expression_with_negative_coeff())))

    # Printers
    def __repr__(self):
        # type: (Condition) -> str
        return self.toStr()

    def __str__(self):
        # type: (Condition) -> str
        return self.toStr()

    def toStr(self):
        # type: (Condition) -> str
        return str(self.f) + self.op + str(self.g)

    # Equality functions
    def __eq__(self, other):
        # type: (Condition, Condition) -> bool
        return (self.f == other.f) and \
               (self.op == other.op) and \
               (self.g == other.g)

    def __ne__(self, other):
        # type: (Condition, Condition) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Condition) -> int
        return hash((self.f, self.op, self.g))

    # Membership functions
    def __contains__(self, p):
        # type: (Condition, tuple) -> bool
        return self.member(p) is True

    def all_coeff_are_positive(self):
        # type: (Condition) -> bool
        coeffs = self.get_coeff_of_expression()
        all_positives = True
        for i in coeffs:
            all_positives = all_positives and (coeffs[i] >= 0)
        return all_positives

    def get_coeff_of_expression(self):
        # type: (Condition) -> dict
        expr = self.get_expression()
        expanded_expr = expand(expr)
        simpl_expr = simplify(expanded_expr)
        coeffs = simpl_expr.as_coefficients_dict()
        return coeffs

    def get_positive_coeff_of_expression(self):
        # type: (Condition) -> dict
        expr = self.get_expression()
        expanded_expr = expand(expr)
        simpl_expr = simplify(expanded_expr)
        coeffs = simpl_expr.as_coefficients_dict()
        positive_coeff = {i: coeffs[i] for i in coeffs if coeffs[i] >= 0}
        return positive_coeff

    def get_negative_coeff_of_expression(self):
        # type: (Condition) -> dict
        expr = self.get_expression()
        expanded_expr = expand(expr)
        simpl_expr = simplify(expanded_expr)
        coeffs = simpl_expr.as_coefficients_dict()
        negative_coeff = {i: coeffs[i] for i in coeffs if coeffs[i] < 0}
        return negative_coeff

    def get_expression_with_negative_coeff(self):
        # type: (Condition) -> Expr
        negative_coeff = self.get_negative_coeff_of_expression()
        l = ['%s * %s' % (negative_coeff[i], i) for i in negative_coeff]
        return simplify(''.join(l))

    def get_expression_with_positive_coeff(self):
        # type: (Condition) -> Expr
        positive_coeff = self.get_positive_coeff_of_expression()
        l = ['%s * %s' % (positive_coeff[i], i) for i in positive_coeff]
        return simplify('+'.join(l))

    def get_expression(self):
        # type: (Condition) -> Expr
        return simplify(self.f - self.g)

    def get_variables(self):
        # type: (Condition) -> list
        expr = self.get_expression()
        return sorted(expr.free_symbols, key=default_sort_key)

    def eval_tuple(self, xpoint):
        # type: (Condition, tuple) -> Expr
        keys_fv = self.get_variables()
        di = {key: xpoint[i] for i, key in enumerate(keys_fv)}

        vprint('Condition ', str(self), ' evaluates ', str(xpoint), ' to ', str(self.eval_dict(di)))
        vprint('di ', str(di))
        return self.eval_dict(di)

    def eval_dict(self, d=None):
        # type: (Condition, dict) -> Expr
        keys_fv = self.get_variables()
        if d is None:
            # di = dict.fromkeys(expr.free_symbols)
            di = {key: 0 for key in keys_fv}
        else:
            di = d
            keys = set(d.keys())
            assert keys.issuperset(keys_fv), "Keys in dictionary " \
                                             + str(d) \
                                             + " do not match with the variables in the condition"
        expr = self.get_expression()
        res = expr.subs(di)
        ex = str(res) + self.op + '0'
        vprint('Expression ', str(simplify(ex)))
        return simplify(ex)

    def eval_var_val(self, variable=None, val='0'):
        # type: (Condition, Symbol, int) -> Expr
        if variable is None:
            fvset = self.get_variables()
            fv = fvset.pop()
        else:
            fv = variable
        expr = self.get_expression()
        res = expr.subs(fv, val)
        ex = str(res) + self.op + '0'
        vprint('Expression ', str(simplify(ex)))
        return simplify(ex)

    # Membership functions
    def member(self, xpoint):
        # type: (Condition, tuple) -> Expr
        keys = self.get_variables()
        di = {key: xpoint[i] for i, key in enumerate(keys)}
        return self.eval_dict(di)

    def membership(self):
        # type: (Condition, tuple) -> function
        return lambda xpoint: self.member(xpoint)

    # Read/Write file functions
    def fromFile(self, fname='', human_readable=False):
        # type: (Condition, str, bool) -> None
        assert (fname != ''), "Filename should not be null"

        mode = 'rb'
        finput = open(fname, mode)
        if human_readable:
            self.fromFileHumRead(finput)
        else:
            self.fromFileNonHumRead(finput)
        finput.close()

    def fromFileNonHumRead(self, finput=None):
        # type: (Condition, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self.f = pickle.load(finput)
        self.op = pickle.load(finput)
        self.g = pickle.load(finput)

    def fromFileHumRead(self, finput=None):
        # type: (Condition, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        poly_function = finput.readline()
        self.initFromString(poly_function)

    def toFile(self, fname='', append=False, human_readable=False):
        # type: (Condition, str, bool, bool) -> None
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
        # type: (Condition, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        pickle.dump(self.f, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.op, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.g, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        # type: (Condition, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        # str(self.f) + self.op + str(self.g)
        foutput.write(str(self) + '\n')


class ConditionList:
    # List of conditions:
    # [c1, c2,..., cn]

    def __init__(self):
        self.l = []
        self.solution = None

    # Printers
    def __repr__(self):
        # type: (ConditionList) -> str
        return self.toStr()

    def __str__(self):
        # type: (ConditionList) -> str
        return self.toStr()

    def toStr(self):
        # type: (ConditionList) -> str
        _string = "["
        for i, item in enumerate(self.l):
            _string += str(item)
            if i < (len(self.l) - 1): _string += ', '
        _string += "]"
        return _string

    # Equality functions
    def __eq__(self, other):
        # type: (ConditionList, ConditionList) -> bool
        return self.l == other.l

    def __ne__(self, other):
        # type: (ConditionList, ConditionList) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (ConditionList) -> int
        return hash(tuple(self.l))

    # Membership functions
    def __contains__(self, cond):
        # type: (ConditionList, Condition) -> bool
        return cond in self.l

    # ConditionList functions
    def add(self, cond):
        # type: (ConditionList, Condition) -> None
        self.l.append(cond)

    def get_variables(self):
        # type: (ConditionList) -> list
        fv = set()
        for i in self.l:
            fv = fv.union(i.get_variables())
        return list(fv)

    def eval_tuple(self, xpoint):
        # type: (ConditionList, tuple) -> Expr
        _eval = True
        for i in self.l:
            _eval = _eval and i.eval_tuple(xpoint)
        # _eval = all(i.eval_tuple(xpoint) for i in self.l)
        vprint('Condition list ', self.toStr(), ' evaluates ', str(xpoint), ' to ', str(_eval))
        return _eval

    def eval_dict(self, d=None):
        # type: (ConditionList, dict) -> Expr
        _eval = True
        for i in self.l:
            _eval = _eval and i.eval_dict(d)
        # _eval = all(i.eval_dict(d) for i in self.l)
        vprint('Condition list ', self.toStr(), ' evaluates ', str(d), ' to ', str(_eval))
        return _eval

    def eval_var_val(self, var=None, val='0'):
        # type: (ConditionList, Symbol, int) -> Expr
        _eval = True
        for i in self.l:
            _eval = _eval and i.eval_var_val(var, val)
        vprint('Condition list ', self.toStr(), ' evaluates ', str(var), ' with ', str(val), ' to ', str(_eval))
        return _eval

    def solve(self):
        # type: (ConditionList) -> Interval
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
                # _ineq = (Poly(poly_ineq.f - poly_ineq.g, domain='RR'), poly_ineq.op)
                _ineq = (Poly(poly_ineq.get_expression(), domain='RR'), poly_ineq.op)
                _ineq_list += (_ineq,)
            vprint(_ineq_list)
            self.solution = self.solve_poly(_ineq_list)
        return self.solution

    def solve_poly(self, polys):
        # return self.solve_poly_inequalities_and(polys)
        return self.solve_poly_inequalities_or(polys)

    def solve_poly_inequalities_and(self, polys):
        return Intersection(*[solve_poly_inequality(*p) for p in polys])

    def solve_poly_inequalities_or(self, polys):
        # return Union(*[solve_poly_inequality(*p) for p in polys])
        return solve_poly_inequalities(polys)

    # Membership functions
    def member(self, xpoint):
        # type: (ConditionList, tuple) -> Expr
        # return self.eval_tuple(xpoint)
        keys = self.get_variables()
        di = {key: xpoint[i] for i, key in enumerate(keys)}
        # di = dict.fromkeys(keys)
        return self.eval_dict(di)

    # TOREMOVE
    def member2(self, x):
        # type: (ConditionList, int) -> _
        self.solve()
        return x in self.solution

    def membership(self):
        # type: (ConditionList, tuple) -> function
        return lambda xpoint: self.member(xpoint)

    # Read/Write file functions
    def fromFile(self, fname='', human_readable=False):
        # type: (ConditionList, str, bool) -> None
        assert (fname != ''), "Filename should not be null"

        mode = 'rb'
        finput = open(fname, mode)
        if human_readable:
            self.fromFileHumRead(finput)
        else:
            self.fromFileNonHumRead(finput)
        finput.close()

    def fromFileNonHumRead(self, finput=None):
        # type: (ConditionList, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self.l = pickle.load(finput)
        self.solution = pickle.load(finput)

    def fromFileHumRead(self, finput=None):
        # type: (ConditionList, BinaryIO) -> None
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
        # type: (ConditionList, str, bool, bool) -> None
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
        # type: (ConditionList, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        pickle.dump(self.l, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.solution, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        # type: (ConditionList, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        # <num_constraints_dimension_i>
        foutput.write(str(len(self.l)) + '\n')

        for cond_i in self.l:
            cond_i.toFileHumRead(foutput)


class OracleFunction:
    # An OracleFunction is an array of ConditionList, i.e., OracleFunction[i] contains the ConditionList for ith-dimension
    # For each one of the n-dimensions, we should have a ConditionList

    # Dimension = [0,..,n-1]
    def __init__(self, ndimension=1):
        # type: (OracleFunction, int) -> None
        # self.oracle = {}
        keys = range(ndimension)
        #self.oracle = {key: None for key in keys}
        self.oracle = {key: ConditionList() for key in keys}

    # Printers
    def __repr__(self):
        # type: (OracleFunction) -> str
        return self.toStr()

    def __str__(self):
        # type: (OracleFunction) -> str
        return self.toStr()

    def toStr(self):
        # type: (OracleFunction) -> str
        last_key = self.oracle.keys()[-1]
        _string = "["
        for key in self.oracle.keys():
            _string += str(self.oracle[key])
            if key != last_key: _string += ', '
        _string += "]"
        return _string

    # Equality functions
    def __eq__(self, other):
        # type: (OracleFunction, OracleFunction) -> bool
        return self.oracle == other.oracle

    def __ne__(self, other):
        # type: (OracleFunction, OracleFunction) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (OracleFunction) -> int
        return hash(tuple(self.oracle))

    # Addition of ConditionLists.
    # Overwrites previous ConditionLists
    def add(self, condlist, idimension):
        # type: (OracleFunction, ConditionList, int) -> None
        self.oracle[idimension] = condlist

    def get_variables(self):
        # type: (OracleFunction) -> list
        # By construction,
        # dimension = number of keys in self.oracle (or, at least, the key with highest value, in case that intermediate dimensions do not have conditions)
        # dimension = number of variables in all the ConditionLists
        highest_key = sorted(self.oracle.keys()).pop()
        fv = set()
        for i in self.oracle:
            fv = fv.union(self.oracle[i].get_variables())
        #        assert (highest_key == (len(fv) - 1)), \
        #            "Number of dimensions in OracleFunction do not match. Got " + str(highest_key) + ". Expected: " + str(len(fv) - 1)
        return list(fv)

    def dim(self):
        # type: (OracleFunction) -> int
        return len(self.get_variables())

    def eval_tuple(self, xpoint):
        # type: (OracleFunction, tuple) -> Expr
        _eval = True
        for i in self.oracle:
            _eval = _eval and self.oracle[i].eval_tuple(xpoint)
        vprint('OracleFunction evaluates ', str(xpoint), ' to ', str(_eval))
        return _eval

    def eval_dict(self, d=None):
        # type: (OracleFunction, dict) -> Expr
        vprint('OracleFunction evaluates ', self.toStr())
        _eval = True
        # _eval = False
        for i in self.oracle:
            _eval = _eval and self.oracle[i].eval_dict(d)
            # _eval = _eval or self.oracle[i].eval_dict(d)
        return _eval

    def eval_var_val(self, var=None, val='0'):
        # type: (OracleFunction, Symbol, int) -> Expr
        vprint('OracleFunction evaluates ', self.toStr())
        _eval = True
        for i in self.oracle:
            _eval = _eval and i.eval_var_val(var, val)
        return _eval

    def solve(self, idimension):
        return self.oracle[idimension].solve()

    # TODO
    def list_n_points(self, npoints, idimension):
        return self.oracle[idimension].list_n_points(npoints)

    # Membership functions
    def __contains__(self, p):
        # type: (OracleFunction, tuple) -> bool
        return self.member(p) is True

    def member(self, xpoint):
        # type: (OracleFunction, tuple) -> Expr
        # return self.eval_tuple(xpoint)
        vprint(xpoint)
        keys = self.get_variables()
        di = {key: xpoint[i] for i, key in enumerate(keys)}
        # di = dict.fromkeys(keys)
        return self.eval_dict(di)

    # TOREMOVE
    def member2(self, xpoint):
        # type: (OracleFunction, tuple) -> Expr
        assert (len(self.oracle) >= len(xpoint)), "OracleFunction is not prepared for points of dimension " + str(
            len(xpoint))
        ismember = True
        # for i, condlist in enumerate(self.oracle):
        for i, condlist in self.oracle.iteritems():
            ismember = ismember and condlist.member(xpoint[i])
        return ismember

    def membership(self):
        # type: (OracleFunction) -> function
        return lambda xpoint: self.member(xpoint)

    # Read/Write file functions
    def fromFile(self, fname='', human_readable=False):
        # type: (OracleFunction, str, bool) -> None
        assert (fname != ''), "Filename should not be null"

        mode = 'rb'
        finput = open(fname, mode)
        if human_readable:
            self.fromFileHumRead(finput)
        else:
            self.fromFileNonHumRead(finput)
        finput.close()

    def fromFileNonHumRead(self, finput=None):
        # type: (OracleFunction, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self.oracle = pickle.load(finput)

    def fromFileHumRead(self, finput=None):
        # type: (OracleFunction, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        # <num_dimensions>
        num_dim = int(finput.readline())
        self.oracle = dict.fromkeys(range(num_dim))
        for i in range(num_dim):
            self.oracle[i] = ConditionList()
            self.oracle[i].fromFileHumRead(finput)

    def toFile(self, fname='', append=False, human_readable=False):
        # type: (OracleFunction, str, bool, bool) -> None
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
        # type: (OracleFunction, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        pickle.dump(self.oracle, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        # type: (OracleFunction, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        # <num_dimensions>
        foutput.write(str(len(self.oracle)) + '\n')
        for i, condlist_i in self.oracle.iteritems():
            condlist_i.toFileHumRead(foutput)


EPS = 1e-1


def staircase_oracle(xs, ys):
    # type: (tuple, tuple) -> function
    return lambda p: any(p[0] >= x and p[1] >= y for x, y in zip(xs, ys))


# Point (p0,p1) is closer than a 'epsilon' to point (x,y), which is member point
def membership_oracle(xs, ys, epsilon=EPS):
    # type: (tuple, tuple, float) -> function
    return lambda p: any((abs(p[0] - x) <= epsilon) and (abs(p[1] - y) <= epsilon) for x, y in zip(xs, ys))
