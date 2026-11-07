import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

SPEC = importlib.util.spec_from_file_location("vmegt_command", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vmegt.py"))
VMEGT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VMEGT)
main = VMEGT.main

SOURCE = (
  "volatile Buffer a[4];\n"
  "@emulate \"first\"\n"
  ".kernel k1 direct {\n"
  "  Transfer t = { memory: a, count: 3 };\n"
  "  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n"
  "}\n"
  "@emulate \"second\"\n"
  ".kernel k2 direct {\n"
  "  Transfer t = { memory: a, count: 3 };\n"
  "  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n"
  "}\n"
)


def run_vmegt(source, *arguments, files=None):
  with tempfile.TemporaryDirectory() as folder:
    path = os.path.join(folder, "main.vmeg.cpp")
    if source is not None:
      with open(path, "w", encoding="utf-8") as f:
        f.write(source)
    for name, content in (files or {}).items():
      with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        f.write(content)
    resolved = [os.path.join(folder, a[6:]) if a.startswith("@file:") else a for a in arguments]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
      code = main([path, *resolved])
    return code, out.getvalue(), err.getvalue().replace(folder + os.sep, "")


class ListTest(unittest.TestCase):
  def test_list_prints_all_ids_or_only_the_chosen_ones_in_the_given_order(self):
    code, out, _ = run_vmegt(SOURCE, "--list")
    self.assertEqual(code, 0)
    self.assertEqual(out.splitlines(), ["first", "second"])
    code, out, _ = run_vmegt(SOURCE, "second", "--list")
    self.assertEqual(code, 0)
    self.assertEqual(out.splitlines(), ["second"])


class ErrorTest(unittest.TestCase):
  def test_missing_file_unknown_id_no_emulate_and_missing_pspdev_exit_with_code_2(self):
    code, _, err = run_vmegt(None, "--list")
    self.assertEqual(code, 2)
    self.assertIn("no such file", err)
    code, _, err = run_vmegt(SOURCE, "nope", "--list")
    self.assertEqual(code, 2)
    self.assertIn("not an @emulate id of the file: nope", err)
    code, _, err = run_vmegt("volatile Buffer a[4];\n", "--list")
    self.assertEqual(code, 2)
    self.assertIn("the file has no @emulate", err)
    code, _, err = run_vmegt(SOURCE, "--pspdev", "")
    self.assertEqual(code, 2)
    self.assertIn("give --pspdev or set PSPDEV", err)


class CheckTest(unittest.TestCase):
  def test_reuse_log_checks_buffers_against_the_emulator(self):
    code, _, err = run_vmegt(SOURCE, "--reuse-log")
    self.assertEqual(code, 2)
    self.assertIn("--reuse-log goes with --check", err)
    code, _, err = run_vmegt(SOURCE, "--check", "--reuse-log", "--log", "@file:missing.log")
    self.assertEqual(code, 2)
    self.assertIn("missing.log: no such file", err)
    blocks = "\n\n".join(f"Buffer: BASE {pe}\n0x00000000, 0x00000000, 0x00000000, 0x00000000," for pe in range(4))
    good = f"=== kernel first ===\n{blocks}\n\n=== summary ===\nfirst: done\n"
    code, out, _ = run_vmegt(SOURCE, "first", "--check", "--reuse-log", "--log", "@file:good.log", "--buffers-words", "4", files={"good.log": good})
    self.assertEqual(code, 0)
    self.assertEqual(out.splitlines(), ["first: ok"])
    bad = good.replace("0x00000000,", "0x00000007,", 1)
    code, out, _ = run_vmegt(SOURCE, "first", "--check", "--reuse-log", "--log", "@file:bad.log", "--buffers-words", "4", files={"bad.log": bad})
    self.assertEqual(code, 1)
    self.assertEqual(out.splitlines(), ["first: mismatch: BASE_0 word 0: PSP 0x00000007, emulator 0x00000000"])


if __name__ == "__main__":
  unittest.main()
