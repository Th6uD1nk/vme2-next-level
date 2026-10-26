import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.operations import OPERATIONS
from vmeg.pattern import parse_pattern
from vmeg.selector import candidates, select


def kinds(text, operations=OPERATIONS):
  return [kind for kind, _ in candidates(parse_pattern(text), operations)]


def entry(pattern, *arguments):
  return {"pattern": pattern, "arguments": arguments}


OPERANDS = (("a", "operand"), ("b", "operand"))


class CandidatesTest(unittest.TestCase):
  def test_an_expression_finds_the_opcodes_whose_pattern_covers_it(self):
    self.assertEqual(kinds("a + b"), ["add", "add_ofa"])
    self.assertEqual(kinds("a + b + 5"), ["add_ofa"])
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
    self.assertIsNone(chosen("~(a + 5)"))
    self.assertIsNone(chosen("top0 + top1 + top2"))
    self.assertIsNone(chosen("5 + a"))

  def test_with_the_same_cost_the_first_of_the_table_is_chosen(self):
    table = {"second": dict(entry("a + b", *OPERANDS), registers={}), "first": dict(entry("a + b", *OPERANDS), registers={})}
    self.assertEqual(chosen("x + y", table), "second")


if __name__ == "__main__":
  unittest.main()
