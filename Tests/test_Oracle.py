import os
import tempfile as tf
import copy
import random
import __builtin__

import multiprocessing
import matplotlib.pyplot as plt

from ParetoLib.Search.Search import *
from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Oracle.OraclePoint import *
from ParetoLib.Oracle._NDTree import *


##################
# OracleFunction #
##################

# Test polynomial conditions
def testMembershipCondition():

    c1 = Condition('x', '>', '2')
    c2 = Condition('y', '<', '0.75')

    cl1 = ConditionList()
    cl1.add(c1)
    f1 = cl1.membership()
    # f1(0)
    # f1(3)

    p1 = (0.0, )
    p2 = (3.0, )

    assert (not f1(p1)), \
        "Condition membership failed. Expected to be false:\n(f1, val) = (%s, %s)" % (str(f1), str(p1))
    assert (f1(p2)), \
        "Condition membership failed. Expected to be true:\n(f1, val) = (%s, %s)" % (str(f1), str(p2))

    cl2 = ConditionList()
    cl2.add(c2)
    f2 = cl2.membership()
    # f2(1.0)
    # f2(0.1)

    p1 = (1.0,)
    p2 = (0.1,)

    assert (not f2(p1)), \
        "ConditionList membership failed. Expected to be false:\n(f2, val) = (%s, %s)" % (str(f2), str(p1))
    assert (f2(p2)), \
        "ConditionList membership failed. Expected to be true:\n(f2, val) = (%s, %s)" % (str(f2), str(p2))

    # Oracle
    ora = OracleFunction()
    ora.add(cl1, 0)
    ora.add(cl2, 1)
    fora = ora.membership()
    # fora(p1)
    # fora(p2)
    # fora(p3)

    p1 = (0.0, 1.0)
    p2 = (3.0, 0.1)
    p3 = (2.0, 1.0)

    assert (not fora(p1)), \
        "Oracle membership failed. Expected to be false:\n(fora, val) = (%s, %s)" % (str(fora), str(p1))
    assert (fora(p2)), \
        "Oracle membership failed. Expected to be true:\n(fora, val) = (%s, %s)" % (str(fora), str(p2))
    assert (not fora(p3)), \
        "Oracle membership failed. Expected to be false:\n(fora, val) = (%s, %s)" % (str(fora), str(p3))


# Test OracleFunction
def testOracleFunction(human_readable=False):
    # type: (bool) -> _
    tmpfile = tf.NamedTemporaryFile(delete=False)
    nfile = tmpfile.name

    # Condition
    c1 = Condition()
    c2 = Condition()

    assert (c1 == c2), \
        "Comparison of Condition failed. Expected to be equal:\n(c1, c2) = (%s, %s)" % (str(c1), str(c2))

    c1 = Condition('x', '>', '0.5')
    c2 = Condition('y', '<', '0.75')

    assert (c1 != c2), \
        "Comparison of Condition failed. Expected to be different:\n(c1, c2) = (%s, %s)" % (str(c1), str(c2))

    # ConditionList
    cl1 = ConditionList()
    cl2 = ConditionList()

    assert (cl1 == cl2), \
        "Comparison of ConditionList failed. Expected to be equal:\n(cl1, cl2) = (%s, %s)" % (str(cl1), str(cl2))

    cl1.add(c1)
    cl1.add(c2)

    cl2.add(c2)

    assert (cl1 != cl2), \
        "Comparison of ConditionList failed. Expected to be different:\n(cl1, cl2) = (%s, %s)" % (str(cl1), str(cl2))

    # Read/Write Condition from file
    c1.toFile(nfile, append=False, human_readable=human_readable)
    c2 = Condition()
    c2.fromFile(nfile, human_readable=human_readable)

    assert (c1 == c2), \
        "Comparison of Condition failed. Expected to be equal:\n(c1, c2) = (%s, %s)" % (str(c1), str(c2))

    # Read/Write ConditionList from file
    cl1.toFile(nfile, append=False, human_readable=human_readable)
    cl2 = ConditionList()
    cl2.fromFile(nfile, human_readable=human_readable)

    assert (cl1 == cl2), \
        "Comparison of ConditionList failed. Expected to be equal:\n(cl1, cl2) = (%s, %s)" % (str(cl1), str(cl2))

    # Oracle
    ora1 = OracleFunction()
    ora2 = OracleFunction()

    assert (ora1 == ora2), \
        "Comparison of OracleFunction failed. Expected to be equal:\n(ora1, ora2) = (%s, %s)" % (
        str(ora1), str(ora2))

    ora1.add(cl1, 1)
    ora1.add(cl2, 2)

    ora2.add(cl2, 2)

    assert (ora1 != ora2), \
        "Comparison of OracleFunction failed. Expected to be different:\n(ora1, ora2) = (%s, %s)" % (
        str(ora1), str(ora2))

    # Read/Write Oracle from file
    ora1.toFile(nfile, append=False, human_readable=human_readable)
    ora2 = OracleFunction()
    ora2.fromFile(nfile, human_readable=human_readable)

    assert (ora1 == ora2), \
        "Comparison of OracleFunction failed. Expected to be equal:\n(ora1, ora2) = (%s, %s)" % (str(ora1), str(ora2))

    # Remove tempfile
    os.unlink(nfile)


###############
# OraclePoint #
###############

# Test ND-Tree structure
def testNDTree(min_corner=0.0,
               max_corner=1.0):
    def f1(x):
        return 1 / x if x > 0.0 else 1000

    def f2(x):
        return 0.1 + 1 / x if x > 0.0 else 1001

    def f3(x):
        return 0.2 + 1 / x if x > 0.0 else 1002

    xs = np.arange(min_corner, max_corner, 0.1)
    y1s = [f1(x) for x in xs]
    y2s = [f2(x) for x in xs]
    y3s = [f3(x) for x in xs]

    ND1 = NDTree()
    ND2 = NDTree()

    assert (ND1 == ND2), \
        "Comparison of NDTree failed (1). Expected to be equal:\nND1 = %s\nND2 = %s" % (str(ND1), str(ND2))

    for x, y in zip(xs, y3s):
        point = (x, y)
        ND1.updatePoint(point)
        ND2.updatePoint(point)

    assert (ND1 == ND2), \
        "Comparison of NDTree failed (1). Expected to be equal:\nND1 = %s\nND2 = %s" % (str(ND1), str(ND2))

    # ND1 should remain constant when we insert the same point twice
    for x, y in zip(xs, y3s):
        point = (x, y)
        ND1.updatePoint(point)

    assert (ND1 == ND2), \
        "Comparison of NDTree failed (2). Expected to be equal:\nND1 = %s\nND2 = %s" % (str(ND1), str(ND2))

    # ND1 should change when we insert new dominanting points
    for x, y in zip(xs, y2s):
        point = (x, y)
        ND1.updatePoint(point)

    assert (ND1 != ND2), \
        "Comparison of NDTree failed (3). Expected to be different:\nND1 = %s\nND2 = %s" % (str(ND1), str(ND2))

    # ND1 should change when we insert new dominanting points
    for x, y in zip(xs, y1s):
        point = (x, y)
        ND1.updatePoint(point)

    assert (ND1 != ND2), \
        "Comparison of NDTree failed (4). Expected to be different:\nND1 = %s\nND2 = %s" % (str(ND1), str(ND2))

    oldND1 = copy.deepcopy(ND1)

    # ND1 should remain constant when we insert dominated points
    for x, y in zip(xs, y3s):
        point = (x, y)
        ND1.updatePoint(point)

    assert (ND1 == oldND1), \
         "Comparison of NDTree failed (5). Expected to be equal:\nND1 = %s\noldND1 = %s" % (str(ND1), str(oldND1))

    assert (ND1 != ND2), \
         "Comparison of NDTree failed (6). Expected to be equal:\nND1 = %s\nND2 = %s" % (str(ND1), str(ND2))


# Test OracleFunction
def testOraclePoint(min_corner=0.0,
                    max_corner=1.0,
                    human_readable=False):
    tmpfile = tf.NamedTemporaryFile(delete=False)
    nfile = tmpfile.name

    # Points
    def f1(x):
        return 1 / x if x > 0.0 else 1000

    def f2(x):
        return 0.1 + 1 / x if x > 0.0 else 1001

    def f3(x):
        return -0.1 + 1 / x if x > 0.0 else 999

    xs = np.arange(min_corner, max_corner, 0.1)
    y1s = [f1(x) for x in xs]
    y2s = [f2(x) for x in xs]
    y3s = [f3(x) for x in xs]

    p1 = [(x, y) for x, y in zip(xs, y1s)]
    p2 = [(x, y) for x, y in zip(xs, y2s)]
    p3 = [(x, y) for x, y in zip(xs, y3s)]

    # Oracle
    ora1 = OraclePoint()
    for x, y in zip(xs, y1s):
        point = (x, y)
        ora1.addPoint(point)

    ora2 = OraclePoint()
    ora2.addPoints(set(p1))

    assert (ora1 == ora2), \
        "Comparison of OraclePoint failed. Expected to be equal:\n(ora1, ora2) = (%s, %s)" % (str(ora1), str(ora2))

    fora1 = ora1.membership()
    testIn = [fora1(p) for p in p1]

    assert (all(testIn)), \
        "OraclePoint mambership failed. All points in (%s) are expected to be in the upper closure.\n Got (%s)" % (
        str(p1), str(testIn))

    testIn = [fora1(p) for p in p2]

    assert (all(testIn)), \
        "OraclePoint mambership failed. All points in (%s) are expected to be in the upper closure.\n Got (%s)" % (
        str(p2), str(testIn))

    testOut = [not fora1(p) for p in p3]

    assert (all(testOut)), \
        "OraclePoint mambership failed. All points in (%s) are expected to be in the lower closure.\n Got (%s)" % (
        str(p3), str(testOut))

    ora1.toFile(nfile, append=False, human_readable=human_readable)
    ora2 = OraclePoint()
    ora2.fromFile(nfile, human_readable=human_readable)

    assert (ora1 == ora2), \
        "Comparison of OraclePoint failed. Expected to be equal:\n(ora1, ora2) = (%s, %s)" % (str(ora1), str(ora2))

    # Remove tempfile
    os.unlink(nfile)

# TOREMOVE
#def testInOutFileOraclePoint(infile=os.path.abspath("tests/OraclePoint/oracle2.txt"),
#                             outfile=os.path.abspath("tests/OraclePoint/oracle2_bin.txt")):
def testInOutFileOraclePoint(infile, outfile):
    def readTupleFile(nfile):
        mode = 'rb'
        finput = open(nfile, mode)

        setpoints = set()
        for i, line in enumerate(finput):
            line = line.replace('(', '')
            line = line.replace(')', '')
            line = line.split(',')
            point = tuple(float(pi) for pi in line)
            setpoints.add(point)
        return setpoints

    # ora2 = OraclePoint()
    ora2 = OraclePoint(5, 4)
    ora2.fromFile(infile, human_readable=True)
    ora2.toFile(outfile, human_readable=False)
    points = ora2.getPoints()

    # print('ora2 ' + str(ora2))
    print('ora2 rect' + str(ora2.oracle.root.rect))
    print('numPoints: ' + str(len(points)))

    x = [point[0] for point in points]
    y = [point[1] for point in points]

    rs = ResultSet()
    rs.toMatPlot2D(targetx=x, targety=y, blocking=True)

    originalPoints = readTupleFile(infile)

    x = [point[0] for point in originalPoints]
    y = [point[1] for point in originalPoints]

    rs.toMatPlot2D(targetx=x, targety=y, blocking=True)


if __name__ == '__main__':
    testMembershipCondition()
    testOracleFunction(False)
    testOracleFunction(True)

    testNDTree()
    testOraclePoint(False)
    testOraclePoint(True)
