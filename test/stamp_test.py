import json
from typing import TypedDict
from typing_extensions import NotRequired
from unittest import TestCase
from unittest.mock import Mock
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


class TestCast(TestCase):
    def test_runs_on_mismatch_when_theres_a_mismatch(self):
        class T(TypedDict):
            string: str

        on_mismatch = Mock()
        Stamp.cast(T, {"string": 1}, on_mismatch)
        on_mismatch.assert_called()


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


class NotRequiredTest(BaseTest):
    class NotRequired(TypedDict):
        string: NotRequired[str]

    def test_matching(self):
        self.assertMatch(self.NotRequired, {})
        self.assertMatch(self.NotRequired, {"string": "hi"})

    def test_non_matching(self):
        self.assertNoMatch(self.NotRequired, {"string": 1})
        self.assertNoMatch(self.NotRequired, {"string": None})


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


class NestedTypedDict(TypedDict):
    key: str


class ParentTypedDict(TypedDict):
    nested_typed_dict: NestedTypedDict


class NestedTypedDictTest(BaseTest):
    def test_matching(self):
        self.assertMatch(ParentTypedDict, {"nested_typed_dict": {"key": "hi"}})

    def test_non_matching(self):
        self.assertNoMatch(ParentTypedDict, {"nested_typed_dict": {"key": 1}})


class NestedDictTest(BaseTest):
    class NestedDict(TypedDict):
        nested_dict: dict[str, int]

    def test_matching(self):
        self.assertMatch(self.NestedDict, {"nested_dict": {"key": 1}})

    def test_non_matching_key(self):
        self.assertNoMatch(self.NestedDict, {"nested_dict": {1: 2}})

    def test_non_matching_value(self):
        self.assertNoMatch(self.NestedDict, {"nested_dict": {"key": "hi"}})


def annotations_as_string(annotations: dict[str, object]):
    types = ("\n").join(f"    {key}: {t}" for key, t in annotations.items())
    return f"{{\n{types}\n}}"


def failure_message(
    msg: str, dict_type: type[TypedDict], actual_dict: dict[object, object]
):
    return (
        f"\n\nProvided dict:\n\n{json.dumps(actual_dict, indent=4, sort_keys=True)}\n\n"
        f"{msg} {dict_type.__name__}:\n\n"
        f"{annotations_as_string(dict_type.__annotations__)}"
    )
