def merge_iterative(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    point_a = 0
    point_b = 0
    ret = [0 for _ in range(len(lst_a) + len(lst_b))]
    while point_a < len(lst_a) and point_b < len(lst_b):
        if lst_a[point_a] < lst_b[point_b]:
            ret[point_a + point_b] = lst_a[point_a]
            point_a += 1
        else:
            ret[point_a + point_b] = lst_b[point_b]
            point_b += 1
    while point_a < len(lst_a):
        ret[point_a + point_b] = lst_a[point_a]
        point_a += 1
    while point_b < len(lst_b):
        ret[point_a + point_b] = lst_b[point_b]
        point_b += 1
    return ret


def merge_sorted(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list using `sorted`
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    return sorted(lst_a + lst_b)
