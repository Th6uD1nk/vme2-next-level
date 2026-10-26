import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.blocks import find_blocks
from vmeg.kernel import build_kernel
from vmeg.listing import kernel_operation_lines


def values(line):
  return re.search(r"\w+ = .*$", line).group(0)


def listing(body, compat=None):
  text = ".kernel k direct {\n" + body + "\n}\n@kernel k config | exec\nvoid f() { }\n"
  _, _, _, state = build_kernel(text, find_blocks(text)[0], compat)
  return kernel_operation_lines(state)


class ColumnsTest(unittest.TestCase):
  def test_a_line_gives_the_pe_the_line_of_the_file_the_opcode_and_its_pattern(self):
    lines = listing("  .pe0 { .top0 + base0 + 5; }")
    self.assertEqual(len(lines), 1)
    self.assertTrue(lines[0].startswith("  pe0  line 2  0x030  a + b + c  "))

  def test_the_operations_are_listed_in_the_order_they_are_placed(self):
    lines = listing("  .pe0 { .top0 - base0; }\n  .pe1 { .top1 & base1; }")
    self.assertEqual([line.split()[0:2] for line in lines], [["pe0", "line"], ["pe1", "line"]])
    self.assertTrue(lines[0].startswith("  pe0  line 2  0x018  a - b"))
    self.assertTrue(lines[1].startswith("  pe1  line 3  0x0c0  a & b"))


class BoundValuesTest(unittest.TestCase):
  def test_the_operands_and_the_numbers_are_shown_with_the_names_of_the_pattern(self):
    lines = listing("  .pe0 { .top0 + base0 + 5; }\n  .pe1 { .top1 & 255; }\n  .pe2 { .base2 - (top2 >> 2); }")
    self.assertEqual([values(line) for line in lines], [
      "a = top0, b = base0, c = 5",
      "x = top1, c = 255",
      "a = top2, b = base2, n = 2",
    ])

  def test_the_result_of_another_operation_is_shown_as_a_staging(self):
    lines = listing("  Staging s;\n  .pe0 { s = top0 + 1; .~s; }\n  .pe1 { .clamp(top1 + base1, 0, 9); }")
    self.assertEqual([values(line) for line in lines], [
      "x = top0, c = 1",
      "x = staging0",
      "a = top1, b = base1",
      "x = staging1, low = 0, high = 9",
    ])


if __name__ == "__main__":
  unittest.main()
