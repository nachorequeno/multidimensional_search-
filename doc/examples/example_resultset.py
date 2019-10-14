from ParetoLib.Oracle.OracleFunction import OracleFunction
from ParetoLib.Search.ResultSet import ResultSet

# File containing the definition of the Oracle
nfile = '../../Tests/Oracle/OracleFunction/2D/test1.txt'
human_readable = True

oracle = OracleFunction()
oracle.from_file(nfile, human_readable)

rs = ResultSet()
rs.from_file("result.zip")
rs.plot_2D_light(var_names=oracle.get_var_names())
