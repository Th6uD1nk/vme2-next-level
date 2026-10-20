import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.macros import macro_events


def summary(text):
  return [(event["name"], event["params"], event["body"]) for event in macro_events(text)]


class MacroEventsTest(unittest.TestCase):
  def test_a_define_with_its_body_and_a_comment(self):
    text = "#define A 1\n#define B (x + 1) // note\n#define C /* c */ 2\n#define E\nint y = 1; // #define NOT 3\n"
    self.assertEqual(summary(text), [("A", None, "1"), ("B", None, "(x + 1)"), ("C", None, "2"), ("E", None, "")])

  def test_a_body_on_several_lines(self):
    self.assertEqual(summary("#define L a + \\\n  b /* c */\n"), [("L", None, "a + b")])

  def test_a_macro_with_parameters_is_told_from_an_object_macro(self):
    self.assertEqual(summary("#define F(x) ((x) * 2)\n#define G (x)\n"), [("F", "(x)", "((x) * 2)"), ("G", None, "(x)")])


if __name__ == "__main__":
  unittest.main()
