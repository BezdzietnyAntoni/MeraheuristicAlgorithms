from enum import IntEnum

import flow_shop as fs


class NeighborMoves(IntEnum):
    """Type of available move in neighbor"""

    SWAP = (0,)
    REVERSE_SUBSEQUENCE = (1,)
    INSERT_BEFORE = (2,)
    INSERT_AFTER = 3


TRANSFORMS = {
    0: fs.swap,
    1: fs.reverse_subsequence,
    2: fs.insert_before,
    3: fs.insert_after,
}
