from vmeg.kernel import source_ref
from vmeg.operations import OPERATIONS
from vmeg.parser import BUFFER_NAME
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
