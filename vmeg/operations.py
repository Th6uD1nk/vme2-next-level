import textwrap

from vmeg.pattern import check_patterns, parse_pattern

OPERATIONS = {
  "add": {
    "opcode": 0x010,
    "not_portable": True,
    "pattern": "a + b",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_ADD)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the sum of a and b",
  },
  "add_ofa": {
    "opcode": 0x030,
    "pattern": "a + b + c",
    "arguments": (("a", "operand"), ("b", "operand"), ("c", "number")),
    "registers": {"A": "c"},
    "code": "fu_code(OP_ADD_OFA)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "(a + b) + c, c is a number written in the register A, 0 when it is not written",
  },
  "add_cst": {
    "opcode": 0x024,
    "pattern": "x + c",
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_ADD_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the sum of x and c, c is a number written in the register B",
  },
  "sub": {
    "opcode": 0x018,
    "pattern": "a - b",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_SUB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "a minus b, no constant",
  },
  "subacst": {
    "opcode": 0x048,
    "pattern": "a - b + c",
    "aliases": ("subacst(a, b, c)",),
    "arguments": (("a", "operand"), ("b", "operand"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_SUB_OFB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "(a - b) + c, c is a number written in the register B of the operation",
  },
  "subshr": {
    "opcode": 0x050,
    "pattern": "b - (a >> n)",
    "aliases": ("subshr(a, b, n)",),
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
    "pattern": "a * b",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "VME_FU_OPCODE_MUL_RSHIFT_0",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "(a * b) >> k, k is the `>> n` written after the operation",
  },
  "and": {
    "opcode": 0x0c0,
    "pattern": "a & b",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_AND)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the bitwise and of a and b",
  },
  "and_cst": {
    "opcode": 0x0c4,
    "pattern": "x & c",
    "aliases": ("and(x, c)",),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_AND_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the bitwise and of x and c, c is a number written in the register B",
  },
  "nand": {
    "opcode": 0x0c8,
    "pattern": "~(a & b)",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_NAD)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the complement of the bitwise and of a and b, one operation",
  },
  "nand_cst": {
    "opcode": 0x0cc,
    "pattern": "~(x & c)",
    "aliases": ("~and(x, c)",),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_NAD_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the complement of the bitwise and of x and c, one operation, c is a number written in the register B",
  },
  "or": {
    "opcode": 0x0d0,
    "pattern": "a | b",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_OR)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the bitwise or of a and b",
  },
  "nor": {
    "opcode": 0x0d8,
    "pattern": "~(a | b)",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_NOR)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the complement of the bitwise or of a and b, one operation",
  },
  "or_cst": {
    "opcode": 0x0d4,
    "pattern": "x | c",
    "aliases": ("or(x, c)",),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_OR_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the bitwise or of x and c, c is a number written in the register B",
  },
  "nor_cst": {
    "opcode": 0x0dc,
    "pattern": "~(x | c)",
    "aliases": ("~or(x, c)",),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_NOR_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the complement of the bitwise or of x and c, one operation, c is a number written in the register B",
  },
  "xor": {
    "opcode": 0x0e0,
    "pattern": "a ^ b",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_XOR)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the bitwise exclusive or of a and b",
  },
  "xor_cst": {
    "opcode": 0x0e4,
    "pattern": "x ^ c",
    "aliases": ("xor(x, c)",),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_XOR_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the bitwise exclusive or of x and c, c is a number written in the register B",
  },
  "xnor_cst": {
    "opcode": 0x0ec,
    "pattern": "~(x ^ c)",
    "aliases": ("~xor(x, c)",),
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_XOR_CST_NOT)",
    "operands": ("back",),
    "units": "any",
    "note": "the complement of the bitwise exclusive or of x and c, one operation, c is a number written in the register B",
  },
  "not": {
    "opcode": 0x0fc,
    "pattern": "~x",
    "arguments": (("x", "source"),),
    "registers": {},
    "code": "fu_code(OP_NOT)",
    "operands": ("back",),
    "units": "any",
    "note": "the bitwise complement of x, x is a buffer, a Staging variable or an operation",
  },
  "clamp": {
    "opcode": 0x07c,
    "pattern": "clamp(x, low, high)",
    "arguments": (("x", "source"), ("low", "number"), ("high", "number")),
    "registers": {"A": "high", "B": "low"},
    "code": "fu_code(OP_CLP)",
    "operands": ("back",),
    "units": "any",
    "note": "registers A = high and B = low, x is a buffer, a Staging variable or an operation",
  },
  "mac": {
    "opcode": 0x240,
    "pattern": "mac(a, b)",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "VME_FU_OPCODE_MAC_INNER_PRODUCT_BIAS",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "running inner product (sum of a * b + bias) >> k",
  },
  "acc": {
    "opcode": 0x250,
    "pattern": "acc(x)",
    "arguments": (("x", "operand"),),
    "registers": {},
    "code": "VME_FU_OPCODE_MAC_ACC_SHIFT_BIAS",
    "operands": ("back",),
    "units": "primary",
    "note": "running sum, x is a buffer or a Staging variable",
  },
}

check_patterns(OPERATIONS)


def calls_of(operations):
  found = {}
  for kind, specification in operations.items():
    for text in (specification["pattern"], *specification.get("aliases", ())):
      tree = parse_pattern(text)
      if tree[0] == "call":
        found.setdefault(tree[1], kind)
  return found


def operators_of(operations):
  found = []
  for specification in operations.values():
    tree = parse_pattern(specification["pattern"])
    if tree[0] == "bin" and tree[1] not in found:
      found.append(tree[1])
  return found


FUNCTIONS = calls_of(OPERATIONS)

OPERATORS = operators_of(OPERATIONS)

FIELDS = (
  ("sat(op, bits)", "fu_sat(bits)", "the saturation of the operation it wraps, bits 0 to 31"),
  ("op >> n", "k = n", "the shift applied to the result of the operation, n 0 to 63"),
  ("op << n", "k = 64 - n", "the rotary shift, n 0 to 63"),
)


def reads(specification):
  return tuple(name for name, kind in specification["arguments"] if kind in ("operand", "source"))


def slots(specification):
  return len(reads(specification)) + len(specification["registers"])


DESCRIPTION_WIDTH = 40


def operation_block(specification):
  indent = " " * 7
  lines = [f"0x{specification['opcode']:03x}: {specification['pattern']}"]
  lines.extend(indent + line for line in textwrap.wrap(specification["note"], DESCRIPTION_WIDTH))
  if specification.get("aliases"):
    lines.append(indent + "also written " + ", ".join(specification["aliases"]))
  if specification["registers"]:
    lines.append(indent + "registers " + ", ".join(f"{name} = {register}" for register, name in specification["registers"].items()))
  lines.append(indent + ("position first operation of the pe only" if specification["units"] == "primary" else "position any"))
  if specification.get("not_portable"):
    lines.append(indent + "not portable")
  return lines


def format_operations():
  lines = ["operations:", ""]
  blocks = ["\n".join(operation_block(specification)) for specification in sorted(OPERATIONS.values(), key=lambda specification: specification["opcode"])]
  lines.append("\n\n".join(blocks))
  lines.append("")
  lines.append("options of the operation they wrap:")
  syntax_width = max(len(field[0]) for field in FIELDS)
  code_width = max(len(field[1]) for field in FIELDS)
  for syntax, code, note in FIELDS:
    lines.append("  " + syntax.ljust(syntax_width) + "  " + code.ljust(code_width) + "  " + note)
  return "\n".join(lines) + "\n"
