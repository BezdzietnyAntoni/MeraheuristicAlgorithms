import random
from enum import IntEnum

import numpy as np

import flow_shop as fs
from neighbor_moves import *

def roll_two_different_index(n_jobs):
    idx1 = random.randint(0, n_jobs - 1)
    idx2 = random.randint(0, n_jobs - 1)
    while idx1 == idx2:
        idx2 = random.randint(0, n_jobs - 1)
    return [idx1, idx2]


def generate_n_different_value(n_values: int, min_value: int, max_value: int):
    if (max_value - min_value + 1) < n_values:
        raise ValueError("Incorrect range value")

    values = list()
    while len(values) < n_values:
        value = random.randint(min_value, max_value)
        if value not in values:
            values.append(value)
    
    return values

def generate_neighbor_options(n_jobs):    
    action = random.choice(list(TRANSFORMS.keys())) # Roll action on set
    indexes = roll_two_different_index # Roll 2 indexes
    if action in [NeighborMoves.SWAP, NeighborMoves.REVERSE_SUBSEQUENCE]: #If action is fs.swap or fs.reverse_subsequence then sort indexes
        indexes.sort()

    return {'action': action, 'indexes': indexes}

def variable_neighborhood(
    data: np.ndarray,
    move_type_prime: NeighborMoves,
    neighbor_size: int = 20,
    max_iter: int = 100,
    return_hist=False,
):

    move_prime = TRANSFORMS[move_type_prime.value]

    #Basic solve
    x_curr = data.copy()
    t_curr = fs.calculate_completion_time(x_curr, x_curr.shape[1], x_curr.shape[0])

    #Best solve
    x_best = x_curr.copy()
    t_best = t_curr

    for i in range(max_iter):
        indexes = roll_two_different_index(n_jobs)
    if move_type_prime in [NeighborMoves.SWAP, NeighborMoves.REVERSE_SUBSEQUENCE]:
        indexes.sort()

    x_prime = move_prime(x_curr, indexes[0], indexes[1])
    t_prime = fs.calculate_completion_time(x_prime, x_prime.shape[1], x_prime.shape[0])

    neighbor_actions = [generate_neighbor_options(n_jobs) for _ in range(neighbor_size)]
    neighbor_time = [1e6 for _ in range(neighbor_size)]
    for i, action in enumerate(neighbor_actions):
        xp = TRANSFORMS[action['action']](x_curr, action['indexes'][0],action['indexes'][1])
        neighbor_time[i] = fs.calculate_completion_time(xp, xp.shape[1], xp.shape[0]) 
    best_neighbor_idx = neighbor_time.index(min(neighbor_time))

    x_bis = TRANSFORMS[action['action']](x_curr, action['indexes'][0],action['indexes'][1])
    t_bis = fs.calculate_completion_time(x_bis, x_bis.shape[1], x_bis.shape[0])

    if t_bis < t_best:
        t_best = t_bis
        x_best = t_bis.copy()

    if t_bis < t_curr:
        t_curr = t_bis
        x_curr = x_bis.copy()