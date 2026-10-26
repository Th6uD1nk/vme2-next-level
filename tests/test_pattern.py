import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.pattern import check_patterns, match, parse_pattern


def found(pattern, text, constants=()):
  return match(parse_pattern(pattern), parse_pattern(text), constants)


class MatchTest(unittest.TestCase):
  def test_the_two_sides_of_a_commutative_operator_can_be_swapped(self):
    self.assertEqual(found("a + c", "5 + x", "c"), {"a": ("name", "x"), "c": ("num", 5)})
    self.assertEqual(found("a + b", "x + y"), {"a": ("name", "x"), "b": ("name", "y")})
    for operator in ["+", "*", "&", "|", "^"]:
      self.assertIsNotNone(found(f"a {operator} c", f"5 {operator} x", "c"))

  def test_the_grouping_written_is_the_grouping_searched(self):
    self.assertIsNone(found("a + b + c", "x + (y + 5)", "c"))
    self.assertIsNone(found("a + b + c", "5 + x + y", "c"))


def entry(pattern, *arguments):
  return {"pattern": pattern, "arguments": arguments}


OPERANDS = (("a", "operand"), ("b", "operand"))


class CheckPatternsTest(unittest.TestCase):
  def test_a_pattern_must_use_exactly_its_arguments(self):
    with self.assertRaisesRegex(ValueError, r"the pattern of 'sub' must use its arguments \(a, b\)"):
      check_patterns({"sub": entry("a - b + c", *OPERANDS)})
    with self.assertRaisesRegex(ValueError, r"the pattern of 'sub' must use its arguments \(a, b\)"):
      check_patterns({"sub": entry("a - a", *OPERANDS)})

  def test_two_patterns_that_differ_only_by_the_order_of_a_commutative_operator_are_refused(self):
    with self.assertRaisesRegex(ValueError, "'or' and 'xor' have the same pattern"):
      check_patterns({"xor": entry("a | b", *OPERANDS), "or": entry("b | a", *OPERANDS)})

  def test_a_minus_and_the_minus_reversed_are_two_different_patterns(self):
    check_patterns({"sub": entry("a - b", *OPERANDS), "rsub": entry("b - a", *OPERANDS)})


if __name__ == "__main__":
  unittest.main()
