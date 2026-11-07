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


def run_vmegt(source, *arguments):
  with tempfile.TemporaryDirectory() as folder:
    path = os.path.join(folder, "main.vmeg.cpp")
    if source is not None:
      with open(path, "w", encoding="utf-8") as f:
        f.write(source)
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
      code = main([path, *arguments])
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


if __name__ == "__main__":
  unittest.main()
