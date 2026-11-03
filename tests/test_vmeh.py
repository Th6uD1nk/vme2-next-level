import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmeg.blocks import find_blocks
from vmegc import render
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

  def test_the_pointers_of_an_emulation_are_written_after_the_arrays_and_one_without_an_array_is_refused(self):
    kernel = ".kernel k direct {\n  Transfer t = { memory: %s, count: 3 };\n  .load { .transfer = t; .scope = %s; .offsets { .top0 = 0; } }\n}\n"
    glob = "volatile Buffer a[4];\nvolatile Buffer* g = a;\n" + kernel % ("g", "global") + "void meLibOnProcess(void) {\n  @emulate \"e\" {\n    @kernel k config | exec {\n    }\n  }\n}\n"
    out = extract_source(glob, "e")
    self.assertLess(out.index("volatile Buffer a[4];"), out.index("volatile Buffer* g = a;"))
    self.assertLess(out.index("volatile Buffer* g = a;"), out.index("void meLibOnProcess(void) {"))
    local = "volatile Buffer a[4];\n" + kernel % ("p", "local") + "void meLibOnProcess(void) {\n  volatile Buffer* p = a;\n  @emulate \"e\" {\n    @kernel k config | exec {\n    }\n  }\n}\n"
    out = extract_source(local, "e")
    self.assertLess(out.index("void meLibOnProcess(void) {"), out.index("  volatile Buffer* p = a;"))
    computed = local.replace("volatile Buffer* p = a;", "volatile Buffer* p = table[1];")
    with self.assertRaisesRegex(ValueError, "the pointer p of the @emulate \"e\" is initialised with an expression that vmeh cannot write"):
      extract_source(computed, "e")

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


class UseTest(unittest.TestCase):
  def test_a_use_gives_an_array_to_a_pointer_only_and_each_use_goes_to_the_emulations_that_read_the_pointer(self):
    kernel = ".kernel %s direct {\n  Transfer t = { memory: %s, count: 3 };\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n}\n"
    text = (
      "volatile Buffer a[4];\nvolatile Buffer b[4];\nvolatile Buffer* p1 = a;\nvolatile Buffer* p2 = table[1];\n"
      + kernel % ("k1", "p1") + kernel % ("k2", "p2")
      + "void meLibOnProcess(void) {\n  @emulate \"first\" {\n    @kernel k1 config | exec {\n    }\n  }\n  @emulate \"second\" {\n    @kernel k2 config | exec {\n    }\n  }\n}\n"
    )
    out = extract_source(text, "second", (), 0, 32, [("p2", "b")])
    self.assertIn("volatile Buffer* p2 = b;", out)
    self.assertLess(out.index("volatile Buffer b[4];"), out.index("volatile Buffer* p2 = b;"))
    self.assertNotIn("volatile Buffer a[4];", out)
    both = extract_program([("t.vmeg.cpp", text)], 0, 32, [("p2", "b")])
    self.assertEqual(both.count("volatile Buffer* p2 = b;"), 1)
    self.assertEqual(both.count("volatile Buffer* p1 = a;"), 1)
    with self.assertRaisesRegex(ValueError, "--use a=b: a is not a pointer that the @emulate reads or writes, vmeh gives an array to a pointer only"):
      extract_source(text, "second", (), 0, 32, [("a", "b")])
    with self.assertRaisesRegex(ValueError, "--use zzz=b: zzz is not a pointer"):
      extract_program([("t.vmeg.cpp", text)], 0, 32, [("zzz", "b")])
    with self.assertRaisesRegex(ValueError, "the array nothing is defined in no file"):
      extract_source(text, "second", (), 0, 32, [("p2", "nothing")])


class DeclareTest(unittest.TestCase):
  def test_a_declare_of_the_file_goes_before_the_kernels_and_a_declare_of_a_function_stays_in_the_function(self):
    kernel = ".kernel k direct {\n  Agu %s = { count: 3 }, w = { count: 3, cyc: auto };\n  .pe0 { .top = %s; .write = w; .spad = top0 + top0; }\n%s}\n"
    load = "  .load { .transfer = shared; .scope = global; .offsets { .top0 = 0; } }\n"
    declare = "@declare {\n  Transfer shared = { memory: a, count: 3 };\n}\n"
    call = "void meLibOnProcess(void) {\n  @emulate \"e\" {\n%s    @kernel k config | exec {\n%s    }\n  }\n}\n"
    whole = "volatile Buffer a[4];\nvolatile Buffer b[4];\n" + declare + kernel % ("t", "t", load) + call % ("", "")
    out = extract_source(whole, "e")
    self.assertLess(out.index("@declare {"), out.index(".kernel k direct"))
    self.assertLess(out.index("volatile Buffer a[4];"), out.index("@declare {"))
    self.assertEqual(out.count("@declare {"), 1)
    render(out, find_blocks(out), "t.vmeg.cpp")
    local = "volatile Buffer a[4];\n" + kernel % ("shared", "shared", "") + call % (declare, "      .load { .transfer = shared; .scope = global; .offsets { .top0 = 0; } }\n")
    out = extract_source(local, "e")
    self.assertLess(out.index(".kernel k direct"), out.index("void meLibOnProcess(void) {"))
    self.assertLess(out.index("void meLibOnProcess(void) {"), out.index("@declare {"))
    render(out, find_blocks(out), "t.vmeg.cpp")
    spread = local.replace("Transfer shared = { memory: a, count: 3 };", "Transfer shared = { memory: a, count: 3 };\n  Transfer other = { ...shared, memory: b };").replace("volatile Buffer a[4];", "volatile Buffer a[4];\nvolatile Buffer b[4];").replace(".transfer = shared; .scope = global; .offsets { .top0 = 0; } }\n    }", ".transfer = other; .scope = global; .offsets { .top0 = 0; } }\n    }")
    out = extract_source(spread, "e")
    self.assertIn("volatile Buffer a[4];", out)
    self.assertIn("volatile Buffer b[4];", out)
    render(out, find_blocks(out), "t.vmeg.cpp")
