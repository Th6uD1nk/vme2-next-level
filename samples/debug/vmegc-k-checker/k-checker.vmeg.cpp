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
  0xffffffff, 0xfffffffe, 0xffff8000, 0xff800000,
  0x555555, 0x2aaaaa, 100, 0xffffff9c,
};

volatile Buffer addTop1[16] = {
  0, 1, 0xffffffff, 0x10,
  0x100, 0x1, 0xffff8000, 0x1,
  1, 2, 0x8000, 0xffffffff,
  0x2aaaaa, 0x555555, 23, 23,
};

@emulate "add"
.kernel checkAdd direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: addTop0, count };
  Transfer top1Transfer = { memory: addTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 + top1) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) >> 24; }
  .pe2 { .write = write; .spad = (top0 + top1) >> 32; }
  .pe3 { .write = write; .spad = (top0 + top1) >> 56; }
}

@kernel checkAdd config | exec
void checkAddRun(void) {
}

volatile Buffer addOfaTop0[16] = {
  0, 1, 2, 0xf,
  0xff, 0x7fff, 0x8000, 0x7fffff,
  0xffffffff, 0xfffffffe, 0xffff8000, 0xff800000,
  0x555555, 0x2aaaaa, 100, 0xffffff9c,
};

volatile Buffer addOfaTop1[16] = {
  0, 1, 0xffffffff, 0x10,
  0x100, 0x7ffffa, 0xffff8000, 1,
  1, 2, 0x8000, 0xfffffffa,
  0x2aaaaa, 0x555555, 23, 0xfffffffb,
};

@emulate "add_ofa"
.kernel checkAddOfa direct {
  Int count = 16 - 1;
  Int five = 5;

  Transfer top0Transfer = { memory: addOfaTop0, count };
  Transfer top1Transfer = { memory: addOfaTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 + top1 + 5) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1 + 5) >> 24; }
  .pe2 { .write = write; .spad = (top0 + top1 + 5) >> 32; }
  .pe3 { .write = write; .spad = (top0 + top1 + 5) >> 56; }
}

@kernel checkAddOfa config | exec
void checkAddOfaRun(void) {
}

volatile Buffer addCstTop0[16] = {
  0, 1, 2, 0xfffffffd,
  0xfffffffc, 0xff, 0x7fffff, 0x7ffffd,
  0x7ffffc, 0xff800000, 0xff800002, 0x555555,
  0x2aaaaa, 100, 0xffffff9c, 0xffffffff,
};

@emulate "add_cst"
.kernel checkAddCst direct {
  Int count = 16 - 1;
  Int three = 3;

  Transfer top0Transfer = { memory: addCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 + 3) >> 1; }
  .pe1 { .write = write; .spad = (top0 + 3) >> 24; }
  .pe2 { .write = write; .spad = (top0 + 3) >> 32; }
  .pe3 { .write = write; .spad = (top0 + 3) >> 56; }
}

@kernel checkAddCst config | exec
void checkAddCstRun(void) {
}

volatile Buffer subTop0[16] = {
  0, 1, 0, 5,
  0x100, 0x7fffff, 0x7fffff, 0xff800000,
  0xff800000, 0xffffffff, 0x555555, 0x2aaaaa,
  0x2aaaaa, 100, 0xffffff9c, 0xff800001,
};

volatile Buffer subTop1[16] = {
  0, 1, 1, 0xfffffffb,
  0x1, 0xffffffff, 0x7fffff, 1,
  0xffffffff, 0xffffffff, 0x2aaaaa, 0x555555,
  0xffaaaaab, 0xffffffe9, 23, 0x7fffff,
};

@emulate "sub"
.kernel checkSub direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: subTop0, count };
  Transfer top1Transfer = { memory: subTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 - top1) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (top0 - top1) >> 24; }
  .pe2 { .write = write; .spad = (top0 - top1) >> 32; }
  .pe3 { .write = write; .spad = (top0 - top1) >> 56; }
}

@kernel checkSub config | exec
void checkSubRun(void) {
}

volatile Buffer subAcstTop0[16] = {
  0, 10, 3, 0xfffffffd,
  100, 0x7ffffa, 0x7fffff, 0xff800000,
  0xff800003, 0xffffffff, 0x555555, 0x2aaaaa,
  7, 0xfffffff9, 0x1000, 0xfffff000,
};

volatile Buffer subAcstTop1[16] = {
  0, 3, 10, 0xfffffff6,
  0xffffffce, 0, 0xffffffff, 0xfffffff9,
  4, 0xffffffff, 0xffd55556, 0x2aaaaa,
  7, 7, 0x1, 0xffffffff,
};

@emulate "subacst"
.kernel checkSubAcst direct {
  Int count = 16 - 1;
  Int seven = 7;

  Transfer top0Transfer = { memory: subAcstTop0, count };
  Transfer top1Transfer = { memory: subAcstTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 - top1 + 7) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (top0 - top1 + 7) >> 24; }
  .pe2 { .write = write; .spad = (top0 - top1 + 7) >> 32; }
  .pe3 { .write = write; .spad = (top0 - top1 + 7) >> 56; }
}

@kernel checkSubAcst config | exec
void checkSubAcstRun(void) {
}

volatile Buffer subShrTop0[16] = {
  0, 4, 8, 3,
  0xfffffffc, 0xffffffff, 0xfffffffd, 0x100,
  0x7fffff, 0xff800000, 0x555555, 0xffaaaaab,
  0x2aaaaa, 0xffd55555, 1, 0xfffffffe,
};

volatile Buffer subShrTop1[16] = {
  0, 0, 10, 10,
  10, 0, 0, 0xffffff00,
  0, 0, 0x555555, 0x555555,
  0xff800000, 0x7fffff, 0, 0,
};

@emulate "subshr"
.kernel checkSubShr direct {
  Int count = 16 - 1;
  Int two = 2;

  Transfer top0Transfer = { memory: subShrTop0, count };
  Transfer top1Transfer = { memory: subShrTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 - (top0 >> 2)) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (top1 - (top0 >> 2)) >> 24; }
  .pe2 { .write = write; .spad = (top1 - (top0 >> 2)) >> 32; }
  .pe3 { .write = write; .spad = (top1 - (top0 >> 2)) >> 56; }
}

@kernel checkSubShr config | exec
void checkSubShrRun(void) {
}

volatile Buffer andTop0[16] = {
  0, 0xffffffff, 0x555555, 0xffaaaaaa,
  0x0f0f0f, 0xfff0f0f0, 0x7fffff, 0xff800000,
  1, 0xfffffffe, 0x123456, 0xffedcba9,
  0xffff, 0xffff0000, 0xff, 0xffffff00,
};

volatile Buffer andTop1[16] = {
  0, 0xffffffff, 0x555555, 0x555555,
  0xfff0f0f0, 0xfff0f0f0, 0x7fffff, 0xff800000,
  0xffffffff, 0xfffffffe, 0xff00, 0xff00,
  0xffffff00, 0xff, 0xff, 0xf,
};

@emulate "and"
.kernel checkAnd direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: andTop0, count };
  Transfer top1Transfer = { memory: andTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & top1) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (top0 & top1) >> 24; }
  .pe2 { .write = write; .spad = (top0 & top1) >> 32; }
  .pe3 { .write = write; .spad = (top0 & top1) >> 56; }
}

@kernel checkAnd config | exec
void checkAndRun(void) {
}

volatile Buffer orTop0[16] = {
  0, 0xffffffff, 0x555555, 0xffaaaaaa,
  0x0f0f0f, 0xfff0f0f0, 0x7fffff, 0xff800000,
  1, 0xfffffffe, 0x123456, 0xffedcba9,
  0xff00, 0xffff0000, 0xf, 0xffffff00,
};

volatile Buffer orTop1[16] = {
  0, 0, 0x2aaaaa, 0x555555,
  0xf0f0, 0xf0f0, 0, 1,
  2, 1, 0xff0000, 0xff,
  0xff, 0xffff, 0xfffffff0, 0xff,
};

@emulate "or"
.kernel checkOr direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: orTop0, count };
  Transfer top1Transfer = { memory: orTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 | top1) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (top0 | top1) >> 24; }
  .pe2 { .write = write; .spad = (top0 | top1) >> 32; }
  .pe3 { .write = write; .spad = (top0 | top1) >> 56; }
}

@kernel checkOr config | exec
void checkOrRun(void) {
}

volatile Buffer xorTop0[16] = {
  0, 0xffffffff, 0x555555, 0xffaaaaaa,
  0x0f0f0f, 0xfff0f0f0, 0x7fffff, 0xff800000,
  1, 0xfffffffe, 0x123456, 0xffedcba9,
  0xffff, 0xffff0000, 0x555555, 0xffffffff,
};

volatile Buffer xorTop1[16] = {
  0, 0xffffffff, 0x555555, 0x555555,
  0x0f0f0f, 0x0f0f0f, 0x7fffff, 0x7fffff,
  0xffffffff, 1, 0xffffff, 0xff000000,
  0xffff, 0xffff, 0xffaaaaaa, 0xffaaaaaa,
};

@emulate "xor"
.kernel checkXor direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: xorTop0, count };
  Transfer top1Transfer = { memory: xorTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 ^ top1) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (top0 ^ top1) >> 24; }
  .pe2 { .write = write; .spad = (top0 ^ top1) >> 32; }
  .pe3 { .write = write; .spad = (top0 ^ top1) >> 56; }
}

@kernel checkXor config | exec
void checkXorRun(void) {
}

volatile Buffer nandTop0[16] = {
  0, 0xffffffff, 0x555555, 0xffaaaaaa,
  0x0f0f0f, 0xfff0f0f0, 0x7fffff, 0xff800000,
  1, 0xfffffffe, 0x123456, 0xffedcba9,
  0xffff, 0xffff0000, 0xff, 0xffffff00,
};

volatile Buffer nandTop1[16] = {
  0, 0xffffffff, 0x555555, 0x555555,
  0xfff0f0f0, 0x0f0f0f, 0xffffffff, 0xffffffff,
  0xffffffff, 0x7fffff, 0xff00, 0xff00,
  0xffffff00, 0xff, 0xff, 0xf,
};

@emulate "nand"
.kernel checkNand direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: nandTop0, count };
  Transfer top1Transfer = { memory: nandTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Staging s2, s3;

  Agu top = { count };
  Agu write = { count, cyc: auto };
  Agu writeTwo = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (~(top0 & top1)) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (~(top0 & top1)) >> 24; }
  .pe2 { .write = writeTwo; s2 = top0 & top1; .spad = (~(top0 & top1)) >> 32; }
  .pe3 { .write = writeTwo; s3 = top1 & top0; .spad = (~(top0 & top1)) >> 56; }
}

@kernel checkNand config | exec
void checkNandRun(void) {
}

volatile Buffer norTop0[16] = {
  0, 0xffffffff, 0x555555, 0xffaaaaaa,
  0x0f0f0f, 0xfff0f0f0, 0x7fffff, 0xff800000,
  1, 0xfffffffe, 0x123456, 0xffedcba9,
  0xff00, 0xffff0000, 0xf, 0xffffff00,
};

volatile Buffer norTop1[16] = {
  0, 0, 0x2aaaaa, 0x555555,
  0xf0f0, 0xf0f0, 0, 1,
  2, 1, 0xff0000, 0xff,
  0xff, 0xffff, 0xfffffff0, 0xff,
};

@emulate "nor"
.kernel checkNor direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: norTop0, count };
  Transfer top1Transfer = { memory: norTop1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Staging s2, s3;

  Agu top = { count };
  Agu write = { count, cyc: auto };
  Agu writeTwo = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (~(top0 | top1)) >> 1; }
  .pe1 { .top = top; .write = write; .spad = (~(top0 | top1)) >> 24; }
  .pe2 { .write = writeTwo; s2 = top0 | top1; .spad = (~(top0 | top1)) >> 32; }
  .pe3 { .write = writeTwo; s3 = top1 | top0; .spad = (~(top0 | top1)) >> 56; }
}

@kernel checkNor config | exec
void checkNorRun(void) {
}

volatile Buffer notTop0[16] = {
  0, 0xffffffff, 1, 0xfffffffe,
  0x555555, 0xffaaaaaa, 0x0f0f0f, 0xfff0f0f0,
  0x7fffff, 0xff800000, 0x7ffffe, 0xff800001,
  0xff, 0xffffff00, 0x123456, 0xffedcba9,
};

@emulate "not"
.kernel checkNot direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: notTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (~top0) >> 1; }
  .pe1 { .write = write; .spad = (~top0) >> 24; }
  .pe2 { .write = write; .spad = (~top0) >> 32; }
  .pe3 { .write = write; .spad = (~top0) >> 56; }
}

@kernel checkNot config | exec
void checkNotRun(void) {
}

volatile Buffer andCstTop0[16] = {
  0, 0xffffffff, 0xff, 0x100,
  0x1ff, 0x123456, 0x7fffff, 0xff800000,
  0xffffff00, 0xfffffeff, 0x555555, 0xffaaaaaa,
  0x80, 0x7f, 0xffffff80, 0xffffff7f,
};

@emulate "and_cst"
.kernel checkAndCst direct {
  Int count = 16 - 1;
  Int mask = 255;

  Transfer top0Transfer = { memory: andCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0xff) >> 1; }
  .pe1 { .write = write; .spad = (top0 & 0xff) >> 24; }
  .pe2 { .write = write; .spad = (top0 & 0xff) >> 32; }
  .pe3 { .write = write; .spad = (top0 & 0xff) >> 56; }
}

@kernel checkAndCst config | exec
void checkAndCstRun(void) {
}

volatile Buffer orCstTop0[16] = {
  0, 0xffffffff, 0x80, 0x7f,
  0xff, 0x100, 0x180, 0x555555,
  0xffaaaaaa, 0xffffff7f, 0xffffff80, 0xffffff00,
  0x7fffff, 0xff800000, 1, 0xfffffffe,
};

@emulate "or_cst"
.kernel checkOrCst direct {
  Int count = 16 - 1;
  Int bit = 128;

  Transfer top0Transfer = { memory: orCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 | 0x80) >> 1; }
  .pe1 { .write = write; .spad = (top0 | 0x80) >> 24; }
  .pe2 { .write = write; .spad = (top0 | 0x80) >> 32; }
  .pe3 { .write = write; .spad = (top0 | 0x80) >> 56; }
}

@kernel checkOrCst config | exec
void checkOrCstRun(void) {
}

volatile Buffer xorCstTop0[16] = {
  0, 0xffffffff, 0x55, 0xaa,
  0xff, 0x555555, 0xffaaaaaa, 0x7fffff,
  0xff800000, 1, 0xfffffffe, 0x100,
  0x155, 0xffffffaa, 0x123456, 0xffedcba9,
};

@emulate "xor_cst"
.kernel checkXorCst direct {
  Int count = 16 - 1;
  Int pattern = 0x55;

  Transfer top0Transfer = { memory: xorCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 ^ 0x55) >> 1; }
  .pe1 { .write = write; .spad = (top0 ^ 0x55) >> 24; }
  .pe2 { .write = write; .spad = (top0 ^ 0x55) >> 32; }
  .pe3 { .write = write; .spad = (top0 ^ 0x55) >> 56; }
}

@kernel checkXorCst config | exec
void checkXorCstRun(void) {
}

volatile Buffer nandCstTop0[16] = {
  0, 0xffffffff, 0xff, 0x100,
  0x1ff, 0x80, 0x7f, 0x7fffff,
  0xff800000, 0xffffff00, 0xfffffeff, 0x555555,
  0xffaaaaaa, 0x0f0f0f, 0xfff0f0f0, 1,
};

@emulate "nand_cst"
.kernel checkNandCst direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: nandCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Staging s3;

  Agu top = { count };
  Agu write = { count, cyc: auto };
  Agu writeTwo = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (~(top0 & 0xff)) >> 1; }
  .pe1 { .write = write; .spad = (~(top0 & 0xff)) >> 24; }
  .pe2 { .write = write; .spad = (~(top0 & 0xff)) >> 32; }
  .pe3 { .write = writeTwo; s3 = top0 & 0xff; .spad = (~(top0 & 0xff)) >> 56; }
}

@kernel checkNandCst config | exec
void checkNandCstRun(void) {
}

volatile Buffer norCstTop0[16] = {
  0, 0xffffffff, 0xf, 0x10,
  0xf0, 0xff, 0x100, 0x1f,
  0x7fffff, 0xff800000, 0xfffffff0, 0xffffffef,
  0x555555, 0xffaaaaaa, 0x123450, 0xffedcbaf,
};

@emulate "nor_cst"
.kernel checkNorCst direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: norCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Staging s3;

  Agu top = { count };
  Agu write = { count, cyc: auto };
  Agu writeTwo = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (~(top0 | 0x0f)) >> 1; }
  .pe1 { .write = write; .spad = (~(top0 | 0x0f)) >> 24; }
  .pe2 { .write = write; .spad = (~(top0 | 0x0f)) >> 32; }
  .pe3 { .write = writeTwo; s3 = top0 | 0x0f; .spad = (~(top0 | 0x0f)) >> 56; }
}

@kernel checkNorCst config | exec
void checkNorCstRun(void) {
}

volatile Buffer xnorCstTop0[16] = {
  0, 0xffffffff, 0x55, 0xaa,
  0xff, 0x100, 0x155, 0x555555,
  0xffaaaaaa, 0x7fffff, 0xff800000, 1,
  0xfffffffe, 0xffffffaa, 0x123456, 0xffedcba9,
};

@emulate "xnor_cst"
.kernel checkXnorCst direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: xnorCstTop0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }

  Staging s3;

  Agu top = { count };
  Agu write = { count, cyc: auto };
  Agu writeTwo = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (~(top0 ^ 0x55)) >> 1; }
  .pe1 { .write = write; .spad = (~(top0 ^ 0x55)) >> 24; }
  .pe2 { .write = write; .spad = (~(top0 ^ 0x55)) >> 32; }
  .pe3 { .write = writeTwo; s3 = top0 ^ 0x55; .spad = (~(top0 ^ 0x55)) >> 56; }
}

@kernel checkXnorCst config | exec
void checkXnorCstRun(void) {
}

