IN0 = [1, 2, 3, 4, 0x100, 0x10000, 0x7fffff, -1, -2, -0x800000, 0x1234, 0x555555, -0x555556, 255, -256, 5]
IN1 = [0, 1, 1, 2, 0x80, 0x100, 0x7ffffe, 1, -1, 1, 0x234, 0x2aaaaa, 0x555555, 5, 0x100, -5]


def unsigned(v):
  return v & 0xffffff


def amount(v):
  v &= 63
  return v - 64 if v >= 32 else v


def shift_left(v, n):
  return v << n if n >= 0 else v >> -n


def byte0(v):
  return v & 0xff


def byte1(v):
  return (v >> 8) & 0xff


SPECS = [
  dict(id="pass", opcode=0x004, lot=1, writings=["top1", "(top1)", "pass(top1)", "sat(top1, 31)"], expected=lambda f, b: b),
  dict(id="cst", opcode=0x00c, lot=1, writings=["5", "cst(5)", "10 - 5", "(1 << 2) | 1"], expected=lambda f, b: 5),
  dict(id="add", opcode=0x010, lot=2, writings=["top0 + top1", "top1 + top0", "(top0 + top1)", "top0 + (top1)"], expected=lambda f, b: f + b),
  dict(id="bak_shr", opcode=0x014, lot=2, writings=["top1 >> 3", "(top1 >> 3)", "top1 >> (1 + 2)", "(top1) >> 3"], expected=lambda f, b: b >> 3),
  dict(id="sub", opcode=0x018, lot=2, writings=["top0 - top1", "(top0 - top1)", "top0 - (top1)", "(top0) - (top1)"], expected=lambda f, b: f - b),
  dict(id="add_cst", opcode=0x024, lot=3, writings=["top1 + 3", "3 + top1", "(top1) + 3", "(top1 + 3)"], expected=lambda f, b: b + 3),
  dict(id="neg_ofb", opcode=0x02c, lot=3, writings=["7 - top1", "(7 - top1)", "7 - (top1)", "(7) - top1"], expected=lambda f, b: 7 - b),
  dict(id="add_ofa", opcode=0x030, lot=4, writings=["top0 + top1 + 5", "(top0 + top1) + 5", "5 + (top0 + top1)", "top1 + top0 + 5"], expected=lambda f, b: f + b + 5),
  dict(id="subacst", opcode=0x034, lot=4, writings=["top0 - top1 + 5", "subacst(top0, top1, 5)", "(top0 - top1) + 5", "5 + (top0 - top1)"], expected=lambda f, b: f - b + 5),
  dict(id="add_byt", opcode=0x038, lot=4, writings=["addbyt(top0, top1)", "addbyt(top1, top0)", "addbyt( top0 , top1 )", "(addbyt(top0, top1))"], expected=lambda f, b: byte0(f) + byte0(b) + byte1(f) + byte1(b)),
  dict(id="sub_byt", opcode=0x03c, lot=4, writings=["subbyt(top0, top1)", "(subbyt(top0, top1))", "subbyt( top0 , top1 )", "subbyt(top0,top1)"], expected=lambda f, b: byte0(f) - byte0(b) + byte1(f) - byte1(b)),
]
