import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmee.listing import emulations
from vmeg.blocks import find_blocks
from vmegc import render


def translated(text):
  return render(text, find_blocks(text), "t.vmeg.cpp")


def code(text):
  return "\n".join(line for line in translated(text).split("\n") if not line.startswith("#line") and line.strip())


KERNEL = ".kernel k direct {\n  Agu t = { count: 3 };\n  .pe0 { .top = t; .spad = top0 + top0; }\n}\n"
CALL = "@kernel k config | exec {\n%s}\n"


class DeclareTest(unittest.TestCase):
  def test_a_declare_block_gives_its_variables_to_the_kernels_and_the_calls_of_its_level_and_below(self):
    places = (
      "@declare { Int a = 1; }\n"
      "void f(void) {\n  @declare { Int b = 2; }\n  @emulate \"e\" {\n    @declare { Int c = 3; }\n    @kernel k config | exec { }\n  }\n}\n"
    )
    self.assertEqual([kind for kind, _, _, _ in find_blocks(KERNEL + places)], ["kernel", "declare", "declare", "emulate-block", "declare", "kernel-block", "kernel-block-end", "emulate-block-end"])
    self.assertNotIn("declare", translated(KERNEL + places))
    errors = {
      "@declare\nvoid f(void) {}\n": "line 1: @declare is followed by a block { ... }",
      "@declare {\n  Int x = 1;\n": "line 1: unterminated @declare block",
      "@declare {\n  Int x = 1;\n  .load { .transfer = t; }\n}\n": "line 3: only Agu, Staging, Transfer and Int variables are accepted in @declare",
      "@declare {\n  Int x = 1;\n  Int x = 2;\n}\n": "line 3: 'x' is already declared in a @declare, at line 2",
    }
    for text, message in errors.items():
      with self.subTest(text=text):
        with self.assertRaises(ValueError) as ctx:
          translated(text)
        self.assertEqual(str(ctx.exception), message)
    shared = "@declare { Int stride = 8; Agu top = { count: 3, step: stride }; }\n.kernel a direct {\n  .pe0 { .top = top; .spad = top0 + top0; }\n}\n.kernel b direct {\n  .pe2 { .top = top; .spad = top2 + top2; }\n}\n@kernel a config | exec\nvoid fa(void) {}\n@kernel b config | exec\nvoid fb(void) {}\n"
    out = code(shared)
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(8), 3);", out)
    self.assertIn("vme_pe2(agu_top(COUNT), agu_step(8), 3);", out)
    staging = "@declare { Staging x; Agu top = { count: 3 }, write = { count: 3, cyc: auto }; }\n.kernel a direct {\n  .pe0 { .top = top; .write = write; x = top0 + top0; .spad = x + top0; }\n}\n.kernel b direct {\n  .pe2 { .top = top; .write = write; x = top2 + top2; .spad = x + top2; }\n}\n@kernel a config | exec\nvoid fa(void) {}\n@kernel b config | exec\nvoid fb(void) {}\n"
    out = code(staging)
    self.assertIn("vme_mux(STAGING_0, TOP_0)", out)
    self.assertIn("vme_mux(STAGING_2, TOP_2)", out)
    scoped = KERNEL + "void f(void) {\n  @declare { Int local = 2; }\n  @kernel k config | exec {\n    Int local = 5;\n  }\n}\n"
    with self.assertRaisesRegex(ValueError, "line 8: 'local' is defined twice"):
      translated(scoped)
    other = KERNEL + "void f(void) {\n  @declare { Int local = 2; }\n  @kernel k config | exec { }\n}\nvoid g(void) {\n  @kernel k config | exec {\n    Int local = 5;\n  }\n}\n"
    translated(other)
    with self.assertRaisesRegex(ValueError, "line 3: 'stride' is defined twice"):
      translated("@declare { Int stride = 8; }\n.kernel k direct {\n  Int stride = 4;\n  Agu t = { count: 3 };\n  .pe0 { .top = t; .spad = top0 + top0; }\n}\n@kernel k config | exec\nvoid f(void) {}\n")
    local_transfer = "volatile Buffer a[4];\n.kernel k direct {\n  Transfer in = { memory: a, count: 3 };\n  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }\n  Agu t = { count: 3 };\n  .pe0 { .top = t; .spad = top0 + top0; }\n}\n@kernel k config | exec\nvoid f(void) {}\n"
    declared_transfer = "volatile Buffer a[4];\n@declare { Transfer in = { memory: a, count: 3 }; }\n.kernel k direct {\n  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }\n  Agu t = { count: 3 };\n  .pe0 { .top = t; .spad = top0 + top0; }\n}\n@kernel k config | exec\nvoid f(void) {}\n"
    declared = code(declared_transfer)
    self.assertIn("typedef struct { volatile u32* memory; u32 count; } VmegTransfer;", declared)
    self.assertIn("VmegTransfer vmeVarIn = { a, 3 };", declared)
    self.assertIn("vmeTransferLoad(&vmeVarIn, VME_TOP_BUFF0_WOFF);", declared)
    self.assertIn("static inline void vmeTransferLoad(const VmegTransfer* transfer, u32 spadOffset) {", declared)
    self.assertIn("vme_dma(ITERATION, DIMS, transfer->count);", declared)
    self.assertNotIn("kInLoad", declared)
    self.assertIn("kInLoad(a, VME_TOP_BUFF0_WOFF);", code(local_transfer))
    words = "volatile Buffer a[4];\n@declare {\n  Int last = 3;\n  Transfer(Words) w = { memory: a, count: last, gap: 1, step: 4, group: { size: 3, outer: 16, inner: 1 } };\n  Transfer(Words) z = { memory: a, count: 3 };\n}\n"
    out = code(words)
    self.assertIn("typedef struct { volatile u32* memory; u32 count; u32 gap; u32 step; u32 groupSize; u32 groupOuter; u32 groupInner; } VmegTransferWords;", out)
    self.assertIn("VmegTransferWords vmeVarW = { a, 3, 1, 4, 3, 16, 1 };", out)
    self.assertIn("VmegTransferWords vmeVarZ = { a, 3, 0, 0, 0, 0, 0 };", out)
    self.assertNotIn("VmegTransfer;", out)
    used = "volatile Buffer a[16], b[16];\n@declare {\n  Transfer in = { memory: a, count: 15 };\n  Transfer(Words) w = { memory: b, count: 15, step: 4 };\n}\n.kernel k direct {\n  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }\n  .load { .transfer = w; .scope = global; .offsets { .top1 = 0; } }\n  .store { .transfer = in; .scope = global; .offsets { .base0 = 0; } }\n  Agu t = { count: 15 };\n  .pe0 { .top = t; .spad = top0 + top0; }\n}\n@kernel k config | exec\nvoid f(void) {}\nvoid g(void) {\n  @kernel k config | exec {\n    .load { .transfer = in; .scope = global; .offsets { .top2 = 4; } }\n  }\n}\n"
    out = code(used)
    for name in ("vmeTransferLoad", "vmeTransferLoadWords", "vmeTransferStore"):
      self.assertEqual(out.count(f"static inline void {name}("), 1)
    self.assertIn("vme_dma(ITERATION, DIMS, transfer->count, transfer->gap);", out)
    self.assertIn("vme_dma(CTRL, VALUE, 0x58);", code(used.replace(".load { .transfer = w;", ".store { .transfer = w;")))
    self.assertEqual(out.count("vmeTransferLoad(&vmeVarIn, VME_TOP_BUFF0_WOFF);"), 2)
    self.assertIn("vmeTransferLoad(&vmeVarIn, VME_TOP_BUFF2_WOFF + 4);", out)
    self.assertIn("vmeTransferLoadWords(&vmeVarW, VME_TOP_BUFF1_WOFF);", out)
    self.assertIn("vmeTransferStore(&vmeVarIn, VME_BASE_BUFF0_WOFF);", out)
    waits = "volatile Buffer a[16], b[16];\n@declare {\n  Transfer in = { memory: a, count: 15 };\n  Transfer other = { memory: b, count: 7 };\n}\n.kernel k direct {\n  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }\n  .load { .transfer = %s; .scope = global; .offsets { .top1 = 0; } }\n  Agu t = { count: 15 };\n  .pe0 { .top = t; .spad = top0 + top0; }\n}\n@kernel k config | exec\nvoid f(void) {}\n"
    self.assertEqual(code(waits % "in").count("meCoreDMACPrimWaitTransferFinish();"), 1)
    spread = "volatile Buffer a[16], b[16];\n@declare {\n  Int last = 7;\n  Transfer(Words) w = { memory: a, count: 15, step: 4, group: { size: 3, outer: 16, inner: 1 } };\n}\n.kernel k direct {\n  .load { .transfer = { ...w, memory: b, count: last, group: { ..., outer: 8 } }; .scope = global; .offsets { .top0 = 0; .top1 = 4; } }\n  .store { .transfer = { ...w, group: { size: 1, outer: 2, inner: 3 } }; .scope = global; .offsets { .base0 = 0; } }\n  Agu t = { count: 15 };\n  .pe0 { .top = t; .spad = top0 + top0; }\n}\n@kernel k config | exec\nvoid f(void) {}\n"
    out = code(spread)
    for line in ("VmegTransferWords vmeCopyVar = vmeVarW;", "vmeCopyVar.memory = b;", "vmeCopyVar.count = 7;", "vmeCopyVar.groupOuter = 8;", "vmeTransferLoadWords(&vmeCopyVar, VME_TOP_BUFF0_WOFF);", "vmeTransferLoadWords(&vmeCopyVar, VME_TOP_BUFF1_WOFF + 4);", "vmeCopyVar.groupSize = 1;", "vmeCopyVar.groupInner = 3;", "vmeTransferStoreWords(&vmeCopyVar, VME_BASE_BUFF0_WOFF);"):
      self.assertIn(line, out)
    self.assertNotIn("vmeCopyVar.groupSize = 3", out)
    listed = "volatile Buffer one[16], two[16];\n@declare {\n  Int last = 7;\n  Transfer in = { memory: one, count: 15 };\n  Transfer(Words) w = { memory: one, count: 15, step: 4, group: { size: 3, outer: 16, inner: 1 } };\n}\n.kernel d direct {\n  Agu t = { count: 3 };\n  .pe0 { .top = t; .spad = top0 + top0; }\n}\nvoid meLibOnProcess(void) {\n  @emulate \"e\" {\n    @kernel d config {\n      .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }\n      .load { .transfer = { ...in, memory: two, count: last }; .scope = global; .offsets { .top1 = 0; } }\n      .load { .transfer = { ...w, count: last, group: { ..., outer: 8 } }; .scope = global; .offsets { .top2 = 0; } }\n    }\n    @kernel d exec {\n      .store { .transfer = { ...in, memory: two, count: 3 }; .scope = global; .offsets { .base0 = 0; } }\n    }\n  }\n}\n"
    entry = emulations(listed)[0]
    self.assertEqual([(link[0], link[1], link[3], link[5]) for link in entry["global"]], [("TOP_0", 16, "one", False), ("TOP_1", 8, "two", False), ("TOP_2", 8, "one", True)])
    self.assertEqual([(link[0], link[1], link[3]) for link in entry["stores"]["global"]], [("BASE_0", 4, "two")])
    with self.assertRaisesRegex(ValueError, r"line 2: Transfer\(Halves\) is not generated yet"):
      translated("volatile Buffer a[4];\n@declare { Transfer(Halves) h = { memory: a, count: 3 }; }\n")


if __name__ == "__main__":
  unittest.main()
