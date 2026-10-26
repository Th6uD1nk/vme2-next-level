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
    for body in [".top0 * 5;", ".top0 + base0 + top1;", ". 5 + top0 + base0;"]:
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

  def test_a_fused_complement_can_read_an_operation(self):
    self.assertEqual(codes(".~and(top0 + base0, 255);"), ["OP_ADD", "OP_NAD_CST"])

  def test_a_complement_of_what_no_opcode_covers_is_refused(self):
    with self.assertRaisesRegex(ValueError, "an operand must be a buffer"):
      codes(".~(top0 * 5);")
    with self.assertRaisesRegex(ValueError, "sat must wrap an operation"):
      codes(".~sat(top0, 8);")


class ShiftTest(unittest.TestCase):
  def test_a_shift_inside_a_pattern_finds_its_opcode_like_the_function_writing(self):
    expected = ("fu_code(OP_SUB_INV_SHF)", [("B", "2")])
    self.assertEqual(used(".top1 - (top0 >> 2);"), expected)
    self.assertEqual(used(".subshr(top0, top1, 2);"), expected)

  def test_a_shift_around_an_operation_is_written_in_the_shift_of_the_opcode(self):
    self.assertEqual(kernel_lines(".(top1 - top0) >> 2;", None), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_1, TOP_0), fu_code(OP_SUB), 2);"])
    self.assertEqual(kernel_lines(".top1 - top0 >> 2;", None), kernel_lines(".(top1 - top0) >> 2;", None))
    lines = kernel_lines(".(top1 - (top0 >> 2)) >> 1;", None)
    self.assertEqual(lines[0], "vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, TOP_1), fu_code(OP_SUB_INV_SHF), 1);")

  def test_the_error_of_a_shift_inside_a_pattern_names_the_opcode(self):
    for body in [".top1 - (top0 >> -1);", ".subshr(top0, top1, -1);"]:
      with self.subTest(body=body):
        with self.assertRaisesRegex(ValueError, "subshr n cannot be less than 0"):
          used(body)


class NestedTest(unittest.TestCase):
  def test_an_operation_inside_a_clamp_is_chosen_like_alone(self):
    rows = [
      (".clamp(top0 + base0 + 5, 0, 255);", ["OP_ADD_OFA", "OP_CLP"]),
      (".clamp(top0 & 255, 0, 9);", ["OP_AND_CST", "OP_CLP"]),
      (".clamp(top1 - (top0 >> 2), 0, 255);", ["OP_SUB_INV_SHF", "OP_CLP"]),
      (".clamp(~(top0 & base0), 0, 9);", ["OP_NAD", "OP_CLP"]),
    ]
    for body, expected in rows:
      for compat in (None, "fat"):
        with self.subTest(body=body, compat=compat):
          self.assertEqual(codes(body, compat), expected)

  def test_an_operation_kept_in_a_staging_variable_is_chosen_like_alone(self):
    rows = [
      ("Staging s; s = top0 + base0 + 5; .s & 255;", ["OP_ADD_OFA", "OP_AND_CST"]),
      ("Staging s; s = top1 - (top0 >> 2); .~s;", ["OP_SUB_INV_SHF", "OP_NOT"]),
      ("Staging s; s = top0 & 255; .s + base0 + 3;", ["OP_AND_CST", "OP_ADD_OFA"]),
    ]
    for body, expected in rows:
      with self.subTest(body=body):
        self.assertEqual(codes(body), expected)

  def test_an_operand_that_is_an_operation_is_still_refused_inside_a_clamp(self):
    with self.assertRaisesRegex(ValueError, "an operand must be a buffer"):
      codes(".clamp(top0 + top1 + top2, 0, 9);")


if __name__ == "__main__":
  unittest.main()
