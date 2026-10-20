import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.macros import evaluate, known_macros, macro_events, trusted_macros


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


def trusted(text):
  return trusted_macros(text, text.index("int use;"))


class TrustedMacrosTest(unittest.TestCase):
  def test_a_macro_defined_once_before_the_use_is_trusted(self):
    self.assertEqual(trusted("#define A 1\n#define B (A + 1)\nint use;\n"), {"A": "1", "B": "(A + 1)"})

  def test_a_macro_defined_twice_is_not_trusted(self):
    self.assertEqual(trusted("#define A 1\n#define B 5\n#define A 2\nint use;\n"), {"B": "5"})
    self.assertEqual(trusted("#define A 1\nint use;\n#define A 2\n"), {})

  def test_a_macro_in_a_condition_is_not_trusted(self):
    self.assertEqual(trusted("#ifdef Z\n#define A 1\n#else\n#define A 2\n#endif\n#define B 3\nint use;\n"), {"B": "3"})

  def test_a_macro_after_the_use_is_not_trusted(self):
    self.assertEqual(trusted("#define A 1\nint use;\n#define B 2\n"), {"A": "1"})

  def test_a_macro_with_parameters_or_undone_is_not_trusted(self):
    self.assertEqual(trusted("#define F(x) (x)\n#define A 1\n#define B 2\n#undef B\nint use;\n"), {"A": "1"})


class EvaluateTest(unittest.TestCase):
  def test_a_number_in_decimal_or_hexadecimal_and_a_calculation(self):
    nothing = lambda name: None
    self.assertEqual([evaluate(body, nothing) for body in ["4", "0x10", "-3", "(1 << 4) & 0xff", "3 + 2 * 4"]], [4, 16, -3, 16, 11])

  def test_the_names_are_given_by_the_resolver(self):
    numbers = {"A": 16, "B": 3}
    self.assertEqual(evaluate("(A * 4) - B", numbers.get), 61)

  def test_an_unknown_name_or_a_body_that_is_not_an_expression_gives_nothing(self):
    numbers = {"A": 16}
    self.assertEqual([evaluate(body, numbers.get) for body in ["(FROM_A_HEADER + 1)", "sizeof(int)", "(1 +", "", "A A", "(int)A"]], [None] * 6)


def known(text):
  return known_macros(text, text.index("int use;"))


class KnownMacrosTest(unittest.TestCase):
  def test_a_macro_in_another_macro_even_through_a_chain(self):
    text = "#define VECTOR_COUNT 16\n#define VECTOR_BATCH_WORD_COUNT (VECTOR_COUNT * 4)\n#define LAST (VECTOR_BATCH_WORD_COUNT - 1)\nint use;\n"
    self.assertEqual(known(text), {"VECTOR_COUNT": 16, "VECTOR_BATCH_WORD_COUNT": 64, "LAST": 63})

  def test_an_unknown_part_makes_the_whole_macro_and_the_ones_that_use_it_unknown(self):
    text = "#define A (FROM_A_HEADER + 1)\n#define B (A * 2)\n#define C sizeof(int)\n#define E 8\nint use;\n"
    self.assertEqual(known(text), {"E": 8})

  def test_a_macro_that_is_not_trusted_makes_the_ones_that_use_it_unknown(self):
    self.assertEqual(known("#define A 1\n#define A 2\n#define B (A + 1)\n#define C 3\nint use;\n"), {"C": 3})

  def test_a_cycle_gives_no_number(self):
    self.assertEqual(known("#define A B\n#define B A\n#define C 1\nint use;\n"), {"C": 1})


if __name__ == "__main__":
  unittest.main()
