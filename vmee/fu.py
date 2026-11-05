from vmee.registers import FU_OPERAND_REGISTERS
from vmeg.operations import OPERATIONS


def signed32(value):
  return value - (1 << 32) if value & 0x80000000 else value


def saturate(value, n):
  if n == 0:
    return value
  return max(-(1 << (n - 1)), min((1 << (n - 1)) - 1, value))


def fu_operands(registers, pe, kind):
  if kind not in FU_OPERAND_REGISTERS:
    raise ValueError(f"unknown fu '{kind}' ({', '.join(FU_OPERAND_REGISTERS)})")
  if not 0 <= pe <= 3:
    raise ValueError(f"pe{pe}: processing element out of range (pe0 to pe3)")
  first = FU_OPERAND_REGISTERS[kind] + 2 * pe
  return signed32(registers[first]), signed32(registers[first + 1])


def shifted(value, fu):
  k = fu["k"]
  return (value + (1 << k - 1) if fu["round"] and k else value) >> k


def op_add(back, front, fu, a, b, previous, state):
  return shifted(back + front, fu)


def op_clp(back, front, fu, a, b, previous, state):
  return max(b, min(a, back))


def op_and(back, front, fu, a, b, previous, state):
  return back & front


def op_and_cst(back, front, fu, a, b, previous, state):
  return back & b


def op_nand(back, front, fu, a, b, previous, state):
  return ~(back & front)


def op_nand_cst(back, front, fu, a, b, previous, state):
  return ~(b & back)


def op_or(back, front, fu, a, b, previous, state):
  return back | front


def op_or_cst(back, front, fu, a, b, previous, state):
  return back | b


def op_nor(back, front, fu, a, b, previous, state):
  return ~(back | front)


def op_nor_cst(back, front, fu, a, b, previous, state):
  return (~back) & ~b


def op_xor(back, front, fu, a, b, previous, state):
  return back ^ front


def op_xor_cst(back, front, fu, a, b, previous, state):
  return back ^ b


def op_xnor_cst(back, front, fu, a, b, previous, state):
  return (~back) ^ b


def op_not(back, front, fu, a, b, previous, state):
  return ~back


def op_mac_acc_shift_bias(back, front, fu, a, b, previous, state):
  return (b >> fu["k"] if previous is None else previous) + (back >> fu["k"])


def op_mac_inner_product_bias(back, front, fu, a, b, previous, state):
  state["sum"] = state.get("sum", 0) + back * front
  return (state["sum"] + b) >> fu["k"]


def op_mul_rshift(back, front, fu, a, b, previous, state):
  return shifted(back * front, fu)


def op_bak_shr(back, front, fu, a, b, previous, state):
  return shifted(back, fu)


def op_cst(back, front, fu, a, b, previous, state):
  return b


def op_pass(back, front, fu, a, b, previous, state):
  return shifted(back, fu)


def op_mul_cst(back, front, fu, a, b, previous, state):
  return shifted(back * b, fu)


def shift_right(value, amount):
  return value >> amount if amount >= 0 else value << -amount


def op_shl_cst(back, front, fu, a, b, previous, state):
  amount = b & 63
  if amount >= 32:
    amount -= 64
  return back << amount if amount >= 0 else back >> -amount


def op_subshr(back, front, fu, a, b, previous, state):
  return front - shift_right(back, b)


def op_shrsub(back, front, fu, a, b, previous, state):
  return shift_right(back, b) - front


def op_add_ofa(back, front, fu, a, b, previous, state):
  return (back + front) + a


def op_add_cst(back, front, fu, a, b, previous, state):
  return back + b


def op_sub(back, front, fu, a, b, previous, state):
  return shifted(front - back, fu)


def op_subacst(back, front, fu, a, b, previous, state):
  return (front - back) + a


HANDLERS = {
  "add": op_add,
  "add_ofa": op_add_ofa,
  "add_cst": op_add_cst,
  "sub": op_sub,
  "subacst": op_subacst,
  "subshr": op_subshr,
  "shrsub": op_shrsub,
  "mul": op_mul_rshift,
  "pass": op_pass,
  "cst": op_cst,
  "bak_shr": op_bak_shr,
  "mul_cst": op_mul_cst,
  "shl_cst": op_shl_cst,
  "mul_vec": op_mul_rshift,
  "and": op_and,
  "and_cst": op_and_cst,
  "nand": op_nand,
  "nand_cst": op_nand_cst,
  "or": op_or,
  "or_cst": op_or_cst,
  "nor": op_nor,
  "nor_cst": op_nor_cst,
  "xor": op_xor,
  "xor_cst": op_xor_cst,
  "xnor_cst": op_xnor_cst,
  "not": op_not,
  "clamp": op_clp,
  "mac": op_mac_inner_product_bias,
  "acc": op_mac_acc_shift_bias,
}

if sorted(HANDLERS) != sorted(OPERATIONS):
  raise ValueError(f"the computations of the emulator and the operations table differ: {', '.join(sorted(set(HANDLERS) ^ set(OPERATIONS)))}")

OPCODES = {specification["opcode"]: (HANDLERS[kind], specification["operands"]) for kind, specification in OPERATIONS.items()}

ROUNDED = {OPERATIONS[kind]["opcode"] for kind in ("add", "sub", "mul", "mul_cst", "mul_vec", "subacst", "subshr", "shrsub")}

if len(OPCODES) != len(OPERATIONS):
  raise ValueError("two operations of the table have the same opcode")


def opcode_entry(fu):
  entry = OPCODES.get(fu["opcode"])
  if entry is None:
    raise ValueError(f"the opcode {fu['opcode']:#x} is not modeled (modeled: {', '.join(hex(opcode) for opcode in sorted(OPCODES))})")
  if fu["round"] and fu["opcode"] not in ROUNDED:
    raise ValueError(f"the rounding bit of the opcode {fu['opcode']:#x} is not modeled")
  return entry


def execute(fu, back, front, a=0, b=0, previous=None, state=None):
  handler, _ = opcode_entry(fu)
  return saturate(handler(back, front, fu, a, b, previous, {} if state is None else state), fu["sat"])
