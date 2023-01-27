import numpy as np
from scipy import signal
from . import rvns_filter
from . import filter_utils



def generate_init_solutions_window(filter_: dict, k_init : int = 14):
    filter_n = filter_utils.normalize_filter (filter_)

    WINDOWS = ['boxcar', 'triang', 'blackman', 'hamming', 'hann', 'bartlett', 'flattop', 
               'parzen', 'bohman', 'blackmanharris', 'nuttall', 'barthann', 'cosine', 'tukey']
    M_order = filter_n['m_order']
    solutions = np.zeros((k_init, M_order))
    cost_value = np.zeros((k_init))

    
    # Generate first solution
    for i, w in enumerate(WINDOWS[:k_init]):
        coef = signal.firwin(filter_['m_order'], filter_['f_pass'], fs=filter_['fs'], window=w)
        solutions[i] = coef
        f, f_res = signal.freqz(coef, worN=filter_['N_fft'])
        cost_value[i] = filter_utils.cost_LP_filter(abs(f_res), filter_utils.db_to_linear(filter_n['d1_db'])-1, 
                        filter_utils.db_to_linear(filter_n['d2_db']), filter_n['f_pass'], filter_n['tr_band'])

    return [solutions, cost_value]


def hybrid_gen_rvns(
filter_: dict, 
N_iter: int = 500, 
K_parents: int = 14, 
prob: float = 0.8, 
init_sol: list = None,
rvnsc_param: dict = None):

    filter_n = filter_utils.normalize_filter (filter_)

    M_order = filter_n['m_order']
    L_individuals = K_parents + K_parents // 2
    solutions = np.zeros((L_individuals, M_order))
    cost_value = np.zeros((L_individuals))

    # Parametry zagnieżdżonego algorytmu RVNS
    if rvnsc_param == None:
        rvnsc_param = {
            'k_prime': 50,    # Ilość iteracji I stopnia
            'k_bis':   20,     # Ilość iteracji II stopnia
        }

    # Generate init solution
    solutions_init, cost_value_init = generate_init_solutions_window(filter_, K_parents)
    solutions[:K_parents] = solutions_init
    cost_value[:K_parents] = cost_value_init

    for n_i in range(N_iter):
        # Wylosuj permutacje z 12 najlepszych
        permutation = np.random.permutation(np.arange(K_parents)).reshape((K_parents//2, 2))

        # Mieszanie genów losowo    
        gen_rand = np.random.choice([True, False], (M_order), p=[prob, 1-prob])
        for i in range(K_parents//2):
            solutions[K_parents + i] = gen_rand * solutions[permutation[i, 0]] + np.logical_not(gen_rand) * solutions[permutation[i, 1]]
            # Poprawa filtru algorytmem RVNS
            cost, solutions[K_parents + i] = rvns_filter.rvns_con(solutions[K_parents + i], filter_n, rvnsc_param['k_prime'], rvnsc_param['k_bis'])
            cost_value[K_parents + i] = cost

        # Metoda wyboru rodzica - najlepsi rodzice 
        parents_arg = np.argsort(cost_value)[:K_parents]

        # Modyfikacja rodzica 
        solutions[:K_parents] = solutions[parents_arg]
        cost_value[:K_parents] = cost_value[parents_arg]

    return cost_value[0], solutions[0]