"""
Module with dataclass for flow shop problem.
"""

from dataclasses import dataclass, field

import numpy as np


@dataclass
class DataFrame:
    """Class store data for benchmark J.E Beasley
    http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/
    """

    n_jobs: int = 0
    m_machines: int = 0
    init_seed: int = 0
    up_bound: int = 0
    low_bound: int = 0
    processing_time: np.ndarray = field(
        default_factory=lambda: np.zeros(shape=(int, int))  # type: ignore
    )

    def __init__(self) -> None:
        pass
