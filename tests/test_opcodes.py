import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from test_values import kernel_lines


def used(body, compat=None):
  lines = kernel_lines(body, compat)
  code = re.search(r"(fu_code\(\w+\)|VME_FU_OPCODE_\w+)", lines[0]).group(1)
  registers = re.findall(r"fu_reg\(PRIMARY, (\w)\), (\w+)\)", " ".join(lines[1:]))
  return code, registers


WRITTEN = [
  (".top0 + base0;", None, "fu_code(OP_ADD)", []),
  (".top1 + top2;", None, "fu_code(OP_ADD)", []),
  (".top0 + base0;", "fat", "fu_code(OP_ADD_OFA)", [("A", "0")]),
  (".top0 + base0 + 5;", None, "fu_code(OP_ADD_OFA)", [("A", "5")]),
  (".top0 + base0 + 5;", "fat", "fu_code(OP_ADD_OFA)", [("A", "5")]),
  (".top0 - base0;", None, "fu_code(OP_SUB)", []),
  (".top1 - top0;", "fat", "fu_code(OP_SUB)", []),
  (".top0 * base0;", None, "VME_FU_OPCODE_MUL_RSHIFT_0", []),
  (".top0 & base0;", None, "fu_code(OP_AND)", []),
  (".top1 & 255;", None, "fu_code(OP_AND_CST)", [("B", "0xff")]),
  (".top0 | base0;", None, "fu_code(OP_OR)", []),
  (".top1 | 15;", None, "fu_code(OP_OR_CST)", [("B", "0xf")]),
  (".top0 ^ base0;", None, "fu_code(OP_XOR)", []),
  (".top1 ^ 1;", None, "fu_code(OP_XOR_CST)", [("B", "1")]),
]


class WrittenExpressionTest(unittest.TestCase):
  def test_each_written_expression_falls_on_the_expected_opcode(self):
    for body, compat, code, registers in WRITTEN:
      with self.subTest(body=body, compat=compat):
        self.assertEqual(used(body, compat), (code, registers))

  def test_the_constant_can_be_written_before_the_operand(self):
    self.assertEqual(used(". 255 & top1;"), ("fu_code(OP_AND_CST)", [("B", "0xff")]))
    self.assertEqual(used(". 5 + (top0 + base0);"), ("fu_code(OP_ADD_OFA)", [("A", "5")]))

  def test_an_expression_that_no_opcode_covers_is_refused(self):
    for body in [".top0 + 5;", ".top0 + base0 + top1;", ". 5 + top0 + base0;"]:
      with self.subTest(body=body):
        with self.assertRaisesRegex(ValueError, "an operand must be a buffer"):
          used(body)


def codes(body, compat=None):
  return re.findall(r"fu_code\((OP_\w+)\)", " ".join(kernel_lines(body, compat)))


class ComplementTest(unittest.TestCase):
  def test_a_complement_that_the_hardware_fuses_is_one_operation(self):
    rows = [
      (".~(top0 & base0);", ["OP_NAD"]),
      (".~(top0 | base0);", ["OP_NOR"]),
      (".~(top0 & 255);", ["OP_NAD_CST"]),
      (".~(top0 | 15);", ["OP_NOR_CST"]),
      (".~(top0 ^ 1);", ["OP_XOR_CST_NOT"]),
      (".~and(top0, 255);", ["OP_NAD_CST"]),
      (".~or(top0, 15);", ["OP_NOR_CST"]),
      (".~xor(top0, 1);", ["OP_XOR_CST_NOT"]),
    ]
    for body, expected in rows:
      with self.subTest(body=body):
        self.assertEqual(codes(body), expected)

  def test_a_complement_of_an_operation_that_is_not_fused_is_two_operations(self):
    self.assertEqual(codes(".~top0;"), ["OP_NOT"])
    self.assertEqual(codes(".~(top0 + base0);"), ["OP_ADD", "OP_NOT"])
    self.assertEqual(codes(".~(top0 + base0);", "fat"), ["OP_ADD_OFA", "OP_NOT"])
    self.assertEqual(codes(".~(top0 - base0);"), ["OP_SUB", "OP_NOT"])

  def test_a_sat_or_a_shift_in_the_complement_keeps_it_apart_from_the_operation(self):
    self.assertEqual(codes(".~sat(top0 & base0, 8);"), ["OP_AND", "OP_NOT"])
    self.assertEqual(codes(".~((top0 & base0) >> 2);"), ["OP_AND", "OP_NOT"])


if __name__ == "__main__":
  unittest.main()
