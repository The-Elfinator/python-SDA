import numpy as np
import numpy.typing as npt


def replace_nans(matrix: npt.NDArray[np.float_]) -> npt.NDArray[np.float_]:
    """
    Replace all nans in matrix with average of other values.
    If all values are nans, then return zero matrix of the same size.
    :param matrix: matrix,
    :return: replaced matrix
    """
    if np.all(np.isnan(matrix)):
        return np.zeros_like(matrix)
    matrix[np.isnan(matrix)] = np.nanmean(matrix)
    return matrix
