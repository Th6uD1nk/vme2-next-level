import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.pattern import parse_pattern


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


if __name__ == "__main__":
  unittest.main()
