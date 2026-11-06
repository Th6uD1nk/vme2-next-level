import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.expr import value
from vmeg.parser import Parser, parse_expr
from vmeg.scanner import tokens


def evaluate(text, env):
  toks = list(tokens(text))
  return value(parse_expr(Parser(text, toks, len(text))), env)


def chain(rows):
  env = {}
  for name, text in rows:
    env[name] = evaluate(text, env)
  return env


class KnownValueTest(unittest.TestCase):
  def test_the_division_and_the_modulo_follow_c(self):
    self.assertEqual([evaluate(text, {})[1] for text in ("7 / 2", "-7 / 2", "7 % 3", "-7 % 3", "7 % -3")], [3, -3, 1, -1, 1])
    with self.assertRaises(ValueError):
      evaluate("1 / 0", {})

  def test_a_calculation_of_numbers_gives_a_number(self):
    results = [evaluate(text, {}) for text in ["2", "3 + 2 * 4", "(1 << 4) & 0xff", "0 - 3"]]
    self.assertEqual(results, [("num", 2), ("num", 11), ("num", 16), ("num", -3)])

  def test_and_binds_over_xor_over_or_below_the_shifts_and_the_complement_binds_first(self):
    results = [evaluate(text, {}) for text in ["1 | 6 & 3", "5 ^ 3 & 1", "1 | 4 ^ 5", "1 << 2 | 1", "~5 & 0xff"]]
    self.assertEqual(results, [("num", 3), ("num", 4), ("num", 1), ("num", 5), ("num", 250)])

  def test_the_comparisons_give_1_or_0_and_bind_as_in_c(self):
    results = [evaluate(text, {}) for text in ["3 == 3", "3 != 3", "1 + 1 == 2", "4 & 2 == 2", "(4 & 6) == 4", "-1 == 0xffffff"]]
    self.assertEqual(results, [("num", 1), ("num", 0), ("num", 1), ("num", 0), ("num", 1), ("num", 0)])

  def test_the_logical_shift_works_on_the_24_bits_without_the_sign(self):
    results = [evaluate(text, {}) for text in ["0x800000 >>> 3", "-1 >>> 20", "0x10 >>> 2 + 1", "1 << 2 >>> 1", "0x10 >>> -2", "-1 <<< 4", "0x100 <<< -4"]]
    self.assertEqual(results, [("num", 1048576), ("num", 15), ("num", 2), ("num", 2), ("num", 64), ("num", 0xfffff0), ("num", 16)])

  def test_the_ternary_picks_its_branch_and_nests_to_the_right(self):
    results = [evaluate(text, {}) for text in ["1 ? 2 : 3", "0 ? 2 : 3", "0 ? 1 : 0 ? 4 : 5", "(3 & 4) ? 7 : 8", "1 + 1 ? 2 : 3"]]
    self.assertEqual(results, [("num", 2), ("num", 3), ("num", 5), ("num", 8), ("num", 2)])

  def test_a_chain_of_assignments_is_evaluated_from_the_previous_ones(self):
    env = chain([("a", "2"), ("b", "a * 3"), ("c", "b + a"), ("d", "(c - a) * b")])
    self.assertEqual(env, {"a": ("num", 2), "b": ("num", 6), "c": ("num", 8), "d": ("num", 36)})


class UnknownValueTest(unittest.TestCase):
  def test_an_unknown_name_alone_stays_a_name(self):
    self.assertEqual(evaluate("X", {}), ("name", "X"))

  def test_one_unknown_part_copies_the_whole_expression_between_parentheses(self):
    self.assertEqual(evaluate("(1 + VECTOR_COUNT) * 16 - 1", {}), ("name", "(((1 + VECTOR_COUNT) * 16) - 1)"))

  def test_a_name_of_the_language_is_replaced_by_its_value_in_a_copy(self):
    env = chain([("k", "3")])
    self.assertEqual(evaluate("M + k", env), ("name", "(M + 3)"))

  def test_the_unknown_spreads_along_a_chain_and_never_becomes_a_number_again(self):
    env = chain([("lost", "12"), ("m", "(1 + VECTOR_COUNT) * 16 - 1"), ("w", "m + lost"), ("z", "w - w")])
    self.assertEqual(env["w"], ("name", "((((1 + VECTOR_COUNT) * 16) - 1) + 12)"))
    self.assertEqual(env["z"], ("name", "(((((1 + VECTOR_COUNT) * 16) - 1) + 12) - ((((1 + VECTOR_COUNT) * 16) - 1) + 12))"))


if __name__ == "__main__":
  unittest.main()
