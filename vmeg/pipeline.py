from vmeg.operations import OPERATIONS

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
