import typing as tp


def convert_to_common_type(data: list[tp.Any]) -> list[tp.Any]:
    """
    Takes list of multiple types' elements and convert each element to common type according to given rules
    :param data: list of multiple types' elements
    :return: list with elements converted to common type
    """
    default_type: type = str
    only_none: bool = True
    has_number: bool = False
    only_zero_or_one: bool = True
    for element in data:
        if not isinstance(element, bool) and (element == "" or element == 0 or element is None):
            if element == 0:
                has_number = True
            continue
        only_none = False
        if isinstance(element, tuple) or isinstance(element, list):
            default_type = list
            break
        if isinstance(element, float):
            default_type = float
            continue
        if isinstance(element, int) and default_type is not float:
            default_type = int
            only_zero_or_one = only_zero_or_one and (element in [0, 1])
            continue
        if isinstance(element, bool) and default_type is not float and default_type is not int:
            default_type = bool
            continue
    if only_none:
        if has_number:
            default_type = int
    elif default_type is int and only_zero_or_one:
        default_type = bool
    ret: list[tp.Any] = []
    for element in data:
        if default_type is list:
            if element == 0 or element == "" or element is None:
                ret.append([])
            else:
                if isinstance(element, tuple) or isinstance(element, list):
                    ret.append(list(element))
                else:
                    ret.append([element])
        elif default_type is float:
            if element == 0 or element == "" or element is None:
                ret.append(0.0)
            else:
                ret.append(float(element))
        elif default_type is int:
            if element == "" or element is None:
                ret.append(0)
            else:
                ret.append(int(element))
        elif default_type is bool:
            if element == 0 or element == "" or element is None:
                ret.append(False)
            else:
                if isinstance(element, bool):
                    ret.append(element)
                else:
                    ret.append(True)
        else:
            # default_type is str
            if element == 0 or element == "" or element is None:
                ret.append("")
            else:
                ret.append(str(element))
    return ret
