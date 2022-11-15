import random
from enum import IntEnum

import numpy as np

import flow_shop as fs
from neighbor_moves import *


class SlopeType(IntEnum):
    GEOMETRIC = (0,)
    LOGARITHMIC = (1,)
    LINEAR = (2,)


EPS = np.finfo(float).eps
EPS2 = np.finfo(np.float32).eps


def assign_temp_init(dt: float, p: float):
    """Function appoint initial temperature for simulated annealing
    Args:
        dt (float): Standard length between solutions
        p (float): Probability for first iteration (should be close to 1)
    """
    return -dt / np.log10(p)


def probably(chance):
    return random.random() < chance


def roll_two_different_index(n_jobs):
    idx1 = random.randint(0, n_jobs - 1)
    idx2 = random.randint(0, n_jobs - 1)
    while idx1 == idx2:
        idx2 = random.randint(0, n_jobs - 1)
    return [idx1, idx2]


def geometric_slope(t0, tk, n):
    lmb = (EPS / t0) ** (1 / n)
    return lmb * tk


def logarithmic_slope(t0, tk, n):
    lmb = (t0 - EPS) / (n * t0 * EPS)
    return tk / (1 + lmb * tk)


def linear_slope(t0, tk, n):
    return t0 / n


FALL_FUNCTIONS = {0: geometric_slope, 1: logarithmic_slope, 2: linear_slope}


def simulated_annealing(
    data: np.ndarray,
    move_type: NeighborMoves,
    slope_type: SlopeType,
    temp_init: int = 1000,
    max_iter: int = 1000,
    return_hist=False,
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

    for k in range(max_iter):
        indexes = roll_two_different_index(n_jobs)
        if move_type in [NeighborMoves.SWAP, NeighborMoves.REVERSE_SUBSEQUENCE]:
            indexes.sort()

        x_prime = move(x_curr, indexes[0], indexes[1])
        t_prime = fs.calculate_completion_time(
            x_prime, x_prime.shape[1], x_prime.shape[0]
        )

        probability = np.min([1, np.exp(-((t_prime - t_curr) + EPS) / (temp_k + EPS))])
        if probably(probability):
            x_curr = x_prime.copy()
            t_curr = t_prime

        if t_prime < t_best:
            t_best = t_prime
            x_best = x_prime.copy()

        temp_k = slope_function(temp_init, temp_k, max_iter)

        if return_hist:
            t_hist[k, 0] = t_best
            t_hist[k, 1] = t_curr
            t_hist[k, 2] = temp_k

    if not return_hist:
        return (t_best, x_best)

    return (t_best, x_best, t_hist)
