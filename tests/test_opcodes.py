import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from test_values import kernel_lines
from vmeg.blocks import find_blocks
from vmeg.kernel import generate


def used(body, compat=None):
  lines = kernel_lines(body, compat)
  code = re.search(r"(fu_code\(\w+\)|VME_FU_OPCODE_\w+)", lines[0]).group(1)
  registers = re.findall(r"fu_reg\(PRIMARY, (\w)\), (\w+)\)", " ".join(lines[1:]))
  return code, registers


WRITTEN = [
  (".spad = top0 + base0;", None, "fu_code(OP_ADD)", []),
  (".spad = top1 + top2;", None, "fu_code(OP_ADD)", []),
  (".spad = top0 + base0;", "fat", "fu_code(OP_ADD_OFA)", [("A", "0")]),
  (".spad = top0 + base0 + 5;", None, "fu_code(OP_ADD_OFA)", [("A", "5")]),
  (".spad = top1 - base1 + 3;", None, "fu_code(OP_SUB_OFB)", [("B", "3")]),
  (".spad = top1 + 1;", None, "fu_code(OP_ADD_CST)", [("B", "1")]),
  (".spad = top1 + 1;", "fat", "fu_code(OP_ADD_CST)", [("B", "1")]),
  (".spad = top0 + base0 + 5;", "fat", "fu_code(OP_ADD_OFA)", [("A", "5")]),
  (".spad = top0 - base0;", None, "fu_code(OP_SUB)", []),
  (".spad = top1 - top0;", "fat", "fu_code(OP_SUB)", []),
  (".spad = top0 * base0;", None, "VME_FU_OPCODE_MUL_RSHIFT_0", []),
  (".spad = top0 & base0;", None, "fu_code(OP_AND)", []),
  (".spad = top1 & 255;", None, "fu_code(OP_AND_CST)", [("B", "0xff")]),
  (".spad = top0 | base0;", None, "fu_code(OP_OR)", []),
  (".spad = top1 | 15;", None, "fu_code(OP_OR_CST)", [("B", "0xf")]),
  (".spad = top0 ^ base0;", None, "fu_code(OP_XOR)", []),
  (".spad = top1 ^ 1;", None, "fu_code(OP_XOR_CST)", [("B", "1")]),
]


class WrittenExpressionTest(unittest.TestCase):
  def test_each_written_expression_falls_on_the_expected_opcode(self):
    for body, compat, code, registers in WRITTEN:
      with self.subTest(body=body, compat=compat):
        self.assertEqual(used(body, compat), (code, registers))

  def test_the_constant_can_be_written_before_the_operand(self):
    self.assertEqual(used(".spad = 255 & top1;"), ("fu_code(OP_AND_CST)", [("B", "0xff")]))
    self.assertEqual(used(".spad = 1 + top1;"), ("fu_code(OP_ADD_CST)", [("B", "1")]))
    self.assertEqual(used(".spad = 5 + (top0 + base0);"), ("fu_code(OP_ADD_OFA)", [("A", "5")]))

  def test_an_expression_that_no_opcode_covers_is_refused(self):
    for body in [".spad = top0 * 5;", ".spad = top0 + base0 + top1;", ".spad = 5 + top0 + base0;"]:
      with self.subTest(body=body):
        with self.assertRaisesRegex(ValueError, "no opcode covers this expression"):
          used(body)


def codes(body, compat=None):
  return re.findall(r"fu_code\((OP_\w+)\)", " ".join(kernel_lines(body, compat)))


class ComplementTest(unittest.TestCase):
  def test_a_complement_that_the_hardware_fuses_is_one_operation(self):
    rows = [
      (".spad = ~(top0 & base0);", ["OP_NAD"]),
      (".spad = ~(top0 | base0);", ["OP_NOR"]),
      (".spad = ~(top0 & 255);", ["OP_NAD_CST"]),
      (".spad = ~(top0 | 15);", ["OP_NOR_CST"]),
      (".spad = ~(top0 ^ 1);", ["OP_XOR_CST_NOT"]),
      (".spad = ~and(top0, 255);", ["OP_NAD_CST"]),
      (".spad = ~or(top0, 15);", ["OP_NOR_CST"]),
      (".spad = ~xor(top0, 1);", ["OP_XOR_CST_NOT"]),
    ]
    for body, expected in rows:
      with self.subTest(body=body):
        self.assertEqual(codes(body), expected)

  def test_a_complement_of_an_operation_that_is_not_fused_is_two_operations(self):
    self.assertEqual(codes(".spad = ~top0;"), ["OP_NOT"])
    self.assertEqual(codes(".spad = ~(top0 + base0);"), ["OP_ADD", "OP_NOT"])
    self.assertEqual(codes(".spad = ~(top0 + base0);", "fat"), ["OP_ADD_OFA", "OP_NOT"])
    self.assertEqual(codes(".spad = ~(top0 - base0);"), ["OP_SUB", "OP_NOT"])
    self.assertEqual(codes(".spad = ~(top0 + 1);"), ["OP_ADD_CST", "OP_NOT"])

  def test_a_sat_or_a_shift_in_the_complement_keeps_it_apart_from_the_operation(self):
    self.assertEqual(codes(".spad = ~sat(top0 & base0, 8);"), ["OP_AND", "OP_NOT"])
    self.assertEqual(codes(".spad = ~((top0 & base0) >> 2);"), ["OP_AND", "OP_NOT"])

  def test_a_fused_complement_can_read_an_operation(self):
    self.assertEqual(codes(".spad = ~and(top0 + base0, 255);"), ["OP_ADD", "OP_NAD_CST"])

  def test_a_complement_of_what_no_opcode_covers_is_refused(self):
    with self.assertRaisesRegex(ValueError, "no opcode covers this expression"):
      codes(".spad = ~(top0 * 5);")
    with self.assertRaisesRegex(ValueError, "sat must wrap an operation"):
      codes(".spad = ~sat(top0, 8);")


class ShiftTest(unittest.TestCase):
  def test_a_shift_inside_a_pattern_finds_its_opcode_like_the_function_writing(self):
    expected = ("fu_code(OP_SUB_INV_SHF)", [("B", "2")])
    self.assertEqual(used(".spad = top1 - (top0 >> 2);"), expected)
    self.assertEqual(used(".spad = subshr(top0, top1, 2);"), expected)

  def test_a_shift_around_an_operation_is_written_in_the_shift_of_the_opcode(self):
    self.assertEqual(kernel_lines(".spad = (top1 - top0) >> 2;", None), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_1, TOP_0), fu_code(OP_SUB), 2);"])
    self.assertEqual(kernel_lines(".spad = top1 - top0 >> 2;", None), kernel_lines(".spad = (top1 - top0) >> 2;", None))
    lines = kernel_lines(".spad = (top1 - (top0 >> 2)) >> 1;", None)
    self.assertEqual(lines[0], "vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, TOP_1), fu_code(OP_SUB_INV_SHF), 1);")

  def test_the_error_of_a_shift_inside_a_pattern_names_the_opcode(self):
    for body in [".spad = top1 - (top0 >> -1);", ".spad = subshr(top0, top1, -1);"]:
      with self.subTest(body=body):
        with self.assertRaisesRegex(ValueError, "subshr n cannot be less than 0"):
          used(body)


class NestedTest(unittest.TestCase):
  def test_an_operation_inside_a_clamp_is_chosen_like_alone(self):
    rows = [
      (".spad = clamp(top0 + base0 + 5, 0, 255);", ["OP_ADD_OFA", "OP_CLP"]),
      (".spad = clamp(top0 & 255, 0, 9);", ["OP_AND_CST", "OP_CLP"]),
      (".spad = clamp(top1 - (top0 >> 2), 0, 255);", ["OP_SUB_INV_SHF", "OP_CLP"]),
      (".spad = clamp(~(top0 & base0), 0, 9);", ["OP_NAD", "OP_CLP"]),
      (".spad = clamp(top0 + 1, 0, 9);", ["OP_ADD_CST", "OP_CLP"]),
    ]
    for body, expected in rows:
      for compat in (None, "fat"):
        with self.subTest(body=body, compat=compat):
          self.assertEqual(codes(body, compat), expected)

  def test_an_operation_kept_in_a_staging_variable_is_chosen_like_alone(self):
    rows = [
      ("Staging s; s = top0 + base0 + 5; .spad = s & 255;", ["OP_ADD_OFA", "OP_AND_CST"]),
      ("Staging s; s = top1 - (top0 >> 2); .spad = ~s;", ["OP_SUB_INV_SHF", "OP_NOT"]),
      ("Staging s; s = top0 & 255; .spad = s + base0 + 3;", ["OP_AND_CST", "OP_ADD_OFA"]),
    ]
    for body, expected in rows:
      with self.subTest(body=body):
        self.assertEqual(codes(body), expected)

  def test_an_operand_that_is_an_operation_is_still_refused_inside_a_clamp(self):
    with self.assertRaisesRegex(ValueError, "no opcode covers this expression"):
      codes(".spad = clamp(top0 + top1 + top2, 0, 9);")


class AfterAnOperationTest(unittest.TestCase):
  def test_a_number_added_to_a_product_is_a_second_operation(self):
    lines = kernel_lines(".spad = (top0 * base0) + 1;", None)
    self.assertEqual(lines, [
      "vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), VME_FU_OPCODE_MUL_RSHIFT_0);",
      "vme_pe0(vme_fu(SECONDARY), vme_mux(NONE, STAGING_0), fu_code(OP_ADD_CST));",
      "vme_pe0(fu_reg(SECONDARY, B), 1);",
    ])

class StagingInTheKernelTest(unittest.TestCase):
  def test_a_staging_variable_declared_in_the_kernel_is_used_by_a_pe(self):
    text = ".kernel k direct {\n  Staging s;\n  .pe0 { s = top0 + base0; .spad = s & 255; }\n}\n@kernel k config | exec\nvoid f() { }\n"
    code = generate(text, find_blocks(text)[0], [], None)
    self.assertEqual(re.findall(r"fu_code\((OP_\w+)\)", code), ["OP_ADD", "OP_AND_CST"])


class RemapTest(unittest.TestCase):
  def test_a_remap_gives_the_opcode_and_the_registers_of_its_unit(self):
    self.assertEqual(kernel_lines(".remap = { operator: \"*\", primary: 0x220 }; .spad = top0 * base0;", None), [
      "vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), VME_FU_OPCODE_MUL_VEC_RSHIFT);",
    ])
    self.assertEqual(kernel_lines(".spad = top0 * base0; .remap = { operator: \"*\", primary: 0x220 };", None), [
      "vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), VME_FU_OPCODE_MUL_VEC_RSHIFT);",
    ])
    self.assertEqual(kernel_lines(".remap = { operator: \"+\", primary: 0x030 }; .spad = top0 + base0;", None), [
      "vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_ADD_OFA));",
      "vme_pe0(fu_reg(PRIMARY, A), 0);",
    ])
    self.assertEqual(kernel_lines("Staging s; s = top0 + base0; .remap = { operator: \"*\", secondary: 0x220 }; .spad = s * top1;", None), [
      "vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_ADD));",
      "vme_pe0(vme_fu(SECONDARY), vme_mux(STAGING_0, TOP_1), VME_FU_OPCODE_MUL_VEC_RSHIFT);",
    ])

  def test_a_remap_warns_for_a_value_without_register_and_refuses_an_opcode_without_the_operator(self):
    def warnings_of(body):
      text = ".kernel k direct {\n  .pe0 { " + body + " }\n}\n@kernel k config | exec\nvoid f() { }\n"
      found = []
      generate(text, find_blocks(text)[0], found, None)
      return [message for _, message in found if "remap" in message]
    self.assertEqual(warnings_of(".remap = { operator: \"+\", primary: 0x010 }; .spad = top0 + base0 + 5;"), [
      "the value of 'c' is not written, the opcode 0x010 of .remap primary has no register for it",
    ])
    self.assertEqual(warnings_of(".remap = { operator: \"+\", primary: 0x030 }; .spad = top0 + base0;"), [])
    with self.assertRaisesRegex(ValueError, "the opcode 0x220 of .remap primary has no operator '\\+'"):
      kernel_lines(".remap = { operator: \"+\", primary: 0x220 }; .spad = top0 + base0;", None)
    with self.assertRaisesRegex(ValueError, "the opcode 0x999 of .remap primary is not in the table"):
      kernel_lines(".remap = { operator: \"+\", primary: 0x999 }; .spad = top0 + base0;", None)


if __name__ == "__main__":
  unittest.main()
