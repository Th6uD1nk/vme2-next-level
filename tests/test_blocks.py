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
    text = "int a;\nkernel k {\n  local buffers {\n    top0, 1 words, from x;\n  }\n}\nint b;\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertEqual(out, '#line 1 "t.vmeg.c"\nint a;\n\n#line 6 "t.vmeg.c"\n\nint b;\n')

  def test_buffer_keyword(self):
    text = 'volatile Buffer a[4];\nconst char* s = "Buffer";\n/* Buffer */\nint Buffers, MyBuffer;\nvoid f(void) { Buffer b[2]; }\n'
    out = render(text, [], "t.vmeg.c")
    t = "u32 __attribute__((aligned(64)))"
    self.assertEqual(out, f'#line 1 "t.vmeg.c"\nvolatile {t} a[4];\nconst char* s = "Buffer";\n/* Buffer */\nint Buffers, MyBuffer;\nvoid f(void) {{ {t} b[2]; }}\n')

  def test_top_level_buffers_is_refused(self):
    text = "int a;\nbuffers {\n  top0, 1 words, from x;\n}\n"
    with self.assertRaises(ValueError) as ctx:
      render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("line 2", str(ctx.exception))


if __name__ == "__main__":
  unittest.main()
