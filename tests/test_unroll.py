import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.unroll import unroll_loops


def squeezed(text):
  return " ".join("\n".join(line for line in text.replace("\r", "").split("\n") if not line.startswith("#line")).split())


def around(block):
  return "void f(void) {\n  @emulate \"a\" {\n" + block + "\n  }\n}\nint after;\n"



class UnrollTest(unittest.TestCase):
  def test_a_loop_is_the_copies_of_its_body_with_the_variable_replaced_and_the_lines_kept(self):
    out = unroll_loops(around("    for s in 1..3 {\n      @kernel k config | exec { .params = { n: 8 >> s }; }\n    }"))
    self.assertEqual(squeezed(out), squeezed(around("    @kernel k config | exec { .params = { n: 8 >> 1 }; } @kernel k config | exec { .params = { n: 8 >> 2 }; } @kernel k config | exec { .params = { n: 8 >> 3 }; }")))
    self.assertEqual(out.split("\n").index("int after;"), around("    for s in 1..3 {\n      @kernel k config | exec { .params = { n: 8 >> s }; }\n    }").split("\n").index("int after;"))

  def test_loops_inside_loops_are_unrolled_in_order(self):
    out = unroll_loops(around("    for a in 0..1 { for b in 5..6 { @kernel k config | exec { .params = { x: a * 10 + b }; } } }"))
    self.assertEqual(squeezed(out).count("@kernel k"), 4)
    self.assertEqual([word for word in squeezed(out).split() if word in ("0", "1", "5", "6")], ["0", "5", "0", "6", "1", "5", "1", "6"])

  def test_a_comment_in_the_body_does_not_swallow_the_next_call_and_a_string_is_kept(self):
    out = unroll_loops(around("    for s in 0..1 {\n      @kernel k config | exec { .params = { n: s }; } // s of the stage\n      @kernel q config | exec { .params = { name: \"s\" }; }\n    }"))
    self.assertEqual(squeezed(out).count("@kernel q"), 2)
    self.assertEqual(squeezed(out).count('"s"'), 2)
    self.assertNotIn("//", out)

  def test_a_key_or_a_member_named_like_the_variable_stays_and_its_value_is_replaced(self):
    out = unroll_loops(around("    for stride in 4..5 {\n      @kernel k config | exec { .params = { stride: 8 >> stride }; .stride = stride; }\n    }"))
    self.assertEqual(squeezed(out).count("{ stride: 8 >> 4 }"), 1)
    self.assertEqual(squeezed(out).count("{ stride: 8 >> 5 }"), 1)
    self.assertEqual(squeezed(out).count(".stride = 4"), 1)

  def test_what_is_not_a_loop_of_an_emulate_block_is_left_as_it_is(self):
    kept = (
      "void f(void) {\n  for (int s = 0; s < 4; s++) { g(s); }\n  @emulate \"a\" {\n"
      "    @kernel k config {\n      for i in 0..3 { .load { .transfer = t; .scope = global; .offsets { .top0 = i; } } }\n    }\n  }\n}\n"
    )
    self.assertEqual(unroll_loops(kept), kept)
    self.assertEqual(unroll_loops("for s in 0..2 { @kernel k config | exec { } }\n"), "for s in 0..2 { @kernel k config | exec { } }\n")


if __name__ == "__main__":
  unittest.main()
