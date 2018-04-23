import random

import pickle
from sympy import poly, polys
from sympy import var


# dict.fromkeys([1, 2, 3, 4])

# keys = [1, 2, 3, 5, 6, 7]
# {key: None for key in keys}


def list_n_variables(n):
    # type(n) = int
    assert (n >= 0), "n>=1"
    return var('x:' + str(n))


def get_variables(poly_eq):
    # type(poly_eq) = sympy.poly
    return poly_eq.free_symbols


def poly_func(eq):
    # type(eq) = string
    return poly(eq)


def random_values(min_val, max_val, d):
    # type(min/max_val) = int/float
    # type(d) = dictionary
    for i in d.keys():
        d[i] = random.uniform(min_val, max_val)
    return 0


def eval_poly_function(poly_eq, d):
    # type(poly_eq) = sympy.poly
    # type(d) = dictionary
    temp_poly_eq = poly_eq
    setsymbols = poly_eq.free_symbols

    # expr = x ** 3 + 4 * x * y - z
    # expr.subs([(x, 2), (y, 4), (z, 0)])
    for i in setsymbols:
        if i in d.keys():
            temp_poly_eq = temp_poly_eq.subs(i, d[i])

    return temp_poly_eq


# Tools for creating point datasets
# Random points
def create_random_point_ndimension(min_val, max_val, ndimension):
    # type(min/max_val) = int/float
    # type(ndimension) = int
    random.seed()
    point = ()
    for i in range(ndimension):
        point += (random.uniform(min_val, max_val),)
    return point


def create_random_points_ndimension(min_val, max_val, ndimension, num_random_points):
    return [create_random_point_ndimension(min_val, max_val, ndimension) for _ in range(num_random_points)]


def set_random_points(min_corner, max_corner, num_random_points):
    random.seed()
    xpoints = ()
    for i in range(num_random_points):
        xpoints += (random.uniform(min_corner, max_corner),)
    return xpoints


# Polynomial functions
def create_n_random_poly_functions(min_val, max_val, pol_degree, n):
    # sympy.polys.specialpolys.random_poly(x, n, inf, sup, domain=ZZ, polys=False)
    x = list_n_variables(1)
    return [polys.specialpolys.random_poly(x[0], pol_degree, min_val, max_val) for _ in range(n)]


def create_random_poly_points_ndimension(min_val, max_val, ndimension, num_random_points):
    pol_degree = int(random.uniform(1, 3))
    point = create_n_random_poly_functions(min_val, max_val, pol_degree, ndimension)
    #
    print('point: ')
    print(point)
    #
    list_points = []
    for i in range(num_random_points):
        temp_point = ()
        for poly_eq in point:
            print('poly_eq:')
            print(poly_eq)
            d = dict.fromkeys(get_variables(poly_eq))
            random_values(min_val, max_val, d)
            print('d:')
            print(d)
            temp_point += (eval_poly_function(poly_eq, d),)
        list_points.append(temp_point)
    return list_points


# Read/write numerical points from/to file
def readPoints(file):
    # Set of n points with m-dimension each one
    # (p1, p2,...,pn)
    # pi = (pi_1, pi_2,..., pi_m)
    with open(file, 'rb') as input:
        setPoints = pickle.load(input)
    return setPoints


def savePoints(file, setPoints):
    with open(file, 'wb') as output:
        pickle.dump(setPoints, output, pickle.HIGHEST_PROTOCOL)
    return 0
