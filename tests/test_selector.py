import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.operations import OPERATIONS
from vmeg.pattern import parse_pattern
from vmeg.selector import candidates, choose_opcode, select


def kinds(text, operations=OPERATIONS):
  return [kind for kind, _ in candidates(parse_pattern(text), operations)]


def entry(pattern, *arguments):
  return {"pattern": pattern, "arguments": arguments}


OPERANDS = (("a", "operand"), ("b", "operand"))


class CandidatesTest(unittest.TestCase):
  def test_an_expression_finds_the_opcodes_whose_pattern_covers_it(self):
    self.assertEqual(kinds("a + b"), ["add", "add_ofa"])
    self.assertEqual(kinds("a + b + 5"), ["add_ofa", "add_cst"])
    self.assertEqual(kinds("a & b"), ["and"])
    self.assertEqual(kinds("x & 5"), ["and_cst"])

  def test_a_constant_that_is_not_written_is_bound_to_zero(self):
    found = dict(candidates(parse_pattern("a + b")))
    self.assertEqual(found["add_ofa"]["c"], ("num", 0))

  def test_a_pattern_that_would_give_zero_is_a_candidate_only_when_the_zero_is_written(self):
    table = {"mul3": entry("a * b * c", *OPERANDS, ("c", "number"))}
    self.assertEqual(kinds("a * b", table), [])
    self.assertEqual(kinds("a * b * 0", table), ["mul3"])

  def test_an_operand_cannot_be_an_operation_but_a_source_can(self):
    self.assertEqual(kinds("top0 + top1 + top2"), [])
    self.assertIn("not", kinds("~(a + b)"))

  def test_the_candidates_follow_the_order_of_the_table(self):
    table = {"second": entry("a + b", *OPERANDS), "first": entry("a + b", ("b", "operand"), ("a", "operand"))}
    self.assertEqual(kinds("x + y", table), ["second", "first"])


def chosen(text, operations=OPERATIONS):
  found = select(parse_pattern(text), operations)
  return None if found is None else found[0]


class SelectTest(unittest.TestCase):
  def test_the_opcode_that_uses_the_fewest_slots_is_chosen(self):
    self.assertEqual(chosen("a + b"), "add")
    self.assertEqual(chosen("a + b + 5"), "add_ofa")
    self.assertEqual(chosen("a - b"), "sub")
    self.assertEqual(chosen("a - b + 3"), "subacst")

  def test_an_opcode_that_covers_the_whole_need_wins_over_two_that_cover_it_together(self):
    self.assertEqual(chosen("~(a & b)"), "nand")
    self.assertEqual(chosen("~(x & 5)"), "nand_cst")
    self.assertEqual(chosen("~(a ^ 5)"), "xnor_cst")
    self.assertEqual(chosen("~(a + b)"), "not")

  def test_the_cost_adds_the_operations_inside_a_source(self):
    self.assertEqual(select(parse_pattern("~(a & b)"))[2], 2)
    self.assertEqual(select(parse_pattern("~(a + b)"))[2], 3)
    self.assertEqual(select(parse_pattern("clamp(a + b, 0, 255)"))[2], 5)

  def test_nothing_is_chosen_when_a_part_of_the_expression_has_no_opcode(self):
    self.assertIsNone(chosen("~(a * 5)"))
    self.assertIsNone(chosen("top0 + top1 + top2"))
    self.assertIsNone(chosen("a * 5"))

  def test_with_the_same_cost_the_first_of_the_table_is_chosen(self):
    table = {"second": dict(entry("a + b", *OPERANDS), registers={}), "first": dict(entry("a + b", *OPERANDS), registers={})}
    self.assertEqual(chosen("x + y", table), "second")


def chosen_for(text, compat, operations=OPERATIONS):
  found = choose_opcode(parse_pattern(text), compat, operations)
  return None if found is None else found[0]


class ChooseOpcodeTest(unittest.TestCase):
  def test_the_default_keeps_every_opcode(self):
    self.assertEqual(chosen_for("a + b", None), "add")

  def test_the_fat_leaves_out_the_opcodes_that_do_not_work_on_it(self):
    self.assertEqual(chosen_for("a + b", "fat"), "add_ofa")
    self.assertEqual(chosen_for("a - b", "fat"), "sub")

  def test_the_fat_applies_to_the_operations_inside_a_source_too(self):
    self.assertEqual(select(parse_pattern("~(a + b)"), OPERATIONS)[2], 3)
    self.assertEqual(choose_opcode(parse_pattern("~(a + b)"), "fat")[2], 4)

  def test_an_opcode_with_no_replacement_on_the_fat_is_an_error(self):
    table = {"only": dict(entry("a + b", *OPERANDS), registers={}, not_portable=True)}
    self.assertEqual(chosen_for("x + y", None, table), "only")
    with self.assertRaisesRegex(ValueError, "only does not work on the fat and nothing replaces it"):
      chosen_for("x + y", "fat", table)

  def test_an_expression_without_opcode_stays_without_opcode_on_the_fat(self):
    self.assertIsNone(chosen_for("a * 5", "fat"))


class AliasTest(unittest.TestCase):
  def test_a_function_writing_finds_the_opcode_of_its_alias(self):
    self.assertEqual(chosen("and(x, 5)"), "and_cst")
    self.assertEqual(chosen("subacst(a, b, 3)"), "subacst")
    self.assertEqual(chosen("subshr(a, b, 2)"), "subshr")

  def test_the_two_writings_of_an_opcode_find_the_same_one(self):
    self.assertEqual(chosen("x & 5"), chosen("and(x, 5)"))
    self.assertEqual(chosen("~(x | 5)"), chosen("~or(x, 5)"))
    self.assertEqual(chosen("~(x ^ 5)"), chosen("~xor(x, 5)"))

  def test_the_alias_written_exactly_wins_over_a_looser_reading_of_the_pattern(self):
    self.assertEqual(chosen("~or(x, 5)"), "nor_cst")
    self.assertEqual(chosen("~xor(top0, 1)"), "xnor_cst")

  def test_a_function_writing_with_an_operand_instead_of_a_number_has_no_opcode(self):
    self.assertIsNone(chosen("and(a, b)"))


class WrapperTest(unittest.TestCase):
  def test_a_sat_or_a_shift_around_a_source_does_not_change_the_cost(self):
    plain = select(parse_pattern("~(a & b)"))
    self.assertEqual(plain[0], "nand")
    for text in ["~sat(a & b, 8)", "~((a & b) >> 2)", "~((a & b) << 3)"]:
      self.assertEqual(chosen(text), "not", text)
      self.assertEqual(select(parse_pattern(text))[2], 3, text)

  def test_a_sat_that_wraps_no_operation_has_no_opcode(self):
    self.assertIsNone(chosen("~sat(top0, 8)"))


if __name__ == "__main__":
  unittest.main()
