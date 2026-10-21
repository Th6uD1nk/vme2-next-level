OPERATIONS = {
  "add": {
    "opcode": 0x010,
    "syntax": "a + b",
    "code": "fu_code(OP_ADD)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "a on the front socket, b on the back one",
  },
  "sub": {
    "opcode": 0x018,
    "syntax": "a - b",
    "code": "fu_code(OP_SUB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "a on the front socket and b on the back one, no constant",
  },
  "subacst": {
    "opcode": 0x048,
    "syntax": "subacst(a, b, c)",
    "code": "fu_code(OP_SUB_OFB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "(a - b) + c, a on the front socket and b on the back one, c is a number written in the register B of the FU",
  },
  "subshr": {
    "opcode": 0x050,
    "syntax": "subshr(a, b, n)",
    "code": "fu_code(OP_SUB_INV_SHF)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "b - (a >> n), a on the front socket and b on the back one, n is a number written in the register B of the FU",
  },
  "mul": {
    "opcode": 0x200,
    "syntax": "a * b",
    "code": "VME_FU_OPCODE_MUL_RSHIFT_0",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "(a * b) >> k, a on the front socket and b on the back one, k is the `>> n` written after the operation",
  },
  "and": {
    "opcode": 0x0c0,
    "syntax": "a & b",
    "code": "fu_code(OP_AND)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the bits and, a on the front socket and b on the back one",
  },
  "clamp": {
    "opcode": 0x07c,
    "syntax": "clamp(x, low, high)",
    "code": "fu_code(OP_CLP)",
    "operands": ("back",),
    "units": "any",
    "note": "registers A = high and B = low, x is a buffer, a Staging variable or an operation",
  },
  "mac": {
    "opcode": 0x240,
    "syntax": "mac(a, b)",
    "code": "VME_FU_OPCODE_MAC_INNER_PRODUCT_BIAS",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "running inner product (sum of a * b + bias) >> k, a on the front socket and b on the back one",
  },
  "acc": {
    "opcode": 0x250,
    "syntax": "acc(x)",
    "code": "VME_FU_OPCODE_MAC_ACC_SHIFT_BIAS",
    "operands": ("back",),
    "units": "primary",
    "note": "running sum, x is a buffer or a Staging variable",
  },
}

FIELDS = (
  ("sat(op, bits)", "fu_sat(bits)", "the saturator of the FU of the operation it wraps, bits 0 to 31"),
  ("op >> n", "k = n", "the shift in the 6 low bits of the FU register, n 0 to 63, the last layer of an operation"),
  ("op << n", "k = 64 - n", "the rotary shift, n 0 to 63"),
)


def operation_columns(specification):
  units = "primary FU only" if specification["units"] == "primary" else "any FU"
  return (specification["syntax"], f"0x{specification['opcode']:03x}", specification["code"], ", ".join(specification["operands"]), units)


def format_operations():
  rows = [operation_columns(specification) for specification in OPERATIONS.values()]
  widths = [max(len(row[i]) for row in rows) for i in range(5)]
  lines = ["operations, each one takes one FU:"]
  for specification, row in zip(OPERATIONS.values(), rows):
    lines.append("  " + "  ".join(column.ljust(width) for column, width in zip(row, widths)).rstrip())
    lines.append("      " + specification["note"])
  lines.append("")
  lines.append("fields of the FU of the operation they wrap:")
  syntax_width = max(len(field[0]) for field in FIELDS)
  code_width = max(len(field[1]) for field in FIELDS)
  for syntax, code, note in FIELDS:
    lines.append("  " + syntax.ljust(syntax_width) + "  " + code.ljust(code_width) + "  " + note)
  return "\n".join(lines) + "\n"
