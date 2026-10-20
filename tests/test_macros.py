import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.macros import macro_events


def summary(text):
  return [(event["kind"], event["name"], event["params"], event["body"], event["conditional"]) for event in macro_events(text)]


class MacroEventsTest(unittest.TestCase):
  def test_a_define_with_its_body_and_a_comment(self):
    text = "#define A 1\n#define B (x + 1) // note\n#define C /* c */ 2\n#define E\nint y = 1; // #define NOT 3\n"
    self.assertEqual(summary(text), [
      ("define", "A", None, "1", False),
      ("define", "B", None, "(x + 1)", False),
      ("define", "C", None, "2", False),
      ("define", "E", None, "", False),
    ])

  def test_a_body_on_several_lines(self):
    self.assertEqual(summary("#define L a + \\\n  b /* c */\n"), [("define", "L", None, "a + b", False)])

  def test_a_macro_with_parameters_is_told_from_an_object_macro(self):
    self.assertEqual(summary("#define F(x) ((x) * 2)\n#define G (x)\n"), [
      ("define", "F", "(x)", "((x) * 2)", False),
      ("define", "G", None, "(x)", False),
    ])

  def test_a_define_inside_a_condition_is_marked(self):
    text = "#define A 1\n#ifdef Z\n#define B 2\n#else\n#define C 3\n#endif\n#if 1\n#ifndef Y\n#define D 4\n#endif\n#endif\n#define E 5\n"
    self.assertEqual([(event["name"], event["conditional"]) for event in macro_events(text)], [
      ("A", False), ("B", True), ("C", True), ("D", True), ("E", False),
    ])

  def test_an_undef_and_the_position_of_each_event(self):
    text = "#define A 1\n#undef A\n"
    events = macro_events(text)
    self.assertEqual([(event["kind"], event["name"], event["start"]) for event in events], [("define", "A", 0), ("undef", "A", 12)])


if __name__ == "__main__":
  unittest.main()
