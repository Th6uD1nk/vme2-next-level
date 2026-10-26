import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.operations import OPERATIONS
from vmeg.pattern import parse_pattern
from vmeg.selector import candidates


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


if __name__ == "__main__":
  unittest.main()
