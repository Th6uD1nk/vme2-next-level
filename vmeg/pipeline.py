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
