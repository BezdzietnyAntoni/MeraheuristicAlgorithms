import random
from enum import IntEnum

import numpy as np

import flow_shop as fs

from .neighbor_moves import *


class SlopeType(IntEnum):
    GEOMETRIC = (0,)
    LOGARITHMIC = (1,)
    LINEAR = (2,)


EPS = np.finfo(float).eps
EPS2 = np.finfo(np.float32).eps


def roll_two_different_index(n_jobs):
    idx1 = random.randint(0, n_jobs - 1)
    idx2 = random.randint(0, n_jobs - 1)
    while idx1 == idx2:
        idx2 = random.randint(0, n_jobs - 1)
    return [idx1, idx2]


def geometric_slope(t0, tk, n, k):
    lmb = (EPS / t0) ** (1 / n)
    return lmb * tk


def logarithmic_slope(t0, tk, n, k):
    lmb = t0 / (n * t0 + EPS)
    return tk / (1 + lmb * tk)


def linear_slope(t0, tk, n, k):
    return t0 / k


FALL_FUNCTIONS = {0: geometric_slope, 1: logarithmic_slope, 2: linear_slope}


def threshold_algorithm(
    data: np.ndarray,
    move_type: NeighborMoves,
    slope_type: SlopeType,
    temp_init: int = 1000,
    max_iter: int = 1000,
    return_hist=False,
    pulse_temp=False,
):
    n_jobs = data.shape[1]
    temp_k = temp_init

    slope_function = FALL_FUNCTIONS[slope_type]
    move = TRANSFORMS[move_type.value]

    # Best solution
    x_best = data.copy()
    t_best = fs.calculate_completion_time(x_best, data.shape[1], data.shape[0])

    # Current solution
    x_curr = x_best.copy()
    t_curr = fs.calculate_completion_time(x_curr, data.shape[1], data.shape[0])

    # Save history
    if return_hist:
        t_hist = np.zeros((max_iter, 3))

    # For pulse slope function
    pulse_value = 0.5 * temp_init
    t_best_prime = t_best
    max_val_no_change = np.min([int(max_iter * 0.10), 100])
    counter_no_change = 0 

    for k in range(max_iter):
        indexes = roll_two_different_index(n_jobs)
        if move_type in [NeighborMoves.SWAP, NeighborMoves.REVERSE_SUBSEQUENCE]:
            indexes.sort()

        x_prime = move(x_curr, indexes[0], indexes[1])
        t_prime = fs.calculate_completion_time(
            x_prime, x_prime.shape[1], x_prime.shape[0]
        )

        if (t_prime - t_curr) < temp_k:
            x_curr = x_prime.copy()
            t_curr = t_prime

        if t_prime < t_best:
            t_best = t_prime
            x_best = x_prime.copy()

        if pulse_temp:
            # Add pulse do temp function
            if t_best_prime == t_best:
                counter_no_change += 1
                if counter_no_change >= max_val_no_change:
                    temp_k += pulse_value
                    counter_no_change = 0
                    max_val_no_change *= 2
            else:
                t_best_prime = t_best
                counter_no_change = 0

        temp_k = slope_function(temp_init, temp_k, max_iter, k)

        if return_hist:
            t_hist[k, 0] = t_best
            t_hist[k, 1] = t_prime
            t_hist[k, 2] = temp_k

    if not return_hist:
        return (t_best, x_best)

    return (t_best, x_best, t_hist)
