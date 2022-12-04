import random

import numpy as np
from scipy import signal

from .filter_utils import *


def slope_parameters(start_res, final_res, iter):
    return (final_res / start_res) ** (1 / iter)


def rvns_con(
    coef: np.ndarray,
    filter_n: dict,
    k_max: int = 1000,
    k_sub_max: int = 300,
    return_hist=False,
):

    # Current solution
    _, f_res = signal.freqz(coef, worN=filter_n["N_fft"])
    cost_curr = cost_LP_filter(
        abs(f_res),
        db_to_linear(filter_n["d1_db"]) - 1,
        db_to_linear(filter_n["d2_db"]),
        filter_n["f_pass"],
        filter_n["tr_band"],
    )
    coef_curr = coef.copy()

    # Best solution (in first step is the same as current)
    cost_best = cost_curr
    coef_best = coef_curr.copy()

    # Resolution
    sigma_prime_range = {
        "start": 1e-3,
        "final": 1e-6,
    }

    sigma_bis_range = {
        "start": 1e-3,
        "final": 1e-6,
    }

    sigma_prime = sigma_prime_range["start"]
    sigma_bis = sigma_bis_range["start"]

    lmb_prime = slope_parameters(
        sigma_prime_range["start"], sigma_prime_range["final"], k_max
    )
    lmb_bis = slope_parameters(
        sigma_bis_range["start"], sigma_bis_range["final"], k_sub_max
    )

    # Main part
    for i in range(k_max):
        # Update new coef
        idx_prime = np.random.randint(0, coef.shape[0])
        coef_prime = coef_curr.copy()
        coef_prime[idx_prime] += sigma_prime * np.random.randn()

        # For bis search
        cost_bis_min = 1e6
        for j in range(k_sub_max):
            idx_bis = np.random.randint(0, coef.shape[0])

            coef_bis = coef_prime.copy()
            coef_bis[idx_bis] += sigma_bis * np.random.randn()

            _, f_res = signal.freqz(coef_bis, worN=filter_n["N_fft"])
            cost_bis = cost_LP_filter(
                abs(f_res),
                db_to_linear(filter_n["d1_db"]) - 1,
                db_to_linear(filter_n["d2_db"]),
                filter_n["f_pass"],
                filter_n["tr_band"],
            )

            if cost_bis < cost_bis_min:
                cost_bis_min = cost_bis
                coef_bis_min = coef_bis.copy()

            # Update resolution
            sigma_prime = lmb_prime * sigma_prime

        if cost_bis_min < cost_best:
            cost_best = cost_bis_min
            coef_best = coef_bis_min.copy()

        if cost_bis_min < cost_curr:
            cost_curr = cost_bis_min
            coef_curr = coef_bis_min.copy()

        # Update resolution
        sigma_bis = lmb_bis * sigma_bis

    return cost_best, coef_best
