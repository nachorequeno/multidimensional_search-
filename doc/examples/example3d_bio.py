from ParetoLib.Oracle.OracleBio import OracleBio3D
from ParetoLib.Search.Search import Search3D, EPS, DELTA, STEPS

# Definition of the n-dimensional space
# ['k', 'e', 'gamma']
min_x, min_y, min_z = (1.0, 1.0, 0.0)
max_x, max_y, max_z = (2.0, 5.0, 2.0)

# alpha = relative recruitement strength
# alpha = e/k
oracle = OracleBio3D(max_k=max_x, max_e=max_y, max_gamma=max_z, N_MF10=10, n_simulations_MF10=100, nthreads=2)
rs = Search3D(ora=oracle,
              min_cornerx=min_x,
              min_cornery=min_y,
              min_cornerz=min_z,
              max_cornerx=max_x,
              max_cornery=max_y,
              max_cornerz=max_z,
              epsilon=EPS,
              delta=DELTA,
              max_step=STEPS,
              blocking=False,
              sleep=0,
              opt_level=0,
              parallel=False,
              logging=False,
              simplify=False)
rs.to_file("result.zip")