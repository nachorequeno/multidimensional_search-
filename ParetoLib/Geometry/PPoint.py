import numpy as np
from numpy import linalg as la

from ParetoLib._py3k import reduce


# Point = n-dimensional tuple
def dim(x):
    # type: (tuple) -> int
    return len(x)


def norm(x):
    # type: (tuple) -> float
    return la.norm(x)


# Euclidean distance between two points
def distance(x, xprime):
    # type: (tuple, tuple) -> float
    temp = subtract(x, xprime)
    return norm(temp)


# Hamming distance between two points
def hamming_distance(x, xprime):
    # type: (tuple, tuple) -> float
    temp = subtract(x, xprime)
    _sum = reduce(lambda si, sj: abs(si) + abs(sj), temp)
    return _sum


# Binary operations between points
def subtract(x, xprime):
    # type: (tuple, tuple) -> tuple
    return tuple(np.array(x) - np.array(xprime))


def add(x, xprime):
    # type: (tuple, tuple) -> tuple
    return tuple(np.array(x) + np.array(xprime))


def mult(x, i):
    # type: (tuple, float) -> tuple
    return tuple(np.array(x) * i)


def div(x, i):
    # type: (tuple, float) -> tuple
    return tuple(np.array(x) / i)


# Comparing the coordinates of two points
def greater(x, xprime):
    # type: (tuple, tuple) -> bool
    return all(np.array(x) > np.array(xprime))


def greater_equal(x, xprime):
    # type: (tuple, tuple) -> bool
    return all(np.array(x) >= np.array(xprime))


def less(x, xprime):
    # type: (tuple, tuple) -> bool
    return all(np.array(x) < np.array(xprime))


def less_equal(x, xprime):
    # type: (tuple, tuple) -> bool
    return all(np.array(x) <= np.array(xprime))


def incomparables(x, xprime):
    # type: (tuple, tuple) -> bool
    return (not greater_equal(x, xprime)) and (not greater_equal(xprime, x))


def maximum(x, xprime):
    # type: (tuple, tuple) -> tuple
    if greater_equal(x, xprime):
        return x
    else:
        return xprime


def minimum(x, xprime):
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
    assert ((0 <= i) and (i < n) and (i < m)), 'index out of range'
    out = np.array(x)
    out[i] = xprime[i]
    return tuple(out)


def select(x, xprime):
    # type: (tuple, tuple) -> tuple
    # x = (5, 6, 7)
    # xprime = (0, 0, 1)
    # select(x, xprime) == (0, 0, 7)
    n = len(x)
    m = len(xprime)
    assert (n == m), 'index out of range'
    return tuple(np.array(x) * np.array(xprime))


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
