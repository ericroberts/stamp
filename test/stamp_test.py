import json
from typing import TypedDict
from unittest import TestCase
from stamp import Stamp


class BaseTest(TestCase):
    def assertMatch(
        self, dict_type: type[TypedDict], actual_dict: dict[object, object]
    ):
        self.assertTrue(
            Stamp.is_match(dict_type, actual_dict),
            failure_message(
                f"does not match type {dict_type.__name__}",
                dict_type,
                actual_dict,
            ),
        )

    def assertNoMatch(
        self, dict_type: type[TypedDict], actual_dict: dict[object, object]
    ):
        self.assertFalse(
            Stamp.is_match(dict_type, actual_dict),
            failure_message(
                f"unexpectedly matches type {dict_type.__name__}",
                dict_type,
                actual_dict,
            ),
        )


class SimpleTest(BaseTest):
    class Simple(TypedDict):
        string: str
        integer: int

    def test_matching(self):
        self.assertMatch(self.Simple, {"string": "hi", "integer": 1})

    def test_non_matching(self):
        self.assertNoMatch(self.Simple, {"string": "hi", "integer": "not an integer"})

    def test_missing_keys(self):
        self.assertNoMatch(self.Simple, {"string": "hi"})

    def test_allows_extra_keys(self):
        self.assertMatch(self.Simple, {"string": "hi", "integer": 1, "extra_key": True})


class UnionTest(BaseTest):
    class Union(TypedDict):
        str_or_int: str | int

    def test_matching(self):
        self.assertMatch(self.Union, {"str_or_int": "hi"})
        self.assertMatch(self.Union, {"str_or_int": 1})

    def test_non_matching(self):
        self.assertNoMatch(self.Union, {"str_or_int": 0.2})


class NestedListTest(BaseTest):
    class NestedList(TypedDict):
        list_of_strings: list[str]

    def test_matching(self):
        self.assertMatch(self.NestedList, {"list_of_strings": ["hi"]})

    def test_non_matching(self):
        self.assertNoMatch(self.NestedList, {"list_of_strings": [1]})


class NestedListWithUnionTest(BaseTest):
    class NestedList(TypedDict):
        list_of_stuff: list[str | int]

    def test_matching(self):
        self.assertMatch(self.NestedList, {"list_of_stuff": ["hi", 1]})

    def test_non_matching(self):
        self.assertNoMatch(self.NestedList, {"string": "hi", "list_of_strings": [1.01]})


def annotations_as_string(annotations: dict[str, object]):
    types = ("\n").join(f"    {key}: {t}" for key, t in annotations.items())
    return f"{{\n{types}\n}}"


def failure_message(
    msg: str, dict_type: type[TypedDict], actual_dict: dict[object, object]
):
    return (
        f"\n\nProvided dict:\n\n{json.dumps(actual_dict, indent=4, sort_keys=True)}\n\n"
        f"{msg} {dict_type.__name__}:\n\n"
        f"{annotations_as_string(dict_type.__annotations__)}",
    )
