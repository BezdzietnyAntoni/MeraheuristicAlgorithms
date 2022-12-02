import random

import numpy as np

import flow_shop as fs

from .neighbor_moves import *


def roll_two_different_index(n_jobs):
    idx1 = random.randint(0, n_jobs - 1)
    idx2 = random.randint(0, n_jobs - 1)
    while idx1 == idx2:
        idx2 = random.randint(0, n_jobs - 1)
    return [idx1, idx2]


def roll_move():
    t_number = np.random.randint(0, 4)
    return TRANSFORMS[t_number]


def reduced_variable_neighborhood_search(
    data: np.ndarray,
    k_max: int = 100,
    k_sub_max: int = 30,
    return_hist=False,
):

    # Current solution
    t_curr = fs.calculate_completion_time(data, data.shape[1], data.shape[0])
    x_curr = data.copy()

    # Best solution
    t_best = t_curr
    x_best = data.copy()

    for i in range(k_max):
        indexes = roll_two_different_index(data.shape[1])
        move = roll_move()
        if move in [TRANSFORMS[0], TRANSFORMS[1]]:
            indexes.sort()

        x_prime = move(x_curr, indexes[0], indexes[1])
        t_prime = fs.calculate_completion_time(x_prime, data.shape[1], data.shape[0])

        # For subspace
        t_bis_min = 1e6
        for j in range(k_sub_max):
            indexes = roll_two_different_index(data.shape[1])
            move = roll_move()
            if move in [TRANSFORMS[0], TRANSFORMS[1]]:
                indexes.sort()

            x_bis = move(x_prime, indexes[0], indexes[1])
            t_bis = fs.calculate_completion_time(x_bis, data.shape[1], data.shape[0])

            if t_bis < t_bis_min:
                t_bis_min = t_bis
                x_bis_min = x_bis.copy()

        if t_bis_min < t_best:
            t_best = t_bis_min
            x_best = x_bis_min.copy()

        if t_bis_min < t_curr:
            t_curr = t_bis_min
            x_curr = x_bis_min.copy()

    return t_best, x_best
