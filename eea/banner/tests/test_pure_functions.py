"""Unit tests for eea.banner pure functions

These tests cover pure functions that don't require Plone context:
- isTrue
"""

import unittest
from eea.banner.restapi.get import isTrue


class TestIsTrue(unittest.TestCase):
    """Tests for isTrue function"""

    def test_true_string(self):
        self.assertTrue(isTrue("true"))

    def test_false_string(self):
        self.assertFalse(isTrue("false"))

    def test_one_string(self):
        self.assertTrue(isTrue("1"))

    def test_zero_string(self):
        self.assertFalse(isTrue("0"))

    def test_t_string(self):
        self.assertTrue(isTrue("t"))

    def test_on_string(self):
        self.assertTrue(isTrue("on"))

    def test_yes_string(self):
        self.assertTrue(isTrue("yes"))

    def test_y_string(self):
        self.assertTrue(isTrue("y"))

    def test_bool_true(self):
        self.assertTrue(isTrue(True))

    def test_bool_false(self):
        self.assertFalse(isTrue(False))

    def test_uppercase_true(self):
        self.assertTrue(isTrue("TRUE"))

    def test_mixed_case(self):
        self.assertTrue(isTrue("Yes"))

    def test_empty_string(self):
        self.assertFalse(isTrue(""))

    def test_random_string(self):
        self.assertFalse(isTrue("maybe"))

    def test_integer(self):
        self.assertFalse(isTrue(1))

    def test_none(self):
        self.assertFalse(isTrue(None))

    def test_list(self):
        self.assertFalse(isTrue([1]))


if __name__ == "__main__":
    unittest.main()
