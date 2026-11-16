from vmeg.expr import fold
from vmeg.kernel import base_name, constant, emit_statement, resolve_var, source_ref, unrolled
from vmeg.operations import OPERATIONS
from vmeg.parser import BUFFER_NAME, buffer_ref
from vmeg.pattern import rebuild

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
