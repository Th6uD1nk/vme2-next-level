import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.variants import expand_variants

KERNEL = (
  ".kernel shifted direct\n"
  "{\n"
  "  .with buffer in 0..1, slot in 0..3;\n"
  "  .as row[slot][buffer];\n"
  "  Agu t = { count: 3, offset: slot };\n"
  "  pe[buffer] { .top = t; .spad = top[buffer] | top[buffer]; }\n"
  "}\n"
)


def call(body):
  return KERNEL + "void f(void) { " + body + " }\n"


class VariantsTest(unittest.TestCase):
  def test_a_variant_is_named_with_the_values_of_the_as_and_only_the_called_ones_are_kept(self):
    text = expand_variants(call("@kernel shifted config | exec { .as row[3][1]; } @kernel shifted config | exec { .as row[0][1]; }"))
    self.assertEqual(text.count(".kernel shifted_"), 2)
    self.assertIn(".kernel shifted_3_1 direct", text)
    self.assertIn(".kernel shifted_0_1 direct", text)
    self.assertIn("@kernel shifted_3_1 config", text)
    self.assertIn("offset: 3", text)

  def test_the_with_of_a_call_repeats_the_call_for_each_value(self):
    text = expand_variants(call("@kernel shifted config | exec { .as row[a][0]; .with a in 0..2; }"))
    self.assertEqual(text.count("@kernel shifted_"), 3)
    self.assertEqual(text.count(".kernel shifted_"), 3)

  def test_a_kernel_never_called_is_refused(self):
    with self.assertRaisesRegex(ValueError, "line 1: kernel 'shifted' is never called"):
      expand_variants(call(""))

  def test_a_with_in_a_block_of_the_kernel_is_refused(self):
    text = ".kernel k direct\n{\n  Agu t = { count: 3 };\n  .pe0 { .with a in 0..1; .top = t; .spad = top0 | top0; }\n}\n"
    with self.assertRaisesRegex(ValueError, "line 4: the .with of a kernel is written directly in the kernel"):
      expand_variants(text)

  def test_a_with_that_makes_too_many_copies_is_refused(self):
    with self.assertRaisesRegex(ValueError, "makes 1000 copies, at most 256"):
      expand_variants(call("@kernel shifted config | exec { .as row[0][0]; .with a in 0..9, b in 0..9, c in 0..9; }"))


if __name__ == "__main__":
  unittest.main()
