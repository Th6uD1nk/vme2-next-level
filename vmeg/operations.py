OPERATIONS = {
  "add": {
    "opcode": 0x010,
    "form": ("operator", "+"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_ADD)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the sum of a and b",
  },
  "sub": {
    "opcode": 0x018,
    "form": ("operator", "-"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_SUB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "a minus b, no constant",
  },
  "subacst": {
    "opcode": 0x048,
    "form": ("function", "subacst"),
    "arguments": (("a", "operand"), ("b", "operand"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_SUB_OFB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "(a - b) + c, c is a number written in the register B of the operation",
  },
  "subshr": {
    "opcode": 0x050,
    "form": ("function", "subshr"),
    "arguments": (("a", "operand"), ("b", "operand"), ("n", "number")),
    "registers": {"B": "n"},
    "minimums": {"n": 0},
    "code": "fu_code(OP_SUB_INV_SHF)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "b - (a >> n), n is a number written in the register B of the operation",
  },
  "mul": {
    "opcode": 0x200,
    "form": ("operator", "*"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "VME_FU_OPCODE_MUL_RSHIFT_0",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "(a * b) >> k, k is the `>> n` written after the operation",
  },
  "and": {
    "opcode": 0x0c0,
    "form": ("operator", "&"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_AND)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the bitwise and of a and b",
  },
  "clamp": {
    "opcode": 0x07c,
    "form": ("function", "clamp"),
    "arguments": (("x", "source"), ("low", "number"), ("high", "number")),
    "registers": {"A": "high", "B": "low"},
    "code": "fu_code(OP_CLP)",
    "operands": ("back",),
    "units": "any",
    "note": "registers A = high and B = low, x is a buffer, a Staging variable or an operation",
  },
  "mac": {
    "opcode": 0x240,
    "form": ("function", "mac"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "VME_FU_OPCODE_MAC_INNER_PRODUCT_BIAS",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "running inner product (sum of a * b + bias) >> k",
  },
  "acc": {
    "opcode": 0x250,
    "form": ("function", "acc"),
    "arguments": (("x", "operand"),),
    "registers": {},
    "code": "VME_FU_OPCODE_MAC_ACC_SHIFT_BIAS",
    "operands": ("back",),
    "units": "primary",
    "note": "running sum, x is a buffer or a Staging variable",
  },
}

OPERATORS = {specification["form"][1]: kind for kind, specification in OPERATIONS.items() if specification["form"][0] == "operator"}

FUNCTIONS = {specification["form"][1]: kind for kind, specification in OPERATIONS.items() if specification["form"][0] == "function"}

FIELDS = (
  ("sat(op, bits)", "fu_sat(bits)", "the saturation of the operation it wraps, bits 0 to 31"),
  ("op >> n", "k = n", "the shift applied to the result of the operation, n 0 to 63"),
  ("op << n", "k = 64 - n", "the rotary shift, n 0 to 63"),
)


def reads(specification):
  return tuple(name for name, kind in specification["arguments"] if kind in ("operand", "source"))


def syntax(specification):
  names = [name for name, _ in specification["arguments"]]
  form, name = specification["form"]
  if form == "operator":
    return f"{names[0]} {name} {names[1]}"
  return f"{name}({', '.join(names)})"


def operation_columns(specification):
  units = "first operation of the pe only" if specification["units"] == "primary" else "any position"
  return (syntax(specification), f"0x{specification['opcode']:03x}", specification["code"], ", ".join(reads(specification)), units)


def format_operations():
  rows = [operation_columns(specification) for specification in OPERATIONS.values()]
  widths = [max(len(row[i]) for row in rows) for i in range(5)]
  lines = ["operations:"]
  for specification, row in zip(OPERATIONS.values(), rows):
    lines.append("  " + "  ".join(column.ljust(width) for column, width in zip(row, widths)).rstrip())
    lines.append("      " + specification["note"])
  lines.append("")
  lines.append("options of the operation they wrap:")
  syntax_width = max(len(field[0]) for field in FIELDS)
  code_width = max(len(field[1]) for field in FIELDS)
  for syntax, code, note in FIELDS:
    lines.append("  " + syntax.ljust(syntax_width) + "  " + code.ljust(code_width) + "  " + note)
  return "\n".join(lines) + "\n"
