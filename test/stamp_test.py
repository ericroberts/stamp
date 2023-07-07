from typing import TypedDict
import unittest
from stamp import Stamp


class SimpleTest(unittest.TestCase):
    class TestDict(TypedDict):
        string: str
        integer: int

    def test_matching(self):
        self.assertMatch(self.TestDict, { "string": "hi", "integer": 1})

    def test_non_matching_type(self):
        self.assertNoMatch(self.TestDict, {"string": "hi", "integer": "not an integer"})

    def test_missing_keys(self):
        self.assertNoMatch(self.TestDict, {"string": "hi"})

    def test_allows_extra_keys(self):
        self.assertMatch(self.TestDict, { "string": "hi", "integer": 1, "extra_key": True })

    def assertMatch(self, dict_type: type[TypedDict], actual_dict: dict[object, object]):
        self.assertTrue(Stamp.is_match(dict_type, actual_dict))

    def assertNoMatch(self, dict_type: type[TypedDict], actual_dict: dict[object, object]):
        self.assertFalse(Stamp.is_match(dict_type, actual_dict))

class StampTest(unittest.TestCase):
    def test_union(self):
        class Union(TypedDict):
            str_or_int: str | int

        with self.subTest("matching"):
            self.assertTrue(Stamp.is_match(Union, {"str_or_int": "hi"}))
            self.assertTrue(Stamp.is_match(Union, {"str_or_int": 1}))

        with self.subTest("non-matching"):
            self.assertFalse(Stamp.is_match(Union, {"str_or_int": 0.2}))

    def test_nested_list(self):
        class NestedList(TypedDict):
            string: str
            list_of_strings: list[str]

        with self.subTest("matching"):
            self.assertTrue(
                Stamp.is_match(NestedList, {"string": "hi", "list_of_strings": ["hi"]})
            )

        with self.subTest("non-matching"):
            self.assertFalse(
                Stamp.is_match(NestedList, {"string": "hi", "list_of_strings": [1]})
            )

    def test_nested_list_union(self):
        class NestedList(TypedDict):
            string: str
            list_of_strings: list[str | int]

        with self.subTest("matching"):
            self.assertTrue(
                Stamp.is_match(
                    NestedList, {"string": "hi", "list_of_strings": ["hi", 1]}
                )
            )

        with self.subTest("non-matching"):
            self.assertFalse(
                Stamp.is_match(NestedList, {"string": "hi", "list_of_strings": [1.01]})
            )
