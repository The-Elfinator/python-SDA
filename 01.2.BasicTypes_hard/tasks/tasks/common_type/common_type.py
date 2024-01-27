def get_common_type(type1: type, type2: type) -> type:
    """
    Calculate common type according to rule, that it must have the most adequate interpretation after conversion.
    Look in tests for adequacy calibration.
    :param type1: one of [bool, int, float, complex, list, range, tuple, str] types
    :param type2: one of [bool, int, float, complex, list, range, tuple, str] types
    :return: the most concrete common type, which can be used to convert both input values
    """
    if type1 is str or type2 is str:
        return str
    if type1 is list:
        if type2 is list or type2 is range or type2 is tuple:
            return list
        return str
    if type2 is list:
        if type1 is list or type1 is range or type1 is tuple:
            return list
        return str
    if type1 is tuple or type1 is range:
        if type2 is int or type2 is float or type2 is complex or type2 is bool:
            return str
        return tuple
    if type2 is tuple or type2 is range:
        if type1 is int or type1 is float or type1 is complex or type1 is bool:
            return str
        return tuple
    if type1 is complex or type2 is complex:
        return complex
    if type1 is float or type2 is float:
        return float
    if type1 is int or type2 is int:
        return int
    return bool
