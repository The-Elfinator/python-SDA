from queue import Queue
import typing as tp


def traverse_dictionary_immutable(
        dct: tp.Mapping[str, tp.Any],
        prefix: str = "") -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param prefix: prefix for key used for passing total path through recursion
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    ret = []
    for key, value in dct.items():
        if type(value) is dict:
            for inner_key, inner_value in traverse_dictionary_immutable(value, prefix + key + "."):
                ret.append((inner_key, inner_value))
        else:
            ret.append((prefix + key, value))
    return ret


def traverse_dictionary_mutable(
        dct: tp.Mapping[str, tp.Any],
        result: list[tuple[str, int]],
        prefix: str = "") -> None:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param result: list with pairs: (full key from root to leaf joined by ".", value)
    :param prefix: prefix for key used for passing total path through recursion
    :return: None
    """
    result.extend(traverse_dictionary_immutable(dct, prefix))


def traverse_dictionary_iterative(
        dct: tp.Mapping[str, tp.Any]
        ) -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    q: Queue[tuple[str, tp.Any]] = Queue()
    for k, v in dct.items():
        q.put((k, v))
    ret: list[tuple[str, int]] = []
    while not q.empty():
        key, value = q.get()
        if type(value) is not dict:
            ret.append((key, value))
            continue
        for inner_key, inner_value in value.items():
            q.put((key + "." + inner_key, inner_value))
    return ret
