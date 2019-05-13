from ParetoLib.Oracle.OracleBio import OracleBio2D
from ParetoLib.Search.Search import Search2D, EPS, DELTA, STEPS

# Definition of the n-dimensional space
# ['alpha', 'gamma']
min_x, min_y = (1.0, 0.0)
max_x, max_y = (2.0, 2.0)

# alpha = relative recruitement strength
# alpha = e/k
oracle = OracleBio2D(max_alpha=max_x, max_gamma=max_y, N_MF10=10, n_simulations_MF10=100, nthreads=2)
rs = Search2D(ora=oracle,
              min_cornerx=min_x,
              min_cornery=min_y,
              max_cornerx=max_x,
              max_cornery=max_y,
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
