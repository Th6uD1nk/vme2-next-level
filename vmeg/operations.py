OPERATIONS = {
  "add": {
    "opcode": 0x010,
    "not_portable": True,
    "form": ("operator", "+"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_ADD)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the sum of a and b",
  },
  "add_ofa": {
    "opcode": 0x030,
    "form": ("variant", "add"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "fixed": {"A": 0},
    "code": "fu_code(OP_ADD_OFA)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "variant of a + b for the models where 0x010 does not work: (a + b) + A, with the register A written at 0",
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
  "and_cst": {
    "opcode": 0x0c4,
    "form": ("function", "and"),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_AND_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the bitwise and of x and c, c is a number written in the register B",
  },
  "nand": {
    "opcode": 0x0c8,
    "form": ("fused", "and"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_NAD)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the complement of the bitwise and of a and b, one operation",
  },
  "nand_cst": {
    "opcode": 0x0cc,
    "form": ("fused", "and_cst"),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_NAD_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the complement of the bitwise and of x and c, one operation, c is a number written in the register B",
  },
  "or": {
    "opcode": 0x0d0,
    "form": ("operator", "|"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_OR)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the bitwise or of a and b",
  },
  "nor": {
    "opcode": 0x0d8,
    "form": ("fused", "or"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_NOR)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the complement of the bitwise or of a and b, one operation",
  },
  "or_cst": {
    "opcode": 0x0d4,
    "form": ("function", "or"),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_OR_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the bitwise or of x and c, c is a number written in the register B",
  },
  "nor_cst": {
    "opcode": 0x0dc,
    "form": ("fused", "or_cst"),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_NOR_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the complement of the bitwise or of x and c, one operation, c is a number written in the register B",
  },
  "xor": {
    "opcode": 0x0e0,
    "form": ("operator", "^"),
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_XOR)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the bitwise exclusive or of a and b",
  },
  "xor_cst": {
    "opcode": 0x0e4,
    "form": ("function", "xor"),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_XOR_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the bitwise exclusive or of x and c, c is a number written in the register B",
  },
  "xnor_cst": {
    "opcode": 0x0ec,
    "form": ("fused", "xor_cst"),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_XOR_CST_NOT)",
    "operands": ("back",),
    "units": "any",
    "note": "the complement of the bitwise exclusive or of x and c, one operation, c is a number written in the register B",
  },
  "not": {
    "opcode": 0x0fc,
    "form": ("operator", "~"),
    "arguments": (("x", "source"),),
    "registers": {},
    "code": "fu_code(OP_NOT)",
    "operands": ("back",),
    "units": "any",
    "note": "the bitwise complement of x, x is a buffer, a Staging variable or an operation",
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

OPERATORS = {specification["form"][1]: kind for kind, specification in OPERATIONS.items() if specification["form"][0] == "operator" and len(specification["arguments"]) == 2}

UNARY_OPERATORS = {specification["form"][1]: kind for kind, specification in OPERATIONS.items() if specification["form"][0] == "operator" and len(specification["arguments"]) == 1}

FUSIONS = {specification["form"][1]: kind for kind, specification in OPERATIONS.items() if specification["form"][0] == "fused"}

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
  if form == "variant":
    return syntax(OPERATIONS[name])
  if form == "fused":
    inner = OPERATIONS[name]
    return f"~({syntax(inner)})" if inner["form"][0] == "operator" else f"~{syntax(inner)}"
  if form == "operator":
    return f"{name}{names[0]}" if len(names) == 1 else f"{names[0]} {name} {names[1]}"
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
