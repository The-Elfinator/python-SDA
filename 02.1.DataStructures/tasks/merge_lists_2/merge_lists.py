import typing as tp
import heapq


def merge(seq: tp.Sequence[tp.Sequence[int]]) -> list[int]:
    """
    :param seq: sequence of sorted sequences
    :return: merged sorted list
    """
    heap: list[tuple[int, int]] = []
    k = len(seq)
    indexes = [0 for _ in range(k)]  # which indexes are now in heap
    for i in range(k):
        if len(seq[i]) != 0:
            heapq.heappush(heap, (seq[i][0], i))
    ret: list[int] = []
    while len(heap) != 0:
        elem, ind = heapq.heappop(heap)
        ret.append(elem)
        indexes[ind] += 1
        if indexes[ind] < len(seq[ind]):
            heapq.heappush(heap, (seq[ind][indexes[ind]], ind))
    return ret
