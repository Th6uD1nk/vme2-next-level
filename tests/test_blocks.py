import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmegc import find_blocks, render


def found(text):
  return [(kind, text[start:end]) for kind, start, _, end in find_blocks(text)]


class FindBlocksTest(unittest.TestCase):
  def test_valid_blocks(self):
    cases = {
      "buffers { a }": [("buffers", "buffers { a }")],
      "kernel k { a }": [("kernel", "kernel k { a }")],
      "kernel k direct { a }": [("kernel", "kernel k direct { a }")],
      "void f() { }\nbuffers { a }": [("buffers", "buffers { a }")],
      "#include <a.h>\nbuffers { a }": [("buffers", "buffers { a }")],
      "buffers { a { b } c }": [("buffers", "buffers { a { b } c }")],
      "buffers { /* } */ \"}\" '}' }": [("buffers", "buffers { /* } */ \"}\" '}' }")],
      "buffers { }\nkernel k { }": [("buffers", "buffers { }"), ("kernel", "kernel k { }")],
    }
    for text, expected in cases.items():
      with self.subTest(text=text):
        self.assertEqual(found(text), expected)

  def test_plain_c_is_not_a_block(self):
    cases = [
      "struct buffers { int a; };",
      "struct kernel { int a; };",
      "typedef struct { int a; } buffers;",
      "typedef struct { int a; } kernel;",
      "int buffers = 3;",
      "int kernel = 1;",
      "kernel_t kernel;",
      "kernel foo;",
      "kernel { }",
      "buffers = 1;",
      "void f() { buffers { } }",
      "void f() { kernel k { } }",
      "#define X buffers {\nint a;",
      "/* buffers { */ int a;",
      "// kernel k {\nint a;",
      "const char* s = \"buffers {\";",
    ]
    for text in cases:
      with self.subTest(text=text):
        self.assertEqual(find_blocks(text), [])

  def test_unterminated_block(self):
    with self.assertRaises(ValueError) as ctx:
      find_blocks("int a;\nbuffers {\n x\n")
    self.assertIn("line 2", str(ctx.exception))


class RenderTest(unittest.TestCase):
  def test_blocks_removed_and_lines_kept(self):
    text = "volatile Buffer x[1];\nkernel k direct {\n  global buffers {\n    top0, 1 words, from x;\n  }\n}\n@kernel k\nvoid f(void) { }\nint b;\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertTrue(out.startswith('#line 1 "t.vmeg.c"\nvolatile u32 __attribute__((aligned(64))) x[1];\n'))
    self.assertIn('#line 6 "t.vmeg.c"', out)
    self.assertTrue(out.endswith('void f(void) {\n  k();\n#line 8 "t.vmeg.c"\n }\nint b;\n'))

  def test_decorator(self):
    text = "kernel k direct {\n}\n@kernel k\n\n/* c */\nstatic void run(int a) { }\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertNotIn("@", out)
    self.assertIn("static void run(int a) {", out)
    self.assertIn("\n  k();", out)
    bad = ["@kernel\nvoid run() { }\n", "@kernel k\nrun() { }\n", "@kernel k\nint x;\n", "@kernel k\nvoid run();\n", "@other k\nvoid run() { }\n", "@kernel k\n"]
    for text in bad:
      with self.subTest(text=text):
        with self.assertRaises(ValueError):
          find_blocks(text)

  def test_decorator_needs_a_known_kernel(self):
    text = "kernel k direct {\n}\n@kernel z\nvoid run() { }\n"
    with self.assertRaises(ValueError) as ctx:
      render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("line 3", str(ctx.exception))
    self.assertIn("'z'", str(ctx.exception))

  def test_decorator_with_a_list_of_kernels(self):
    kernels = "kernel a direct {\n}\nkernel b direct {\n}\nkernel c direct {\n}\n"
    ok = kernels + "@kernel a, b\nvoid r1() { }\n@kernel c\nvoid r2() { }\n"
    out = render(ok, find_blocks(ok), "t.vmeg.c")
    self.assertNotIn("@", out)
    again = kernels + "@kernel a, a, b\nvoid r() { }\n@kernel c\nvoid s() { }\n"
    render(again, find_blocks(again), "t.vmeg.c")
    for text in [kernels + "@kernel a, z\nvoid r() { }\n", kernels + "@kernel a, b\nvoid r() { }\n"]:
      with self.subTest(text=text):
        with self.assertRaises(ValueError):
          render(text, find_blocks(text), "t.vmeg.c")

  def test_global_sources_must_be_declared_with_buffer(self):
    def build(declarations):
      return declarations + "kernel k direct {\n  global buffers {\n    top0, 1 words, from x;\n    top1, 1 words, from y;\n  }\n}\n@kernel k\nvoid f() { }\n"
    ok = build("volatile Buffer x[1], y[1];\n")
    render(ok, find_blocks(ok), "t.vmeg.c")
    for declarations in ["", "volatile Buffer x[1];\n", "volatile Buffer x[1], z[1];\n", "volatile u32 x[1], y[1];\n"]:
      text = build(declarations)
      with self.subTest(declarations=declarations):
        with self.assertRaises(ValueError) as ctx:
          render(text, find_blocks(text), "t.vmeg.c")
        self.assertIn("global buffers", str(ctx.exception))

  def test_every_kernel_needs_a_decorated_function(self):
    kernel = "kernel k direct {\n  icn top = 0;\n}\n"
    with self.assertRaises(ValueError) as ctx:
      render(kernel, find_blocks(kernel), "t.vmeg.c")
    self.assertIn("line 1", str(ctx.exception))
    self.assertIn("'k'", str(ctx.exception))
    text = kernel + "@kernel k\nvoid run() { }\n"
    render(text, find_blocks(text), "t.vmeg.c")

  def test_buffer_keyword(self):
    text = 'volatile Buffer a[4];\nconst char* s = "Buffer";\n/* Buffer */\nint Buffers, MyBuffer;\nvoid f(void) { static volatile Buffer b[2]; }\n'
    out = render(text, [], "t.vmeg.c")
    t = "u32 __attribute__((aligned(64)))"
    self.assertEqual(out, f'#line 1 "t.vmeg.c"\nvolatile {t} a[4];\nconst char* s = "Buffer";\n/* Buffer */\nint Buffers, MyBuffer;\nvoid f(void) {{ static volatile {t} b[2]; }}\n')

  def test_buffer_without_volatile_is_refused(self):
    for text in ["Buffer a[4];\n", "int x;\nstatic Buffer a[4];\n", "const Buffer a[4];\n"]:
      with self.subTest(text=text):
        with self.assertRaises(ValueError) as ctx:
          render(text, [], "t.vmeg.c")
        self.assertIn("volatile", str(ctx.exception))

  def test_buffer_only_declares_a_variable(self):
    cases = ["volatile Buffer* p;\n", "void f(volatile Buffer* p) { }\n", "void f(volatile Buffer a[]) { }\n", "int* p = (volatile Buffer*)x;\n", "volatile Buffer;\n"]
    for text in cases:
      with self.subTest(text=text):
        with self.assertRaises(ValueError) as ctx:
          render(text, [], "t.vmeg.c")
        self.assertIn("Buffer", str(ctx.exception))

  def test_volatile_among_qualifiers(self):
    for text in ["static volatile Buffer a[4];\n", "volatile static Buffer a[4];\n", "const volatile Buffer a[4];\n", "extern volatile Buffer a[4];\n"]:
      with self.subTest(text=text):
        self.assertIn("u32 __attribute__", render(text, [], "t.vmeg.c"))

  def test_top_level_buffers_is_refused(self):
    text = "int a;\nbuffers {\n  top0, 1 words, from x;\n}\n"
    with self.assertRaises(ValueError) as ctx:
      render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("line 2", str(ctx.exception))


if __name__ == "__main__":
  unittest.main()
