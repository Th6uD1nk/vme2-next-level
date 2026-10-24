from emu.registers import FU_OPERAND_REGISTERS
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


def op_add(back, front, fu, a, b, previous, state):
  if fu["round"] and fu["k"]:
    raise ValueError("the rounding bit of an ADD with a shift is not modeled")
  return (back + front) >> fu["k"]


def op_clp(back, front, fu, a, b, previous, state):
  return max(b, min(a, back))


def op_and(back, front, fu, a, b, previous, state):
  return back & front


def op_mac_acc_shift_bias(back, front, fu, a, b, previous, state):
  return (b >> fu["k"] if previous is None else previous) + (back >> fu["k"])


def op_mac_inner_product_bias(back, front, fu, a, b, previous, state):
  state["sum"] = state.get("sum", 0) + back * front
  return (state["sum"] + b) >> fu["k"]


def op_mul_rshift(back, front, fu, a, b, previous, state):
  return (back * front) >> fu["k"]


def op_sub_inv_shf(back, front, fu, a, b, previous, state):
  if b < 0:
    raise ValueError("a negative shift (register B) of the opcode 0x50 is not modeled")
  return back - (front >> b)


def op_sub(back, front, fu, a, b, previous, state):
  return front - back


def op_sub_ofb(back, front, fu, a, b, previous, state):
  return (front - back) + b


HANDLERS = {
  "add": op_add,
  "sub": op_sub,
  "subacst": op_sub_ofb,
  "subshr": op_sub_inv_shf,
  "mul": op_mul_rshift,
  "and": op_and,
  "clamp": op_clp,
  "mac": op_mac_inner_product_bias,
  "acc": op_mac_acc_shift_bias,
}

if sorted(HANDLERS) != sorted(OPERATIONS):
  raise ValueError(f"the computations of the emulator and the operations table differ: {', '.join(sorted(set(HANDLERS) ^ set(OPERATIONS)))}")

OPCODES = {specification["opcode"]: (HANDLERS[kind], specification["operands"]) for kind, specification in OPERATIONS.items()}

if len(OPCODES) != len(OPERATIONS):
  raise ValueError("two operations of the table have the same opcode")


def opcode_entry(fu):
  entry = OPCODES.get(fu["opcode"])
  if entry is None:
    raise ValueError(f"the opcode {fu['opcode']:#x} is not modeled (modeled: {', '.join(hex(opcode) for opcode in sorted(OPCODES))})")
  return entry


def execute(fu, back, front, a=0, b=0, previous=None, state=None):
  handler, _ = opcode_entry(fu)
  return saturate(handler(back, front, fu, a, b, previous, {} if state is None else state), fu["sat"])
