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

