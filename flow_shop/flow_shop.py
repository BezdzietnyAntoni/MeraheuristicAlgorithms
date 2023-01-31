"""Module implements useful function for flow shop problem
"""

import random
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from .data_frame import DataFrame


def calculate_completion_time(
    data: Union[DataFrame, np.ndarray],
    n_jobs: Optional[int] = None,
    m_machines: Optional[int] = None,
    return_comp_arr: bool = False,
):
    """Calculate completion time for flow shop problem.

    Args:
        data (Union[DataFrame, np.ndarray]): data with processing time
        n_jobs (Optional[int], optional): Number of jobs. Defaults to None.
        m_machines (Optional[int], optional): Number of machines. Defaults to None.
        return_comp_arr (bool, optional): Option for return completion array. Defaults to False.

    Raises:
        ValueError: If some parameters are invalid

    Returns:
        completion_time(int): Return completion_time, if return_comp_arr flag is False.
        (completion_time(int), completion_array(numpy.ndarray)):
        Return completion_time and completion_array, if return_comp_arr flag is True.
    """

    if isinstance(data, DataFrame):
        n_jobs = data.n_jobs
        m_machines = data.m_machines
        data = data.processing_time
    else:
        if n_jobs is None or m_machines is None:
            raise ValueError("Parameters error")
        if not (isinstance(data, np.ndarray) or isinstance(data, list)):
            raise ValueError("Parameters data error")

    completion_array = np.zeros((m_machines, n_jobs))
    for i in range(m_machines):
        completion_array[i][0] = data[i][0] + completion_array[i - 1][0]
    # Fill first row for first machine
    for j in range(1, n_jobs):
        completion_array[0][j] = data[0][j] + completion_array[0][j - 1]
    # Fill array for next task
    for i in range(1, m_machines):
        for j in range(1, n_jobs):
            completion_array[i][j] = (
                np.max((completion_array[i - 1][j], completion_array[i][j - 1]))
                + data[i][j]
            )

    completion_time = completion_array[-1][-1]

    if return_comp_arr:
        return [completion_time, completion_array]

    return completion_time


def display_graph(
    data_frame: DataFrame, completion_time: int, completion_array: np.ndarray
) -> None:
    """Display graph for flow shop problem

    Args:
        data_frame (DataFrame): DataFrame with data
        completion_time (int): Completion time
        completion_array (np.ndarray): Completion array
    """
    plt.figure()
    ax = plt.gca()
    colors = plt.cm.Set3(np.linspace(0, 1, data_frame.n_jobs))  # type: ignore
    rand_val = [i for i in range(data_frame.n_jobs)]
    random.shuffle(rand_val)
    for i, machine in enumerate(completion_array):
        size_y = 0.9
        pos_y_box = i - size_y / 2 + 1
        for ti, task in enumerate(machine):
            size_x = data_frame.processing_time[i][ti]
            pos_x_box = task - size_x
            ax.add_patch(
                Rectangle(
                    (pos_x_box, pos_y_box),
                    size_x,
                    size_y,
                    facecolor=colors[rand_val[ti]],
                    alpha=0.9,
                    linewidth=0.4,
                    edgecolor="k",
                )
            )
    plt.title("Flow Shop Problem")
    plt.xlabel("Time")
    plt.ylabel("Machines")
    plt.yticks(range(1, data_frame.m_machines + 1))
    plt.xlim([0, completion_time])
    plt.ylim([0, data_frame.m_machines + 1])
    plt.ylim([0, data_frame.m_machines + 1])
    plt.show()


def swap(array: np.ndarray, idx_1: int, idx_2: int) -> np.ndarray:
    """Swap two columns in array

    Args:
        array (np.ndarray): Array
        idx_1 (int): Index of first element
        idx_2 (int): Index of second element

    Returns:
        array (np.ndarray): Copy array with swapping elements
    """
    cp_array = array.copy()
    cp_array[:, [idx_1, idx_2]] = cp_array[:, [idx_2, idx_1]]  # type: ignore
    return cp_array


def insert_before(array: np.ndarray, idx_1: int, idx_2: int) -> np.ndarray:
    """Insert element from idx_1 before element idx_2

    Args:
        array (np.ndarray): Array
        idx_1 (int): Index of moving element
        idx_2 (int): Position before which element will be insert
    Returns:
        array (np.ndarray): Copy array with insert elements
    """
    cp_array = array.copy()
    tmp = np.copy(cp_array[:, idx_1])
    if idx_1 < idx_2:
        cp_array[:, idx_1:idx_2] = cp_array[:, idx_1 + 1 : idx_2 + 1]
        cp_array[:, idx_2 - 1] = tmp
    elif idx_1 > idx_2:
        cp_array[:, idx_2 + 1 : idx_1 + 1] = cp_array[:, idx_2:idx_1]
        cp_array[:, idx_2] = tmp

    return cp_array


def insert_after(array: np.ndarray, idx_1: int, idx_2: int) -> np.ndarray:
    """Insert element from idx_1 after element idx_2

    Args:
        array (np.ndarray): Array
        idx_1 (int): Index of moving element
        idx_2 (int): Position after which element will be insert
    Returns:
        array (np.ndarray): Copy array with insert elements
    """
    cp_array = array.copy()
    tmp = np.copy(cp_array[:, idx_1])
    if idx_1 < idx_2:
        cp_array[:, idx_1:idx_2] = cp_array[:, idx_1 + 1 : idx_2 + 1]
        cp_array[:, idx_2] = tmp
    elif idx_1 > idx_2:
        cp_array[:, idx_2 + 1 : idx_1 + 1] = cp_array[:, idx_2:idx_1]
        cp_array[:, idx_2 + 1] = tmp

    return cp_array


def reverse_subsequence(array: np.ndarray, idx_1: int, idx_2: int) -> np.ndarray:
    """Reverse order in subsequence of array

    Args:
        array (np.ndarray): Array
        idx_1 (int): Index of initial element
        idx_2 (int): Index of closing element

    Returns:
        array (np.ndarray): Copy array with reverse order subsequence
    """
    cp_array = array.copy()
    temp = cp_array[:, idx_1 : idx_2 + 1][:, ::-1]
    cp_array[:, idx_1 : idx_2 + 1] = temp
    return cp_array
