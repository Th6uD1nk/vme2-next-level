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
]
