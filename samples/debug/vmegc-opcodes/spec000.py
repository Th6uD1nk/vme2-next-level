LIMITS = [0, 1, -1, 2, -2, 0x7fffff, -0x800000, 0x555555, -0x555556, 0xff, -0x100, 0x1234]


def signed24(v):
  v &= 0xffffff
  return v - 0x1000000 if v & 0x800000 else v


def series(seed, count):
  state = seed
  values = []
  for _ in range(count):
    state ^= (state << 13) & 0xffffffff
    state ^= state >> 17
    state ^= (state << 5) & 0xffffffff
    values.append(signed24(state))
  return values


def with_amount(value, n):
  return signed24(((value >> 6) << 6) | n)


FIRST = series(2463534242, 112)
SECOND = series(1812433253, 112)
IN0 = [a for a in LIMITS for b in LIMITS] + [with_amount(v, i) for i, v in enumerate(FIRST[:64])] + FIRST[64:]
IN1 = [b for a in LIMITS for b in LIMITS] + [with_amount(v, (i * 37 + 11) & 63) for i, v in enumerate(SECOND[:64])] + SECOND[64:]


def unsigned(v):
  return v & 0xffffff


def amount(v):
  v &= 63
  return v - 64 if v >= 32 else v


def shift_left(v, n):
  return v << n if n >= 0 else v >> -n


def shifted_right(v, n):
  return shift_left(v, -amount(n))


def byte0(v):
  return v & 0xff


def byte1(v):
  return (v >> 8) & 0xff


SPECS = [
  dict(id="pass", opcode=0x004, lot=1, writings=["top1", "(top1)", "pass(top1)", "sat(top1, 31)"], expected=lambda f, b: b),
  dict(id="cst", opcode=0x00c, lot=1, writings=["{0}", "cst({0})", "({0} + 1) - 1", "({0} * 1) | 0"], values=[(5,), (0,), (-1,), (8388607,), (-8388608,), (4660,), (16777215,), (4278190083,)], expected=lambda f, b, c: c),
  dict(id="add", opcode=0x010, lot=2, writings=["top0 + top1", "top1 + top0", "(top0 + top1)", "top0 + (top1)"], expected=lambda f, b: f + b),
  dict(id="bak_shr", opcode=0x014, lot=2, writings=["top1 >> 3", "(top1 >> 3)", "top1 >> (1 + 2)", "(top1) >> 3"], expected=lambda f, b: b >> 3),
  dict(id="sub", opcode=0x018, lot=2, writings=["top0 - top1", "(top0 - top1)", "top0 - (top1)", "(top0) - (top1)"], expected=lambda f, b: f - b),
  dict(id="add_cst", opcode=0x024, lot=3, writings=["top1 + {0}", "{0} + top1", "(top1) + {0}", "(top1 + {0})"], values=[(3,), (0,), (-1,), (8388607,), (-8388608,), (4660,), (16777215,), (4278190083,)], expected=lambda f, b, c: b + c),
  dict(id="neg_ofb", opcode=0x02c, lot=3, writings=["{0} - top1", "({0} - top1)", "{0} - (top1)", "({0}) - top1"], values=[(7,), (0,), (-1,), (8388607,), (-8388608,), (16777215,), (4278190083,)], expected=lambda f, b, c: c - b),
  dict(id="add_ofa", opcode=0x030, lot=4, writings=["top0 + top1 + {0}", "(top0 + top1) + {0}", "{0} + (top0 + top1)", "top1 + top0 + {0}"], values=[(5,), (-1,), (8388607,), (-8388608,), (4660,), (16777215,), (4278190083,)], expected=lambda f, b, c: f + b + c),
  dict(id="subacst", opcode=0x034, lot=4, writings=["top0 - top1 + {0}", "subacst(top0, top1, {0})", "(top0 - top1) + {0}", "{0} + (top0 - top1)"], values=[(5,), (-1,), (8388607,), (-8388608,), (4660,), (16777215,), (4278190083,)], expected=lambda f, b, c: f - b + c),
  dict(id="add_byt", opcode=0x038, lot=4, writings=["addbyt(top0, top1)", "addbyt(top1, top0)", "addbyt( top0 , top1 )", "(addbyt(top0, top1))"], expected=lambda f, b: byte0(f) + byte0(b) + byte1(f) + byte1(b)),
  dict(id="sub_byt", opcode=0x03c, lot=4, writings=["subbyt(top0, top1)", "(subbyt(top0, top1))", "subbyt( top0 , top1 )", "subbyt(top0,top1)"], expected=lambda f, b: byte0(f) - byte0(b) + byte1(f) - byte1(b)),
  dict(id="add_shf", opcode=0x040, lot=5, writings=["top0 + (top1 >> {0})", "(top1 >> {0}) + top0", "top0 + (top1 >> ({0} + 0))", "(top0) + ((top1) >> {0})"], values=[(3,), (0,), (1,), (31,), (-1,), (-32,), (40,), (16777215,), (4278190083,)], expected=lambda f, b, n: f + shifted_right(b, n)),
  dict(id="shr_cst_ofa", opcode=0x044, lot=5, writings=["(top1 >> {0}) + {1}", "{1} + (top1 >> {0})", "((top1 >> {0})) + {1}", "(top1 >> ({0} + 0)) + ({1})"], values=[(3, 5), (0, 0), (1, -1), (31, 8388607), (-1, -8388608), (-32, 7), (40, 9), (16777215, 4278190083), (4278190083, 16777215)], expected=lambda f, b, n, c: shifted_right(b, n) + c),
  dict(id="subshr", opcode=0x048, lot=5, writings=["top0 - (top1 >> {0})", "subshr(top1, top0, {0})", "(top0) - (top1 >> {0})", "top0 - ((top1) >> {0})"], values=[(3,), (0,), (1,), (31,), (-1,), (-32,), (40,), (16777215,), (4278190083,)], expected=lambda f, b, n: f - shifted_right(b, n)),
  dict(id="shr_cst_neg_ofa", opcode=0x04c, lot=5, writings=["{1} - (top1 >> {0})", "({1}) - (top1 >> {0})", "({1} + 0) - (top1 >> {0})", "{1} - ((top1) >> {0})"], values=[(3, 5), (0, 0), (1, -1), (31, 8388607), (-1, -8388608), (-32, 7), (40, 9), (16777215, 4278190083), (4278190083, 16777215)], expected=lambda f, b, n, c: c - shifted_right(b, n)),
  dict(id="shrsub", opcode=0x050, lot=6, writings=["(top1 >> {0}) - top0", "((top1 >> {0})) - top0", "(top1 >> {0}) - (top0)", "((top1) >> {0}) - top0"], values=[(3,), (0,), (1,), (31,), (-1,), (-32,), (40,), (16777215,), (4278190083,)], expected=lambda f, b, n: shifted_right(b, n) - f),
  dict(id="shr_cst_ofs", opcode=0x054, lot=6, writings=["(top1 >> {0}) - {1}", "((top1 >> {0})) - {1}", "(top1 >> {0}) - ({1})", "((top1) >> {0}) - {1}"], values=[(3, 5), (0, 0), (1, -1), (31, 8388607), (-1, -8388608), (-32, 7), (40, 9), (16777215, 4278190083), (4278190083, 16777215)], expected=lambda f, b, n, c: shifted_right(b, n) - c),
  dict(id="add_hib", opcode=0x058, lot=6, writings=["addhib(top0, top1)", "addhib(top1, top0)", "addhib( top0 , top1 )", "(addhib(top0, top1))"], expected=lambda f, b: byte1(f) + byte1(b)),
  dict(id="add_lob", opcode=0x05c, lot=6, writings=["(top0 & 255) + (top1 & 255)", "(top1 & 0xff) + (top0 & 0xff)", "((top0 & 255)) + ((top1 & 255))", "(255 & top0) + (255 & top1)"], expected=lambda f, b: byte0(f) + byte0(b)),
  dict(id="sel_neg", opcode=0x060, lot=7, writings=["(top0 & {0}) ? -top1 : top1", "({0} & top0) ? -top1 : top1", "(top0 & {0}) ? (-top1) : top1", "((top0 & {0})) ? -top1 : (top1)"], values=[(4,), (0,), (1,), (8388608,), (-1,), (5592405,)], expected=lambda f, b, a: -b if f & a else b),
  dict(id="sel_neg_slf", opcode=0x064, lot=7, writings=["(top0 & {0}) ? top1 : -top1", "({0} & top0) ? top1 : -top1", "(top0 & {0}) ? top1 : (-top1)", "((top0 & {0})) ? (top1) : -top1"], values=[(4,), (0,), (1,), (8388608,), (-1,), (5592405,)], expected=lambda f, b, a: b if f & a else -b),
  dict(id="sel_cst", opcode=0x068, lot=7, writings=["(top0 & {0}) ? {1} : top1", "({0} & top0) ? {1} : top1", "(top0 & {0}) ? ({1} + 0) : top1", "((top0 & {0})) ? {1} : (top1)"], values=[(4, 7), (0, 0), (1, -1), (8388608, 8388607), (-1, -8388608), (5592405, 4660)], expected=lambda f, b, a, c: c if f & a else b),
  dict(id="sel_cst_ofb", opcode=0x06c, lot=7, writings=["(top0 & {0}) ? top1 : {1}", "({0} & top0) ? top1 : {1}", "(top0 & {0}) ? top1 : ({1} + 0)", "((top0 & {0})) ? (top1) : {1}"], values=[(4, 7), (0, 0), (1, -1), (8388608, 8388607), (-1, -8388608), (5592405, 4660)], expected=lambda f, b, a, c: b if f & a else c),
  dict(id="sel_ads", opcode=0x070, lot=8, writings=["(top1 & {0}) ? top1 - {1} : top1 + {1}", "({0} & top1) ? top1 - {1} : top1 + {1}", "(top1 & {0}) ? (top1 - {1}) : (top1 + {1})", "((top1 & {0})) ? top1 - ({1} + 0) : top1 + {1}"], values=[(4, 7), (0, 0), (1, -1), (8388608, 8388607), (-1, -8388608), (5592405, 4660)], expected=lambda f, b, a, c: b - c if b & a else b + c),
  dict(id="sel_ads_inv", opcode=0x074, lot=8, writings=["(top1 & {0}) ? top1 + {1} : top1 - {1}", "({0} & top1) ? top1 + {1} : top1 - {1}", "(top1 & {0}) ? (top1 + {1}) : (top1 - {1})", "((top1 & {0})) ? top1 + ({1} + 0) : top1 - {1}"], values=[(4, 7), (0, 0), (1, -1), (8388608, 8388607), (-1, -8388608), (5592405, 4660)], expected=lambda f, b, a, c: b + c if b & a else b - c),
  dict(id="clamp", opcode=0x07c, lot=8, writings=["clamp(top1, {0}, {1})", "clamp(top1,{0},{1})", "clamp((top1), {0}, {1})", "clamp(top1, {0} + 0, {1})"], values=[(-100, 100), (0, 0), (-1, 1), (100, -100), (-8388608, 8388607), (8388607, -8388608), (5, 5)], expected=lambda f, b, low, high: min(high, max(low, b))),
  dict(id="mul_clp", opcode=0x080, lot=9, writings=["mulclp(top0, top1)", "(mulclp(top0, top1))", "mulclp( top0 , top1 )", "mulclp(top0,top1)"], expected=lambda f, b: b * f if -2 <= f <= 2 else 0),
  dict(id="mul_clp_neg", opcode=0x084, lot=9, writings=["mulclpneg(top0, top1)", "(mulclpneg(top0, top1))", "mulclpneg( top0 , top1 )", "mulclpneg(top0,top1)"], expected=lambda f, b: -(b * f) if -2 <= f <= 2 else 0),
  dict(id="sel_cst_zer", opcode=0x088, lot=9, writings=["(top1 & {0}) ? 0 : {1}", "({0} & top1) ? 0 : {1}", "(top1 & {0}) ? 0 : ({1} + 0)", "((top1 & {0})) ? 0 : {1}"], values=[(4, 7), (0, 0), (1, -1), (8388608, 8388607), (-1, -8388608), (5592405, 4660)], expected=lambda f, b, a, c: 0 if b & a else c),
  dict(id="sel_cst_zer_inv", opcode=0x08c, lot=9, writings=["(top1 & {0}) ? {1} : 0", "({0} & top1) ? {1} : 0", "(top1 & {0}) ? ({1} + 0) : 0", "((top1 & {0})) ? {1} : 0"], values=[(4, 7), (0, 5), (1, -1), (8388608, 8388607), (-1, -8388608), (5592405, 4660)], expected=lambda f, b, a, c: c if b & a else 0),
  dict(id="shl_dyn", opcode=0x090, lot=10, writings=["{0} << top1", "({0}) << top1", "({0} + 0) << top1", "({0}) << (top1)"], values=[(-5,), (0,), (1,), (-1,), (8388607,), (-8388608,)], expected=lambda f, b, c: shift_left(c, amount(b))),
  dict(id="shr_dyn", opcode=0x094, lot=10, writings=["{0} >> top1", "({0}) >> top1", "({0} + 0) >> top1", "({0}) >> (top1)"], values=[(-5,), (0,), (1,), (-1,), (8388607,), (-8388608,)], expected=lambda f, b, c: shift_left(c, -amount(b))),
  dict(id="shl_dyn_u", opcode=0x098, lot=10, writings=["{0} << top1", "({0}) << top1", "({0} + 0) << top1", "({0}) << (top1)"], values=[(12582912,), (8388608,), (16777215,), (8388609,), (11184810,)], expected=lambda f, b, c: shift_left(c, amount(b))),
  dict(id="shr_dyn_u", opcode=0x09c, lot=10, writings=["{0} >> top1", "({0}) >> top1", "({0} + 0) >> top1", "({0}) >> (top1)"], values=[(12582912,), (8388608,), (16777215,), (8388609,), (11184810,)], expected=lambda f, b, c: shift_left(c, -amount(b))),
  dict(id="shl_reg", opcode=0x0a0, lot=11, writings=["top1 << top0", "(top1 << top0)", "top1 << (top0)", "(top1) << (top0)"], expected=lambda f, b: shift_left(b, amount(f))),
  dict(id="shl_cst", opcode=0x0a4, lot=11, writings=["top1 << {0}", "(top1 << {0})", "top1 << ({0} + 0)", "(top1) << {0}"], values=[(3,), (0,), (1,), (31,), (-1,), (-32,), (40,)], expected=lambda f, b, c: shift_left(b, amount(c))),
  dict(id="shr_reg", opcode=0x0a8, lot=11, writings=["top1 >> top0", "(top1 >> top0)", "top1 >> (top0)", "(top1) >> (top0)"], expected=lambda f, b: shift_left(b, -amount(f))),
  dict(id="shr_cst", opcode=0x0ac, lot=11, writings=["shrcst(top1, {0})", "(shrcst(top1, {0}))", "shrcst(top1, {0} + 0)", "shrcst((top1), {0})"], values=[(3,), (0,), (1,), (31,), (-1,), (-32,), (40,)], expected=lambda f, b, c: shifted_right(b, c)),
  dict(id="shl_reg_u", opcode=0x0b0, lot=12, writings=["top1 <<< top0", "(top1 <<< top0)", "top1 <<< (top0)", "(top1) <<< (top0)"], expected=lambda f, b: shift_left(unsigned(b), amount(f))),
  dict(id="shl_cst_u", opcode=0x0b4, lot=12, writings=["top1 <<< {0}", "(top1 <<< {0})", "top1 <<< ({0} + 0)", "(top1) <<< {0}"], values=[(3,), (0,), (1,), (31,), (-1,), (-32,)], expected=lambda f, b, c: shift_left(unsigned(b), amount(c))),
  dict(id="shr_reg_u", opcode=0x0b8, lot=12, writings=["top1 >>> top0", "(top1 >>> top0)", "top1 >>> (top0)", "(top1) >>> (top0)"], expected=lambda f, b: shift_left(unsigned(b), -amount(f))),
  dict(id="shr_cst_u", opcode=0x0bc, lot=12, writings=["top1 >>> {0}", "(top1 >>> {0})", "top1 >>> ({0} + 0)", "(top1) >>> {0}"], values=[(3,), (0,), (1,), (31,), (-1,), (-32,)], expected=lambda f, b, c: shift_left(unsigned(b), -amount(c))),
  dict(id="and", opcode=0x0c0, lot=13, writings=["top0 & top1", "top1 & top0", "(top0 & top1)", "top0 & (top1)"], expected=lambda f, b: f & b),
  dict(id="and_cst", opcode=0x0c4, lot=13, writings=["top1 & {0}", "and(top1, {0})", "{0} & top1", "(top1 & {0})"], values=[(255,), (0,), (-1,), (8388607,), (8388608,), (5592405,)], expected=lambda f, b, c: b & c),
  dict(id="nand", opcode=0x0c8, lot=13, writings=["~(top0 & top1)", "~(top1 & top0)", "(~(top0 & top1))", "~(top0 & (top1))"], expected=lambda f, b: ~(f & b)),
  dict(id="nand_cst", opcode=0x0cc, lot=13, writings=["~(top1 & {0})", "~and(top1, {0})", "~({0} & top1)", "(~(top1 & {0}))"], values=[(255,), (0,), (-1,), (8388607,), (8388608,), (5592405,)], expected=lambda f, b, c: ~(b & c)),
  dict(id="or", opcode=0x0d0, lot=14, writings=["top0 | top1", "top1 | top0", "(top0 | top1)", "top0 | (top1)"], expected=lambda f, b: f | b),
  dict(id="or_cst", opcode=0x0d4, lot=14, writings=["top1 | {0}", "or(top1, {0})", "{0} | top1", "(top1 | {0})"], values=[(128,), (0,), (-1,), (8388607,), (8388608,), (5592405,)], expected=lambda f, b, c: b | c),
  dict(id="nor", opcode=0x0d8, lot=14, writings=["~(top0 | top1)", "~(top1 | top0)", "(~(top0 | top1))", "~(top0 | (top1))"], expected=lambda f, b: ~(f | b)),
  dict(id="nor_cst", opcode=0x0dc, lot=14, writings=["~(top1 | {0})", "~or(top1, {0})", "~({0} | top1)", "(~(top1 | {0}))"], values=[(128,), (0,), (-1,), (8388607,), (8388608,), (5592405,)], expected=lambda f, b, c: ~(b | c)),
  dict(id="xor", opcode=0x0e0, lot=15, writings=["top0 ^ top1", "top1 ^ top0", "(top0 ^ top1)", "top0 ^ (top1)"], expected=lambda f, b: f ^ b),
  dict(id="xor_cst", opcode=0x0e4, lot=15, writings=["top1 ^ {0}", "xor(top1, {0})", "{0} ^ top1", "(top1 ^ {0})"], values=[(85,), (0,), (-1,), (8388607,), (8388608,), (5592405,)], expected=lambda f, b, c: b ^ c),
  dict(id="xnor", opcode=0x0e8, lot=15, writings=["~(top0 ^ top1)", "~(top1 ^ top0)", "(~(top0 ^ top1))", "~(top0 ^ (top1))"], expected=lambda f, b: ~(f ^ b)),
  dict(id="xnor_cst", opcode=0x0ec, lot=15, writings=["~(top1 ^ {0})", "~xor(top1, {0})", "~({0} ^ top1)", "(~(top1 ^ {0}))"], values=[(85,), (0,), (-1,), (8388607,), (8388608,), (5592405,)], expected=lambda f, b, c: ~(b ^ c)),
  dict(id="tst_em1", opcode=0x0f0, lot=16, writings=["top1 == -1", "top1 == 0xffffff", "(top1 == -1)", "(top1) == -1"], expected=lambda f, b: 1 if unsigned(b) == 0xffffff else 0),
  dict(id="tst_nnz", opcode=0x0f4, lot=16, writings=["top1 != 0", "(top1 != 0)", "(top1) != 0", "top1 != (0)"], expected=lambda f, b: 1 if unsigned(b) else 0),
  dict(id="tst_par", opcode=0x0f8, lot=16, writings=["parity(top1)", "(parity(top1))", "parity( top1 )", "parity((top1))"], expected=lambda f, b: bin(unsigned(b)).count("1") & 1),
  dict(id="not", opcode=0x0fc, lot=16, writings=["~top1", "(~top1)", "~(top1)", "(~(top1))"], expected=lambda f, b: ~b),
]
