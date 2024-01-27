import numpy as np
import numpy.typing as npt


def max_element(array: npt.NDArray[np.int_]) -> int | None:
    """
    Return max element before zero for input array.
    If appropriate elements are absent, then return None
    :param array: array,
    :return: max element value or None
    """
    zero_indices = np.where(array == 0)[0]
    if len(zero_indices) == 0:
        return None

    next_indices = zero_indices + 1
    next_indices = next_indices[next_indices < len(array)]
    if len(next_indices) == 0:
        return None
    return np.max(array[next_indices])
