# NumPy and odeint, our workhorses
import numba
import numpy as np
import scipy.stats as st

# Plotting modules 
import seaborn as sns
import matplotlib.pyplot as plt

import time
import copy
import multiprocessing

import ParetoLib.Bio as LogBio

# This is to enable inline displays for the purposes of the tutorial 
# %matplotlib inline
# %config InlineBackend.figure_formats = {'png', 'retina'}

# JB's favorite Seaborn settings for notebooks 
rc = {'lines.linewidth': 2,
      'axes.labelsize': 18,
      'axes.titlesize': 18,
      'axes.facecolor': 'DFDFE5'}
sns.set_context('notebook', rc=rc)
sns.set_style('darkgrid', rc=rc)

# Column 0 is change in U, column 1 is change in A and column 2 is change in I 
# 1. U to A 
# 2. U to I 
# 3. A to U 
# 4. I to U 
simple_update = np.array([[-1, 1, 0],
                          [-1, 0, 1],
                          [1, -1, 0],
                          [1, 0, -1]], dtype=np.int)

# Multiprocessing pool
p = None


@numba.jit(nopython=True)
def sum_numba(ar):
    return ar.sum()


@numba.jit(nopython=True)
def simple_propensity(params, population):
    """
    Returns an array of propensities given a set of parameters
    and an array of populations.
    """
    # Unpack parameters
    k, e, gamma = params

    # Unpack population state
    St = population
    # St = population.copy()
    N = len(St)

    Ac = np.zeros((N,), dtype=np.float64)
    Ic = np.zeros((N,), dtype=np.float64)

    Pr = np.empty((4, N), dtype=np.float64)

    for i in range(0, N):
        for j in range(0, N):
            if j != i:
                Ac[i] = Ac[i] + pow(abs(j - i), - gamma) * (St[j] == 1)
                Ic[i] = Ic[i] + pow(abs(j - i), - gamma) * (St[j] == -1)

        Pr[0, i] = (St[i] == 0) * (k + e * Ac[i] / float(N))
        Pr[1, i] = (St[i] == 0) * (k + e * Ic[i] / float(N))
        Pr[2, i] = (St[i] == 1) * (k + e * Ic[i] / float(N))
        Pr[3, i] = (St[i] == -1) * (k + e * Ac[i] / float(N))
    return Pr


@numba.jit(nopython=True)
def sample_discrete(probs, probs_sum):
    q = np.random.rand() * probs_sum
    p_sum = 0.0
    rxn = 0
    nuc = 0
    for nuc in range(0, probs.shape[1]):
        for rxn in range(0, probs.shape[0]):
            p_sum += probs[rxn, nuc]
            if p_sum > q:
                break
        if p_sum > q:
            break
    return rxn, nuc


@numba.jit(nopython=True)
def gillespie_draw(params, population):
    """
    Draws a reaction and the time it took to do that reaction.
    """
    # Compute propensities
    props = simple_propensity(params, population)

    # Sum of propensities
    props_sum = sum_numba(props)

    # Compute time
    temp = np.random.exponential(1.0 / float(props_sum))

    # Draw reaction given propensities
    rxn, nuc = sample_discrete(props, props_sum)

    return rxn, nuc, temp


@numba.jit(nopython=True)
def gillespie_ssa(params, population_size, ntime_points, start_time_points, end_time_points):
    """
    Uses the Gillespie stochastic simulation algorithm to sample
    from proability distribution of particle counts over time.
    Parameters
    ----------
    params : arbitrary
    The set of parameters to be passed to propensity_func.
    population_size : integer
    Number of nucleosomes.
    time_points : array_like, shape (num_time_points,)
    Array of points in time for which to sample the probability
    distribution.
    Returns
    -------
    sample : ndarray, shape (num_time_points, num_chemical_species)
    Entry i, j is the count of chemical species j at time
    time_points[i].
    """

    # Initialize output
    pop_out = np.empty((ntime_points, population_size), dtype=np.int8)

    # Initialize and perform simulation
    i_time = 1
    i = 0

    time_points = np.linspace(start_time_points, end_time_points, ntime_points)
    t = time_points[0]
    population = np.full((population_size,), -1)
    pop_out[0, :] = np.full((population_size,), -1)
    while i < ntime_points:
        while t < time_points[i_time]:
            # draw the event and time step
            rxn, nuc, dt = gillespie_draw(params, population)

            # Increment time
            t += dt

            # Update the population
            # population_previous = population.copy()
            # copy only once, just before exiting the inner loop
            if t < time_points[i_time]:
                population[nuc] = (rxn == 0) * (1) + (rxn == 1) * (-1) + (rxn == 2) * (0) + (rxn == 3) * (0)

        # Update the index (Have to be careful about types for Numba)
        i = np.searchsorted((time_points > t).astype(np.int64), 1)

        # Update the population
        new_pop = population.copy()
        for j in np.arange(i_time, min(i, ntime_points)):
            # pop_out[j, :] = population_previous
            # pop_out[j, :] = population.copy()
            pop_out[j, :] = new_pop

        # Increment index
        i_time = i

    return pop_out


def gillespie_fn(args):
    return gillespie_ssa(*args)


def gillespie_parallel(fn, params, population_size, ntime_points,
                       start_time_points, end_time_points, n_simulations, nthreads):
    """
    Convenience function to do parallel Gillespie simulations for simple
    gene expression.
    """
    input_args = (params, population_size, ntime_points, start_time_points, end_time_points)

    global p
    n_threads = min(nthreads, multiprocessing.cpu_count())
    if p is None:
        p = multiprocessing.Pool(n_threads)

    # Explicit copy of population_0 when creating arguments
    # in order to remove concurrent problems (race conditions)
    # when accessing the elements of the np.full array.
    input_args_list = []
    for i in range(n_simulations):
       temp = copy.deepcopy(input_args)
       input_args_list.append(temp)
    # populations = p.map(fn, input_args_list)
    # return np.array(populations)
    populations = p.imap_unordered(fn, input_args_list)
    # populations = p.imap_unordered(fn, [input_args] * n_simulations)
    ## p.close()
    return np.array(list(populations))


def sim(k=1.0, e=5.0, gamma=0.0, N_MF10=10, n_simulations_MF10=1000, nthreads=float('inf')):
    pops_MF10 = simulation(k=k, e=e, gamma=gamma, N_MF10=N_MF10, n_simulations_MF10=n_simulations_MF10, nthreads=nthreads)
    m1, m2 = compile_results(pops_MF10)
    return m1, m2


@numba.jit(nopython=False)
def simulation(k=1.0, e=5.0, gamma=0.0, N_MF10=10, n_simulations_MF10=1000, nthreads=float('inf')):
    assert N_MF10 != 0

    # N_MF10 = Number of nucleosomes (population)
    # n_simulations_MF10

    start = time.time()
    params_MF10 = np.array([k, e, gamma])  # k,e, gamma, N
    ntime_points_MF10 = 40001
    start_time_points_MF10 = 0
    end_time_points_MF10 = 40000

    # Initialize output array
    pops_MF10 = gillespie_parallel(gillespie_fn, params_MF10, N_MF10, ntime_points_MF10, start_time_points_MF10, end_time_points_MF10, n_simulations_MF10, nthreads)

    end = time.time()
    time0 = end - start
    LogBio.logger.debug('Simulation time: {0}'.format(time0))

    return pops_MF10


@numba.jit(nopython=False, parallel=True)
def compile_results(pops_MF10):
    # pops_MF10 = np.empty((n_simulations_MF10, ntime_points_MF10, N_MF10), dtype=np.int8)
    n_simulations_MF10 = pops_MF10.shape[0]
    ntime_points_MF10 = pops_MF10.shape[1]
    N_MF10 = pops_MF10.shape[2]

    start = time.time()
    U_MF10 = np.empty([n_simulations_MF10, ntime_points_MF10], dtype=np.int64)
    A_MF10 = np.empty([n_simulations_MF10, ntime_points_MF10], dtype=np.int64)
    I_MF10 = np.empty([n_simulations_MF10, ntime_points_MF10], dtype=np.int64)

    for n in numba.prange(0, n_simulations_MF10):
        for t in numba.prange(0, ntime_points_MF10):
            U_MF10[n, t] = (pops_MF10[n, t, :] == 0).sum()
            A_MF10[n, t] = (pops_MF10[n, t, :] == 1).sum()
            I_MF10[n, t] = (pops_MF10[n, t, :] == -1).sum()

    Mag_MF10 = A_MF10 - I_MF10
    Mag_MF10 = Mag_MF10 / float(N_MF10)

    start_time_points_MF10 = 0
    end_time_points_MF10 = ntime_points_MF10 - 1

    time_points_MF10 = np.linspace(start_time_points_MF10, end_time_points_MF10, ntime_points_MF10)
    MFPT10 = np.empty(n_simulations_MF10)
    tc = 0
    for n in range(len(MFPT10)):
        while Mag_MF10[n, tc] < 0:
            tc = tc + 1
        MFPT10[n] = time_points_MF10[tc]

    end = time.time()
    time0 = end - start
    LogBio.logger.debug('Time for compiling results: {0}'.format(time0))

    return Mag_MF10, MFPT10


def last_column(Mag_MF10):
    last_column_index = len(Mag_MF10[0]) - 1
    last_col = Mag_MF10[:, last_column_index]
    return last_col


def sample_size(Mag_MF10):
    return len(Mag_MF10)


def plot_histogram(Mag_MF10):
    sns.distplot(last_column(Mag_MF10), hist=True, kde=False,
                 bins=10000, color='red',
                 hist_kws={'edgecolor': 'black'},
                 kde_kws={'linewidth': 2})
    plt.show()


def plot_distribution(Mag_MF10):
    sns.distplot(last_column(Mag_MF10), hist=False, kde=True,
                 bins=10000, color='red',
                 hist_kws={'edgecolor': 'black'},
                 kde_kws={'linewidth': 2})
    plt.show()


def distribution_function(Mag_MF10):
    # KDE (Kernel density function), i.e., function K(x) that generates
    # the y-coordinates of plot_image() for each value x from Mag_MF10
    return st.gaussian_kde(last_column(Mag_MF10))


def histogram(Mag_MF10):
    # y-values
    # h[0] = array([1961781, ...,  173514]),
    # x-axe
    # h[1] = array([-1. , -0.8, -0.6, -0.4, -0.2,  0. ,  0.2,  0.4,  0.6,  0.8,  1. ])
    #
    # Histogram of the last timestamp
    h = np.histogram(last_column(Mag_MF10))
    return h


def bimodality_coeff(Mag_MF10):
    lc = last_column(Mag_MF10)
    sk = st.skew(lc)
    kur = st.kurtosis(lc)
    n = sample_size(lc)
    #
    bc = sk**2.0 + 1.0
    den = 3.0*((n-1)**2.0)/((n-2) * (n-3))
    bc = bc / (kur + den)
    return bc


def normal_test(Mag_MF10):
    norm_test = st.mstats.normaltest(last_column(Mag_MF10))
    # By convention, the data passes the statistical test (i.e., data is 'normal')
    # if pvalue is less or equal to 0.05, 0.01, 0.005, or 0.001
    return norm_test.pvalue < 0.05


def bistable_test(Mag_MF10, offset=0.0):
    # return not normal_test(Mag_MF10)
    # return 9.0 * bimodality_coeff(Mag_MF10) > 5.0
    bc = bimodality_coeff(Mag_MF10)
    test = 9.0 * (bimodality_coeff(Mag_MF10) - offset) > 5.0
    LogBio.logger.info('Bimodality coeff: {0}, {1}'.format(bc, test))
    return test
