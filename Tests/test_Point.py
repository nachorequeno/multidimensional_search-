import time

import numpy as np

import ParetoLib.Geometry.PPoint as pp
import ParetoLib.Geometry.Point as p

REP = 100
DIM = 2

def perfm_for(f, l):
    start = time.time()
    for i in range(l):
        f(i)
    end = time.time()
    print(str(end-start))

def perfmTest(rep=REP,
              dim=DIM):
    xxprime = np.random.rand(2, dim)

    x = tuple(xxprime[0])
    xprime = tuple(xxprime[1])

    print("Point (tuple)")
    perfm_for(lambda z: p.norm(x), rep)
    perfm_for(lambda z: p.distance(x, xprime), rep)
    perfm_for(lambda z: p.distanceHamming(x, xprime), rep)
    perfm_for(lambda z: p.subtract(x, xprime), rep)
    perfm_for(lambda z: p.add(x, xprime), rep)
    perfm_for(lambda z: p.mult(x, 2), rep)
    perfm_for(lambda z: p.div(x, 2), rep)
    perfm_for(lambda z: p.greater(x, xprime), rep)
    perfm_for(lambda z: p.greater_equal(x, xprime), rep)
    perfm_for(lambda z: p.less(x, xprime), rep)
    perfm_for(lambda z: p.less_equal(x, xprime), rep)
    perfm_for(lambda z: p.max(x, xprime), rep)
    perfm_for(lambda z: p.min(x, xprime), rep)

    print("Point (numpy)")
    perfm_for(lambda z: pp.norm(x), rep)
    perfm_for(lambda z: pp.distance(x, xprime), rep)
    perfm_for(lambda z: pp.distanceHamming(x, xprime), rep)
    perfm_for(lambda z: pp.subtract(x, xprime), rep)
    perfm_for(lambda z: pp.add(x, xprime), rep)
    perfm_for(lambda z: pp.mult(x, 2), rep)
    perfm_for(lambda z: pp.div(x, 2), rep)
    perfm_for(lambda z: pp.greater(x, xprime), rep)
    perfm_for(lambda z: pp.greater_equal(x, xprime), rep)
    perfm_for(lambda z: pp.less(x, xprime), rep)
    perfm_for(lambda z: pp.less_equal(x, xprime), rep)
    perfm_for(lambda z: pp.max(x, xprime), rep)
    perfm_for(lambda z: pp.min(x, xprime), rep)

def eq(f1, f2):
    areEq = (f1() == f2())
    assert areEq, "Failed equality test (%s, %s)" % (str(f1), str(f2))
    return areEq

def eqTest(dim=DIM):
    xxprime = np.random.rand(2, dim)

    x = tuple(xxprime[0])
    xprime = tuple(xxprime[1])

    res = [eq(lambda: p.norm(x), lambda: pp.norm(x))]
    res.append(eq(lambda: p.distance(x, xprime), lambda: pp.distance(x, xprime)))
    res.append(eq(lambda: p.distanceHamming(x, xprime), lambda: pp.distanceHamming(x, xprime)))
    res.append(eq(lambda: p.subtract(x, xprime), lambda: pp.subtract(x, xprime)))
    #res.append(eq(lambda: p.add(x, xprime), lambda: pp.add(x, xprime)))
    res.append(eq(lambda: p.add(x, xprime), lambda: pp.subtract(x, xprime))) ####
    res.append(eq(lambda: p.mult(x, 2), lambda: pp.mult(x, 2)))
    res.append(eq(lambda: p.div(x, 2), lambda: pp.div(x, 2)))
    res.append(eq(lambda: p.greater(x, xprime), lambda: pp.greater(x, xprime)))
    res.append(eq(lambda: p.greater_equal(x, xprime), lambda: pp.greater_equal(x, xprime)))
    res.append(eq(lambda: p.less(x, xprime), lambda: pp.less(x, xprime)))
    res.append(eq(lambda: p.less_equal(x, xprime), lambda: pp.less_equal(x, xprime)))
    res.append(eq(lambda: p.max(x, xprime), lambda: pp.max(x, xprime)))
    res.append(eq(lambda: p.min(x, xprime), lambda: pp.min(x, xprime)))
    assert all(res), "Failed equality test"


if __name__ == '__main__':
    eqTest()
    perfmTest()

