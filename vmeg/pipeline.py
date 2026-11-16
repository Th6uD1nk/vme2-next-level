from vmeg.expr import fold
from vmeg.kernel import base_name, check_arguments, constant, emit_statement, resolve_var, source_ref, unrolled
from vmeg.operations import FUNCTIONS, OPERATIONS, OPERATORS
from vmeg.parser import BUFFER_NAME, buffer_ref
from vmeg.pattern import rebuild
from vmeg.selector import OPERATION_NODES, choose_opcode

PIPELINE_FORBIDDEN_KINDS = (("agus", "Agu"), ("stagings", "Staging"), ("transfers", "Transfer"))

PIPELINE_LEFT_SHIFT_OPS = {"<<": "shl_cst", "<<<": "shl_cst_u"}


def can_encode_k_shift(kind, op, round_flag=False):
  if op != ">>":
    return False
  specification = OPERATIONS[kind]
  return specification["k_shift"] and (not round_flag or specification["k_round"])


def make_shift_operation(source, op, amount, round_flag=False, sat_bits=None):
  if op in PIPELINE_LEFT_SHIFT_OPS:
    if round_flag:
      raise ValueError("round applies to right shift >>, not left shift")
    if not 0 <= amount <= 31:
      raise ValueError("the left shift must be 0 to 31")
    return {"kind": PIPELINE_LEFT_SHIFT_OPS[op], "source": source, "numbers": {"c": amount}, "sat": sat_bits}
  if op == ">>>":
    if round_flag:
      raise ValueError("round applies to >>, not >>>")
    if not 0 <= amount <= 31:
      raise ValueError("the logical right shift must be 0 to 31")
    return {"kind": "shr_cst_u", "source": source, "numbers": {"c": amount}, "sat": sat_bits}
  if op != ">>":
    raise ValueError(f"unsupported shift operator '{op}'")
  if not 0 <= amount <= 63:
    raise ValueError("the shift must be 0 to 63")
  if round_flag and (amount == 0 or amount > 23):
    return {"kind": "mul_cst", "source": source, "numbers": {"c": 1}, "sat": sat_bits, "shift": amount, "round": True}
  bias = (1 << (amount - 1)) if round_flag else 0
  return {"kind": "add_cst", "source": source, "numbers": {"c": bias}, "sat": sat_bits, "shift": amount}


def check_flow_var(name, state, line):
  array_kind = state["arrays"].get(name, {}).get("kind")
  for store, kind in PIPELINE_FORBIDDEN_KINDS:
    if name in state[store] or array_kind == kind:
      article = "an" if kind[0] in "AEIOU" else "a"
      raise ValueError(f"line {line}: '{name}' is {article} {kind} variable and cannot be used in .flow")


def resolve_flow_expr(expr, slots, cursor, inputs, state, line):
  kind = expr[0]
  if kind == "num":
    return expr
  if kind in ("name", "index"):
    name = expr[1]
    if kind == "name" and name == "slot":
      if cursor is None:
        raise ValueError(f"line {line}: 'slot' is read before any .slot assignment")
      return cursor
    check_flow_var(name, state, line)
    ref = source_ref(expr, slots, 3, "Slot")
    if isinstance(ref, tuple):
      return ref
    if isinstance(ref, str):
      inputs.add(ref)
      return ("name", ref.lower().replace("_", ""))
    if kind == "name" and BUFFER_NAME.match(name):
      raise ValueError(f"line {line}: {name} is out of range (top0 to top3, base0 to base3)")
    raise ValueError(f"line {line}: unknown {'array' if kind == 'index' else 'variable'} '{name}' in .flow")
  return rebuild(expr, lambda child: resolve_flow_expr(child, slots, cursor, inputs, state, line))


def flow_step(target, expr, ctx, state, line):
  resolved = resolve_flow_expr(fold(expr, ctx["env"]), state["slots"], ctx["cursor"], ctx["inputs"], state, line)
  ref = ("pipe_ref", len(ctx["steps"]))
  ctx["steps"].append({"id": ref[1], "target": target, "expr": resolved, "line": line})
  return ref


def apply_flow_statement(stmt, ctx, state):
  kind, line = stmt[0], stmt[-1]
  if kind in ("int", "elemset", "slotdecl"):
    emit_statement(stmt, ctx["env"], [], state)
  elif kind == "flowcount":
    if ctx["count"] is not None:
      raise ValueError(f"line {line}: duplicate .count in .flow")
    val = fold(stmt[1], ctx["env"])
    if val[0] != "num" or not 0 <= val[1] <= 1023:
      raise ValueError(f"line {line}: .count in .flow must be a number from 0 to 1023")
    ctx["count"] = val[1]
  elif kind == "slotset":
    key = resolve_var(stmt[1], ctx["env"], state)
    if key not in state["slots"]:
      raise ValueError(f"line {line}: unknown Slot variable '{base_name(stmt[1])}'")
    if state["slots"][key] is not None:
      raise ValueError(f"line {line}: the Slot variable '{key}' is already set")
    state["slots"][key] = flow_step(key, stmt[2], ctx, state, line)
  elif kind == "flowslot":
    ctx["cursor"] = flow_step(None, stmt[1], ctx, state, line)


def expand_flow(state, env):
  if state["flow"] is None:
    raise ValueError("pipeline kernel needs a .flow block")
  ctx = {"count": None, "cursor": None, "steps": [], "inputs": set(), "env": dict(env)}
  queue = list(state["flow"][1])
  while queue:
    stmt = queue.pop(0)
    if stmt[0] == "for":
      queue[:0] = unrolled(stmt, ctx["env"])
      continue
    apply_flow_statement(stmt, ctx, state)
  if ctx["count"] is None or ctx["cursor"] is None:
    raise ValueError(f"line {state['flow'][-1]}: .flow needs .count and at least one .slot assignment")
  return {"count": ctx["count"], "steps": ctx["steps"], "inputs": sorted(ctx["inputs"]), "output": ctx["cursor"][1]}


def emit_pipeline_op(ops, operation):
  ops.append(dict(operation, id=len(ops)))
  return ("op_ref", len(ops) - 1)


def flow_operand(expr, ops, slot_refs, compat, lower):
  kind = expr[0]
  if kind == "op_ref":
    return expr
  if kind == "pipe_ref":
    return slot_refs[expr[1]]
  if kind == "name":
    return buffer_ref(expr, 3)
  if kind == "num":
    return emit_pipeline_op(ops, {"kind": "cst", "source": None, "numbers": {"c": expr[1]}, "sat": None})
  return lower(expr, ops, slot_refs, compat)


def build_table_op(kind, bound, ops, slot_refs, compat, lower, label=None):
  spec = OPERATIONS[kind]
  args = [bound[name] for name, _ in spec["arguments"]]
  numbers = {arg: constant(val, f"{label or kind} {arg}") for (arg, role), val in zip(spec["arguments"], args) if role == "number"}
  given = [val for (_, role), val in zip(spec["arguments"], args) if role != "number"]
  if len(spec["operands"]) == 2:
    operands = {slot: flow_operand(val, ops, slot_refs, compat, lower) for slot, val in zip(spec["operands"], given)}
  else:
    operands = {"source": flow_operand(given[0], ops, slot_refs, compat, lower) if given else None}
  op = {"kind": kind, **operands, "numbers": numbers, "sat": None}
  if "shift" in spec:
    if not 0 <= numbers[spec["shift"]] <= 63:
      raise ValueError("the shift must be 0 to 63")
    op["shift"] = numbers[spec["shift"]]
  return emit_pipeline_op(ops, op)


def unwrap_round(expr):
  if expr[0] == "call" and expr[1] == "round":
    if len(expr[2]) != 1:
      raise ValueError("round takes 1 argument (value)")
    inner = expr[2][0]
    if inner[0] == "call" and inner[1] == "round":
      raise ValueError("an operation takes only one round")
    return inner, True
  if expr[0] == "call" and expr[1] == "sat" and len(expr[2]) == 2 and expr[2][0][0] == "call" and expr[2][0][1] == "round":
    inner, round_flag = unwrap_round(expr[2][0])
    return ("call", "sat", [inner, expr[2][1]]), round_flag
  return expr, False


def apply_sat_op(expr, ops, slot_refs, compat, lower):
  if len(expr[2]) != 2:
    raise ValueError("sat takes 2 arguments (value, bits)")
  bits = constant(expr[2][1], "sat bits")
  if not 0 <= bits <= 31:
    raise ValueError("sat bits out of range (0 to 31)")
  inner = expr[2][0]
  ref = flow_operand(inner, ops, slot_refs, compat, lower)
  if inner[0] in ("name", "pipe_ref") or ops[ref[1]]["sat"] is not None:
    return emit_pipeline_op(ops, {"kind": "pass", "source": ref, "numbers": {}, "sat": bits})
  ops[ref[1]]["sat"] = bits
  return ref


def compile_shift_op(expr, ops, slot_refs, compat, lower, round_flag=False):
  _, op, left, right = expr
  left, inner_round = unwrap_round(left)
  if round_flag and inner_round:
    raise ValueError("an operation takes only one round")
  round_flag = round_flag or inner_round
  if right[0] != "num":
    if round_flag:
      raise ValueError("the shift must be a number")
    return None
  amount = right[1]
  if op == ">>" and left[0] not in ("name", "pipe_ref", "num"):
    if not 0 <= amount <= 63:
      raise ValueError("the shift must be 0 to 63")
    src = lower(left, ops, slot_refs, compat)
    target = ops[src[1]]
    if target.get("shift") is None and can_encode_k_shift(target["kind"], op, round_flag):
      target["shift"] = amount
      if round_flag:
        target["round"] = True
      return src
  else:
    src = flow_operand(left, ops, slot_refs, compat, lower)
  return emit_pipeline_op(ops, make_shift_operation(src, op, amount, round_flag))


def lower_child_op(expr, ops, slot_refs, compat, lower):
  return lower(expr, ops, slot_refs, compat) if expr[0] in OPERATION_NODES else expr


def unpack_cond(expr, ops, slot_refs, compat, lower):
  cond, arm_t, arm_f = expr[1], expr[2], expr[3]
  if cond[0] == "bin" and cond[1] == "&" and cond[3][0] == "num":
    f_expr, mask = cond[2], cond[3]
    f_ref = lower_child_op(f_expr, ops, slot_refs, compat, lower)
    if arm_t == ("neg", arm_f) or arm_f == ("neg", arm_t):
      neg_t = arm_t == ("neg", arm_f)
      base = arm_f if neg_t else arm_t
      ref = f_ref if base == f_expr else lower_child_op(base, ops, slot_refs, compat, lower)
      return ("cond", ("bin", "&", f_ref, mask), ("neg", ref) if neg_t else ref, ref if neg_t else ("neg", ref))
    if arm_t[0] == "bin" and arm_f[0] == "bin" and arm_t[1] in ("+", "-") and arm_f[1] in ("+", "-") and arm_t[2] == arm_f[2] == f_expr:
      return ("cond", ("bin", "&", f_ref, mask), ("bin", arm_t[1], f_ref, arm_t[3]), ("bin", arm_f[1], f_ref, arm_f[3]))
    t_val = f_ref if arm_t == f_expr else lower_child_op(arm_t, ops, slot_refs, compat, lower)
    f_val = f_ref if arm_f == f_expr else lower_child_op(arm_f, ops, slot_refs, compat, lower)
    return ("cond", ("bin", "&", f_ref, mask), t_val, f_val)
  return rebuild(expr, lambda child: lower_child_op(child, ops, slot_refs, compat, lower))


def unpack_compound(expr, ops, slot_refs, compat, lower):
  if expr[0] == "not" and expr[1][0] == "bin" and expr[1][1] in ("&", "|", "^"):
    op, left, right = expr[1][1], expr[1][2], expr[1][3]
    return ("not", ("bin", op, lower_child_op(left, ops, slot_refs, compat, lower), lower_child_op(right, ops, slot_refs, compat, lower)))
  if expr[0] == "cond":
    return unpack_cond(expr, ops, slot_refs, compat, lower)
  return rebuild(expr, lambda child: lower_child_op(child, ops, slot_refs, compat, lower))


def lower_flow_call(expr, ops, slot_refs, compat, lower):
  name, args = expr[1], expr[2]
  if name == "sat":
    return apply_sat_op(expr, ops, slot_refs, compat, lower)
  if name == "round":
    if len(args) != 1:
      raise ValueError("round takes 1 argument (value)")
    inner = args[0]
    if inner[0] == "call" and inner[1] == "round":
      raise ValueError("an operation takes only one round")
    if inner[0] == "bin" and inner[1] in (">>", "<<", ">>>", "<<<"):
      return compile_shift_op(inner, ops, slot_refs, compat, lower, round_flag=True)
    ref = flow_operand(inner, ops, slot_refs, compat, lower)
    if inner[0] in ("name", "pipe_ref"):
      ref = emit_pipeline_op(ops, {"kind": "pass", "source": ref, "numbers": {}, "sat": None})
    if OPERATIONS[ops[ref[1]]["kind"]]["k_round"]:
      ops[ref[1]]["round"] = True
    return ref
  if name in FUNCTIONS:
    check_arguments(name, args)
    kind = FUNCTIONS[name]
    bound = {arg: val for (arg, _), val in zip(OPERATIONS[kind]["arguments"], args)}
    return build_table_op(kind, bound, ops, slot_refs, compat, lower, label=name)
  raise ValueError(f"unknown operation '{name}' ({', '.join(['sat', 'round', *FUNCTIONS])})")


def lower_flow_expr(expr, ops, slot_refs, compat):
  kind = expr[0]
  if kind in ("op_ref", "pipe_ref", "name", "num"):
    ref = flow_operand(expr, ops, slot_refs, compat, lower_flow_expr)
    return emit_pipeline_op(ops, {"kind": "pass", "source": ref, "numbers": {}, "sat": None}) if kind == "name" else ref
  if kind == "call":
    return lower_flow_call(expr, ops, slot_refs, compat, lower_flow_expr)
  if kind == "bin":
    shifted = compile_shift_op(expr, ops, slot_refs, compat, lower_flow_expr) if expr[1] in (">>", "<<", ">>>", "<<<") else None
    if shifted is not None:
      return shifted
    if expr[1] not in OPERATORS:
      raise ValueError(f"unsupported operator '{expr[1]}' ({', '.join(OPERATORS)})")
  found = choose_opcode(expr, compat)
  if found is None and kind == "neg":
    return lower_flow_expr(("bin", "-", ("num", 0), expr[1]), ops, slot_refs, compat)
  if found is None:
    found = choose_opcode(unpack_compound(expr, ops, slot_refs, compat, lower_flow_expr), compat)
  if found is None:
    raise ValueError("no opcode covers this expression")
  return build_table_op(found[0], found[1], ops, slot_refs, compat, lower_flow_expr)


def flatten_flow(flow, compat=None):
  ops, slot_refs = [], {}
  for step in flow["steps"]:
    start = len(ops)
    ref = lower_flow_expr(step["expr"], ops, slot_refs, compat)
    for op in ops[start:]:
      op.update(line=step["line"], step=step["id"])
    if step["target"] is not None:
      ops[ref[1]].setdefault("target", step["target"])
    slot_refs[step["id"]] = ref
  return {"count": flow["count"], "inputs": flow["inputs"], "operations": ops, "output": slot_refs[flow["output"]][1], "slot_outputs": slot_refs}


def op_refs(op):
  keys = ("front", "back") if len(OPERATIONS[op["kind"]]["operands"]) == 2 else ("source",)
  return [(key, op[key]) for key in keys if op.get(key) is not None]


def find_free_pe(op, pes):
  if OPERATIONS[op["kind"]]["units"] == "any":
    deps = {ref[1] for _, ref in op_refs(op) if isinstance(ref, tuple)}
    for match_producer in (True, False):
      for pe in pes:
        if pe["secondary"] is None and (not match_producer or pe["primary"]["id"] in deps):
          return pe, "secondary"
  if len(pes) < 4:
    pe = {"primary": None, "secondary": None}
    pes.append(pe)
    return pe, "primary"
  return None


def place_in_pass(op, pes, in_pass):
  depths = [0 if isinstance(ref, str) or ref[1] not in in_pass else in_pass[ref[1]] for _, ref in op_refs(op)]
  slot = find_free_pe(op, pes)
  if slot is None:
    return False
  pe, unit = slot
  depth = max(depths, default=0) + 1
  placed = dict(op, depth=depth)
  pe[unit] = placed
  in_pass[placed["id"]] = depth
  return True


def try_place_with_delays(op, pes, in_pass, next_id):
  saved_pes, saved_in, saved_next = [dict(pe) for pe in pes], dict(in_pass), next_id[0]
  refs = op_refs(op)
  chain = []
  placed = dict(op)
  if len(refs) == 2:
    (k0, r0), (k1, r1) = refs
    d0 = 0 if isinstance(r0, str) or r0[1] not in in_pass else in_pass[r0[1]]
    d1 = 0 if isinstance(r1, str) or r1[1] not in in_pass else in_pass[r1[1]]
    low_key, cur, low_d, high_d = (k0, r0, d0, d1) if d0 < d1 else (k1, r1, d1, d0)
    for _ in range(high_d - low_d):
      delay = {"id": next_id[0], "kind": "pass", "source": cur, "numbers": {}, "sat": None, "delay": True}
      next_id[0] += 1
      chain.append(delay)
      cur = ("op_ref", delay["id"])
    placed[low_key] = cur
  chain.append(placed)
  if all(place_in_pass(item, pes, in_pass) for item in chain):
    return True
  pes[:], next_id[0] = saved_pes, saved_next
  in_pass.clear()
  in_pass.update(saved_in)
  return False


def live_exports(pes, out_id, pending, ops_map):
  needed = {out_id}
  for pid in pending:
    needed.update(ref[1] for _, ref in op_refs(ops_map[pid]) if isinstance(ref, tuple))
  return {op["id"] for pe in pes for op in (pe["primary"], pe["secondary"]) if op is not None and op["id"] in needed}


def evict_pass_ops(root_id, pes, ops_map):
  dead = {root_id}
  changed = True
  while changed:
    changed = False
    live = [op for pe in pes for op in (pe["primary"], pe["secondary"]) if op is not None and op["id"] not in dead]
    used = {ref[1] for op in live for _, ref in op_refs(op) if isinstance(ref, tuple)}
    for op in live:
      deps = [ref[1] for _, ref in op_refs(op) if isinstance(ref, tuple)]
      if any(d in dead for d in deps) or (op.get("delay") and op["id"] not in used):
        dead.add(op["id"])
        changed = True
  kept = []
  for pe in pes:
    pri = None if pe["primary"]["id"] in dead else pe["primary"]
    sec = None if pe["secondary"] is None or pe["secondary"]["id"] in dead else pe["secondary"]
    if pri is None and sec is not None:
      pri, sec = sec, None
    if pri is not None:
      kept.append({"primary": pri, "secondary": sec})
  pes[:] = kept
  return [oid for oid in dead if oid in ops_map]


def finalize_flow_pass(pes, out_id, pending, ops_map, pass_id):
  while True:
    exports = live_exports(pes, out_id, pending, ops_map)
    conflict = next((pe for pe in pes if pe["secondary"] is not None and pe["primary"]["id"] in exports and pe["secondary"]["id"] in exports), None)
    if conflict is None:
      break
    if len(pes) < 4:
      pes.append({"primary": conflict["secondary"], "secondary": None})
      conflict["secondary"] = None
    else:
      pending[:] = sorted([*pending, *evict_pass_ops(conflict["secondary"]["id"], pes, ops_map)])
  exports = live_exports(pes, out_id, pending, ops_map)
  pass_ops, pass_exports, imports, inputs = [], [], set(), set()
  for idx, pe in enumerate(pes):
    pe["pe"] = idx
    pe["output_unit"] = next((u for u in ("primary", "secondary") if pe[u] is not None and pe[u]["id"] in exports), None)
    pe["export"] = pe[pe["output_unit"]]["id"] if pe["output_unit"] else None
    if pe["export"] is not None:
      pass_exports.append(pe["export"])
    for unit in ("primary", "secondary"):
      op = pe[unit]
      if op is not None:
        op.update({"pass": pass_id, "pe": idx, "unit": unit})
        pass_ops.append(op)
  pass_ids = {op["id"] for op in pass_ops}
  for op in pass_ops:
    for _, ref in op_refs(op):
      (imports if isinstance(ref, tuple) else inputs).add(ref[1] if isinstance(ref, tuple) else ref)
  return {"pass_id": pass_id, "pes": pes, "operations": pass_ops, "exports": pass_exports, "imports": sorted(imports - pass_ids), "inputs": sorted(inputs)}


def schedule_flow(flow):
  ops_map = {op["id"]: op for op in flow["operations"]}
  pending = [op["id"] for op in flow["operations"]]
  pass_of, passes, next_id = {}, [], [len(flow["operations"])]
  while pending:
    pes, in_pass, next_pending = [], {}, []
    for pid in pending:
      op = ops_map[pid]
      deps = [ref[1] for _, ref in op_refs(op) if isinstance(ref, tuple)]
      if not (all(d in pass_of or d in in_pass for d in deps) and try_place_with_delays(op, pes, in_pass, next_id)):
        next_pending.append(pid)
    rec = finalize_flow_pass(pes, flow["output"], next_pending, ops_map, len(passes))
    for op in rec["operations"]:
      if op["id"] in ops_map:
        pass_of[op["id"]] = rec["pass_id"]
    passes.append(rec)
    pending = next_pending
  return {"count": flow["count"], "inputs": flow["inputs"], "output": flow["output"], "passes": passes}


def load_reservations(loads):
  reserved, offsets = set(), {}
  for record in loads or ():
    for slot, words, off_text, _, _ in record.get("links", ()):
      if "_" not in slot:
        continue
      try:
        off = 0 if off_text == "" else int(off_text, 0)
      except ValueError:
        off = None
      bank = int(slot.split("_")[1])
      if slot.startswith("BASE_"):
        if off is None:
          reserved.update(((bank, 0), (bank, 1)))
        else:
          if off < 1024:
            reserved.add((bank, 0))
          if off >= 1024 or (isinstance(words, int) and off + words > 1024):
            reserved.add((bank, 1))
      offsets[slot] = (0 if off_text == "" else (off if off is not None else off_text), 1 if off is not None and off >= 1024 else 0)
  return offsets, reserved


def export_lifetimes(passes, out_id):
  consumers, last_use, base_reads = {}, {out_id: len(passes) - 1}, []
  for p, rec in enumerate(passes):
    base_reads.append({int(r.split("_")[1]) for r in rec["inputs"] if r.startswith("BASE_")})
    for imp in rec["imports"]:
      consumers.setdefault(imp, []).append(p)
      last_use[imp] = max(last_use.get(imp, -1), p)
  return consumers, last_use, base_reads


def slot_free(bank, half, op_id, p, used_banks, busy, consumers, base_reads, passes, alloc):
  if bank in used_banks or busy.get((bank, half), -1) >= p:
    return False
  for q in consumers.get(op_id, ()):
    if bank in base_reads[q] or any(alloc[imp][0] == bank for imp in passes[q]["imports"] if imp in alloc and imp != op_id):
      return False
  return True


def assign_flow_buffers(schedule, loads=None):
  count, passes, out_id = schedule["count"], schedule["passes"], schedule["output"]
  if not 0 <= count <= 1023:
    raise ValueError("pipeline flow count must be 0 to 1023 (max 1024 words)")
  load_offsets, reserved = load_reservations(loads)
  for name in schedule["inputs"]:
    off, _ = load_offsets.get(name, (0, 0))
    if isinstance(off, int) and (off < 0 or off >= 2048 or (off & 1023) + count + 1 > 1024):
      raise ValueError(f"{name.lower()}: .load offset {off} and flow count {count} exceed a 1024-word half")
  consumers, last_use, base_reads = export_lifetimes(passes, out_id)
  busy, alloc, out_passes = {slot: len(passes) for slot in reserved}, {}, []
  for p, rec in enumerate(passes):
    pref, used_banks, exports_alloc = p & 1, set(), {}
    own = {pe_rec["pe"] for pe_rec in rec["pes"] if pe_rec["export"] is not None}
    for pe_rec in rec["pes"]:
      pe, op_id = pe_rec["pe"], pe_rec["export"]
      if op_id is None:
        continue
      banks = [pe] + [b for b in range(4) if b != pe and b not in own] + [b for b in range(4) if b != pe and b in own]
      chosen = next(((b, h) for b in banks for h in (pref, 1 - pref) if slot_free(b, h, op_id, p, used_banks, busy, consumers, base_reads, passes, alloc)), None)
      if chosen is None:
        raise ValueError("pipeline kernel needs more than 8 scratchpad half-buffers across passes")
      alloc[op_id] = chosen
      used_banks.add(chosen[0])
      busy[chosen] = last_use.get(op_id, p)
      exports_alloc[pe] = {"op": op_id, "bank": chosen[0], "half": chosen[1]}
    out_passes.append(dict(rec, exports_alloc=exports_alloc, extended_write=any(info["bank"] != pe for pe, info in exports_alloc.items())))
  return {"count": count, "inputs": schedule["inputs"], "output": out_id, "output_buffer": alloc[out_id], "alloc": alloc, "load_offsets": load_offsets, "passes": out_passes}
