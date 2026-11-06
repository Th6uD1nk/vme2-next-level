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
  dict(id="add_shf", opcode=0x040, lot=5, writings=["top0 + (top1 >> 3)", "(top1 >> 3) + top0", "top0 + (top1 >> 1 + 2)", "(top0) + ((top1) >> 3)"], expected=lambda f, b: f + (b >> 3)),
  dict(id="shr_cst_ofa", opcode=0x044, lot=5, writings=["(top1 >> 3) + 5", "5 + (top1 >> 3)", "((top1 >> 3)) + 5", "(top1 >> 3) + (2 + 3)"], expected=lambda f, b: (b >> 3) + 5),
  dict(id="subshr", opcode=0x048, lot=5, writings=["top0 - (top1 >> 3)", "subshr(top1, top0, 3)", "(top0) - (top1 >> 3)", "top0 - ((top1) >> 3)"], expected=lambda f, b: f - (b >> 3)),
  dict(id="shr_cst_neg_ofa", opcode=0x04c, lot=5, writings=["5 - (top1 >> 3)", "(5) - (top1 >> 3)", "(2 + 3) - (top1 >> 3)", "5 - ((top1) >> 3)"], expected=lambda f, b: 5 - (b >> 3)),
  dict(id="shrsub", opcode=0x050, lot=6, writings=["(top1 >> 3) - top0", "((top1 >> 3)) - top0", "(top1 >> 3) - (top0)", "((top1) >> 3) - top0"], expected=lambda f, b: (b >> 3) - f),
  dict(id="shr_cst_ofs", opcode=0x054, lot=6, writings=["(top1 >> 3) - 5", "((top1 >> 3)) - 5", "(top1 >> 3) - (2 + 3)", "((top1) >> 3) - 5"], expected=lambda f, b: (b >> 3) - 5),
  dict(id="add_hib", opcode=0x058, lot=6, writings=["addhib(top0, top1)", "addhib(top1, top0)", "addhib( top0 , top1 )", "(addhib(top0, top1))"], expected=lambda f, b: byte1(f) + byte1(b)),
  dict(id="add_lob", opcode=0x05c, lot=6, writings=["(top0 & 255) + (top1 & 255)", "(top1 & 0xff) + (top0 & 0xff)", "((top0 & 255)) + ((top1 & 255))", "(255 & top0) + (255 & top1)"], expected=lambda f, b: byte0(f) + byte0(b)),
  dict(id="sel_neg", opcode=0x060, lot=7, writings=["(top0 & 4) ? -top1 : top1", "(4 & top0) ? -top1 : top1", "(top0 & 0x4) ? (-top1) : top1", "((top0 & 4)) ? -top1 : (top1)"], expected=lambda f, b: -b if f & 4 else b),
  dict(id="sel_neg_slf", opcode=0x064, lot=7, writings=["(top0 & 4) ? top1 : -top1", "(4 & top0) ? top1 : -top1", "(top0 & 0x4) ? top1 : (-top1)", "((top0 & 4)) ? (top1) : -top1"], expected=lambda f, b: b if f & 4 else -b),
  dict(id="sel_cst", opcode=0x068, lot=7, writings=["(top0 & 4) ? 7 : top1", "(4 & top0) ? 7 : top1", "(top0 & 0x4) ? (3 + 4) : top1", "((top0 & 4)) ? 7 : (top1)"], expected=lambda f, b: 7 if f & 4 else b),
  dict(id="sel_cst_ofb", opcode=0x06c, lot=7, writings=["(top0 & 4) ? top1 : 7", "(4 & top0) ? top1 : 7", "(top0 & 0x4) ? top1 : (3 + 4)", "((top0 & 4)) ? (top1) : 7"], expected=lambda f, b: b if f & 4 else 7),
  dict(id="sel_ads", opcode=0x070, lot=8, writings=["(top1 & 4) ? top1 - 7 : top1 + 7", "(4 & top1) ? top1 - 7 : top1 + 7", "(top1 & 0x4) ? (top1 - 7) : (top1 + 7)", "((top1 & 4)) ? top1 - (3 + 4) : top1 + 7"], expected=lambda f, b: b - 7 if b & 4 else b + 7),
  dict(id="sel_ads_inv", opcode=0x074, lot=8, writings=["(top1 & 4) ? top1 + 7 : top1 - 7", "(4 & top1) ? top1 + 7 : top1 - 7", "(top1 & 0x4) ? (top1 + 7) : (top1 - 7)", "((top1 & 4)) ? top1 + (3 + 4) : top1 - 7"], expected=lambda f, b: b + 7 if b & 4 else b - 7),
  dict(id="clamp", opcode=0x07c, lot=8, writings=["clamp(top1, -100, 100)", "clamp(top1,-100,100)", "clamp((top1), -100, 100)", "clamp(top1, 0 - 100, 50 + 50)"], expected=lambda f, b: max(-100, min(100, b))),
  dict(id="mul_clp", opcode=0x080, lot=9, writings=["mulclp(top0, top1)", "(mulclp(top0, top1))", "mulclp( top0 , top1 )", "mulclp(top0,top1)"], expected=lambda f, b: b * f if -2 <= f <= 2 else 0),
  dict(id="mul_clp_neg", opcode=0x084, lot=9, writings=["mulclpneg(top0, top1)", "(mulclpneg(top0, top1))", "mulclpneg( top0 , top1 )", "mulclpneg(top0,top1)"], expected=lambda f, b: -(b * f) if -2 <= f <= 2 else 0),
  dict(id="sel_cst_zer", opcode=0x088, lot=9, writings=["(top1 & 4) ? 0 : 9", "(4 & top1) ? 0 : 9", "(top1 & 0x4) ? 0 : (3 * 3)", "((top1 & 4)) ? 0 : 9"], expected=lambda f, b: 0 if b & 4 else 9),
  dict(id="sel_cst_zer_inv", opcode=0x08c, lot=9, writings=["(top1 & 4) ? 9 : 0", "(4 & top1) ? 9 : 0", "(top1 & 0x4) ? (3 * 3) : 0", "((top1 & 4)) ? 9 : 0"], expected=lambda f, b: 9 if b & 4 else 0),
  dict(id="shl_dyn", opcode=0x090, lot=10, writings=["-5 << top1", "(-5) << top1", "(0 - 5) << top1", "(-5) << (top1)"], expected=lambda f, b: shift_left(-5, amount(b))),
  dict(id="shr_dyn", opcode=0x094, lot=10, writings=["-5 >> top1", "(-5) >> top1", "(0 - 5) >> top1", "(-5) >> (top1)"], expected=lambda f, b: shift_left(-5, -amount(b))),
  dict(id="shl_dyn_u", opcode=0x098, lot=10, writings=["0xc00000 << top1", "(0xc00000) << top1", "(0x800000 + 0x400000) << top1", "(0xc00000) << (top1)"], expected=lambda f, b: shift_left(0xc00000, amount(b))),
  dict(id="shr_dyn_u", opcode=0x09c, lot=10, writings=["0xc00000 >> top1", "(0xc00000) >> top1", "(0x800000 + 0x400000) >> top1", "(0xc00000) >> (top1)"], expected=lambda f, b: shift_left(0xc00000, -amount(b))),
]
