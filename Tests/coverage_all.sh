#!/usr/bin/env bash
coverage run -m --parallel-mode pytest test_Oracle_OraclePoint.py
coverage run -m --parallel-mode pytest test_Oracle_OracleFunction.py
coverage run -m --parallel-mode pytest test_Oracle_OracleSTL.py
coverage run -m --parallel-mode pytest test_Oracle_OracleSTLe.py
coverage run -m --parallel-mode pytest test_Geometry_Point.py
coverage run -m --parallel-mode pytest test_Geometry_Rectangle.py
coverage run -m --parallel-mode pytest test_Search_ResultSet.py
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleFunctionTestCase::test_2D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleFunctionTestCase::test_3D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOraclePointTestCase::test_2D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOraclePointTestCase::test_3D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLeTestCase::test_1D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLeTestCase::test_2D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLeLibTestCase::test_1D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLeLibTestCase::test_2D
coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLTestCase::test_1D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py::SearchOracleSTLTestCase::test_2D
#coverage run -m --parallel-mode --concurrency=multiprocessing pytest test_Search.py
coverage combine
coverage report
#coverage html -d coverage/report-python
coverage erase