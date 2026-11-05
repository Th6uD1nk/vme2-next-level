import textwrap

from vmeg.pattern import check_patterns, children, parse_pattern

OPERATIONS = {
  "pass": {
    "opcode": 0x004,
    "pattern": "x",
    "aliases": ("pass(x)",),
    "arguments": (("x", "source"),),
    "registers": {},
    "code": "fu_code(OP_BAK)",
    "operands": ("back",),
    "units": "any",
    "note": "x as it is, a buffer or a Staging variable, alone or with the sat, the round and the shift that wrap it",
  },
  "cst": {
    "opcode": 0x00c,
    "pattern": "c",
    "aliases": ("cst(c)",),
    "arguments": (("c", "number"),),
    "registers": {"B": "c"},
    "code": "fu_code(OP_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the number c, whatever the operands are, alone or with the sat, the round and the shift that wrap it",
  },
  "bak_shr": {
    "opcode": 0x014,
    "pattern": "x >> n",
    "arguments": (("x", "source"), ("n", "number")),
    "registers": {},
    "shift": "n",
    "code": "fu_code(0x014)",
    "operands": ("back",),
    "units": "any",
    "note": "x shifted to the right by n, as the k of the opcode (an arithmetic shift of the exact value), x is a buffer or a Staging variable",
  },
  "neg_ofb": {
    "opcode": 0x02c,
    "pattern": "c - x",
    "arguments": (("c", "number"), ("x", "source")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_NEG_OFB)",
    "operands": ("back",),
    "units": "any",
    "note": "the number c minus x, x is a buffer or a Staging variable, the shift of the operation is kept",
  },
  "add_byt": {
    "opcode": 0x038,
    "pattern": "addbyt(a, b)",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(0x038)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the two low bytes of a and of b added together, the sum of the bytes 0 and 1 of both, no register",
  },
  "sub_byt": {
    "opcode": 0x03c,
    "pattern": "subbyt(a, b)",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(0x03c)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the difference of the byte 0 of a and b plus the difference of their byte 1, no register",
  },
  "add_shf": {
    "opcode": 0x040,
    "pattern": "b + (a >> n)",
    "arguments": (("a", "operand"), ("b", "operand"), ("n", "number")),
    "registers": {"B": "n"},
    "code": "fu_code(OP_ADD_SHF)",
    "operands": ("back", "front"),
    "units": "any",
    "note": "b plus a shifted to the right by n, the shift is on a",
  },
  "shr_cst_ofa": {
    "opcode": 0x044,
    "pattern": "(x >> n) + c",
    "arguments": (("x", "source"), ("n", "number"), ("c", "number")),
    "registers": {"A": "c", "B": "n"},
    "code": "fu_code(OP_SHR_CST_OFA)",
    "operands": ("back",),
    "units": "any",
    "note": "x shifted to the right by n, plus c",
  },
  "shr_cst_neg_ofa": {
    "opcode": 0x04c,
    "pattern": "c - (x >> n)",
    "arguments": (("x", "source"), ("n", "number"), ("c", "number")),
    "registers": {"A": "c", "B": "n"},
    "code": "fu_code(OP_SHR_CST_NEG_OFA)",
    "operands": ("back",),
    "units": "any",
    "note": "c minus x shifted to the right by n",
  },
  "shr_cst_ofs": {
    "opcode": 0x054,
    "pattern": "(x >> n) - c",
    "arguments": (("x", "source"), ("n", "number"), ("c", "number")),
    "registers": {"A": "c", "B": "n"},
    "code": "fu_code(OP_SHR_CST_OFS)",
    "operands": ("back",),
    "units": "any",
    "note": "x shifted to the right by n, minus c",
  },
  "add_hib": {
    "opcode": 0x058,
    "pattern": "addhib(a, b)",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_ADD_HIB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the byte 1 of a plus the byte 1 of b",
  },
  "add_lob": {
    "opcode": 0x05c,
    "pattern": "(a & 255) + (b & 255)",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "fu_code(OP_ADD_LOB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the byte 0 of a plus the byte 0 of b",
  },
  "sel_neg": {
    "opcode": 0x060,
    "pattern": "(f & a) ? -x : x",
    "arguments": (("f", "operand"), ("x", "operand"), ("a", "number")),
    "registers": {"A": "a"},
    "code": "fu_code(OP_SEL_NEG)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "x negated when f & a is not zero, x otherwise",
  },
  "sel_neg_slf": {
    "opcode": 0x064,
    "pattern": "(f & a) ? x : -x",
    "arguments": (("f", "operand"), ("x", "operand"), ("a", "number")),
    "registers": {"A": "a"},
    "code": "fu_code(OP_SEL_NEG_SLF)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "x when f & a is not zero, x negated otherwise",
  },
  "sel_cst": {
    "opcode": 0x068,
    "pattern": "(f & a) ? b : x",
    "arguments": (("f", "operand"), ("x", "operand"), ("a", "number"), ("b", "number")),
    "registers": {"A": "a", "B": "b"},
    "code": "fu_code(OP_SEL_CST)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "the number b when f & a is not zero, x otherwise",
  },
  "sel_cst_ofb": {
    "opcode": 0x06c,
    "pattern": "(f & a) ? x : b",
    "arguments": (("f", "operand"), ("x", "operand"), ("a", "number"), ("b", "number")),
    "registers": {"A": "a", "B": "b"},
    "code": "fu_code(OP_SEL_CST_OFB)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "x when f & a is not zero, the number b otherwise",
  },
  "sel_ads": {
    "opcode": 0x070,
    "pattern": "(x & a) ? x - b : x + b",
    "arguments": (("x", "operand"), ("a", "number"), ("b", "number")),
    "registers": {"A": "a", "B": "b"},
    "code": "fu_code(OP_SEL_ADS)",
    "operands": ("back",),
    "units": "any",
    "note": "x minus b when x & a is not zero, x plus b otherwise",
  },
  "sel_ads_inv": {
    "opcode": 0x074,
    "pattern": "(x & a) ? x + b : x - b",
    "arguments": (("x", "operand"), ("a", "number"), ("b", "number")),
    "registers": {"A": "a", "B": "b"},
    "code": "fu_code(OP_SEL_ADS_INV)",
    "operands": ("back",),
    "units": "any",
    "note": "x plus b when x & a is not zero, x minus b otherwise",
  },
  "sel_cst_zer": {
    "opcode": 0x088,
    "pattern": "(x & a) ? 0 : b",
    "arguments": (("x", "operand"), ("a", "number"), ("b", "number")),
    "registers": {"A": "a", "B": "b"},
    "code": "fu_code(OP_SEL_CST_ZER)",
    "operands": ("back",),
    "units": "any",
    "note": "zero when x & a is not zero, the number b otherwise",
  },
  "sel_cst_zer_inv": {
    "opcode": 0x08c,
    "pattern": "(x & a) ? b : 0",
    "arguments": (("x", "operand"), ("a", "number"), ("b", "number")),
    "registers": {"A": "a", "B": "b"},
    "code": "fu_code(OP_SEL_CST_ZER_INV)",
    "operands": ("back",),
    "units": "any",
    "note": "the number b when x & a is not zero, zero otherwise",
  },
  "mul_clp": {
    "opcode": 0x080,
    "pattern": "mulclp(f, x)",
    "arguments": (("f", "operand"), ("x", "operand")),
    "registers": {},
    "code": "fu_code(OP_MUL_CLP)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "x times f when f is from -2 to 2, zero otherwise",
  },
  "mul_clp_neg": {
    "opcode": 0x084,
    "pattern": "mulclpneg(f, x)",
    "arguments": (("f", "operand"), ("x", "operand")),
    "registers": {},
    "code": "fu_code(OP_MUL_CLP_NEG)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "minus x times f when f is from -2 to 2, zero otherwise",
  },
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
    "note": "the sum of a and b plus c, 0 when c is not written",
  },
  "add_cst": {
    "opcode": 0x024,
    "pattern": "x + c",
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_ADD_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "the sum of x and c",
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
    "opcode": 0x034,
    "pattern": "a - b + c",
    "aliases": ("subacst(a, b, c)",),
    "arguments": (("a", "operand"), ("b", "operand"), ("c", "number")),
    "registers": {"A": "c"},
    "code": "fu_code(OP_SUB_INV_OFA)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "a minus b, plus c",
  },
  "subshr": {
    "opcode": 0x048,
    "pattern": "b - (a >> n)",
    "aliases": ("subshr(a, b, n)",),
    "arguments": (("a", "operand"), ("b", "operand"), ("n", "number")),
    "registers": {"B": "n"},
    "code": "fu_code(OP_SUB_OFB)",
    "operands": ("back", "front"),
    "units": "any",
    "note": "b minus a shifted to the right by n",
  },
  "shrsub": {
    "opcode": 0x050,
    "pattern": "(a >> n) - b",
    "arguments": (("a", "operand"), ("b", "operand"), ("n", "number")),
    "registers": {"B": "n"},
    "code": "fu_code(OP_SUB_INV_SHF)",
    "operands": ("back", "front"),
    "units": "any",
    "note": "a shifted to the right by n, minus b",
  },
  "mul": {
    "opcode": 0x200,
    "pattern": "a * b",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "VME_FU_OPCODE_MUL_RSHIFT_0",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "the product of a and b, shifted by the `>> n` after it",
  },
  "mul_cst": {
    "opcode": 0x204,
    "pattern": "x * c",
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "VME_FU_OPCODE_MUL_CONST_RSHIFT_0",
    "operands": ("back",),
    "units": "primary",
    "note": "the product of x and c, shifted by the `>> n` after it",
  },
  "mul_vec": {
    "opcode": 0x220,
    "auxiliary": True,
    "pattern": "a * b",
    "arguments": (("a", "operand"), ("b", "operand")),
    "registers": {},
    "code": "VME_FU_OPCODE_MUL_VEC_RSHIFT",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "the product of a and b, shifted by the `>> n` after it",
  },
  "shl_cst": {
    "opcode": 0x0a4,
    "pattern": "x << c",
    "arguments": (("x", "source"), ("c", "number")),
    "registers": {"B": "c"},
    "code": "fu_code(OP_SHL_CST)",
    "operands": ("back",),
    "units": "any",
    "note": "x shifted to the left by c, c is a signed number of 6 bits and a negative c shifts to the right",
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
    "note": "the bitwise and of x and c",
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
    "note": "the complement of the bitwise and of x and c, one operation",
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
    "note": "the bitwise or of x and c",
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
    "note": "the complement of the bitwise or of x and c, one operation",
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
    "note": "the bitwise exclusive or of x and c",
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
    "note": "the complement of the bitwise exclusive or of x and c, one operation",
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
    "note": "x limited between low and high, x is a buffer, a Staging variable or an operation",
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

OPERATIONS = dict(sorted(OPERATIONS.items(), key=lambda entry: entry[1]["opcode"]))

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


def name_operator(specification):
  return "cst" if dict(specification["arguments"])[parse_pattern(specification["pattern"])[1]] == "number" else "pass"


def pattern_operators(specification):
  found = set()
  if parse_pattern(specification["pattern"])[0] == "name":
    found.add(name_operator(specification))

  def walk(tree):
    if tree[0] == "bin":
      found.add(tree[1])
    for child in children(tree):
      walk(child)

  for text in (specification["pattern"], *specification.get("aliases", ())):
    walk(parse_pattern(text))
  return found


def root_operator(specification):
  tree = parse_pattern(specification["pattern"])
  if tree[0] == "name":
    return name_operator(specification)
  return tree[1] if tree[0] == "bin" else None


FUNCTIONS = calls_of(OPERATIONS)

ROOT_OPERATORS = {kind: root_operator(specification) for kind, specification in OPERATIONS.items()}

PATTERN_OPERATORS = {kind: pattern_operators(specification) for kind, specification in OPERATIONS.items()}

OPCODE_KINDS = {specification["opcode"]: kind for kind, specification in OPERATIONS.items()}

OPERATORS = operators_of(OPERATIONS)

FIELDS = (
  ("sat(op, bits)", "fu_sat(bits)", "the saturation of the operation it wraps, bits 0 to 31"),
  ("round(op)", "1 << 6", "the rounding of the shift of the operation it wraps, the bit 6 of its register"),
  ("op >> n", "k = n", "the shift applied to the result of the operation, n 0 to 63"),
  ("op << n", "k = 64 - n", "the rotary shift, n 0 to 63"),
)


def reads(specification):
  return tuple(name for name, kind in specification["arguments"] if kind in ("operand", "source"))


def slots(specification):
  return len(reads(specification)) + len(specification["registers"])


DESCRIPTION_WIDTH = 60


def operation_block(specification):
  indent = " " * 7
  lines = [f"0x{specification['opcode']:03x}: {specification['pattern']}"]
  lines.extend(indent + line for line in textwrap.wrap(specification["note"], DESCRIPTION_WIDTH))
  if specification.get("aliases"):
    lines.append(indent + "also written " + ", ".join(specification["aliases"]))
  if specification["registers"]:
    lines.append(indent + "registers " + ", ".join(f"{name} = {register}" for register, name in specification["registers"].items()))
  kind = OPCODE_KINDS[specification["opcode"]]
  root = ROOT_OPERATORS[kind]
  others = sorted(OPERATIONS[other]["opcode"] for other, operators in PATTERN_OPERATORS.items() if other != kind and root in operators) if root else []
  if others:
    lines.append(indent + "can be remapped with " + ", ".join(f"0x{opcode:03x}" for opcode in others))
  if specification.get("auxiliary"):
    lines.append(indent + "only reached by a remap")
  lines.append(indent + ("position first operation of the pe, a warning in the second one" if specification["units"] == "primary" else "position any"))
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
