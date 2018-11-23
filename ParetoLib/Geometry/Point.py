# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Point.

This module introduces a set of operations for managing 
Cartesian points in n-dimensional spaces as vectors (i.e., tuples) 
of n components.
"""

import math

import ParetoLib.Geometry
from ParetoLib._py3k import reduce


# Auxiliary functions for computing the algebraic properties
# of a vector (e.g., norm, distance, etc.)

def r(i):
    # type: (float) -> float
    """
    Rounds a float number with n decimals to a float number
    with m decimals, where m is the maximum arithmetic precision
    supported by our tool.

    The maximum number of decimals supported by our tool is
    specified by the following variable:

    ParetoLib.Geometry.__numdigits__

    Args:
        i (float): A float number.

    Returns:
        float: round(i)

    Example:
    >>> i = 0.500...01
    >>> r(i)
    >>> 0.5
    """

    return round(i, ParetoLib.Geometry.__numdigits__)


def dim(x):
    # type: (tuple) -> int
    """
    Dimension of a Cartesian point.
    
    Args:
        x (tuple): A Cartesian point.

    Returns:
        int: len(x)
        
    Example:
    >>> x = (2, 4, 6)
    >>> dim(x)
    >>> 3
    """
    return len(x)


def norm(x):
    # type: (tuple) -> float
    """
    Norm of a vector.
    
    Args:
        x (tuple): A vector.

    Returns:
        float: sqrt(sum(x[i]**2)) for i = 0..dim(x)-1
        
    Example:
    >>> x = (2, 4, 6)
    >>> norm(x)
    >>> 7.48
    """
    square_element_i = tuple(xi * xi for xi in x)
    _sum = sum(square_element_i)
    return math.sqrt(_sum)


def distance(x, xprime):
    # type: (tuple, tuple) -> float
    """
    Euclidean distance between two Cartesian points.
    
    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        float: norm(x - xprime)
        
    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> distance(x, xprime)
    >>> 7.48
    """
    temp = subtract(x, xprime)
    return norm(temp)


def hamming_distance(x, xprime):
    # type: (tuple, tuple) -> float
    """
    Hamming distance between two Cartesian points.
    
    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        float: sum(x[i] - xprime[i]) for i = 0..dim(x)-1
        
    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> distance(x, xprime)
    >>> 12.0
    """
    temp = subtract(x, xprime)
    _sum = reduce(lambda si, sj: abs(si) + abs(sj), temp)
    return _sum


# Arithmetic operations between two Cartesian points or between
# a Cartesian point and a scale factor.

def subtract(x, xprime):
    # type: (tuple, tuple) -> tuple
    """
    Component wise subtraction of two Cartesian points
    
    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        tuple: x[i] - xprime[i] for i = 0..dim(x)-1
        
    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> subtract(x, xprime)
    >>> (2, 4, 6)
    """
    return tuple(xi[0] - xi[1] for xi in zip(x, xprime))


def add(x, xprime):
    # type: (tuple, tuple) -> tuple
    """
    Component wise addition of two Cartesian points
    
    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        tuple: x[i] + xprime[i] for i = 0..dim(x)-1
        
    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> add(x, xprime)
    >>> (8, 8, 8)
    """
    return tuple(xi[0] + xi[1] for xi in zip(x, xprime))


def mult(x, i):
    # type: (tuple, float) -> tuple
    """
    Multiplication of a Cartesian point by a scale factor
    
    Args:
        x (tuple): A Cartesian point.
        i (float): The scale factor.

    Returns:
        tuple: x[j]*i for j = 0..dim(x)-1
        
    Example:
    >>> x = (5, 6, 7)
    >>> i = 2.0
    >>> mult(x, i)
    >>> (10.0, 12.0, 14.0)
    """
    return tuple(xi * i for xi in x)


def div(x, i):
    # type: (tuple, float) -> tuple
    """
    Division of a Cartesian point by a scale factor
    
    Args:
        x (tuple): A Cartesian point.
        i (float): The scale factor.

    Returns:
        tuple: x[j]/i for j = 0..dim(x)-1
        
    Example:
    >>> x = (5, 6, 7)
    >>> i = 2.0
    >>> div(x, i)
    >>> (2.5, 3.0, 3.5)
    """
    return tuple(xi / i for xi in x)


# Comparison of two points
def greater(x, xprime):
    # type: (tuple, tuple) -> bool
    """
    Component wise comparison of two Cartesian points

    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        bool: x[i] > xprime[i] for i = 0..dim(x)-1

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> greater(x, xprime)
    >>> True
    """
    return all(xi[0] > xi[1] for xi in zip(x, xprime))


def greater_equal(x, xprime):
    # type: (tuple, tuple) -> bool
    """
    Component wise comparison of two Cartesian points

    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        bool: x[i] >= xprime[i] for i = 0..dim(x)-1

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> greater_equal(x, xprime)
    >>> True
    """
    return all(xi[0] >= xi[1] for xi in zip(x, xprime))


def less(x, xprime):
    # type: (tuple, tuple) -> bool
    """
    Component wise comparison of two Cartesian points

    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        bool: x[i] < xprime[i] for i = 0..dim(x)-1

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> less(x, xprime)
    >>> False
    """
    return all(xi[0] < xi[1] for xi in zip(x, xprime))


def less_equal(x, xprime):
    # type: (tuple, tuple) -> bool
    """
    Component wise comparison of two Cartesian points

    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        bool: x[i] <= xprime[i] for i = 0..dim(x)

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> less_equal(x, xprime)
    >>> False
    """
    return all(xi[0] <= xi[1] for xi in zip(x, xprime))


def incomparables(x, xprime):
    # type: (tuple, tuple) -> bool
    """
    Component wise comparison of two Cartesian points

    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        bool: (not greater_equal(x, xprime)) and
              (not greater_equal(xprime, x))

        Equivalently,
        for i = 0..j-1,j+1..dim(x): x[i] <= xprime[i]
        and for some j: x[j] > xprime[j]

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 8, 1)
    >>> incomparables(x, xprime)
    >>> True
    """

    return (not greater_equal(x, xprime)) and (not greater_equal(xprime, x))


def maximum(x, xprime):
    # type: (tuple, tuple) -> tuple
    """
    Component wise comparison of two Cartesian points

    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        tuple: x if x[i] > xprime[i] for i = 0..dim(x)-1, else xprime

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> maximum(x, xprime)
    >>> (5, 6, 7)
    """
    if greater_equal(x, xprime):
        return x
    else:
        return xprime


def minimum(x, xprime):
    # type: (tuple, tuple) -> tuple
    """
    Component wise comparison of two Cartesian points

    Args:
        x (tuple): The first point.
        xprime (tuple): The second point.

    Returns:
        tuple: x if x[i] < xprime[i] for i = 0..dim(x)-1, else xprime

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> minimum(x, xprime)
    >>> (3, 2, 1)
    """
    if less_equal(x, xprime):
        return x
    else:
        return xprime


def subt(i, x, xprime):
    # type: (int, tuple, tuple) -> tuple
    """
    Substitution of the i-th component of a Cartesian point
    by the i-th component of another Cartesian point.

    Args:
        i (int): Index
        x (tuple): The first point.
        xprime (tuple): The second point.

    Return:
        tuple: (x[0],...,x[i-1], xprime[i], x[i+1],..., x[dim(x)-1])

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (0, 0, 1)
    >>> select(x, xprime)
    >>> (0, 0, 7)
    """
    n = len(x)
    m = len(xprime)
    assert ((0 <= i) and (i < n) and (i < m)), 'index out of range'
    # Substitution of i-th element in xpoint
    tup1 = x[0:i]
    tup2 = (xprime[i],)
    tup3 = x[(i + 1):]
    return tup1 + tup2 + tup3


def select(x, xprime):
    # type: (tuple, tuple) -> tuple
    """
    Selection of components from a Cartesian point
    according to an index vector.
    
    Args:
        x (tuple): A Cartesian point.
        xprime (tuple): An index vector.

    Return:
        tuple: Components of x selected by xprime.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (0, 0, 1)
    >>> select(x, xprime)
    >>> (0, 0, 7)
    """
    n = len(x)
    m = len(xprime)
    assert (n == m), 'index out of range'
    return tuple(xi if yi > 0 else 0 for xi, yi in zip(x, xprime))


# Integer to binary notation
def int_to_bin_list(x, pad=0):
    # type: (int, int) -> list
    """
    Conversion of a integer number to binary notation.
    The result is stored as a list of digits [0,1]
    Args:
        x (int): A Cartesian point.
        pad (int): Length of the result list.
                   By default, 0 (i.e., no need of padding)

    Return:
        list: Representation of x as a list of binary digits.

    Example:
    >>> x = 4
    >>> int_to_bin_list(x, 0)
    >>> [1, 0, 0]
    >>> int_to_bin_list(x, 4)
    >>> [0, 1, 0, 0]
    """

    temp1 = [int(i) for i in bin(x)[2:]]
    pad_temp = pad if pad > 0 else len(temp1)
    temp2 = [0] * (pad_temp - len(temp1)) + temp1
    return temp2


def int_to_bin_tuple(x, pad=0):
    # type: (int, int) -> tuple
    """ Equivalent to int_to_bin_list(x, pad=0).
    Returns a tuple instead of a list.

    Args:
        x (int): A Cartesian point.
        pad (int): Length of the result list.
                   By default, 0 (i.e., no need of padding)

    Return:
        tuple: Representation of x as a tuple of binary digits.

    Example:
    >>> x = 4
    >>> int_to_bin_list(x, 0)
    >>> (1, 0, 0)
    >>> int_to_bin_list(x, 4)
    >>> (0, 1, 0, 0)
    """
    return tuple(int_to_bin_list(x, pad))


# Domination
def dominates(x, xprime):
    # type: (tuple, tuple) -> bool
    """
    Synonym of less_equal(x, xprime)
    """
    return less_equal(x, xprime)


def is_dominated(x, xprime):
    # type: (tuple, tuple) -> bool
    """
    Synonym of less_equal(xprime, x)
    """
    return less_equal(xprime, x)
