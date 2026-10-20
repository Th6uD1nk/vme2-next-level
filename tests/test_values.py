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

  def test_a_transfer_of_a_kernel_block_counts_with_a_macro_of_the_file(self):
    text = (
      "#define BATCH 64\nvolatile Buffer arr[64];\n.kernel k direct {\n}\n"
      "void f() {\n  @kernel k config, exec {\n    Int last = BATCH - 1;\n"
      "    Transfer t = { type: words, mode: extended, memory: arr, dims: { count: last, gap: 0 } };\n"
      "    .load { .transfer = t; .scope = global; }\n  }\n}\n"
    )
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("vme_dma(ITERATION, DIMS, 63, 0);", out)


class UnknownMacrosInAKernelTest(unittest.TestCase):
  def test_a_macro_that_is_not_in_the_file_copies_the_whole_chain(self):
    self.assertEqual(agu_count("  Int a = HEADER_N * 2, n = a + 1;"), count_line("((HEADER_N * 2) + 1)"))

  def test_a_known_part_is_replaced_by_its_number_in_a_copy(self):
    self.assertEqual(agu_count("  Int n = N + HEADER;", "#define N 3\n"), count_line("(3 + HEADER)"))

  def test_the_unknown_spreads_along_a_chain(self):
    self.assertEqual(agu_count("  Int a = HEADER, b = a * 2, n = b - a;"), count_line("((HEADER * 2) - HEADER)"))

  def test_a_macro_defined_twice_is_copied(self):
    self.assertEqual(agu_count("  Int n = M + 1;", "#define M 1\n#define M 2\n"), count_line("(M + 1)"))

  def test_a_macro_in_a_condition_is_copied(self):
    self.assertEqual(agu_count("  Int n = M + 1;", "#ifdef Z\n#define M 1\n#endif\n"), count_line("(M + 1)"))

  def test_a_macro_defined_after_the_kernel_is_copied(self):
    self.assertEqual(agu_count("  Int n = M + 1;", "", "#define M 1\n"), count_line("(M + 1)"))


if __name__ == "__main__":
  unittest.main()
