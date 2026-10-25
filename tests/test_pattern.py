import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.pattern import match, parse_pattern


class ParsePatternTest(unittest.TestCase):
  def test_a_pattern_is_read_as_an_expression_tree(self):
    self.assertEqual(parse_pattern("a + b"), ("bin", "+", ("name", "a"), ("name", "b")))
    self.assertEqual(parse_pattern("~and(x, c)"), ("not", ("call", "and", [("name", "x"), ("name", "c")])))

  def test_spaces_and_useless_parentheses_do_not_change_the_tree(self):
    self.assertEqual(parse_pattern("a+b"), parse_pattern("  a   +  b "))
    self.assertEqual(parse_pattern("(a + b)"), parse_pattern("a + b"))
    self.assertEqual(parse_pattern("(a + b) + c"), parse_pattern("a + b + c"))

  def test_a_grouping_parenthesis_changes_the_tree(self):
    self.assertNotEqual(parse_pattern("a + (b + c)"), parse_pattern("a + b + c"))
    self.assertNotEqual(parse_pattern("(a + b) * c"), parse_pattern("a + b * c"))

  def test_text_after_the_pattern_is_refused(self):
    with self.assertRaisesRegex(ValueError, "unexpected text after the pattern"):
      parse_pattern("a + b c")


def found(pattern, text, constants=()):
  return match(parse_pattern(pattern), parse_pattern(text), constants)


class MatchTest(unittest.TestCase):
  def test_the_names_of_the_pattern_are_bound_to_what_is_written(self):
    self.assertEqual(found("a + b", "top0 + base1"), {"a": ("name", "top0"), "b": ("name", "base1")})
    self.assertEqual(found("a + b + c", "(x + y) + 5", "c"), {"a": ("name", "x"), "b": ("name", "y"), "c": ("num", 5)})

  def test_an_operand_can_be_a_nested_operation(self):
    self.assertEqual(found("a + b", "x + y + z"), {"a": ("bin", "+", ("name", "x"), ("name", "y")), "b": ("name", "z")})

  def test_an_operand_is_not_a_number_and_a_constant_is_only_a_number(self):
    self.assertIsNone(found("a + b", "x + 5"))
    self.assertIsNone(found("a + c", "x + y", "c"))

  def test_the_two_sides_of_a_commutative_operator_can_be_swapped(self):
    self.assertEqual(found("a + c", "5 + x", "c"), {"a": ("name", "x"), "c": ("num", 5)})
    self.assertEqual(found("a + b", "x + y"), {"a": ("name", "x"), "b": ("name", "y")})
    for operator in ["+", "*", "&", "|", "^"]:
      self.assertIsNotNone(found(f"a {operator} c", f"5 {operator} x", "c"))

  def test_the_two_sides_of_a_minus_or_a_shift_keep_their_order(self):
    self.assertIsNone(found("a - c", "5 - x", "c"))
    self.assertIsNone(found("a >> c", "5 >> x", "c"))

  def test_the_grouping_written_is_the_grouping_searched(self):
    self.assertIsNone(found("a + b + c", "x + (y + 5)", "c"))
    self.assertIsNone(found("a + b + c", "5 + x + y", "c"))

  def test_the_operator_and_the_function_must_be_the_same(self):
    self.assertIsNone(found("a + b", "x - y"))
    self.assertEqual(found("~and(x, c)", "~and(top0, 255)", "c"), {"x": ("name", "top0"), "c": ("num", 255)})
    self.assertIsNone(found("~and(x, c)", "~or(top0, 255)", "c"))
    self.assertIsNone(found("~and(x, c)", "and(top0, 255)", "c"))


if __name__ == "__main__":
  unittest.main()
