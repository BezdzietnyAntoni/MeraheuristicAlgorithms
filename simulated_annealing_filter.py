import random
from enum import IntEnum

import numpy as np
from scipy import signal

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


def geometric_slope(t0, tk, n):
    lmb = (EPS / t0) ** (1 / n)
    return lmb * tk


def logarithmic_slope(t0, tk, n):
    lmb = (t0 - EPS) / (n * t0 * EPS)
    return tk / (1 + lmb * tk)


def linear_slope(t0, tk, n):
    return t0 / n


FALL_FUNCTIONS = {0: geometric_slope, 1: logarithmic_slope, 2: linear_slope}


def cost_function_filter(f_response, f_pass_norm, a_stop, a_pass_rip):
    a_pass_rip = 10 ** (a_pass_rip / 20)
    a_stop = 10 ** (a_stop / 20)
    lim_pass_stop = np.ceil(f_pass_norm * f_response.shape[0] / np.pi).astype(int)

    f_response_abs = np.abs(f_response)
    cost = 0
    # Cost function in pass band
    temp_cost = f_response_abs[:lim_pass_stop] ** 2 - a_pass_rip**2
    cost += np.sum(temp_cost > 0 * temp_cost)
    # Cost function in stop band
    temp_cost = f_response_abs[lim_pass_stop:] ** 2 - a_stop**2
    cost += np.sum((f_response_abs[lim_pass_stop:] - a_stop) > 0 * temp_cost)
    return cost


def simulated_annealing_filter(
    coeff: np.ndarray,
    slope_type: SlopeType,
    temp_init: int = 1000,
    f_pass_norm: float = 0.5,
    a_stop_db: float = -80,
    a_pass_rip: float = 1,
    N_fft: int = 512,
    max_iter: int = 1000,
    return_hist=False,
):
    n_coeff = coeff.shape[0]
    temp_k = temp_init
    sigma = 0.00001

    slope_function = FALL_FUNCTIONS[slope_type]

    # Frequency response
    w, h = signal.freqz(coeff, worN=N_fft)

    # Best solution
    x_best = coeff.copy()
    t_best = cost_function_filter(h, f_pass_norm, a_stop_db, a_pass_rip)

    # Current solution
    x_curr = coeff.copy()
    t_curr = cost_function_filter(h, f_pass_norm, a_stop_db, a_pass_rip)

    # Save history
    if return_hist:
        t_hist = np.zeros((max_iter, 3))

    for k in range(max_iter):
        rand_coeff = np.random.randint(0, n_coeff)

        x_prime = x_curr.copy()
        x_prime[rand_coeff] = x_prime[rand_coeff] + sigma * np.random.randn(1)
        w, h = signal.freqz(x_prime, worN=N_fft)
        t_prime = cost_function_filter(h, f_pass_norm, a_stop_db, a_pass_rip)

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
