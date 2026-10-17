import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmeg.blocks import find_blocks
from vmegc import check_on_process, default_output, merged_file, merge_globals, render, translate


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
    self.assertTrue(out.endswith('void f(void) {\n  vmeLibEnable();\n  k();\n  vmeLibDisable();\n#line 8 "t.vmeg.c"\n }\nint b;\n'))

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

  def test_local_sources_must_be_declared_in_every_decorated_function(self):
    kernel = "kernel k direct {\n  local buffers {\n    top0, 1 words, from x;\n  }\n}\n"
    declared = "void f() {\n  volatile Buffer x[1];\n}\n"
    ok = kernel + "@kernel k\n" + declared
    render(ok, find_blocks(ok), "t.vmeg.c")
    bad = [
      kernel + "@kernel k\nvoid f() { }\n",
      "volatile Buffer x[1];\n" + kernel + "@kernel k\nvoid f() { }\n",
      kernel + "@kernel k\nvoid f() {\n  if (1) { volatile Buffer x[1]; }\n}\n",
      kernel + "@kernel k\n" + declared + "@kernel k\nvoid g() { }\n",
    ]
    for text in bad:
      with self.subTest(text=text):
        with self.assertRaises(ValueError) as ctx:
          render(text, find_blocks(text), "t.vmeg.c")
        self.assertIn("local buffers", str(ctx.exception))
    both = kernel + "@kernel k\n" + declared + "@kernel k\n" + declared.replace("f()", "g()")
    render(both, find_blocks(both), "t.vmeg.c")

  def test_local_buffers_are_uploaded_in_the_decorated_function(self):
    text = "kernel k direct {\n  local buffers {\n    top0, 4 words, from a;\n    base1, 2 words, at 8, from b;\n  }\n}\n@kernel k\nvoid f() {\n  volatile Buffer a[4], b[2];\n  go();\n}\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    body = out[out.index("void f() {"):]
    expected = ["void f() {", "volatile u32 __attribute__((aligned(64))) a[4], b[2];", "vmeLibEnable();",
      "vmeLibMemoryToRingBuffer((void*)a, VME_TOP_BUFF0_WOFF, 4);",
      "vmeLibMemoryToRingBuffer((void*)b, VME_BASE_BUFF1_WOFF + 8, 2);", "k();", "vmeLibDisable();"]
    position = 0
    for piece in expected:
      position = body.index(piece, position) + len(piece)
    self.assertLess(body.index("vmeLibDisable();"), body.index("go();"))

  def test_summary_of_a_file(self):
    text = "volatile Buffer g[4];\nkernel a direct {\n  global buffers {\n    base1, 4 words, at OFFSET + 4, from g;\n    top2, 4 words, from g;\n  }\n}\n@kernel a\nvoid f() { }\nvoid meLibOnProcess(void) { }\n"
    _, info = translate(text, find_blocks(text), "t.vmeg.c")
    self.assertEqual(info, "vmeg-info\t1\nsource\tt.vmeg.c\nglobal\tBASE_1\t4\t(OFFSET + 4)\tg\t4\nglobal\tTOP_2\t4\t\tg\t5\non-process\t10\n")
    plain = "int x;\n"
    self.assertEqual(translate(plain, find_blocks(plain), "p.vmeg.c")[1], "vmeg-info\t1\nsource\tp.vmeg.c\n")

  def test_global_uploads_in_on_process(self):
    text = "int before;\nvoid meLibOnProcess(void)\n{\n  go();\n}\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertTrue(out.startswith('static void vmegUploadGlobals(void);\n#line 1 "t.vmeg.c"\n'))
    self.assertTrue(out.endswith('\n#include "t.gen.h"\n'))
    self.assertEqual(out.count("vmegUploadGlobals();"), 1)
    self.assertIn("{\n  vmeLibEnable();\n  vmeLibWipe();\n  vmegUploadGlobals();\n  vmeLibDisable();\n#line 3", out)
    self.assertEqual(out.count("vmeLibWipe();"), 1)
    self.assertLess(out.index("vmeLibDisable();"), out.index("go();"))
    plain = "void f() { meLibOnProcess(); }\nvoid meLibOnProcess(void);\n"
    self.assertNotIn("vmegUploadGlobals", render(plain, find_blocks(plain), "t.vmeg.c"))
    twice = "void meLibOnProcess(void) { }\nvoid meLibOnProcess(int x) { }\n"
    with self.assertRaises(ValueError) as ctx:
      render(twice, find_blocks(twice), "t.vmeg.c")
    self.assertIn("line 2", str(ctx.exception))

  def test_one_block_when_on_process_carries_the_kernel(self):
    text = "kernel k direct {\n  local buffers {\n    top0, 4 words, from a;\n  }\n}\n@kernel k\nvoid meLibOnProcess(void)\n{\n  volatile Buffer a[4];\n  go();\n}\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertEqual(out.count("vmeLibEnable();"), 1)
    self.assertEqual(out.count("vmeLibDisable();"), 1)
    expected = ["volatile u32 __attribute__((aligned(64))) a[4];", "vmeLibEnable();", "vmeLibWipe();", "vmegUploadGlobals();",
      "vmeLibMemoryToRingBuffer((void*)a, VME_TOP_BUFF0_WOFF, 4);", "k();", "vmeLibDisable();", "go();"]
    position = out.index("void meLibOnProcess")
    for piece in expected:
      position = out.index(piece, position) + len(piece)
    other = "kernel k direct {\n}\n@kernel k\nvoid run() { }\nvoid meLibOnProcess(void) { }\n"
    out = render(other, find_blocks(other), "t.vmeg.c")
    self.assertEqual(out.count("vmeLibEnable();"), 2)
    self.assertEqual(out.count("vmegUploadGlobals();"), 1)
    self.assertEqual(out.count("vmeLibWipe();"), 1)
    self.assertLess(out.index("vmeLibWipe();"), out.index("vmegUploadGlobals();"))

  def test_merge_of_global_lines(self):
    def info(source, *lines):
      return {"source": source, "globals": list(lines), "on_process": []}
    a = info("a.vmeg.c", ("TOP_0", 16, "", "x", 4), ("BASE_0", 16, "OFF", "w", 5))
    same = info("b.vmeg.c", ("TOP_0", 16, "0", "x", 9), ("BASE_0", 16, "OFF", "w", 10), ("TOP_1", 8, "", "y", 11))
    self.assertEqual(merge_globals([a, same]), [("TOP_0", 16, "", "x"), ("BASE_0", 16, "OFF", "w"), ("TOP_1", 8, "", "y")])
    apart = info("b.vmeg.c", ("BASE_0", 16, "8", "w", 3))
    self.assertEqual(len(merge_globals([a, apart])), 3)
    for other in [("TOP_0", 16, "", "other", 9), ("TOP_0", 8, "", "x", 9)]:
      with self.subTest(other=other):
        with self.assertRaises(ValueError) as ctx:
          merge_globals([a, info("b.vmeg.c", other)])
        self.assertEqual(str(ctx.exception), "b.vmeg.c:9: top0 is already loaded at the same offset by a.vmeg.c:4 with a different source or size")

  def test_on_process_over_the_summaries(self):
    def info(source, globals_=(), on_process=()):
      return {"source": source, "globals": list(globals_), "on_process": list(on_process)}
    lines = [("TOP_0", 16, "", "x", 40)]
    check_on_process([info("a.vmeg.c", lines), info("b.vmeg.c", on_process=[7])])
    check_on_process([info("a.vmeg.c", lines, [7])])
    check_on_process([info("a.vmeg.c"), info("b.vmeg.c")])
    check_on_process([info("a.vmeg.c", on_process=[3])])
    with self.assertRaises(ValueError) as ctx:
      check_on_process([info("a.vmeg.c", lines), info("b.vmeg.c")])
    self.assertEqual(str(ctx.exception), "a.vmeg.c:40: global buffers need a function meLibOnProcess in one of the files, none defines it")
    with self.assertRaises(ValueError) as ctx:
      check_on_process([info("a.vmeg.c", on_process=[3]), info("b.vmeg.c", on_process=[12])])
    self.assertEqual(str(ctx.exception), "meLibOnProcess is defined more than once: a.vmeg.c:3 and b.vmeg.c:12")

  def test_merged_file(self):
    merged = [("TOP_0", 4, "", "inA"), ("BASE_1", 8, "OFFSET + 2", "inB"), ("TOP_2", 4, "", "inA")]
    expected = "extern volatile u32 inA[];\nextern volatile u32 inB[];\nstatic void vmegUploadGlobals(void) {\n  vmeLibMemoryToRingBuffer((void*)inA, VME_TOP_BUFF0_WOFF, 4);\n  vmeLibMemoryToRingBuffer((void*)inB, VME_BASE_BUFF1_WOFF + OFFSET + 2, 8);\n  vmeLibMemoryToRingBuffer((void*)inA, VME_TOP_BUFF2_WOFF, 4);\n}\n"
    self.assertEqual(merged_file(merged), expected)
    self.assertEqual(merged_file([]), "static void vmegUploadGlobals(void) {\n}\n")

  def test_vme_is_removed_and_the_block_is_kept(self):
    text = "void f(void) {\n  before();\n  @vme {\n    runContext();\n  }\n  while (1) { }\n}\n"
    blocks = find_blocks(text)
    self.assertEqual([block[0] for block in blocks], ["vme", "vme-end"])
    out = render(text, blocks, "t.vmeg.c")
    self.assertNotIn("@", out)
    self.assertEqual(out.count("vmeLibEnable();"), 1)
    self.assertEqual(out.count("vmeLibDisable();"), 1)
    for piece in ["before();", "{", "runContext();", "}", "while (1)"]:
      self.assertIn(piece, out)
    inside_kernel = "kernel k direct {\n  icn top = 0;\n}\n@kernel k\nvoid f() {\n  const char* s = \"@vme {\";\n}\n"
    self.assertEqual([block[0] for block in find_blocks(inside_kernel)], ["kernel", "decorator"])

  def test_context_is_an_alias_of_kernel(self):
    mixed = "kernel a direct {\n}\ncontext b direct {\n}\n@context a, b\nvoid run() { }\n"
    blocks = find_blocks(mixed)
    self.assertEqual([block[0] for block in blocks], ["kernel", "kernel", "decorator"])
    out = render(mixed, blocks, "t.vmeg.c")
    self.assertNotIn("@", out)
    self.assertEqual(out.count("a();") + out.count("b();"), 2)
    plain = "struct context { int x; };\nint context_count = 0;\ntypedef struct { int a; } context_t;\ncontext_t c = { 1 };\n"
    self.assertEqual(find_blocks(plain), [])

  def test_output_names(self):
    self.assertEqual(default_output("dir/a.vmeg.c"), "a.c")
    self.assertEqual(default_output("dir/a.vmeg.cpp"), "a.cpp")
    with self.assertRaises(SystemExit):
      default_output("a.cpp")

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
