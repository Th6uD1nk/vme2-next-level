import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmee.extract import host_source
from vmeg.blocks import find_blocks
from vmeg.qformat import buffer_format, to_q, translate_buffer
from vmeg.registry import array_definitions, extern_declaration
from vmeg.scanner import tokens
from vmegc import render


def read(text):
  toks = list(tokens(text))
  return buffer_format(toks, next(i for i, token in enumerate(toks) if token[1] == "Buffer"))


class BufferFormatTest(unittest.TestCase):
  def test_a_buffer_has_no_format_or_a_qm_n_that_fits_the_24_bits(self):
    self.assertEqual(read("volatile Buffer x[4];"), (None, 2))
    self.assertEqual(read("volatile Buffer(Q8.8) x[4];"), ((8, 8), 7))
    self.assertEqual(read("volatile Buffer(Q1.23) x[4];")[0], (1, 23))
    self.assertEqual(read("volatile Buffer(Q12.12) x[4];")[0], (12, 12))

  def test_a_form_other_than_qm_n_an_integer_part_under_1_and_more_than_24_bits_are_refused(self):
    for form in ("Foo", "Q8", "Q8.", "Q0.8", "Q20.10", "Q1.24"):
      with self.assertRaises(ValueError):
        read(f"volatile Buffer({form}) x;")


class ValueTest(unittest.TestCase):
  def test_a_decimal_is_truncated_toward_zero_and_written_on_32_bits_with_the_sign_and_the_rest_is_left_alone(self):
    self.assertEqual(to_q("0.5", 8, 8), "0x00000080")
    self.assertEqual(to_q("-0.5", 8, 8), "0xffffff80")
    self.assertEqual(to_q("0.866028f", 8, 8), "0x000000dd")
    self.assertEqual(to_q("-1.25f", 8, 8), "0xfffffec0")
    self.assertEqual(to_q("3", 8, 8), "0x00000300")
    self.assertEqual(to_q("-50.0", 8, 8), "0xffffce00")
    for text in ("0x1234", "N", "F2Q(1)"):
      self.assertIsNone(to_q(text, 8, 8))

  def test_a_value_outside_the_range_of_the_format_is_refused_and_the_edges_are_accepted(self):
    self.assertEqual(to_q("-128", 8, 8), "0xffff8000")
    self.assertEqual(to_q("127.999", 8, 8), "0x00007fff")
    for text, integer, fraction in (("128", 8, 8), ("-128.1", 8, 8), ("1.0", 1, 15)):
      with self.assertRaises(ValueError):
        to_q(text, integer, fraction)


class DeclarationTest(unittest.TestCase):
  def test_a_declaration_loses_its_format_and_only_its_numbers_are_converted(self):
    self.assertEqual(translate_buffer("volatile Buffer x[2] = { -1, 2 };", "T"), "volatile T x[2] = { -1, 2 };")
    self.assertEqual(translate_buffer("volatile Buffer(Q8.8) m[4] = { 0.5, -1.25f, 3, 0x10 };", "T"), "volatile T m[4] = { 0x00000080, 0xfffffec0, 0x00000300, 0x10 };")
    self.assertEqual(translate_buffer("static volatile Buffer(Q1.15) a[1] = { 0.25 }, b[1] = { - 0.5 };", "T"), "static volatile T a[1] = { 0x00002000 }, b[1] = { 0xffffc000 };")
    self.assertEqual(translate_buffer("volatile Buffer(Q8.8) g[2][1] = { { 1.0 }, { 0.5 } };", "T"), "volatile T g[2][1] = { { 0x00000100 }, { 0x00000080 } };")
    self.assertEqual(translate_buffer("volatile Buffer(Q8.8) f[3] = { F2Q(1), FOO(a, 2, b), N };", "T"), "volatile T f[3] = { F2Q(1), FOO(a, 2, b), N };")


HOST = (
  "volatile Buffer(Q8.8) input[2] = { 0.5, -1.25f };\n"
  "@emulate \"double\"\n.kernel k direct {\n  Transfer t = { memory: input, count: 1 };\n"
  "  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n}\n"
  "@kernel k config | exec\nvoid run(void) {\n}\n"
)


class FileTest(unittest.TestCase):
  def test_the_translation_of_a_file_accepts_a_format_and_gives_the_line_of_a_wrong_one(self):
    out = render(HOST, find_blocks(HOST), "t.vmeg.c")
    self.assertIn("input[2] = { 0x00000080, 0xfffffec0 };", out)
    wrong = "volatile Buffer a[4];\nvolatile Buffer(Q20.10) b[4];\n"
    with self.assertRaisesRegex(ValueError, "line 2"):
      render(wrong, find_blocks(wrong), "t.vmeg.c")

  def test_the_extern_written_for_another_file_has_no_format_and_no_value(self):
    definition = array_definitions("a.vmeg.c", "volatile Buffer(Q8.8) shared[4] = { 0.5, -1 };\n")[0]
    self.assertEqual(extern_declaration(definition), "extern volatile Buffer shared[4];")

  def test_the_host_program_of_the_emulator_has_the_converted_values(self):
    out = host_source(HOST, "double")
    self.assertIn("{ 0x00000080, 0xfffffec0 }", out)
    self.assertNotIn("Q8.8", out)


if __name__ == "__main__":
  unittest.main()
