import os, re, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vmee.listing import emulations, format_listing
from vmeg.blocks import find_blocks, kernel_mode
from vmeg.kernel import emit_statement, new_env, new_state
from vmeg.parser import declare_statements, kernel_statements
from vmeg.pipeline import build_table_op, emit_pipeline_op, expand_flow, flow_operand
from vmeg.registry import check_calls, needed_prototypes, project_registry

def parse_kernel(source):
  block = next(item for item in find_blocks(source) if item[0] == "kernel")
  return kernel_mode(source, block), kernel_statements(source, block, {})

def expand_kernel(source):
  _, statements = parse_kernel(source)
  state, env = new_state(pipeline=True), new_env()
  for stmt in statements:
    emit_statement(stmt, env, [], state)
  return expand_flow(state, env)

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


class PipelineRegistryAndListingTest(unittest.TestCase):
  def test_registry_prototypes_calls_and_listing_for_pipeline_kernel(self):
    kernel_src = (
      "volatile Buffer a[16], out[16];\n@emulate \"pipe\"\n.kernel p pipeline {\n"
      "  Transfer in0 = { memory: a, count: 15 }, dst = { memory: out, count: 15 };\n"
      "  .load { .transfer = in0; .scope = global; .offsets { .top0 = 0; } }\n"
      "  .flow { .count = 15; .slot = top0 + 1; }\n  .store { .transfer = dst; .scope = global; }\n}\n"
    )
    caller_src = "@kernel p config | exec\nvoid run(void) { }\n"
    reg = project_registry([("p.vmeg.c", kernel_src), ("c.vmeg.c", caller_src)])
    entry = reg["kernels"]["p"][0]
    self.assertEqual((entry["mode"], entry["direct"]), ("pipeline", True))
    self.assertTrue(entry["stores"][0]["auto_store"])
    self.assertEqual(entry["stores"][0]["links"], [("BASE_0", 16, "", "out", False)])
    self.assertEqual(needed_prototypes(reg, "c.vmeg.c"), ["void p();"])
    check_calls(reg)
    with self.assertRaisesRegex(ValueError, "kernel 'p' is never called"):
      check_calls(project_registry([("p.vmeg.c", kernel_src)]))
    listed = format_listing(emulations(kernel_src), [])
    self.assertIn("kernel p (pipeline,", listed)
    self.assertIn("BASE_0  16 words  to out", listed)
    self.assertNotIn("<--", listed)


class PipelineFlowExpansionTest(unittest.TestCase):
  def test_expand_flow_unrolls_for_and_threads_slots_and_inputs(self):
    src = (
      "volatile Buffer buf[16];\n.kernel p pipeline {\n  Int base_k = 2;\n  Slot pre;\n"
      "  Transfer t = { memory: buf, count: 7 };\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; .base2 = 0; } }\n"
      "  .flow {\n    .count = base_k + 5;\n    Slot arr[2], tag = top0 + base_k;\n"
      "    for i in 0..1 { arr[i] = tag + i; }\n    pre = arr[0] + arr[1];\n"
      "    .slot = pre * base2;\n    .slot = slot + arr[1];\n  }\n}\n"
    )
    flow = expand_kernel(src)
    self.assertEqual((flow["count"], flow["inputs"], flow["output"]), (7, ["BASE_2", "TOP_0"], 5))
    self.assertEqual([step["target"] for step in flow["steps"]], ["tag", "arr[0]", "arr[1]", "pre", None, None])
    self.assertEqual(flow["steps"][0]["expr"], ("bin", "+", ("name", "top0"), ("num", 2)))
    self.assertEqual(flow["steps"][5]["expr"], ("bin", "+", ("pipe_ref", 4), ("pipe_ref", 2)))
    self.assertEqual(expand_kernel(".kernel p pipeline { .flow { .count = 0; .slot = top0; } }\n")["count"], 0)
    self.assertEqual(expand_kernel(".kernel p pipeline { .flow { .count = 1023; .slot = top3; } }\n")["count"], 1023)

  def test_expand_flow_rejects_invalid_flow_slots_counts_and_vars(self):
    decl = "volatile Buffer buf[4];\n@declare { Agu a[1]; Staging g; Transfer t = { memory: buf, count: 1 }; }\n"
    cases = [
      (".kernel p pipeline { Int x = 1; }\n", "pipeline kernel needs a .flow block"),
      (".kernel p pipeline { .flow { .count = 1; .slot = top0; } .flow { .count = 1; .slot = top0; } }\n", "duplicate .flow block"),
      (".kernel p pipeline { .flow { .slot = top0; } }\n", ".flow needs .count and at least one .slot assignment"),
      (".kernel p pipeline { .flow { .count = 1; } }\n", ".flow needs .count and at least one .slot assignment"),
      (".kernel p pipeline { .flow { .count = 1; .count = 2; .slot = top0; } }\n", "duplicate .count in .flow"),
      (".kernel p pipeline { .flow { .count = -1; .slot = top0; } }\n", ".count in .flow must be a number from 0 to 1023"),
      (".kernel p pipeline { .flow { .count = 1024; .slot = top0; } }\n", ".count in .flow must be a number from 0 to 1023"),
      (".kernel p pipeline { .flow { .count = top0; .slot = top0; } }\n", ".count in .flow must be a number from 0 to 1023"),
      (".kernel p pipeline { Slot slot; }\n", "slot is reserved in a pipeline kernel"),
      (".kernel p pipeline { Slot s = top0; }\n", "Slot assignment must be inside .flow"),
      (".kernel p pipeline { .flow { .count = 1; .slot = slot + 1; } }\n", "'slot' is read before any .slot assignment"),
      (".kernel p pipeline { .flow { .count = 1; slot = top0; .slot = top0; } }\n", "unknown Slot variable 'slot'"),
      (".kernel p pipeline { Slot s; .flow { .count = 1; .slot = s; } }\n", "the Slot variable 's' is read before it is set"),
      (".kernel p pipeline { Slot s; .flow { .count = 1; s = top0; s = top1; .slot = s; } }\n", "the Slot variable 's' is already set"),
      (".kernel p pipeline { Slot s; .flow { .count = 1; .slot = s[0]; } }\n", "'s' is not an array"),
      (".kernel p pipeline { Slot a[2]; .flow { .count = 1; .slot = a; } }\n", "'a' is an array, write a[...]"),
      (".kernel p pipeline { Slot a[2]; .flow { .count = 1; .slot = a[2]; } }\n", "a[2]: index out of range (0 to 1)"),
      (".kernel p pipeline { .flow { .count = 1; .slot = top4; } }\n", "top4 is out of range (top0 to top3, base0 to base3)"),
      (".kernel p pipeline { .flow { .count = 1; .slot = missing; } }\n", "unknown variable 'missing' in .flow"),
      (".kernel p pipeline { .flow { .count = 1; .slot = missing[0]; } }\n", "unknown array 'missing' in .flow"),
      (decl + ".kernel p pipeline { .flow { .count = 1; .slot = a[0]; } }\n", "'a' is an Agu variable and cannot be used in .flow"),
      (decl + ".kernel p pipeline { .flow { .count = 1; .slot = g; } }\n", "'g' is a Staging variable and cannot be used in .flow"),
      (decl + ".kernel p pipeline { .flow { .count = 1; .slot = t; } }\n", "'t' is a Transfer variable and cannot be used in .flow"),
    ]
    for source, expected in cases:
      with self.subTest(source=source), self.assertRaisesRegex(ValueError, re.escape(expected)):
        expand_kernel(source)


class PipelineMicroOpBuilderTest(unittest.TestCase):
  def test_emit_flow_operand_and_build_table_op(self):
    ops, slot_refs, seen = [], {0: ("op_ref", 7)}, []
    def stub_lower(expr, cur_ops, cur_slots, compat):
      seen.append(expr)
      return ("op_ref", 9)
    self.assertEqual(emit_pipeline_op(ops, {"kind": "pass", "source": "TOP_0", "numbers": {}, "sat": None}), ("op_ref", 0))
    self.assertEqual(ops[0]["id"], 0)
    self.assertEqual(flow_operand(("op_ref", 2), ops, slot_refs, None, stub_lower), ("op_ref", 2))
    self.assertEqual(flow_operand(("pipe_ref", 0), ops, slot_refs, None, stub_lower), ("op_ref", 7))
    self.assertEqual(flow_operand(("name", "base2"), ops, slot_refs, None, stub_lower), "BASE_2")
    self.assertEqual(flow_operand(("num", 99), ops, slot_refs, None, stub_lower), ("op_ref", 1))
    self.assertEqual(ops[1], {"id": 1, "kind": "cst", "source": None, "numbers": {"c": 99}, "sat": None})
    self.assertEqual(flow_operand(("bin", "+", ("name", "top0"), ("num", 1)), ops, slot_refs, None, stub_lower), ("op_ref", 9))
    self.assertEqual(len(seen), 1)
    ref_shf = build_table_op("add_shf", {"a": ("pipe_ref", 0), "b": ("name", "top1"), "n": ("num", 3)}, ops, slot_refs, None, stub_lower)
    self.assertEqual((ref_shf, ops[2]["back"], ops[2]["front"], ops[2]["numbers"]), (("op_ref", 2), ("op_ref", 7), "TOP_1", {"n": 3}))
    self.assertEqual(ops[build_table_op("bak_shr", {"x": ("name", "top0"), "n": ("num", 4)}, ops, slot_refs, None, stub_lower)[1]]["shift"], 4)
    self.assertEqual(ops[build_table_op("cst", {"c": ("num", 12)}, ops, slot_refs, None, stub_lower)[1]]["source"], None)
    with self.assertRaisesRegex(ValueError, "clamp low must be a number"):
      build_table_op("clamp", {"x": ("name", "top0"), "low": ("name", "top1"), "high": ("num", 5)}, ops, slot_refs, None, stub_lower, label="clamp")
    with self.assertRaisesRegex(ValueError, "the shift must be 0 to 63"):
      build_table_op("bak_shr", {"x": ("name", "top0"), "n": ("num", 64)}, ops, slot_refs, None, stub_lower)


if __name__ == "__main__":
  unittest.main()
