from dataclasses import dataclass
from types import GenericAlias, UnionType
from typing import TypeVar, TypedDict, Callable, cast


@dataclass(frozen=True)
class NotPresent:
    pass


T = TypeVar("T", bound=TypedDict)


class Stamp:
    @staticmethod
    def is_match(dict_type: type[TypedDict], actual_dict: dict[object, object]) -> bool:
        return all(
            is_match(t, actual_dict.get(key, NotPresent()))
            for key, t in dict_type.__annotations__.items()
        )

    @staticmethod
    def cast(
        dict_type: type[T],
        actual_dict: dict[object, object],
        on_mismatch: Callable[[], object] = lambda: None,
    ) -> T:
        if not Stamp.is_match(dict_type, actual_dict):
            on_mismatch()

        return cast(T, actual_dict)


def is_match(t: type[object], value: object):
    if type(t) == GenericAlias and isinstance(value, list):
        return all(is_match(t.__args__[0], v) for v in value)

    if type(t) == UnionType:
        return any(is_match(arg_type, value) for arg_type in t.__args__)

    if t.__name__ == "NotRequired":
        return type(value) == NotPresent or type(value) == t.__args__[0]

    return t == type(value)
