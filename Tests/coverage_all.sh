#!/usr/bin/env bash
export MATLAB_INSTALLED=$(python -c 'import matlab')
coverage run -m --parallel-mode pytest test_Oracle_OraclePoint.py
coverage run -m --parallel-mode pytest test_Oracle_OracleFunction.py
coverage run -m --parallel-mode pytest test_Oracle_OracleSTL.py
coverage run -m --parallel-mode pytest test_Oracle_OracleSTLe.py
if [ !  $MATLAB_INSTALLED ]
then
  coverage run -m --parallel-mode pytest test_Oracle_OracleMatlab.py
fi
coverage run -m --parallel-mode pytest test_Geometry_Point.py
coverage run -m --parallel-mode pytest test_Geometry_Rectangle.py
coverage run -m --parallel-mode pytest test_Geometry_Segment.py
coverage run -m --parallel-mode pytest test_Search_ResultSet.py
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleFunctionTestCase::test_2D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleFunctionTestCase::test_3D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleFunctionTestCase::test_ND
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOraclePointTestCase::test_2D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOraclePointTestCase::test_3D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLeTestCase::test_1D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLeTestCase::test_2D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLeLibTestCase::test_1D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLeLibTestCase::test_2D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLTestCase::test_1D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLTestCase::test_2D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py
if [ !  $MATLAB_INSTALLED ]
then
  coverage2 run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleMatlabTestCase::test_2D
  coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleMatlabTestCase::test_3D
  coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleMatlabTestCase::test_ND
fi
coverage combine
coverage report --omit=*ParetoLib/_py3k*
coverage html -d coverage/report-python
coverage erase