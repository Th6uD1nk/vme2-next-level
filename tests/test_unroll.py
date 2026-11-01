import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.unroll import unroll_loops

HEAD = (
  "volatile Buffer input[4] = { 1, 2, 3, 4 };\n"
  "volatile Buffer middle[4];\n"
  ".kernel bump memory {\n"
  "  .params { int rounds; }\n"
  "  Int count = 4 - 1;\n"
  "  Transfer in = { memory: input, count };\n"
  "  Transfer out = { memory: middle, count };\n"
  "  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }\n"
  "  Agu top = { count };\n"
  "  Agu write = { count, cyc: auto };\n"
  "  .pe0 { .top = top; .write = write; .spad = top0 + top0; }\n"
  "  .store { .transfer = out; .scope = global; .offsets { .base0 = 0; } }\n"
  "}\n"
)
BODY = "@kernel bump build {\n      .params = { rounds: 8 >> %s };\n    }\n    @kernel bump config | exec {\n    }\n"
LOOP = HEAD + "void meLibOnProcess(void) {\n  @emulate \"loop\" {\n    for s in 0..2 {\n    " + (BODY % "s") + "    }\n  }\n}\n"
MANUAL = HEAD + "void meLibOnProcess(void) {\n  @emulate \"loop\" {\n" + "".join("    " + BODY % s for s in range(3)) + "  }\n}\n"


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

  def test_a_file_with_windows_line_ends_gives_the_same_copies_and_the_same_number_of_lines(self):
    text = LOOP.replace("\n", "\r\n")
    out = unroll_loops(text)
    self.assertEqual(out.count("\n"), text.count("\n"))
    self.assertEqual(squeezed(out), squeezed(MANUAL))

  def test_a_loop_that_cannot_be_unrolled_is_refused_with_the_line_of_its_for(self):
    cases = [
      ("for s in 0...1 { @kernel k config | exec { } }", "line 3: expected 'for name in low..high {'"),
      ("for s in 0..N { @kernel k config | exec { } }", "line 3: the bounds of a for are integers, '0..N' is not accepted"),
      ("for s in 3..1 { @kernel k config | exec { } }", "line 3: the for runs from 3 to 1"),
      ("for s in 0..1 { go(); }", "line 3: the for calls no kernel"),
      ("for s in 0..1 {\n#define X 1\n@kernel k config | exec { } }", "line 3: a preprocessor line cannot be inside a for"),
      ("for a in 0..1 { for b in 2..1 { @kernel k config | exec { } } }", "line 3: the for runs from 2 to 1"),
    ]
    for block, message in cases:
      with self.assertRaisesRegex(ValueError, message.replace("(", "\\(").replace(".", "\\.")):
        unroll_loops(around(block))


if __name__ == "__main__":
  unittest.main()
