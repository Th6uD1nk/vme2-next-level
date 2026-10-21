import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmeg.blocks import find_blocks
from vmeg.registry import array_definitions, check_calls, check_definitions, check_uses, extern_declaration, needed_externs, project_registry
from vmeg.vmecalls import finish_calls, wait_marker
from vmegc import default_output, render, translate


def found(text):
  return [(kind, text[start:end]) for kind, start, _, end in find_blocks(text)]


class FindBlocksTest(unittest.TestCase):
  def test_valid_blocks(self):
    cases = {
      ".kernel k { a }": [("kernel", ".kernel k { a }")],
      ".kernel k direct { a }": [("kernel", ".kernel k direct { a }")],
      "void f() { }\n.kernel k { a }": [("kernel", ".kernel k { a }")],
      "#include <a.h>\n.kernel k { a }": [("kernel", ".kernel k { a }")],
      ".kernel k { a { b } c }": [("kernel", ".kernel k { a { b } c }")],
      ".kernel k { /* } */ \"}\" '}' }": [("kernel", ".kernel k { /* } */ \"}\" '}' }")],
      ".kernel j { }\n.kernel k { }": [("kernel", ".kernel j { }"), ("kernel", ".kernel k { }")],
    }
    for text, expected in cases.items():
      with self.subTest(text=text):
        self.assertEqual(found(text), expected)

  def test_plain_c_is_not_a_block(self):
    cases = [
      "struct kernel { int a; };",
      "typedef struct { int a; } kernel;",
      "int kernel = 1;",
      "kernel_t kernel;",
      "kernel foo;",
      "kernel { }",
      "void f() { .kernel k { } }",
      "#define X .kernel k {\nint a;",
      "// .kernel k {\nint a;",
      "const char* s = \".kernel k {\";",
    ]
    for text in cases:
      with self.subTest(text=text):
        self.assertEqual(find_blocks(text), [])

  def test_unterminated_block(self):
    with self.assertRaises(ValueError) as ctx:
      find_blocks("int a;\n.kernel k {\n x\n")
    self.assertIn("line 2", str(ctx.exception))


class RenderTest(unittest.TestCase):
  def test_blocks_removed_and_lines_kept(self):
    text = "volatile Buffer x[1];\n.kernel k direct {\n  Transfer t = { type: words, mode: basic, memory: x, count: 0 };\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n}\n@kernel k config, exec\nvoid f(void) { }\nint b;\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertTrue(out.startswith('#line 1 "t.vmeg.c"\nvolatile u32 __attribute__((aligned(64))) x[1];\n'))
    self.assertIn('#line 5 "t.vmeg.c"', out)
    self.assertEqual(out.count("static inline void kTLoad(volatile u32* memory, u32 spadOffset) {"), 1)
    self.assertLess(out.index("static inline void kTLoad"), out.index("void f(void) {"))
    self.assertTrue(out.endswith('void f(void) {\n  vmeLibEnable();\n  kTLoad(x, VME_TOP_BUFF0_WOFF);\n  meCoreDMACPrimWaitTransferFinish();\n  vmeLibStart();\n  k();\n  vmeLibFinish();\n  vmeLibDisable();\n#line 7 "t.vmeg.c"\n }\nint b;\n'))

  def test_decorator(self):
    text = ".kernel k direct {\n}\n@kernel k config, exec\n\n/* c */\nstatic void run(int a) { }\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertNotIn("@", out)
    self.assertIn("static void run(int a) {", out)
    self.assertIn("\n  k();", out)
    bad = ["@kernel\nvoid run() { }\n", "@kernel k config, exec\nrun() { }\n", "@kernel k config, exec\nint x;\n", "@kernel k config, exec\nvoid run();\n", "@other k\nvoid run() { }\n", "@kernel k config, exec\n"]
    for text in bad:
      with self.subTest(text=text):
        with self.assertRaises(ValueError):
          find_blocks(text)

  def test_decorator_needs_a_known_kernel(self):
    text = ".kernel k direct {\n}\n@kernel z config, exec\nvoid run() { }\n"
    with self.assertRaises(ValueError) as ctx:
      render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("line 3", str(ctx.exception))
    self.assertIn("'z'", str(ctx.exception))

  def test_decorator_with_a_list_of_kernels(self):
    kernels = ".kernel a direct {\n}\n.kernel b direct {\n}\n.kernel c direct {\n}\n"
    ok = kernels + "@kernel a config, exec, b config, exec\nvoid r1() { }\n@kernel c config, exec\nvoid r2() { }\n"
    out = render(ok, find_blocks(ok), "t.vmeg.c")
    self.assertNotIn("@", out)
    again = kernels + "@kernel a config, exec, a config, exec, b config, exec\nvoid r() { }\n@kernel c config, exec\nvoid s() { }\n"
    render(again, find_blocks(again), "t.vmeg.c")
    unknown = kernels + "@kernel a config, exec, z config, exec\nvoid r() { }\n"
    with self.assertRaises(ValueError):
      render(unknown, find_blocks(unknown), "t.vmeg.c")
    forgotten = kernels + "@kernel a config, exec, b config, exec\nvoid r() { }\n"
    with self.assertRaises(ValueError):
      check_calls(project_registry([("t.vmeg.c", forgotten)]))

  def test_global_sources_must_be_declared_with_buffer(self):
    def build(declarations):
      return declarations + ".kernel k direct {\n  Transfer tx = { type: words, mode: basic, memory: x, count: 0 };\n  Transfer ty = { type: words, mode: basic, memory: y, count: 0 };\n  .load { .transfer = tx; .scope = global; .offsets { .top0 = 0; } }\n  .load { .transfer = ty; .scope = global; .offsets { .top1 = 0; } }\n}\n@kernel k config, exec\nvoid f() { }\n"
    ok = build("volatile Buffer x[1], y[1];\n")
    check_uses(project_registry([("t.vmeg.c", ok)]))
    for declarations in ["", "volatile Buffer x[1];\n", "volatile Buffer x[1], z[1];\n", "volatile u32 x[1], y[1];\n"]:
      text = build(declarations)
      with self.subTest(declarations=declarations):
        with self.assertRaises(ValueError) as ctx:
          check_uses(project_registry([("t.vmeg.c", text)]))
        self.assertIn("is not declared with Buffer in any file", str(ctx.exception))

  def test_local_sources_must_be_declared_in_every_decorated_function(self):
    kernel = ".kernel k direct {\n  Transfer t = { type: words, mode: basic, memory: x, count: 0 };\n  .load { .transfer = t; .offsets { .top0 = 0; } }\n}\n"
    declared = "void f() {\n  volatile Buffer x[1];\n}\n"
    ok = kernel + "@kernel k config, exec\n" + declared
    render(ok, find_blocks(ok), "t.vmeg.c")
    bad = [
      kernel + "@kernel k config, exec\nvoid f() { }\n",
      "volatile Buffer x[1];\n" + kernel + "@kernel k config, exec\nvoid f() { }\n",
      kernel + "@kernel k config, exec\nvoid f() {\n  if (1) { volatile Buffer x[1]; }\n}\n",
      kernel + "@kernel k config, exec\n" + declared + "@kernel k config, exec\nvoid g() { }\n",
    ]
    for text in bad:
      with self.subTest(text=text):
        with self.assertRaises(ValueError) as ctx:
          render(text, find_blocks(text), "t.vmeg.c")
        self.assertIn("(local load)", str(ctx.exception))
    both = kernel + "@kernel k config, exec\n" + declared + "@kernel k config, exec\n" + declared.replace("f()", "g()")
    render(both, find_blocks(both), "t.vmeg.c")

  def test_local_buffers_are_uploaded_in_the_decorated_function(self):
    text = ".kernel k direct {\n  Transfer ta = { type: words, mode: basic, memory: a, count: 3 };\n  Transfer tb = { type: words, mode: basic, memory: b, count: 1 };\n  .load { .transfer = ta; .offsets { .top0 = 0; } }\n  .load { .transfer = tb; .offsets { .base1 = 8; } }\n}\n@kernel k config, exec\nvoid f() {\n  volatile Buffer a[4], b[2];\n  go();\n}\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    body = out[out.index("void f() {"):]
    expected = ["void f() {", "volatile u32 __attribute__((aligned(64))) a[4], b[2];", "vmeLibEnable();",
      "kTaLoad(a, VME_TOP_BUFF0_WOFF);", "kTbLoad(b, VME_BASE_BUFF1_WOFF + 8);", "k();", "vmeLibDisable();"]
    position = 0
    for piece in expected:
      position = body.index(piece, position) + len(piece)
    self.assertLess(body.index("vmeLibDisable();"), body.index("go();"))

  def test_global_uploads_in_on_process(self):
    text = "int before;\nvoid meLibOnProcess(void)\n{\n  go();\n}\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertTrue(out.startswith('#line 1 "t.vmeg.c"\n'))
    self.assertNotIn("gen.h", out)
    self.assertEqual(out.count("vmegUploadGlobals();"), 0)
    self.assertIn("{\n  meCoreDcacheWritebackInvalidateAll();\n  meLibExceptionHandlerInit(0);\n  vmeLibEnable();\n  vmeLibWipe();\n  vmeLibDisable();\n#line 3", out)
    self.assertEqual(out.count("vmeLibWipe();"), 1)
    self.assertLess(out.index("vmeLibDisable();"), out.index("go();"))
    plain = "void f() { meLibOnProcess(); }\nvoid meLibOnProcess(void);\n"
    self.assertNotIn("vmegUploadGlobals", render(plain, find_blocks(plain), "t.vmeg.c"))
    twice = "void meLibOnProcess(void) { }\nvoid meLibOnProcess(int x) { }\n"
    with self.assertRaises(ValueError) as ctx:
      render(twice, find_blocks(twice), "t.vmeg.c")
    self.assertIn("line 2", str(ctx.exception))

  def test_one_block_when_on_process_carries_the_kernel(self):
    text = ".kernel k direct {\n  Transfer t = { type: words, mode: basic, memory: a, count: 3 };\n  .load { .transfer = t; .offsets { .top0 = 0; } }\n}\n@kernel k config, exec\nvoid meLibOnProcess(void)\n{\n  volatile Buffer a[4];\n  go();\n}\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertEqual(out.count("vmeLibEnable();"), 1)
    self.assertEqual(out.count("vmeLibDisable();"), 1)
    expected = ["volatile u32 __attribute__((aligned(64))) a[4];", "vmeLibEnable();", "vmeLibWipe();",
      "kTLoad(a, VME_TOP_BUFF0_WOFF);", "k();", "vmeLibDisable();", "go();"]
    position = out.index("void meLibOnProcess")
    for piece in expected:
      position = out.index(piece, position) + len(piece)
    other = ".kernel k direct {\n}\n@kernel k config, exec\nvoid run() { }\nvoid meLibOnProcess(void) { }\n"
    out = render(other, find_blocks(other), "t.vmeg.c")
    self.assertEqual(out.count("vmeLibEnable();"), 2)
    self.assertEqual(out.count("vmegUploadGlobals();"), 0)
    self.assertEqual(out.count("vmeLibWipe();"), 1)

  def test_kernel_block_is_removed_and_the_block_is_kept(self):
    text = ".kernel k direct {\n  icn skew = 0;\n}\nvoid f(void) {\n  before();\n  @kernel k config, exec {\n    after();\n  }\n  while (1) { }\n}\n"
    blocks = find_blocks(text)
    self.assertEqual([block[0] for block in blocks], ["kernel", "kernel-block", "kernel-block-end"])
    out = render(text, blocks, "t.vmeg.c")
    self.assertNotIn("@", out)
    self.assertEqual(out.count("vmeLibEnable();"), 1)
    self.assertEqual(out.count("vmeLibDisable();"), 1)
    for piece in ["before();", "{", "k();", "after();", "}", "while (1)"]:
      self.assertIn(piece, out)
    inside_kernel = ".kernel k direct {\n  icn skew = 0;\n}\n@kernel k config, exec\nvoid f() {\n  const char* s = \"@kernel k config, exec {\";\n}\n"
    self.assertEqual([block[0] for block in find_blocks(inside_kernel)], ["kernel", "decorator"])

  def test_context_is_an_alias_of_kernel(self):
    mixed = ".kernel a direct {\n}\n.context b direct {\n}\n@context a config, exec, b config, exec\nvoid run() { }\n"
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
    kernel = ".kernel k direct {\n  icn skew = 0;\n}\n"
    with self.assertRaises(ValueError) as ctx:
      check_calls(project_registry([("t.vmeg.c", kernel)]))
    self.assertIn("t.vmeg.c: line 1", str(ctx.exception))
    self.assertIn("'k'", str(ctx.exception))
    text = kernel + "@kernel k config, exec\nvoid run() { }\n"
    check_calls(project_registry([("t.vmeg.c", text)]))
    check_calls(project_registry([("a.vmeg.c", kernel), ("b.vmeg.c", "@kernel k config, exec\nvoid run() { }\n")]))

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


class EmulateTest(unittest.TestCase):
  def test_both_forms_give_the_same_blocks(self):
    own_line = found('@emulate "sat-1"\n.kernel k direct { a }')
    same_line = found('@emulate "sat-1" .kernel k direct { a }')
    self.assertEqual([kind for kind, _ in own_line], ["emulate", "kernel"])
    self.assertEqual([kind for kind, _ in same_line], ["emulate", "kernel"])
    self.assertEqual(own_line[1], same_line[1])

  def test_bad_emulate_is_an_error_with_its_line(self):
    cases = {
      '@emulate\n.kernel k { }': "line 1: expected @emulate",
      '@emulate "bad id"\n.kernel k { }': "line 1: expected @emulate",
      '@emulate "a"\nvoid f() { }': "line 1: @emulate \"id\" must be followed by '.kernel name'",
      '@emulate "a"\n.kernel k { }\n@emulate "a"\n.kernel m { }': "line 3: the id \"a\" of @emulate is already used at line 1",
    }
    for text, message in cases.items():
      with self.subTest(text=text):
        with self.assertRaises(ValueError) as caught:
          find_blocks(text)
        self.assertIn(message, str(caught.exception))


class KernelBlockTest(unittest.TestCase):
  def test_kernel_block_in_a_function_is_wrapped_with_enable_call_and_disable(self):
    text = ".kernel k direct {\n}\nvoid f() {\n  @kernel k config, exec {\n    a();\n  }\n}\n"
    blocks = find_blocks(text)
    self.assertEqual([block[0] for block in blocks], ["kernel", "kernel-block", "kernel-block-end"])
    out = render(text, blocks, "x.vmeg.c")
    self.assertNotIn("@kernel", out)
    self.assertIn("  {\n    vmeLibEnable();\n    vmeLibStart();\n    k();\n    vmeLibFinish();\n    a();\n", out)
    self.assertLess(out.index("k();"), out.index("a();"))
    self.assertLess(out.index("a();"), out.index("vmeLibDisable();"))

  def test_a_kernel_block_keeps_its_indentation_and_leaves_no_line_of_spaces(self):
    text = (
      "volatile Buffer g[4];\n.kernel k direct {\n}\n"
      "void f() {\n  while (1) {\n    @kernel k exec {\n"
      "      Transfer u = { type: words, mode: basic, memory: g, count: 1 };\n"
      "      if (a()) {\n        .store { .transfer = u; .scope = global; .offsets { .base1 = 8; } }\n      }\n"
      "    }\n  }\n}\n"
    )
    out = render(text, find_blocks(text), "x.vmeg.c")
    self.assertIn("    {\n      vmeLibEnable();\n      vmeLibTrigger();\n      meCoreDMACPrimWaitVMEFinish();\n", out)
    self.assertIn("\n        fUStore(g, VME_BASE_BUFF1_WOFF + 8);\n", out)
    self.assertIn("\n      vmeLibDisable();\n#line 11 \"x.vmeg.c\"\n    }\n", out)
    self.assertEqual([line for line in out.split("\n") if line and not line.strip()], [])

  def test_the_disable_and_the_enable_of_two_blocks_in_a_row_leave_no_line_behind(self):
    text = ".kernel k direct {\n}\nvoid f() {\n  @kernel k config {\n  }\n  @kernel k exec {\n  }\n}\n"
    out = render(text, find_blocks(text), "x.vmeg.c")
    self.assertEqual(out.count("vmeLibEnable();"), 1)
    self.assertEqual(out.count("vmeLibDisable();"), 1)
    self.assertEqual([line for line in out.split("\n") if line and not line.strip()], [])

  def test_the_attributes_and_the_vmeg_for_of_a_kernel_block_are_taken_out_wherever_they_are(self):
    text = (
      ".kernel a direct {\n}\n"
      "void f() {\n"
      "  volatile Buffer m[4];\n"
      "  @kernel a config, exec {\n"
      "    Transfer t = { type: words, mode: basic, memory: m, count: 3 };\n"
      "    .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n"
      "    for p in 0..3 {\n      .load { .transfer = t; .offsets { top[1] = p * 4; } }\n    }\n"
      "    for (int i = 0; i < 2; i++) { go(i); }\n"
      "    if (x) {\n      .load { .transfer = t; }\n    }\n"
      "    while (y) { .store { .transfer = t; } }\n"
      "    after();\n"
      "  }\n}\n"
    )
    blocks = find_blocks(text)
    taken = [text[block[1]:block[3]] for block in blocks if block[0] == "block-statement"]
    self.assertEqual(taken, [
      "Transfer t = { type: words, mode: basic, memory: m, count: 3 };",
      ".load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }",
      "for p in 0..3 {\n      .load { .transfer = t; .offsets { top[1] = p * 4; } }\n    }",
      ".load { .transfer = t; }",
      ".store { .transfer = t; }",
    ])
    out = render(text, blocks, "x.vmeg.c")
    for kept in ["for (int i = 0; i < 2; i++) { go(i); }", "if (x) {", "while (y) {", "after();"]:
      self.assertIn(kept, out)
    for gone in [".load", ".store", "Transfer t", "for p in"]:
      self.assertNotIn(gone, out)

  def test_a_variable_of_a_kernel_block_is_taken_out_only_in_a_vmeg_context(self):
    text = (
      ".kernel a direct {\n}\n"
      "void f() {\n"
      "  @kernel a config, exec {\n"
      "    Transfer t = { type: words, mode: basic, memory: m, count: 3 };\n"
      "    if (x) {\n      Transfer bad = { type: words, mode: basic, memory: m, count: 1 };\n    }\n"
      "    {\n      Transfer inner = { type: words, mode: basic, memory: m, count: 1 };\n    }\n"
      "  }\n}\n"
    )
    blocks = find_blocks(text)
    taken = [text[block[1]:block[3]] for block in blocks if block[0] == "block-statement"]
    self.assertEqual(taken, [
      "Transfer t = { type: words, mode: basic, memory: m, count: 3 };",
      "Transfer inner = { type: words, mode: basic, memory: m, count: 1 };",
    ])
    out = render(text, blocks, "x.vmeg.c")
    self.assertIn("Transfer bad = { type: words, mode: basic, memory: m, count: 1 };", out)
    for gone in ["Transfer t", "Transfer inner"]:
      self.assertNotIn(gone, out)

  def test_block_sends_globals_then_locals(self):
    text = (
      "volatile Buffer g[4] = { 1 };\n"
      ".kernel a direct {\n  Transfer tg = { type: words, mode: basic, memory: g, count: 3 };\n  Transfer tx = { type: words, mode: basic, memory: x, count: 3 };\n  .load { .transfer = tg; .scope = global; .offsets { .top0 = 0; } }\n  .load { .transfer = tx; .scope = local; .offsets { .top1 = 0; } }\n}\n"
      ".kernel o direct {\n  Transfer tg = { type: words, mode: basic, memory: g, count: 3 };\n  .load { .transfer = tg; .scope = global; .offsets { .top2 = 0; } }\n}\n"
      "@kernel o config, exec\nvoid other() {\n}\n"
      "void f() {\n  volatile Buffer x[4];\n  @kernel a config, exec {\n  }\n}\n"
    )
    blocks = find_blocks(text)
    out = render(text, blocks, "x.vmeg.c")
    self.assertLess(out.index("VME_TOP_BUFF0_WOFF"), out.index("VME_TOP_BUFF1_WOFF"))
    self.assertLess(out.index("VME_TOP_BUFF1_WOFF"), out.index("a();"))

  def test_bad_kernel_block_is_an_error_with_its_line(self):
    cases = {
      "void f() {\n  @kernel {\n  }\n}\n": "line 2: expected a kernel name",
      "void f() {\n  @kernel k;\n}\n": "line 2: expected build, config, exec or async after the kernel name",
      "void f() {\n  @kernel nope config, exec {\n  }\n}\n": "line 2: @kernel refers to an unknown kernel 'nope'",
      ".kernel k {\n}\nvoid f() {\n  @kernel k config, exec {\n  }\n}\n": "line 1: kernel 'k' needs the option direct or memory",
      ".kernel k direct memory {\n}\nvoid f() {\n  @kernel k config, exec {\n  }\n}\n": "line 1: a kernel is either direct or memory, not both",
    }
    for text, message in cases.items():
      with self.subTest(text=text):
        with self.assertRaises(ValueError) as caught:
          render(text, find_blocks(text), "x.vmeg.c")
        self.assertIn(message, str(caught.exception))


KERNEL = ".kernel k direct {\n  Transfer t = { type: words, mode: basic, memory: g, count: 3 };\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n}\n"


class RegistryTest(unittest.TestCase):
  def failure(self, check, sources):
    with self.assertRaises(ValueError) as caught:
      check(project_registry(sources))
    return str(caught.exception)

  def test_an_array_or_a_kernel_defined_twice_is_an_error_but_not_an_extern(self):
    check_definitions(project_registry([("a.vmeg.c", "volatile Buffer g[4];\n"), ("b.vmeg.c", "extern Buffer g[4];\n")]))
    check_definitions(project_registry([("a.vmeg.c", "extern Buffer g[4];\n"), ("b.vmeg.c", "extern Buffer g[4];\n")]))
    self.assertEqual(
      self.failure(check_definitions, [("a.vmeg.c", "volatile Buffer g[4];\n"), ("b.vmeg.c", "\nvolatile Buffer g[4];\n")]),
      "b.vmeg.c: line 2: the array 'g' is already defined at a.vmeg.c line 1")
    self.assertEqual(
      self.failure(check_definitions, [("a.vmeg.c", ".kernel k direct {\n}\n"), ("b.vmeg.c", "\n.kernel k direct {\n}\n")]),
      "b.vmeg.c: line 2: the kernel 'k' is already defined at a.vmeg.c line 1")

  def test_the_array_of_a_global_line_must_be_defined_and_visible(self):
    check_uses(project_registry([("a.vmeg.c", "volatile Buffer g[4];\n" + KERNEL)]))
    check_uses(project_registry([("a.vmeg.c", "volatile Buffer g[4];\n"), ("b.vmeg.c", "extern Buffer g[4];\n" + KERNEL)]))
    check_uses(project_registry([("a.vmeg.c", "static volatile Buffer g[4];\n" + KERNEL)]))
    self.assertIn("is not declared with Buffer in any file", self.failure(check_uses, [("a.vmeg.c", KERNEL)]))
    self.assertIn("declared extern but defined in no file", self.failure(check_uses, [("a.vmeg.c", "extern Buffer g[4];\n" + KERNEL)]))
    self.assertIn("is static in a.vmeg.c line 1", self.failure(check_uses, [("a.vmeg.c", "static volatile Buffer g[4];\n"), ("b.vmeg.c", KERNEL)]))

  def test_extern_declaration_of_an_array_and_the_ones_a_file_needs(self):
    text = (
      "volatile Buffer g[4] = { 1, 2, 3, 4 };\n"
      "volatile Buffer a[2] = { 1, 2 }, b[3];\n"
      "const volatile Buffer c[] = { 5, 6 };\n"
      "volatile Buffer m[2][N + 1] = {\n  { 1 }, { 2 },\n};\n"
      "extern Buffer e[16];\n"
    )
    declarations = {definition["name"]: extern_declaration(definition) for definition in array_definitions("a.vmeg.c", text)}
    self.assertEqual(declarations, {
      "g": "extern volatile Buffer g[4];",
      "a": "extern volatile Buffer a[2];",
      "b": "extern volatile Buffer b[3];",
      "c": "extern const volatile Buffer c[];",
      "m": "extern volatile Buffer m[2][N + 1];",
      "e": "extern Buffer e[16];",
    })
    registry = project_registry([("a.vmeg.c", "volatile Buffer g[4] = { 1 };\n"), ("b.vmeg.c", KERNEL), ("c.vmeg.c", "extern Buffer g[4];\n" + KERNEL.replace("kernel k", "kernel j"))])
    self.assertEqual(needed_externs(registry, "a.vmeg.c"), [])
    self.assertEqual(needed_externs(registry, "b.vmeg.c"), ["extern volatile Buffer g[4];"])
    self.assertEqual(needed_externs(registry, "c.vmeg.c"), [])

  def test_a_kernel_of_another_file_is_called_with_its_prototype_extern_and_upload(self):
    a = "volatile Buffer g[4];\n" + KERNEL
    b = "int x;\nvoid f() {\n  @kernel k config, exec {\n  }\n}\n"
    registry = project_registry([("a.vmeg.c", a), ("b.vmeg.c", b)])
    check_calls(registry)
    out = translate(b, find_blocks(b), "b.vmeg.c", registry)
    self.assertIn("extern volatile u32 __attribute__((aligned(64))) g[4];\nvoid k();\n", out)
    self.assertIn("  {\n    vmeLibEnable();\n    kTLoad(g, VME_TOP_BUFF0_WOFF);\n    meCoreDMACPrimWaitTransferFinish();\n    vmeLibStart();\n    k();\n    vmeLibFinish();\n", out)
    self.assertIn("never called", self.failure(check_calls, [("a.vmeg.c", a)]))


def waits_after(names):
  text = "".join(f"  {name}(a);\n  {wait_marker(name)}\n" for name in names)
  return finish_calls(text).count("meCoreDMACPrimWaitTransferFinish();")


class WaitOfTheCallsTest(unittest.TestCase):
  def test_at_most_two_calls_of_the_same_function_share_a_wait(self):
    self.assertEqual([waits_after(["f"] * count) for count in (1, 2, 3, 4, 5)], [1, 1, 2, 2, 3])
    text = finish_calls("f(a);\n" + wait_marker("f") + "\nf(a);\n" + wait_marker("f") + "\nf(a);\n" + wait_marker("f") + "\n")
    self.assertEqual(text, "f(a);\nf(a);\nmeCoreDMACPrimWaitTransferFinish();\nf(a);\nmeCoreDMACPrimWaitTransferFinish();\n")

  def test_different_functions_keep_their_own_wait_also_a_load_then_a_store_of_the_same_transfer(self):
    self.assertEqual(waits_after(["fMatrixLoad", "fMaskLoad", "fMaskLoad"]), 2)
    self.assertEqual(waits_after(["fTLoad", "fTStore"]), 2)
    text = finish_calls("fTLoad(a);\n" + wait_marker("fTLoad") + "\nfTStore(a);\n" + wait_marker("fTStore") + "\n")
    self.assertEqual(text, "fTLoad(a);\nmeCoreDMACPrimWaitTransferFinish();\nfTStore(a);\nmeCoreDMACPrimWaitTransferFinish();\n")


if __name__ == "__main__":
  unittest.main()
