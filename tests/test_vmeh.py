import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmeh.extract import extract_program, extract_source

KERNELS = (
  "volatile Buffer a[4];\nvolatile Buffer b[4];\n"
  "@emulate \"first\"\n.kernel k1 direct {\n  Transfer t = { memory: a, count: 3 };\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n}\n"
  "@emulate \"second\"\n.kernel k2 direct {\n  Transfer t = { memory: b, count: 3 };\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n}\n"
)

BLOCK = "void meLibOnProcess(void) {\n  @emulate \"both\" {\n    @kernel k1 config | exec {\n    }\n    @kernel k2 config | exec {\n    }\n  }\n}\n"


class ProgramTest(unittest.TestCase):
  def test_several_emulations_give_one_program_with_a_function_per_emulation_and_the_keys_to_move(self):
    out = extract_program([("t.vmeg.cpp", KERNELS + BLOCK)])
    self.assertIn("meLibSetSharedUncached32(4);", out)
    self.assertIn('static const char* const vmehNames[] = {"first", "second", "both"};', out)
    for index in (1, 2, 3):
      self.assertIn(f"void vmehRun{index}(void) {{", out)
      self.assertIn(f"        vmehRun{index}();", out)
    self.assertEqual(out.count(".kernel k1 direct"), 1)
    self.assertEqual(out.count(".kernel k2 direct"), 1)
    self.assertIn("index > 0", out)
    self.assertIn("index < vmehCount - 1", out)

  def test_one_emulation_gives_the_program_of_that_emulation_and_no_emulation_is_refused(self):
    text = KERNELS.split("@emulate \"second\"")[0]
    self.assertEqual(extract_program([("t.vmeg.cpp", text)]), extract_source(text, "first"))
    with self.assertRaises(ValueError):
      extract_program([("t.vmeg.cpp", "volatile Buffer a[4];\n")])

  def test_the_window_of_the_dump_is_read_from_a_file_with_the_values_of_the_build_as_defaults_but_not_with_one_emulation(self):
    out = extract_program([("t.vmeg.cpp", KERNELS + BLOCK)], 8, 16)
    self.assertIn('fopen("./config.txt", "r")', out)
    self.assertIn("static int vmehWords = 16;", out)
    self.assertIn("int start = 8;", out)
    self.assertIn("vmeDebugFillWithCount(VME_BASE_BUFFERS + meStart * 4, meCount);", out)
    one = extract_program([("t.vmeg.cpp", KERNELS.split("@emulate \"second\"")[0])], 8, 16)
    self.assertNotIn("config.txt", one)
    self.assertIn("vmeDebugFillWith(VME_BASE_BUFFERS + 8 * 4);", one)


if __name__ == "__main__":
  unittest.main()
