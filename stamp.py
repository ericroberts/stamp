from dataclasses import dataclass
from types import GenericAlias, UnionType
from typing import TypeVar, TypedDict, Callable, cast, _TypedDictMeta


@dataclass(frozen=True)
class NotPresent:
    pass


T = TypeVar("T", bound=TypedDict)


class Stamp:
    @staticmethod
    def cast(
        dict_type: type[T],
        actual_dict: dict[object, object],
        on_mismatch: Callable[[], object] = lambda: None,
    ) -> T:
        if not is_match(dict_type, actual_dict):
            on_mismatch()

        return cast(T, actual_dict)


def is_match(t: type[object], value: object) -> bool:
    if type(t) == _TypedDictMeta:
        return all(
            is_match(_t, value.get(key, NotPresent()))
            for key, _t in t.__annotations__.items()
        )

    if type(t) == GenericAlias and isinstance(value, list):
        return all(is_match(t.__args__[0], v) for v in value)

    if type(t) == GenericAlias and isinstance(value, dict):
        return all(
            is_match(t.__args__[0], k) and is_match(t.__args__[1], v)
            for k, v in value.items()
        )

    if type(t) == UnionType:
        return any(is_match(arg_type, value) for arg_type in t.__args__)

    if t.__name__ == "NotRequired":
        return type(value) == NotPresent or type(value) == t.__args__[0]

    return t == type(value)
