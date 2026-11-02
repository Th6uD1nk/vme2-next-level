import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.unroll import unroll_loops, unroll_marked_loops
from vmegc import main as vmegc_main
from vmeemu import main as vmeemu_main

SPEC = importlib.util.spec_from_file_location("vmeh_command", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vmeh.py"))
VMEH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VMEH)
vmeh_main = VMEH.main

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


def read_file(path):
  if not os.path.exists(path):
    return None
  with open(path, encoding="utf-8") as f:
    return f.read()


def in_files(files, command, read=()):
  with tempfile.TemporaryDirectory() as folder:
    paths = []
    for name, text in files:
      paths.append(os.path.join(folder, name))
      with open(paths[-1], "w", encoding="utf-8", newline="") as f:
        f.write(text)
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
      try:
        code = command(paths, folder)
      except SystemExit as exit:
        code = exit.code
    written = [read_file(os.path.join(folder, name)) for name in read]
    return code, out.getvalue(), err.getvalue().replace(folder + os.sep, ""), written


class UnrollTest(unittest.TestCase):
  def test_a_loop_is_the_copies_of_its_body_with_the_variable_replaced_and_the_lines_kept(self):
    out = unroll_loops(around("    for s in 1..3 {\n      @kernel k config | exec { .params = { n: 8 >> s }; }\n    }"))
    self.assertEqual(squeezed(out), squeezed(around("    @kernel k config | exec { .params = { n: 8 >> 1 }; } @kernel k config | exec { .params = { n: 8 >> 2 }; } @kernel k config | exec { .params = { n: 8 >> 3 }; }")))
    self.assertEqual(out.split("\n").index("int after;"), around("    for s in 1..3 {\n      @kernel k config | exec { .params = { n: 8 >> s }; }\n    }").split("\n").index("int after;"))

  def test_loops_inside_loops_are_unrolled_in_order(self):
    out = unroll_loops(around("    for a in 0..1 { for b in 5..6 { @kernel k config | exec { .params = { x: a * 10 + b }; } } }"))
    self.assertEqual(squeezed(out).count("@kernel k"), 4)
    self.assertEqual([word for word in squeezed(out).split() if word in ("0", "1", "5", "6")], ["0", "5", "0", "6", "1", "5", "1", "6"])

  def test_a_loop_inside_a_c_block_of_the_emulate_block_is_unrolled_and_the_lines_are_kept(self):
    source = around("    while (1) {\n      if (go) {\n        for s in 0..1 {\n          @kernel k config | exec { .params = { n: s }; }\n        }\n      }\n    }")
    out = unroll_loops(source)
    self.assertEqual(squeezed(out).count("@kernel k"), 2)
    self.assertNotIn("for s in", out)
    self.assertEqual(out.split("\n").index("int after;"), source.split("\n").index("int after;"))

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


class UnrollMarkTest(unittest.TestCase):
  def test_a_c_loop_marked_unroll_is_the_copies_for_vmee_and_stays_a_loop_for_vmegc(self):
    call = "@kernel k config | exec { .params = { n: 8 >> s }; }"
    copies = squeezed(around("    " + " ".join(call.replace(">> s", f">> {s}") for s in (1, 2, 3))))
    for header in ("for (int s = 1; s < 4; s++)", "for (unsigned int s = 1; s <= LAST; s += 1)", "for (int s = LOW; s < 2 * 2; s++)"):
      with self.subTest(header=header):
        out = unroll_marked_loops("#define LOW 1\n#define LAST 3\n" + around(f"    @unroll\n    {header} {{ {call} }}"))
        self.assertEqual(squeezed(out).replace("#define LOW 1 #define LAST 3 ", ""), copies)
    for block, message in [
      ("@unroll\n    for (int s = 1; s < get(); s++) { " + call + " }", "line 3: the @unroll loop is not unrolled"),
      ("@unroll\n    for (int s = 0; s < 300; s++) { " + call + " }", "line 3: the @unroll loop runs 300 turns"),
      ("@unroll\n    for (int s = 0; s < 2; s++) { go(s); }", "line 3: the @unroll loop calls no kernel"),
      ("@unroll\n    while (1) { }", "line 3: @unroll is written before a for loop"),
    ]:
      with self.assertRaisesRegex(ValueError, message):
        unroll_marked_loops(around("    " + block))
    marked = LOOP.replace("for s in 0..2 {", "@unroll\n    for (int s = 0; s < 3; s++) {")
    code, _, err, written = in_files([("main.vmeg.cpp", marked)], lambda paths, folder: vmegc_main([paths[0], "-o", os.path.join(folder, "out.cpp")]), ["out.cpp"])
    self.assertEqual((code, err), (0, ""))
    self.assertIn("for (int s = 0; s < 3; s++)", written[0])
    self.assertNotIn("unroll", written[0])


class UnrollToolsTest(unittest.TestCase):
  def test_vmegc_writes_for_a_loop_the_code_of_the_calls_written_one_by_one(self):
    outputs = []
    for text in (LOOP, MANUAL):
      code, _, err, written = in_files([("main.vmeg.cpp", text)], lambda paths, folder: vmegc_main([paths[0], "-o", os.path.join(folder, "out.cpp")]), ["out.cpp"])
      self.assertEqual((code, err), (0, ""))
      outputs.append(squeezed(written[0]))
    self.assertEqual(outputs[0], outputs[1])
    self.assertEqual(outputs[0].count("twice") + outputs[0].count("bump("), outputs[1].count("twice") + outputs[1].count("bump("))
    self.assertIn("bump(8 >> 2)", outputs[0])

  def test_vmegc_reports_the_error_of_a_loop_with_the_name_of_the_file(self):
    code, _, err, _ = in_files([("main.vmeg.cpp", LOOP.replace("0..2", "2..0"))], lambda paths, folder: vmegc_main([paths[0], "-o", os.path.join(folder, "out.cpp")]))
    self.assertEqual(code, 1)
    self.assertTrue(err.startswith("main.vmeg.cpp: line 16: the for runs from 2 to 0"), err)

  def test_vmeemu_lists_the_unrolled_calls_and_names_the_file_of_an_error(self):
    code, out, _, _ = in_files([("main.vmeg.cpp", LOOP)], lambda paths, folder: vmeemu_main(["--list", paths[0]]))
    self.assertEqual(code, 0)
    self.assertEqual(out.count("bump  build"), 3)
    self.assertEqual(out.count("bump  config | exec"), 3)
    code, _, err, _ = in_files([("main.vmeg.cpp", LOOP), ("bad.vmeg.cpp", around("for s in 3..1 { @kernel k config | exec { } }"))], lambda paths, folder: vmeemu_main(["--run", "loop", *paths]))
    self.assertEqual(code, 1)
    self.assertTrue(err.startswith("bad.vmeg.cpp: line 3: the for runs from 3 to 1"), err)

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_vmeemu_plays_a_loop_as_it_plays_the_calls_written_one_by_one(self):
    results = []
    for text in (LOOP, MANUAL):
      code, out, err, written = in_files([("main.vmeg.cpp", text)], lambda paths, folder: vmeemu_main(["--run", "loop", paths[0], "--trace", os.path.join(folder, "trace.txt"), "--buffers-words", "4"]), ["trace.txt"])
      self.assertEqual((code, err), (0, ""))
      results.append((out, written[0]))
    self.assertEqual(results[0], results[1])
    self.assertEqual(results[0][0].splitlines()[1], "0x00000002, 0x00000004, 0x00000006, 0x00000008,")

  def test_vmeh_writes_for_a_loop_the_program_of_the_calls_written_one_by_one(self):
    programs = []
    for text in (LOOP, MANUAL):
      code, _, err, written = in_files([("main.vmeg.cpp", text)], lambda paths, folder: vmeh_main([paths[0], "--extract", "loop", "-o", os.path.join(folder, "hw.vmeg.cpp")]), ["hw.vmeg.cpp"])
      self.assertEqual((code, err), (0, ""))
      programs.append(squeezed(written[0]))
    self.assertEqual(programs[0], programs[1])
    self.assertEqual(programs[0].count("@kernel bump"), 6)


if __name__ == "__main__":
  unittest.main()
