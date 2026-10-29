import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.qformat import buffer_format
from vmeg.scanner import tokens


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


if __name__ == "__main__":
  unittest.main()
