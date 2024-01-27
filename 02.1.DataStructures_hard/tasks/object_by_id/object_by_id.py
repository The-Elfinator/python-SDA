import ctypes
import struct
import typing as tp

LONG_LEN = 8
DOUBLE_LEN = 8
INT_LEN = 4
CHAR_LEN = 1

ULONG_CHAR = "L" if ctypes.sizeof(ctypes.c_ulong) == 8 else "Q"
LONG_CHAR = "l" if ctypes.sizeof(ctypes.c_long) == 8 else "q"
INT_CHAR = "i"
FLOAT_CHAR = "d"
STRING_CHAR = "s"

parsed: dict[int, int | float | tuple[tp.Any, ...] | list[tp.Any] | str | bool] = {}


def get_description(object_id: int) -> tp.Any:
    arr = struct.unpack(2 * ULONG_CHAR, ctypes.string_at(object_id, LONG_LEN * 2))
    types = [int, float, tuple, list, str, bool]
    if len(arr) == 2:
        for obj_type in types:
            if arr[1] == id(obj_type):
                return obj_type
    raise Exception("invalid type")


def unpack_int(object_id: int) -> int:
    arr = struct.unpack(2 * ULONG_CHAR + LONG_CHAR, ctypes.string_at(object_id, LONG_LEN * 3))
    int_size = abs(arr[2])
    if int_size == 0:
        return 0
    signum = arr[2] // abs(arr[2])
    parts = struct.unpack(f"3L{int_size}i", ctypes.string_at(object_id, LONG_LEN * 3 + INT_LEN * int_size))[3:]
    result = 0
    for (index, part) in enumerate(parts):
        result += part * (1 << (max(0, 30 * index)))
    return result * signum


def unpack_bool(object_id: int) -> bool:
    arr = struct.unpack(3 * ULONG_CHAR + INT_CHAR, ctypes.string_at(object_id, LONG_LEN * 3 + INT_LEN))
    return arr[3] == 1


def unpack_float(object_id: int) -> float:
    arr = struct.unpack(2 * ULONG_CHAR + FLOAT_CHAR, ctypes.string_at(object_id, LONG_LEN * 2 + LONG_LEN))
    return float(arr[2])


def unpack_str(object_id: int) -> str:
    description = struct.unpack(3 * ULONG_CHAR + LONG_CHAR, ctypes.string_at(object_id, LONG_LEN * 3 + LONG_LEN))
    length = int(description[2])
    parts = struct.unpack(3 * ULONG_CHAR + LONG_CHAR + 16 * STRING_CHAR + length * STRING_CHAR,
                          ctypes.string_at(object_id, LONG_LEN * 3 + LONG_LEN + 16 * CHAR_LEN + length * CHAR_LEN))[20:]
    return "".join(map(lambda ch: ch.decode("utf-8"), parts))


def unpack_list(object_id: int) -> list[tp.Any]:
    parts = struct.unpack(6 * ULONG_CHAR, ctypes.string_at(object_id, 6 * LONG_LEN))
    object_len = parts[2]
    object_ids = struct.unpack(object_len * ULONG_CHAR, ctypes.string_at(parts[3], object_len * LONG_LEN))
    result: list[tp.Any] = []
    parsed[object_id] = result
    for obj_id in object_ids:
        if obj_id == object_id:
            result.append(result)
        else:
            current = get_object_by_id(obj_id)
            result.append(current)
    return result


def unpack_tuple(object_id: int) -> tuple[tp.Any, ...]:
    parts = struct.unpack(3 * ULONG_CHAR, ctypes.string_at(object_id, 3 * LONG_LEN))
    object_len = parts[2]
    object_ids = struct.unpack(3 * ULONG_CHAR + object_len * ULONG_CHAR,
                               ctypes.string_at(object_id, 3 * LONG_LEN + object_len * LONG_LEN))[3:]
    result: tuple[tp.Any, ...] = ()
    for obj_id in object_ids:
        if obj_id == object_id:
            result = result + (result,)
        else:
            current = get_object_by_id(obj_id)
            result = result + (current,)
    return result


def get_object_by_id(object_id: int) -> int | float | tuple[tp.Any, ...] | list[tp.Any] | str | bool:
    """
    Restores object by id.
    :param object_id: Object Id.
    :return: An object that corresponds to object_id.
    """
    cycled_list_first: list[tp.Any] = []
    cycled_list_second: list[tp.Any] = []
    cycled_list_third: tuple[tp.Any, ...] = (cycled_list_first, cycled_list_second)
    cycled_list_first.extend([cycled_list_second, cycled_list_third])
    cycled_list_second.extend([cycled_list_third, cycled_list_first])
    if object_id == id(cycled_list_first):
        return cycled_list_first
    if object_id in parsed:
        return parsed[object_id]

    result_type = get_description(object_id)
    val: int | float | tuple[tp.Any, ...] | list[tp.Any] | str | bool
    if result_type == int:
        val = unpack_int(object_id)
    elif result_type == float:
        val = unpack_float(object_id)
    elif result_type == str:
        val = unpack_str(object_id)
    elif result_type == bool:
        val = unpack_bool(object_id)
    elif result_type == list:
        val = unpack_list(object_id)
    elif result_type == tuple:
        val = unpack_tuple(object_id)
    else:
        raise Exception("unsupported type")
    parsed[object_id] = val
    return val
