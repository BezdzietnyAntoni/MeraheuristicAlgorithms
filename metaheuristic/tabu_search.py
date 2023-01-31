import random

import numpy as np

import flow_shop as fs

from .neighbor_moves import *


def tabu_search(
    data: np.ndarray,
    move_type: NeighborMoves,
    tabu_size: int = 3,
    aspiration_value: int = 50,
    max_iter: int = 100,
    return_hist=False,
):
    m_machines = data.shape[0]
    n_jobs = data.shape[1]

    data = data.copy()

    # Best solution
    x_best = data.copy()
    t_best = fs.calculate_completion_time(x_best, n_jobs, m_machines)

    # Define available move
    move_type = NeighborMoves.INSERT_BEFORE
    move = TRANSFORMS[move_type.value]

    # Tabu list setting
    tabu_idx = 0
    tabu_list = np.zeros((tabu_size, 2), dtype=int)

    if return_hist:
        t_hist = np.zeros((max_iter,2))

    for k in range(max_iter):
        # Generate neighbor
        idx1 = random.randint(0, n_jobs - 1)
        various_idxs = np.concatenate((np.arange(0, idx1), np.arange(idx1 + 1, n_jobs)))
        neighbor_idxs = np.zeros((n_jobs - 1, 2), dtype=int)  # Static
        for i, v in enumerate(various_idxs):
            neighbor_idxs[i, :] = [idx1, v]
        if move_type in (NeighborMoves.SWAP, NeighborMoves.REVERSE_SUBSEQUENCE):
            neighbor_idxs.sort(axis=1)
        # Check time neighbor
        neighbor_times = np.zeros((n_jobs - 1))  # Static
        for i, n in enumerate(neighbor_idxs):
            neighbor_times[i] = fs.calculate_completion_time(
                move(data, n[0], n[1]), n_jobs, m_machines
            )

        # Find best
        while True:
            best_neighbor_idx = np.argmin(neighbor_times)
            if neighbor_idxs[best_neighbor_idx].tolist() in tabu_list.tolist():
                # Best solution is in tabu-list
                if (neighbor_times[best_neighbor_idx] + aspiration_value) > t_best:
                    # Aspiration criterion not satisfy
                    neighbor_times[best_neighbor_idx] = 1e6
                else:
                    # Aspiration criterion satisfy
                    break
            else:
                # Best solution is not in tabu-list
                break

        if neighbor_times[best_neighbor_idx] < t_best:
            # Better than present best
            t_best = neighbor_times[best_neighbor_idx]
            x_best = move(
                data,
                neighbor_idxs[best_neighbor_idx][0],
                neighbor_idxs[best_neighbor_idx][1],
            )

        data = move(
            data,
            neighbor_idxs[best_neighbor_idx][0],
            neighbor_idxs[best_neighbor_idx][1],
        )

        # Add to tabu list
        tabu_list[tabu_idx] = neighbor_idxs[best_neighbor_idx]
        tabu_idx = (tabu_idx + 1) % tabu_size

        if return_hist:
            t_hist[k, 0] = t_best
            t_hist[k, 1] = neighbor_times[best_neighbor_idx]

    if not return_hist:
        return (t_best, x_best)

    return (t_best, x_best, t_hist)
