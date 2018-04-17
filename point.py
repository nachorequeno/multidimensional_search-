import math


# Point = n-dimensional tuple
def dim(x):
    # type: (tuple) -> int
    return len(x)


def norm(x):
    # type: (tuple) -> float
    square_element_i = map(lambda si: si * si, x)
    _sum = reduce(lambda si, sj: si + sj, square_element_i)
    return math.sqrt(_sum)


# Euclidean distance between two points
def distance(x, xprime):
    # type: (tuple, tuple) -> float
    temp = subtract(x, xprime)
    return norm(temp)


# Hamming distance between two points
def distanceHamming(x, xprime):
    # type: (tuple, tuple) -> float
    temp = subtract(x, xprime)
    _sum = reduce(lambda si, sj: abs(si) + abs(sj), temp)
    return _sum


# Binary operations between points
def subtract(x, xprime):
    # type: (tuple, tuple) -> tuple
    return tuple(xi[0] - xi[1] for xi in zip(x, xprime))


def add(x, xprime):
    # type: (tuple, tuple) -> tuple
    return tuple(xi[0] + xi[1] for xi in zip(x, xprime))


def mult(x, int):
    # type: (tuple, int) -> tuple
    return tuple(xi * int for xi in x)


def div(x, int):
    # type: (tuple, int) -> tuple
    return tuple(xi / int for xi in x)


# Comparing the coordinates of two points
def greater(x, xprime):
    # type: (tuple, tuple) -> bool
    return all(xi[0] > xi[1] for xi in zip(x, xprime))


def greater_equal(x, xprime):
    # type: (tuple, tuple) -> bool
    return all(xi[0] >= xi[1] for xi in zip(x, xprime))


def less(x, xprime):
    # type: (tuple, tuple) -> bool
    return all(xi[0] < xi[1] for xi in zip(x, xprime))


def less_equal(x, xprime):
    # type: (tuple, tuple) -> bool
    return all(xi[0] <= xi[1] for xi in zip(x, xprime))


def incomparable(x, xprime):
    # type: (tuple, tuple) -> bool
    return (not greater_equal(x, xprime)) and (not greater_equal(xprime, x))


def max(x, xprime):
    # type: (tuple, tuple) -> tuple
    if greater_equal(x, xprime):
        return x
    else:
        return xprime


def min(x, xprime):
    # type: (tuple, tuple) -> tuple
    if less_equal(x, xprime):
        return x
    else:
        return xprime


# Subtitution of i-th element in xpoint
def subt(i, x, xprime):
    # type: (int, tuple, tuple) -> tuple
    n = len(x)
    m = len(xprime)
    assert ((0 <= i) and (i < n) and (i < m)), "index out of range"
    tup1 = x[0:i]
    tup2 = (xprime[i],)
    tup3 = x[(i + 1):]
    return tup1 + tup2 + tup3


def select(x, xprime):
    # type: (tuple, tuple) -> tuple
    # x = (5, 6, 7)
    # xprime = (0, 0, 1)
    # select(x, xprime) == (0, 0, 7)
    n = len(x)
    m = len(xprime)
    assert (n == m), "index out of range"
    temp = ()
    for xi, yi in zip(x, xprime):
        if (yi > 0):
            temp += (xi,)
        else:
            temp += (0,)
    return temp


# Integer to binary notation
def int2binlist(x, pad=0):
    # type: (int, int) -> list
    temp1 = [int(i) for i in bin(x)[2:]]
    pad_temp = pad if pad > 0 else len(temp1)
    temp2 = [0] * (pad_temp - len(temp1)) + temp1
    return temp2


def int2bintuple(x, pad=0):
    # type: (int, int) -> tuple
    return tuple(int2binlist(x, pad))

# Printer
# def str(x):
#    _string = "("
# for i, data in enumerate(x):
#    _string += str(data)
#    if i != dim(x) - 1:
#        _string += ", "
# _string += ")"
# return _string
