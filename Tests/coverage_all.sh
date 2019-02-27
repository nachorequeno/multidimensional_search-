#!/usr/bin/env bash
python -m coverage run --parallel-mode test_Oracle_OraclePoint.py
python -m coverage run --parallel-mode test_Oracle_OracleFunction.py
python -m coverage run --parallel-mode test_Oracle_OracleSTL.py
python -m coverage run --parallel-mode test_Geometry_Point.py
python -m coverage run --parallel-mode test_Geometry_Rectangle.py
python -m coverage run --parallel-mode test_Search_ResultSet.py
#python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOracleFunctionTestCase
python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOracleFunctionTestCase.test_2D
python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOracleFunctionTestCase.test_3D
# python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOracleFunctionTestCase.test_ND
# python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOraclePointTestCase
python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOraclePointTestCase.test_2D
python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOraclePointTestCase.test_3D
# python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOraclePointTestCase.test_ND
# python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOracleSTLTestCase
# python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOracleSTLTestCase.test_1D
# python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py SearchOracleSTLTestCase.test_2D
# python -m coverage run --parallel-mode --concurrency=multiprocessing test_Search.py
##python -m coverage combine
##python -m coverage report
##python -m coverage erase