import typing as tp
import json

from decimal import Decimal

STR_TO_TYPE: dict[str, type] = {
    "int": int,
    "float": float,
    "decimal": Decimal
}


def object_hook(dct: dict[str, tp.Any]) -> dict[tp.Any, tp.Any]:
    custom_key = dct.pop("__custom_key_type__", None)
    if custom_key is not None:
        type_py = STR_TO_TYPE[custom_key]
        return {type_py(key): value for key, value in dct.items()}
    return dct


def decode_typed_json(json_value: str) -> tp.Any:
    """
    Returns deserialized object from json string.
    Checks __custom_key_type__ in object's keys to choose appropriate type.

    :param json_value: serialized object in json format
    :return: deserialized object
    """
    return json.loads(json_value, object_hook=object_hook)
