def filter_list_by_list(lst_a: list[int] | range, lst_b: list[int] | range) -> list[int]:
    """
    Filter first sorted list by other sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: filtered sorted list
    """
    ret = []
    point_a = 0
    point_b = 0
    while point_a < len(lst_a) and point_b < len(lst_b):
        if lst_a[point_a] == lst_b[point_b]:
            point_a += 1
            continue
        if lst_a[point_a] < lst_b[point_b]:
            ret.append(lst_a[point_a])
            point_a += 1
        else:
            point_b += 1
    while point_a < len(lst_a):
        ret.append(lst_a[point_a])
        point_a += 1
    return ret
