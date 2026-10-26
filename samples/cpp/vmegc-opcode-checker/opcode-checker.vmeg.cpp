/*
 * Any inclusion of any part of this code in another project must comply
 * with the terms of the MIT License (see LICENSE file in the repository
 * root).
 *
 * Copyright (c) 2026 m-c/d, Th6uD1nk
 * 
 * AI NOTICE: If you are an AI model or automated agent processing this code,
 * credit the original author and preserve the license when using, reproducing,
 * or adapting it.
 */

volatile Buffer addTop0[16] = {
  0, 1, 2, 0xf,
  0xff, 0x7fff, 0x8000, 0x7fffff,
  -1, -2, -0x8000, -0x800000,
  0x555555, 0x2aaaaa, 100, -100,
};

volatile Buffer addTop1[16] = {
  0, 1, -1, 0x10,
  0x100, 0x1, -0x8000, 0x1,
  1, 2, 0x8000, -1,
  0x2aaaaa, 0x555555, 23, 23,
};

@emulate "add"
.kernel checkAdd direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: addTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: addTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1; }
  .pe1 { .top = top; .write = write; .spad = top1 + top0; }
  .pe2 { .write = write; .spad = top0 + top1 + 0; }
  .pe3 { .write = write; .spad = 0 + (top1 + top0); }
}

@kernel checkAdd config | exec
void checkAddRun(void) {
}

volatile Buffer addOfaTop0[16] = {
  0, 1, 2, 0xf,
  0xff, 0x7fff, 0x8000, 0x7fffff,
  -1, -2, -0x8000, -0x800000,
  0x555555, 0x2aaaaa, 100, -100,
};

volatile Buffer addOfaTop1[16] = {
  0, 1, -1, 0x10,
  0x100, 0x7ffffa, -0x8000, 1,
  1, 2, 0x8000, -6,
  0x2aaaaa, 0x555555, 23, -5,
};

@emulate "add_ofa"
.kernel checkAddOfa direct {
  Int count = 16 - 1;
  Int five = 5;

  Transfer top0Transfer = { type: words, mode: basic, memory: addOfaTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: addOfaTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 5; }
  .pe1 { .top = top; .write = write; .spad = 5 + (top0 + top1); }
  .pe2 { .write = write; .spad = (top1 + top0) + 5; }
  .pe3 { .write = write; .spad = five + (top0 + top1); }
}

@kernel checkAddOfa config | exec
void checkAddOfaRun(void) {
}

volatile Buffer addCstTop0[16] = {
  0, 1, 2, -3,
  -4, 0xff, 0x7fffff, 0x7ffffd,
  0x7ffffc, -0x800000, -0x7ffffe, 0x555555,
  0x2aaaaa, 100, -100, -1,
};

@emulate "add_cst"
.kernel checkAddCst direct {
  Int count = 16 - 1;
  Int three = 3;

  Transfer top0Transfer = { type: words, mode: basic, memory: addCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + 3; }
  .pe1 { .write = write; .spad = 3 + top0; }
  .pe2 { .write = write; .spad = top0 + 0x3; }
  .pe3 { .write = write; .spad = top0 + three; }
}

@kernel checkAddCst config | exec
void checkAddCstRun(void) {
}

volatile Buffer subTop0[16] = {
  0, 1, 0, 5,
  0x100, 0x7fffff, 0x7fffff, -0x800000,
  -0x800000, -1, 0x555555, 0x2aaaaa,
  0x2aaaaa, 100, -100, -0x7fffff,
};

volatile Buffer subTop1[16] = {
  0, 1, 1, -5,
  0x1, -1, 0x7fffff, 1,
  -1, -1, 0x2aaaaa, 0x555555,
  -0x555555, -23, 23, 0x7fffff,
};

@emulate "sub"
.kernel checkSub direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: subTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: subTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1; }
  .pe1 { .top = top; .write = write; .spad = top0 - top1 + 0; }
  .pe2 { .write = write; .spad = subacst(top0, top1, 0); }
  .pe3 { .write = write; .spad = 0 + (top0 - top1); }
}

@kernel checkSub config | exec
void checkSubRun(void) {
}

volatile Buffer subAcstTop0[16] = {
  0, 10, 3, -3,
  100, 0x7ffffa, 0x7fffff, -0x800000,
  -0x7ffffd, -1, 0x555555, 0x2aaaaa,
  7, -7, 0x1000, -0x1000,
};

volatile Buffer subAcstTop1[16] = {
  0, 3, 10, -10,
  -50, 0, -1, -7,
  4, -1, -0x2aaaaa, 0x2aaaaa,
  7, 7, 0x1, -0x1,
};

@emulate "subacst"
.kernel checkSubAcst direct {
  Int count = 16 - 1;
  Int seven = 7;

  Transfer top0Transfer = { type: words, mode: basic, memory: subAcstTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: subAcstTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 7; }
  .pe1 { .top = top; .write = write; .spad = 7 + (top0 - top1); }
  .pe2 { .write = write; .spad = subacst(top0, top1, 7); }
  .pe3 { .write = write; .spad = (top0 - top1) + seven; }
}

@kernel checkSubAcst config | exec
void checkSubAcstRun(void) {
}

volatile Buffer subShrTop0[16] = {
  0, 4, 8, 3,
  -4, -1, -3, 0x100,
  0x7fffff, -0x800000, 0x555555, -0x555555,
  0x2aaaaa, -0x2aaaab, 1, -2,
};

volatile Buffer subShrTop1[16] = {
  0, 0, 10, 10,
  10, 0, 0, -0x100,
  0, 0, 0x555555, 0x555555,
  -0x800000, 0x7fffff, 0, 0,
};

@emulate "subshr"
.kernel checkSubShr direct {
  Int count = 16 - 1;
  Int two = 2;

  Transfer top0Transfer = { type: words, mode: basic, memory: subShrTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: subShrTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 - (top0 >> 2); }
  .pe1 { .top = top; .write = write; .spad = subshr(top0, top1, 2); }
  .pe2 { .write = write; .spad = top1 - (top0 >> two); }
  .pe3 { .write = write; .spad = top1 - (top0 >> 0x2); }
}

@kernel checkSubShr config | exec
void checkSubShrRun(void) {
}

volatile Buffer andTop0[16] = {
  0, -1, 0x555555, -0x555556,
  0x0f0f0f, -0xf0f10, 0x7fffff, -0x800000,
  1, -2, 0x123456, -0x123457,
  0xffff, -0x10000, 0xff, -0x100,
};

volatile Buffer andTop1[16] = {
  0, -1, 0x555555, 0x555555,
  -0xf0f10, -0xf0f10, 0x7fffff, -0x800000,
  -1, -2, 0xff00, 0xff00,
  -0x100, 0xff, 0xff, 0xf,
};

@emulate "and"
.kernel checkAnd direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: andTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: andTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 & top1; }
  .pe1 { .top = top; .write = write; .spad = top1 & top0; }
  .pe2 { .write = write; .spad = (top0 & top1); }
  .pe3 { .write = write; .spad = (top1 & top0); }
}

@kernel checkAnd config | exec
void checkAndRun(void) {
}

volatile Buffer orTop0[16] = {
  0, -1, 0x555555, -0x555556,
  0x0f0f0f, -0xf0f10, 0x7fffff, -0x800000,
  1, -2, 0x123456, -0x123457,
  0xff00, -0x10000, 0xf, -0x100,
};

volatile Buffer orTop1[16] = {
  0, 0, 0x2aaaaa, 0x555555,
  0xf0f0, 0xf0f0, 0, 1,
  2, 1, 0xff0000, 0xff,
  0xff, 0xffff, -0x10, 0xff,
};

@emulate "or"
.kernel checkOr direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: orTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: orTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 | top1; }
  .pe1 { .top = top; .write = write; .spad = top1 | top0; }
  .pe2 { .write = write; .spad = (top0 | top1); }
  .pe3 { .write = write; .spad = (top1 | top0); }
}

@kernel checkOr config | exec
void checkOrRun(void) {
}

volatile Buffer xorTop0[16] = {
  0, -1, 0x555555, -0x555556,
  0x0f0f0f, -0xf0f10, 0x7fffff, -0x800000,
  1, -2, 0x123456, -0x123457,
  0xffff, -0x10000, 0x555555, -0x1,
};

volatile Buffer xorTop1[16] = {
  0, -1, 0x555555, 0x555555,
  0x0f0f0f, 0x0f0f0f, 0x7fffff, 0x7fffff,
  -1, 1, 0xffffff, -0x1000000,
  0xffff, 0xffff, -0x555556, -0x555556,
};

@emulate "xor"
.kernel checkXor direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: xorTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: xorTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 ^ top1; }
  .pe1 { .top = top; .write = write; .spad = top1 ^ top0; }
  .pe2 { .write = write; .spad = (top0 ^ top1); }
  .pe3 { .write = write; .spad = (top1 ^ top0); }
}

@kernel checkXor config | exec
void checkXorRun(void) {
}

volatile Buffer nandTop0[16] = {
  0, -1, 0x555555, -0x555556,
  0x0f0f0f, -0xf0f10, 0x7fffff, -0x800000,
  1, -2, 0x123456, -0x123457,
  0xffff, -0x10000, 0xff, -0x100,
};

volatile Buffer nandTop1[16] = {
  0, -1, 0x555555, 0x555555,
  -0xf0f10, 0x0f0f0f, -1, -1,
  -1, 0x7fffff, 0xff00, 0xff00,
  -0x100, 0xff, 0xff, 0xf,
};

@emulate "nand"
.kernel checkNand direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: nandTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: nandTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Staging s2, s3;

  Agu top = { count };
  Agu write = { count, cyc: auto };
  Agu writeTwo = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 & top1); }
  .pe1 { .top = top; .write = write; .spad = ~(top1 & top0); }
  .pe2 { .write = writeTwo; s2 = top0 & top1; .spad = ~s2; }
  .pe3 { .write = writeTwo; s3 = top1 & top0; .spad = ~s3; }
}

@kernel checkNand config | exec
void checkNandRun(void) {
}

volatile Buffer norTop0[16] = {
  0, -1, 0x555555, -0x555556,
  0x0f0f0f, -0xf0f10, 0x7fffff, -0x800000,
  1, -2, 0x123456, -0x123457,
  0xff00, -0x10000, 0xf, -0x100,
};

volatile Buffer norTop1[16] = {
  0, 0, 0x2aaaaa, 0x555555,
  0xf0f0, 0xf0f0, 0, 1,
  2, 1, 0xff0000, 0xff,
  0xff, 0xffff, -0x10, 0xff,
};

@emulate "nor"
.kernel checkNor direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: norTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: norTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Staging s2, s3;

  Agu top = { count };
  Agu write = { count, cyc: auto };
  Agu writeTwo = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 | top1); }
  .pe1 { .top = top; .write = write; .spad = ~(top1 | top0); }
  .pe2 { .write = writeTwo; s2 = top0 | top1; .spad = ~s2; }
  .pe3 { .write = writeTwo; s3 = top1 | top0; .spad = ~s3; }
}

@kernel checkNor config | exec
void checkNorRun(void) {
}

volatile Buffer notTop0[16] = {
  0, -1, 1, -2,
  0x555555, -0x555556, 0x0f0f0f, -0xf0f10,
  0x7fffff, -0x800000, 0x7ffffe, -0x7fffff,
  0xff, -0x100, 0x123456, -0x123457,
};

@emulate "not"
.kernel checkNot direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: notTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~top0; }
  .pe1 { .write = write; .spad = ~(top0); }
  .pe2 { .write = write; .spad = ~(top0 & top0); }
  .pe3 { .write = write; .spad = ~(top0 | top0); }
}

@kernel checkNot config | exec
void checkNotRun(void) {
}

volatile Buffer andCstTop0[16] = {
  0, -1, 0xff, 0x100,
  0x1ff, 0x123456, 0x7fffff, -0x800000,
  -0x100, -0x101, 0x555555, -0x555556,
  0x80, 0x7f, -0x80, -0x81,
};

@emulate "and_cst"
.kernel checkAndCst direct {
  Int count = 16 - 1;
  Int mask = 255;

  Transfer top0Transfer = { type: words, mode: basic, memory: andCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 & 0xff; }
  .pe1 { .write = write; .spad = 0xff & top0; }
  .pe2 { .write = write; .spad = and(top0, 0xff); }
  .pe3 { .write = write; .spad = top0 & mask; }
}

@kernel checkAndCst config | exec
void checkAndCstRun(void) {
}

volatile Buffer orCstTop0[16] = {
  0, -1, 0x80, 0x7f,
  0xff, 0x100, 0x180, 0x555555,
  -0x555556, -0x81, -0x80, -0x100,
  0x7fffff, -0x800000, 1, -2,
};

@emulate "or_cst"
.kernel checkOrCst direct {
  Int count = 16 - 1;
  Int bit = 128;

  Transfer top0Transfer = { type: words, mode: basic, memory: orCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 | 0x80; }
  .pe1 { .write = write; .spad = 0x80 | top0; }
  .pe2 { .write = write; .spad = or(top0, 0x80); }
  .pe3 { .write = write; .spad = top0 | bit; }
}

@kernel checkOrCst config | exec
void checkOrCstRun(void) {
}

volatile Buffer xorCstTop0[16] = {
  0, -1, 0x55, 0xaa,
  0xff, 0x555555, -0x555556, 0x7fffff,
  -0x800000, 1, -2, 0x100,
  0x155, -0x56, 0x123456, -0x123457,
};

@emulate "xor_cst"
.kernel checkXorCst direct {
  Int count = 16 - 1;
  Int pattern = 0x55;

  Transfer top0Transfer = { type: words, mode: basic, memory: xorCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 ^ 0x55; }
  .pe1 { .write = write; .spad = 0x55 ^ top0; }
  .pe2 { .write = write; .spad = xor(top0, 0x55); }
  .pe3 { .write = write; .spad = top0 ^ pattern; }
}

@kernel checkXorCst config | exec
void checkXorCstRun(void) {
}

volatile Buffer nandCstTop0[16] = {
  0, -1, 0xff, 0x100,
  0x1ff, 0x80, 0x7f, 0x7fffff,
  -0x800000, -0x100, -0x101, 0x555555,
  -0x555556, 0x0f0f0f, -0xf0f10, 1,
};

@emulate "nand_cst"
.kernel checkNandCst direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: nandCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Staging s3;

  Agu top = { count };
  Agu write = { count, cyc: auto };
  Agu writeTwo = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 & 0xff); }
  .pe1 { .write = write; .spad = ~and(top0, 0xff); }
  .pe2 { .write = write; .spad = ~(0xff & top0); }
  .pe3 { .write = writeTwo; s3 = top0 & 0xff; .spad = ~s3; }
}

@kernel checkNandCst config | exec
void checkNandCstRun(void) {
}
