import itertools


# Point = n-dimensional tuple
def dim(x):
    return len(x)


# Binary operations between points
def subtract(x, xprime):
    return tuple(xi[0] - xi[1] for xi in zip(x, xprime))


def add(x, xprime):
    return tuple(xi[0] + xi[1] for xi in zip(x, xprime))


def mult(x, int):
    return tuple(xi * int for xi in x)


def div(x, int):
    return tuple(xi / int for xi in x)


# Comparing the coordinates of two points
def greater(x, xprime):
    return all(xi[0] > xi[1] for xi in zip(x, xprime))


def greater_equal(x, xprime):
    return all(xi[0] >= xi[1] for xi in zip(x, xprime))


def less(x, xprime):
    return all(xi[0] < xi[1] for xi in zip(x, xprime))


def less_equal(x, xprime):
    return all(xi[0] <= xi[1] for xi in zip(x, xprime))


def incomparable(x, xprime):
    return (not greater_equal(x, xprime)) and (not greater_equal(xprime, x))


def max(x, xprime):
    if greater_equal(x, xprime):
        return x
    else:
        return xprime

def min(x, xprime):
    if less_equal(x, xprime):
        return x
    else:
        return xprime

# Subtitution of i-th element in xpoint
def subt(i, x, xprime):
    n = len(x)
    m = len(xprime)
    assert ((0 <= i) and (i < n) and (i < m)), "index out of range"
    tup1 = x[0:i]
    tup2 = (xprime[i],)
    tup3 = x[(i + 1):]
    return tup1 + tup2 + tup3

def select(x, xprime):
    # x = (5, 6, 7)
    # xprime = (0, 0, 1)
    # select(x, xprime) == (0, 0, 7)
    n = len(x)
    m = len(xprime)
    assert (n == m), "index out of range"
    temp = ()
    for xi, yi in zip(x, xprime):
        if (yi > 0):
            temp += (xi, )
        else :
            temp += (0, )
    return temp


# Integer to binary notation
def int2binlist(x, pad=0):
    temp1 = [int(i) for i in bin(x)[2:]]
    if pad == 0:
        pad == len(temp1)
    temp2 = [0] * (pad - len(temp1)) + temp1
    return temp2

def int2bintuple(x, pad=0):
    return tuple(int2binlist(x, pad))

# Printer
#def str(x):
    #    _string = "("
    #for i, data in enumerate(x):
    #    _string += str(data)
    #    if i != dim(x) - 1:
    #        _string += ", "
    #_string += ")"
#return _string