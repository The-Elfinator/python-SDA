import typing as tp
from collections import Counter


def get_min_to_drop(seq: tp.Sequence[tp.Any]) -> int:
    """
    :param seq: sequence of elements
    :return: number of elements need to drop to leave equal elements
    """
    cnt = Counter(seq)
    return 0 if len(seq) == 0 else len(seq) - cnt.most_common(1)[0][1]
