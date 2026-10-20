import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.blocks import find_blocks
from vmegc import render


def agu_count(body, prefix="", suffix=""):
  text = prefix + ".kernel k direct {\n" + body + "\n  Agu t = { count: n };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .top0 + top0; }\n}\n@kernel k config, exec\nvoid f() { }\n" + suffix
  out = render(text, find_blocks(text), "t.vmeg.c")
  line = next(line for line in out.splitlines() if "agu_top(COUNT)" in line)
  return line.strip()


def count_line(value):
  return f"vme_pe0(agu_top(COUNT), VME_DEF_STEP, {value});"


class KnownMacrosInAKernelTest(unittest.TestCase):
  def test_a_chain_of_int_built_from_a_macro_of_the_file_is_a_number(self):
    self.assertEqual(agu_count("  Int a = STEP * 2, n = a + 1;", "#define STEP 4\n"), count_line("9"))

  def test_a_macro_in_a_macro_of_the_file_is_a_number(self):
    self.assertEqual(agu_count("  Int n = COUNT_OF - 1;", "#define BASE 16\n#define COUNT_OF (BASE * 4)\n"), count_line("0x3f"))

  def test_an_int_takes_the_name_of_a_macro_without_an_error(self):
    self.assertEqual(agu_count("  Int n = 7;", "#define n 5\n"), count_line("7"))


if __name__ == "__main__":
  unittest.main()
