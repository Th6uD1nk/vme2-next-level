import contextlib
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmegc import main

SOURCE = (
  ".kernel run direct {\n"
  "  Agu t = { count: 15 };\n"
  "  .pe0 { .top = t; .write = { count: 15 }; .top0 + base0 + 5; }\n"
  "}\n"
  ".kernel other direct {\n"
  "  Agu t = { count: 3 };\n"
  "  .pe1 { .top = t; .write = { count: 3 }; .top1 & 255; }\n"
  "}\n"
  "@kernel run config | exec\n"
  "void f() { }\n"
  "@kernel other config | exec\n"
  "void g() { }\n"
)


def vmegc(*arguments):
  with tempfile.TemporaryDirectory() as folder:
    path = os.path.join(folder, "main.vmeg.c")
    with open(path, "w") as f:
      f.write(SOURCE)
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
      try:
        code = main([*arguments, path])
      except SystemExit as exit:
        code = exit.code
    return code, out.getvalue().replace(folder + os.sep, ""), err.getvalue().replace(folder + os.sep, "")


class KernelOptionTest(unittest.TestCase):
  def test_the_kernel_option_lists_only_the_header_of_that_kernel(self):
    code, out, _ = vmegc("--list", "--kernel", "other")
    self.assertEqual(code, 0)
    headers = [line for line in out.splitlines() if not line.startswith("  ")]
    self.assertEqual(len(headers), 1)
    self.assertIn(".kernel other direct", headers[0])

class KernelOptionErrorTest(unittest.TestCase):
  def test_the_kernel_option_goes_with_list(self):
    code, _, err = vmegc("--kernel", "run")
    self.assertEqual(code, 2)
    self.assertIn("--kernel goes with --list", err)

  def test_an_unknown_kernel_names_the_known_ones(self):
    code, _, err = vmegc("--list", "--kernel", "nope")
    self.assertEqual(code, 2)
    self.assertIn("no kernel 'nope' (run, other)", err)

class KernelOperationsTest(unittest.TestCase):
  def test_the_operations_of_the_kernel_follow_its_header(self):
    code, out, _ = vmegc("--list", "--kernel", "run")
    self.assertEqual(code, 0)
    lines = out.splitlines()
    self.assertIn(".kernel run direct", lines[0])
    self.assertEqual(len(lines), 2)
    self.assertTrue(lines[1].startswith("  pe0  line 3  0x030  a + b + c  "))
    self.assertTrue(lines[1].endswith("a = top0, b = base0, c = 5"))

  def test_the_fat_option_changes_the_opcode_of_the_listed_operations(self):
    source = SOURCE.replace("top0 + base0 + 5", "top0 + base0")
    with tempfile.TemporaryDirectory() as folder:
      path = os.path.join(folder, "main.vmeg.c")
      with open(path, "w") as f:
        f.write(source)
      lines = {}
      for compat in ([], ["--compat", "fat"]):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
          main(["--list", "--kernel", "run", *compat, path])
        lines[len(compat)] = out.getvalue().splitlines()[1]
    self.assertIn("0x010  a + b  ", lines[0])
    self.assertIn("0x030  a + b + c  ", lines[2])
    self.assertTrue(lines[2].endswith("a = top0, b = base0, c = 0"))

class OperationsListTest(unittest.TestCase):
  def test_the_ops_option_lists_the_operations_and_ends_without_error(self):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
      code = main(["--ops"])
    self.assertEqual(code, 0)
    self.assertIn("0x030: a + b + c", out.getvalue().splitlines())


if __name__ == "__main__":
  unittest.main()
