import typing as tp


def revert(dct: tp.Mapping[str, str]) -> dict[str, list[str]]:
    """
    :param dct: dictionary to revert in format {key: value}
    :return: reverted dictionary {value: [key1, key2, key3]}
    """
    ret: dict[str, list[str]] = dict()
    for value in dct.values():
        ret[value] = []
    for key, value in dct.items():
        ret[value].append(key)
    return ret
