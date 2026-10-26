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


if __name__ == "__main__":
  unittest.main()
