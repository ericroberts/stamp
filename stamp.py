from types import GenericAlias, UnionType
from typing import TypedDict


class Stamp:
    @staticmethod
    def is_match(dict_type: type[TypedDict], actual_dict: dict[object, object]) -> bool:
        return all(
            is_match(t, actual_dict.get(key))
            for key, t in dict_type.__annotations__.items()
        )


def is_match(t: type[object], value: object):
    if isinstance(t, GenericAlias) and isinstance(value, list):
        return all(is_match(t.__args__[0], v) for v in value)

    if type(t) == UnionType:
        return any(is_match(arg_type, value) for arg_type in t.__args__)

    return t == type(value)
