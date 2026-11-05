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


def op_neg_ofb(back, front, fu, a, b, previous, state):
  return shifted(b - back, fu)


def op_add_byt(back, front, fu, a, b, previous, state):
  return (front & 0xff) + (back & 0xff) + (((front & 0xff00) + (back & 0xff00)) >> 8)


def op_sub_byt(back, front, fu, a, b, previous, state):
  return ((front & 0xff) - (back & 0xff)) + (((front & 0xff00) - (back & 0xff00)) >> 8)


def op_add_shf(back, front, fu, a, b, previous, state):
  return front + shift_by_register(back, b)


def op_shr_cst_ofa(back, front, fu, a, b, previous, state):
  return shift_by_register(back, b) + a


def op_shr_cst_neg_ofa(back, front, fu, a, b, previous, state):
  return a - shift_by_register(back, b)


def op_shr_cst_ofs(back, front, fu, a, b, previous, state):
  return shift_by_register(back, b) - a


def op_add_hib(back, front, fu, a, b, previous, state):
  return (((front & 0xff00) + (back & 0xff00)) >> 8) << (fu["k"] == 1)


def op_add_lob(back, front, fu, a, b, previous, state):
  return ((front & 0xff) + (back & 0xff)) << (fu["k"] == 1)


def op_sel_neg(back, front, fu, a, b, previous, state):
  return -back if front & a else back


def op_sel_neg_slf(back, front, fu, a, b, previous, state):
  return back if front & a else -back


def op_sel_cst(back, front, fu, a, b, previous, state):
  return b if front & a else back


def op_sel_cst_ofb(back, front, fu, a, b, previous, state):
  return back if front & a else b


def op_sel_ads(back, front, fu, a, b, previous, state):
  return (back << (fu["k"] == 1)) - b if back & a else (back << (fu["k"] == 1)) + b


def op_sel_ads_inv(back, front, fu, a, b, previous, state):
  return (back << (fu["k"] == 1)) + b if back & a else (back << (fu["k"] == 1)) - b


def op_sel_cst_zer(back, front, fu, a, b, previous, state):
  return 0 if back & a else b


def op_sel_cst_zer_inv(back, front, fu, a, b, previous, state):
  return b if back & a else 0


def op_mul_clp(back, front, fu, a, b, previous, state):
  return back * front if -2 <= front <= 2 else 0


def op_mul_clp_neg(back, front, fu, a, b, previous, state):
  return -(back * front) if -2 <= front <= 2 else 0


def op_cst(back, front, fu, a, b, previous, state):
  return b


def op_pass(back, front, fu, a, b, previous, state):
  return shifted(back, fu)


def op_mul_cst(back, front, fu, a, b, previous, state):
  return shifted(back * b, fu)


def shift_right(value, amount):
  return value >> amount if amount >= 0 else value << -amount


def shift_by_register(value, b):
  amount = b & 63
  return shift_right(value, amount - 64 if amount >= 32 else amount)


def op_shl_cst(back, front, fu, a, b, previous, state):
  amount = b & 63
  if amount >= 32:
    amount -= 64
  return back << amount if amount >= 0 else back >> -amount


def op_subshr(back, front, fu, a, b, previous, state):
  return front - shift_by_register(back, b)


def op_shrsub(back, front, fu, a, b, previous, state):
  return shift_by_register(back, b) - front


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
  "mul_clp": op_mul_clp,
  "mul_clp_neg": op_mul_clp_neg,
  "sel_cst_zer": op_sel_cst_zer,
  "sel_cst_zer_inv": op_sel_cst_zer_inv,
  "sel_ads": op_sel_ads,
  "sel_ads_inv": op_sel_ads_inv,
  "sel_neg": op_sel_neg,
  "sel_neg_slf": op_sel_neg_slf,
  "sel_cst": op_sel_cst,
  "sel_cst_ofb": op_sel_cst_ofb,
  "shr_cst_ofs": op_shr_cst_ofs,
  "add_hib": op_add_hib,
  "add_lob": op_add_lob,
  "add_shf": op_add_shf,
  "shr_cst_ofa": op_shr_cst_ofa,
  "shr_cst_neg_ofa": op_shr_cst_neg_ofa,
  "add_byt": op_add_byt,
  "sub_byt": op_sub_byt,
  "neg_ofb": op_neg_ofb,
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
