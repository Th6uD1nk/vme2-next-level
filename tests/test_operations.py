import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.operations import OPERATIONS, format_operations


class FormatOperationsTest(unittest.TestCase):
  def setUp(self):
    self.lines = format_operations().splitlines()

  def test_each_operation_is_listed_by_its_pattern_with_its_opcode_and_its_code(self):
    for kind, specification in OPERATIONS.items():
      with self.subTest(kind=kind):
        row = [line for line in self.lines if f" 0x{specification['opcode']:03x} " in line]
        self.assertEqual(len(row), 1)
        self.assertTrue(row[0].startswith("  " + specification["pattern"] + " "))
        self.assertIn(specification["code"], row[0])

  def test_the_aliases_and_the_portability_are_listed_under_the_note(self):
    self.assertIn("      also written and(x, c)", self.lines)
    self.assertIn("      also written ~and(x, c)", self.lines)
    portable = [kind for kind, specification in OPERATIONS.items() if not specification.get("not_portable")]
    self.assertEqual(self.lines.count("      not portable"), len(OPERATIONS) - len(portable))
    index = next(i for i, line in enumerate(self.lines) if " 0x010 " in line)
    self.assertEqual(self.lines[index + 2], "      not portable")

  def test_the_options_of_the_operation_they_wrap_are_listed(self):
    text = "\n".join(self.lines)
    self.assertIn("options of the operation they wrap:", text)
    for option in ["sat(op, bits)", "op >> n", "op << n"]:
      self.assertIn(option, text)


if __name__ == "__main__":
  unittest.main()
