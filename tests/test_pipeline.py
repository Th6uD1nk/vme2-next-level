import os, re, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vmee.listing import emulations, format_listing
from vmeg.blocks import find_blocks, kernel_mode
from vmeg.kernel import emit_statement, new_env, new_state
from vmeg.parser import declare_statements, kernel_statements
from vmeg.pipeline import apply_sat_op, build_table_op, compile_shift_op, emit_pipeline_op, expand_flow, flatten_flow, flow_operand, lower_child_op, lower_flow_call, unpack_compound, unpack_cond, unwrap_round
from vmeg.registry import check_calls, needed_prototypes, project_registry
from vmeg.selector import choose_opcode

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

  def test_unwrap_round_and_apply_sat_op(self):
    inner = ("bin", "+", ("name", "top0"), ("name", "top1"))
    self.assertEqual(unwrap_round(inner), (inner, False))
    self.assertEqual(unwrap_round(("call", "round", [inner])), (inner, True))
    self.assertEqual(unwrap_round(("call", "sat", [("call", "round", [inner]), ("num", 8)])), (("call", "sat", [inner, ("num", 8)]), True))
    ops = []
    def stub_add(expr, cur_ops, cur_slots, compat):
      return emit_pipeline_op(cur_ops, {"kind": "add", "front": "TOP_0", "back": "TOP_1", "numbers": {}, "sat": None})
    def nested_sat(expr, cur_ops, cur_slots, compat):
      return apply_sat_op(expr, cur_ops, cur_slots, compat, stub_add)
    slots = {0: emit_pipeline_op(ops, {"kind": "add", "front": "TOP_0", "back": "TOP_1", "numbers": {}, "sat": None})}
    self.assertEqual(apply_sat_op(("call", "sat", [("name", "top0"), ("num", 8)]), ops, slots, None, stub_add), ("op_ref", 1))
    self.assertEqual((ops[1]["kind"], ops[1]["source"], ops[1]["sat"]), ("pass", "TOP_0", 8))
    self.assertEqual(apply_sat_op(("call", "sat", [("pipe_ref", 0), ("num", 6)]), ops, slots, None, stub_add), ("op_ref", 2))
    self.assertIsNone(ops[0]["sat"])
    self.assertEqual((ops[2]["kind"], ops[2]["source"], ops[2]["sat"]), ("pass", ("op_ref", 0), 6))
    self.assertEqual(ops[apply_sat_op(("call", "sat", [("num", 12), ("num", 5)]), ops, slots, None, stub_add)[1]]["kind"], "cst")
    self.assertEqual(ops[3]["sat"], 5)
    self.assertEqual(ops[apply_sat_op(("call", "sat", [inner, ("num", 7)]), ops, slots, None, stub_add)[1]]["sat"], 7)
    self.assertEqual(apply_sat_op(("call", "sat", [("call", "sat", [inner, ("num", 8)]), ("num", 4)]), ops, slots, None, nested_sat), ("op_ref", 6))
    self.assertEqual((ops[5]["sat"], ops[6]["kind"], ops[6]["source"], ops[6]["sat"]), (8, "pass", ("op_ref", 5), 4))
    for bad, fn, msg in (
      (("call", "round", []), unwrap_round, "round takes 1 argument"),
      (("call", "round", [("call", "round", [inner])]), unwrap_round, "an operation takes only one round"),
      (("call", "sat", [inner]), lambda e: apply_sat_op(e, ops, slots, None, stub_add), "sat takes 2 arguments"),
      (("call", "sat", [inner, ("name", "top0")]), lambda e: apply_sat_op(e, ops, slots, None, stub_add), "sat bits must be a number"),
      (("call", "sat", [inner, ("num", 32)]), lambda e: apply_sat_op(e, ops, slots, None, stub_add), "sat bits out of range"),
    ):
      with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, msg):
        fn(bad)

  def test_compile_shift_op(self):
    def stub_lower(expr, cur_ops, cur_slots, compat):
      if expr[0] == "call" and expr[1] == "sat":
        return apply_sat_op(expr, cur_ops, cur_slots, compat, stub_lower)
      if expr[1] == "&":
        return emit_pipeline_op(cur_ops, {"kind": "and_cst", "source": "TOP_0", "numbers": {"c": 255}, "sat": None})
      if expr[3] == ("num", 5):
        return emit_pipeline_op(cur_ops, {"kind": "add_cst", "source": "TOP_0", "numbers": {"c": 5}, "sat": None})
      return emit_pipeline_op(cur_ops, {"kind": "add", "front": "TOP_0", "back": "TOP_1", "numbers": {}, "sat": None})
    ops = []
    slots = {0: emit_pipeline_op(ops, {"kind": "add", "front": "TOP_0", "back": "TOP_1", "numbers": {}, "sat": None})}
    add_e, and_e, cst_e = ("bin", "+", ("name", "top0"), ("name", "top1")), ("bin", "&", ("name", "top0"), ("num", 255)), ("bin", "+", ("name", "top0"), ("num", 5))
    self.assertEqual(compile_shift_op(("bin", ">>", ("call", "sat", [("call", "round", [add_e]), ("num", 8)]), ("num", 2)), ops, slots, None, stub_lower), ("op_ref", 1))
    self.assertEqual((ops[1]["kind"], ops[1]["sat"], ops[1]["shift"], ops[1]["round"]), ("add", 8, 2, True))
    self.assertEqual(compile_shift_op(("bin", ">>", and_e, ("num", 2)), ops, slots, None, stub_lower), ("op_ref", 3))
    self.assertEqual((ops[2]["kind"], ops[3]["kind"], ops[3]["source"], ops[3]["numbers"], ops[3]["shift"]), ("and_cst", "add_cst", ("op_ref", 2), {"c": 0}, 2))
    self.assertEqual(compile_shift_op(("bin", ">>", cst_e, ("num", 2)), ops, slots, None, stub_lower, round_flag=True), ("op_ref", 5))
    self.assertEqual((ops[4].get("shift"), ops[5]["kind"], ops[5]["numbers"], ops[5]["shift"]), (None, "add_cst", {"c": 2}, 2))
    self.assertEqual(ops[compile_shift_op(("bin", "<<", add_e, ("num", 3)), ops, slots, None, stub_lower)[1]]["kind"], "shl_cst")
    self.assertEqual(ops[compile_shift_op(("bin", ">>>", add_e, ("num", 1)), ops, slots, None, stub_lower)[1]]["kind"], "shr_cst_u")
    self.assertEqual(ops[compile_shift_op(("bin", ">>", ("pipe_ref", 0), ("num", 4)), ops, slots, None, stub_lower)[1]]["source"], ("op_ref", 0))
    self.assertIsNone(ops[0].get("shift"))
    self.assertIsNone(compile_shift_op(("bin", "<<", ("name", "top0"), ("name", "top1")), ops, slots, None, stub_lower))
    for bad, rf, msg in (
      (("bin", ">>", ("call", "round", [add_e]), ("num", 2)), True, "only one round"),
      (("bin", ">>", ("name", "top0"), ("name", "top1")), True, "must be a number"),
      (("bin", ">>", add_e, ("num", 64)), False, "0 to 63"),
      (("bin", "<<", add_e, ("num", 2)), True, "not left shift"),
      (("bin", ">>>", add_e, ("num", 2)), True, "not >>>"),
    ):
      with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, msg):
        compile_shift_op(bad, ops, slots, None, stub_lower, rf)

  def test_unpack_cond_and_compound(self):
    ops, slots, calls = [], {}, []
    def stub_lower(expr, cur_ops, cur_slots, compat):
      calls.append(expr)
      return emit_pipeline_op(cur_ops, {"kind": "stub", "expr": expr})
    self.assertEqual(lower_child_op(("name", "top0"), ops, slots, None, stub_lower), ("name", "top0"))
    self.assertEqual(lower_child_op(("num", 7), ops, slots, None, stub_lower), ("num", 7))
    self.assertEqual(len(calls), 0)
    a1, b2 = ("bin", "+", ("name", "top0"), ("num", 1)), ("bin", "*", ("name", "base0"), ("num", 2))
    neg_u = unpack_cond(("cond", ("bin", "&", a1, ("num", 4)), ("neg", b2), b2), ops, slots, None, stub_lower)
    self.assertEqual(neg_u, ("cond", ("bin", "&", ("op_ref", 0), ("num", 4)), ("neg", ("op_ref", 1)), ("op_ref", 1)))
    self.assertEqual(choose_opcode(neg_u, None)[0], "sel_neg")
    calls.clear()
    ads_u = unpack_cond(("cond", ("bin", "&", a1, ("num", 4)), ("bin", "-", a1, ("num", 3)), ("bin", "+", a1, ("num", 3))), ops, slots, None, stub_lower)
    self.assertEqual((len(calls), choose_opcode(ads_u, None)[0]), (1, "sel_ads"))
    zer_u = unpack_cond(("cond", ("bin", "&", a1, ("num", 4)), ("num", 0), ("num", 9)), ops, slots, None, stub_lower)
    self.assertEqual(choose_opcode(zer_u, None)[0], "sel_cst_zer")
    self.assertEqual(unpack_cond(("cond", a1, ("num", 2), ("num", 3)), ops, slots, None, stub_lower), ("cond", ("op_ref", 4), ("num", 2), ("num", 3)))
    self.assertEqual(choose_opcode(unpack_compound(("not", ("bin", "&", a1, ("name", "base1"))), ops, slots, None, stub_lower), None)[0], "nand")
    self.assertEqual(choose_opcode(unpack_compound(("bin", "*", a1, b2), ops, slots, None, stub_lower), None)[0], "mul")

  def test_lower_flow_call(self):
    def stub_lower(expr, cur_ops, cur_slots, compat):
      return emit_pipeline_op(cur_ops, {"kind": "add", "front": "TOP_0", "back": "TOP_1", "numbers": {}, "sat": None})
    ops = []
    slots = {0: emit_pipeline_op(ops, {"kind": "add", "front": "TOP_0", "back": "TOP_1", "numbers": {}, "sat": None})}
    add_e = ("bin", "+", ("name", "top0"), ("name", "top1"))
    self.assertEqual(ops[lower_flow_call(("call", "sat", [("name", "top0"), ("num", 8)]), ops, slots, None, stub_lower)[1]], {"id": 1, "kind": "pass", "source": "TOP_0", "numbers": {}, "sat": 8})
    self.assertEqual(ops[lower_flow_call(("call", "round", [("bin", ">>", add_e, ("num", 2))]), ops, slots, None, stub_lower)[1]]["shift"], 2)
    self.assertTrue(ops[2]["round"])
    self.assertTrue(ops[lower_flow_call(("call", "round", [add_e]), ops, slots, None, stub_lower)[1]]["round"])
    r_pipe = lower_flow_call(("call", "round", [("pipe_ref", 0)]), ops, slots, None, stub_lower)
    self.assertEqual((ops[r_pipe[1]]["kind"], "round" in ops[r_pipe[1]], "round" in ops[0]), ("pass", False, False))
    r_clp = lower_flow_call(("call", "clamp", [add_e, ("num", -5), ("num", 5)]), ops, slots, None, stub_lower)
    self.assertEqual((ops[r_clp[1]]["kind"], ops[r_clp[1]]["source"][0], ops[r_clp[1]]["numbers"]), ("clamp", "op_ref", {"low": -5, "high": 5}))
    r_shrcst = lower_flow_call(("call", "shrcst", [("name", "top0"), ("num", 3)]), ops, slots, None, stub_lower)
    self.assertEqual((ops[r_shrcst[1]]["kind"], ops[r_shrcst[1]]["numbers"]), ("shr_cst", {"c": 3}))
    for bad, msg in (
      (("call", "round", []), "1 argument"),
      (("call", "round", [("call", "round", [("name", "top0")])]), "only one round"),
      (("call", "clamp", [("name", "top0")]), "clamp takes 3 arguments"),
      (("call", "bogus", [("name", "top0")]), "unknown operation 'bogus'"),
    ):
      with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, msg):
        lower_flow_call(bad, ops, slots, None, stub_lower)

  def test_flatten_flow_nested_dag_and_pipeline_splits(self):
    dag_src = (
      ".kernel p pipeline {\n  .flow {\n    .count = 15;\n"
      "    Slot a = (top0 + top1) * (base0 - base1);\n    Slot b = (a & 0xff) >> 2;\n"
      "    .slot = (b << 3) + round((top0 + top1) >> 1);\n    .slot = slot;\n  }\n}\n"
    )
    dag = flatten_flow(expand_kernel(dag_src))
    self.assertEqual([op["kind"] for op in dag["operations"]], ["add", "sub", "mul", "and_cst", "add_cst", "shl_cst", "add", "add"])
    self.assertEqual((dag["operations"][2]["target"], dag["operations"][4]["target"], dag["output"]), ("a", "b", 7))
    self.assertEqual((dag["operations"][4]["numbers"], dag["operations"][4]["shift"], dag["operations"][6]["shift"], dag["operations"][6]["round"]), ({"c": 0}, 2, 1, True))
    self.assertEqual([op["kind"] for op in flatten_flow(expand_kernel(".kernel p pipeline { .flow { .count = 7; .slot = ~(((top0 + 1) & 4) ? -(top1 * 2) : (top1 * 2)) >> 2; } }\n"))["operations"]], ["add_cst", "mul_cst", "sel_neg", "not", "add_cst"])
    self.assertEqual(flatten_flow(expand_kernel(".kernel p pipeline { .flow { .count = 3; .slot = -top0; } }\n"))["operations"][0]["numbers"], {"c": 0})
    self.assertEqual([op["kind"] for op in flatten_flow(expand_kernel(".kernel p pipeline { .flow { .count = 3; .slot = top0 << (base0 & 7); } }\n"))["operations"]], ["and_cst", "shl_reg"])
    self.assertEqual(flatten_flow(expand_kernel(".kernel p pipeline { .flow { .count = 3; .slot = top0; } }\n"))["operations"][0]["kind"], "pass")
    self.assertEqual(flatten_flow(expand_kernel(".kernel p pipeline { .flow { .count = 3; .slot = 7; } }\n"))["operations"][0]["kind"], "cst")
    self.assertEqual([op["kind"] for op in flatten_flow(expand_kernel(".kernel p pipeline { .flow { .count = 3; .slot = (top0 & 0xff) >> 2; } }\n"), "fat")["operations"]], ["and_cst", "add_cst"])
    for expr, msg in (
      ("top0 / 2", "unsupported operator '/'"),
      ("top0 == 0", "no opcode covers this expression"),
      ("((top0 + 1) & 4) ? top1 : base0", "no opcode covers this expression"),
    ):
      with self.subTest(expr=expr), self.assertRaisesRegex(ValueError, msg):
        flatten_flow(expand_kernel(f".kernel p pipeline {{ .flow {{ .count = 1; .slot = {expr}; }} }}\n"))


if __name__ == "__main__":
  unittest.main()
