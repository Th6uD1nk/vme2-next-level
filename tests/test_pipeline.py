import os, re, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vmeg.blocks import find_blocks, kernel_mode
from vmeg.parser import declare_statements, kernel_statements

def parse_kernel(source):
  block = next(item for item in find_blocks(source) if item[0] == "kernel")
  return kernel_mode(source, block), kernel_statements(source, block, {})

class PipelineParserTest(unittest.TestCase):
  def test_pipeline_mode_and_flow_parsing(self):
    source = (
      "volatile Buffer a[16], out[16];\n.kernel p pipeline {\n  Transfer in0 = { memory: a, count: 15 }, dst = { memory: out, count: 15 };\n"
      "  .load { .transfer = in0; .scope = global; .offsets { .top0 = 0; } }\n  .flow {\n    .count = 15;\n    Slot s0 = top0 + 1, arr[2];\n"
      "    for i in 0..1 { Int c = i + 2; arr[i] = s0 + c; .slot = arr[i] & 0xff; }\n    .slot = (slot & 0xff) >> 2;\n  }\n  .store { .transfer = dst; .scope = global; }\n}\n"
    )
    mode, statements = parse_kernel(source)
    self.assertEqual(mode, "pipeline")
    self.assertEqual([item[0] for item in statements], ["transferdecl", "transferdecl", "load", "flow", "store"])
    self.assertEqual([item[0] for item in statements[3][1]], ["flowcount", "slotdecl", "slotset", "slotdecl", "for", "flowslot"])

  def test_pipeline_rejects_forbidden_constructs(self):
    cases = [(s, f"{d} declarations are not allowed in a pipeline kernel") for d in ("Agu", "Staging") for s in (f"{d} x;", f".flow {{ {d} x; }}")] + [
      (s, f"{w} not allowed in a pipeline kernel") for s, w in (
        (".pe0 { .spad = top0 + 1; }", ".pe0 is"), ("pe[0] { .spad = top0 + 1; }", "pe blocks are"),
        (".regs { .swen = 0; }", ".regs is"), (".params { int n; }", ".params is"), ("icn xpcr = 1;", "icn is"), (".flow { icn xpcr = 1; }", "icn is"),
      )
    ] + [
      ("Transfer d = { memory: out, count: 3 }; .store { .transfer = d; .scope = global; .offsets { .base0 = 0; } }", ".offsets is not allowed on .store in a pipeline kernel"),
      (".flow { Transfer t = { memory: a, count: 3 }; }", "Transfer declarations must be outside .flow"), (".flow { .top0 = 0; }", "unknown attribute '.top0' of .flow (.count, .slot)"),
    ]
    for body, expected in cases:
      with self.subTest(body=body), self.assertRaisesRegex(ValueError, re.escape(expected)):
        parse_kernel(f".kernel p pipeline {{\n  {body}\n}}\n")

  def test_non_pipeline_rejects_flow_and_slot_while_declare_remains_valid(self):
    for bad, expected in ((".kernel d direct { .flow { .count = 3; } }\n", ".flow is only allowed in a pipeline kernel"), (".kernel d direct { Slot s; }\n", "Slot is only allowed in a pipeline kernel")):
      with self.assertRaisesRegex(ValueError, re.escape(expected)):
        parse_kernel(bad)
    with self.assertRaisesRegex(ValueError, "Slot is only allowed in a pipeline kernel"):
      declare_statements("@declare { Slot s; }\n", find_blocks("@declare { Slot s; }\n")[0])
    shared = "@declare { Agu a = { count: 3 }; Transfer t = { memory: buf, count: 3 }; }\n.kernel p pipeline {\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n  .flow { .count = 3; .slot = top0 + 1; }\n}\n"
    self.assertEqual([item[0] for item in parse_kernel(shared)[1]], ["agudecl", "declaredtransfer", "load", "flow"])


if __name__ == "__main__":
  unittest.main()
