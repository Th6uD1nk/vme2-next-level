import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.pattern import check_patterns, match, parse_pattern, simplify, without


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


def simplified(text):
  return simplify(parse_pattern(text))


class SimplifyTest(unittest.TestCase):
  def test_a_zero_that_changes_nothing_is_dropped(self):
    for text in ["a + 0", "0 + a", "a | 0", "0 | a", "a ^ 0", "0 ^ a", "a - 0", "a << 0", "a >> 0"]:
      self.assertEqual(simplified(text), ("name", "a"), text)

  def test_a_product_or_an_and_with_zero_is_zero(self):
    for text in ["a * 0", "0 * a", "a & 0", "0 & a"]:
      self.assertEqual(simplified(text), ("num", 0), text)

  def test_what_is_not_neutral_stays(self):
    for text in ["0 - a", "0 << a", "a + 1", "a * 1", "~and(a, 0)"]:
      self.assertEqual(simplified(text), parse_pattern(text), text)

  def test_the_zeros_inside_an_expression_are_dropped_too(self):
    self.assertEqual(simplified("(a + 0) * (b | 0)"), parse_pattern("a * b"))
    self.assertEqual(simplified("a * 0 + b"), ("name", "b"))


def reduced(pattern, names):
  return without(parse_pattern(pattern), names)


class WithoutTest(unittest.TestCase):
  def test_a_constant_set_to_zero_leaves_what_the_operation_does_without_it(self):
    self.assertEqual(reduced("a + b + c", ["c"]), parse_pattern("a + b"))
    self.assertEqual(reduced("a - b + c", ["c"]), parse_pattern("a - b"))
    self.assertEqual(reduced("(a - b) >> n", ["n"]), parse_pattern("a - b"))

  def test_a_constant_that_makes_the_whole_pattern_zero_gives_zero(self):
    self.assertEqual(reduced("a * b * c", ["c"]), ("num", 0))

  def test_only_the_named_constants_are_set_to_zero(self):
    self.assertEqual(reduced("a + b + c", []), parse_pattern("a + b + c"))
    self.assertEqual(reduced("(a + c) * d", ["c"]), parse_pattern("a * d"))

  def test_a_reduced_pattern_is_found_in_the_written_expression_only_when_it_is_the_same(self):
    self.assertIsNotNone(match(reduced("a + b + c", ["c"]), parse_pattern("x + y"), ()))
    self.assertIsNone(match(reduced("a * b * c", ["c"]), parse_pattern("x * y"), ()))


def entry(pattern, *arguments):
  return {"pattern": pattern, "arguments": arguments}


OPERANDS = (("a", "operand"), ("b", "operand"))


class CheckPatternsTest(unittest.TestCase):
  def test_a_table_whose_patterns_use_their_arguments_is_accepted(self):
    check_patterns({"add": entry("a + b", *OPERANDS), "addc": entry("a + b + c", *OPERANDS, ("c", "number"))})

  def test_a_pattern_that_cannot_be_read_is_refused(self):
    with self.assertRaisesRegex(ValueError, "the pattern of 'sub' is not valid"):
      check_patterns({"sub": entry("a - ", *OPERANDS)})

  def test_a_pattern_must_use_exactly_its_arguments(self):
    with self.assertRaisesRegex(ValueError, r"the pattern of 'sub' must use its arguments \(a, b\)"):
      check_patterns({"sub": entry("a - b + c", *OPERANDS)})
    with self.assertRaisesRegex(ValueError, r"the pattern of 'sub' must use its arguments \(a, b\)"):
      check_patterns({"sub": entry("a - a", *OPERANDS)})

  def test_two_patterns_that_differ_only_by_the_order_of_a_commutative_operator_are_refused(self):
    with self.assertRaisesRegex(ValueError, "'or' and 'xor' have the same pattern"):
      check_patterns({"xor": entry("a | b", *OPERANDS), "or": entry("b | a", *OPERANDS)})

  def test_a_constant_instead_of_an_operand_or_a_minus_reversed_make_two_different_patterns(self):
    check_patterns({"and": entry("a & b", *OPERANDS), "and_cst": entry("x & c", ("x", "source"), ("c", "number"))})
    check_patterns({"sub": entry("a - b", *OPERANDS), "rsub": entry("b - a", *OPERANDS)})


class CheckAliasesTest(unittest.TestCase):
  def test_an_alias_that_uses_the_arguments_is_accepted(self):
    check_patterns({"and_cst": dict(entry("x & c", ("x", "source"), ("c", "number")), aliases=("and(x, c)",))})

  def test_an_alias_is_checked_like_a_pattern(self):
    arguments = (("x", "source"), ("c", "number"))
    with self.assertRaisesRegex(ValueError, "the pattern of 'and_cst' is not valid"):
      check_patterns({"and_cst": dict(entry("x & c", *arguments), aliases=("and(x, ",))})
    with self.assertRaisesRegex(ValueError, r"the pattern of 'and_cst' must use its arguments \(x, c\)"):
      check_patterns({"and_cst": dict(entry("x & c", *arguments), aliases=("and(x, d)",))})

  def test_an_alias_that_repeats_a_pattern_is_refused(self):
    arguments = (("x", "source"), ("c", "number"))
    table = {"and_cst": entry("x & c", *arguments), "or_cst": dict(entry("x | c", *arguments), aliases=("c & x",))}
    with self.assertRaisesRegex(ValueError, "'or_cst' and 'and_cst' have the same pattern"):
      check_patterns(table)


if __name__ == "__main__":
  unittest.main()
