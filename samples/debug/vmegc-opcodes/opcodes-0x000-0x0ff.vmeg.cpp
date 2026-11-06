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

volatile Buffer in0[16] = {
  0x1, 0x2, 0x3, 0x4,
  0x100, 0x10000, 0x7fffff, 0xffffffff,
  0xfffffffe, 0xff800000, 0x1234, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x5,
};

volatile Buffer in1[16] = {
  0x0, 0x1, 0x1, 0x2,
  0x80, 0x100, 0x7ffffe, 0x1,
  0xffffffff, 0x1, 0x234, 0x2aaaaa,
  0x555555, 0x5, 0x100, 0xfffffffb,
};

@emulate "pass"
.kernel checkPass direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1; }
  .pe1 { .top = top; .write = write; .spad = (top1); }
  .pe2 { .write = write; .spad = pass(top1); }
  .pe3 { .write = write; .spad = sat(top1, 31); }
}

@kernel checkPass config | exec
void checkPassRun(void) {
}

@emulate "cst"
.kernel checkCst direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 5; }
  .pe1 { .top = top; .write = write; .spad = cst(5); }
  .pe2 { .write = write; .spad = 10 - 5; }
  .pe3 { .write = write; .spad = (1 << 2) | 1; }
}

@kernel checkCst config | exec
void checkCstRun(void) {
}

@emulate "add"
.kernel checkAdd direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1; }
  .pe1 { .top = top; .write = write; .spad = top1 + top0; }
  .pe2 { .write = write; .spad = (top0 + top1); }
  .pe3 { .write = write; .spad = top0 + (top1); }
}

@kernel checkAdd config | exec
void checkAddRun(void) {
}

@emulate "bak_shr"
.kernel checkBakShr direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >> 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 3); }
  .pe2 { .write = write; .spad = top1 >> (1 + 2); }
  .pe3 { .write = write; .spad = (top1) >> 3; }
}

@kernel checkBakShr config | exec
void checkBakShrRun(void) {
}

@emulate "sub"
.kernel checkSub direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1; }
  .pe1 { .top = top; .write = write; .spad = (top0 - top1); }
  .pe2 { .write = write; .spad = top0 - (top1); }
  .pe3 { .write = write; .spad = (top0) - (top1); }
}

@kernel checkSub config | exec
void checkSubRun(void) {
}

@emulate "add_cst"
.kernel checkAddCst direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 3; }
  .pe1 { .top = top; .write = write; .spad = 3 + top1; }
  .pe2 { .write = write; .spad = (top1) + 3; }
  .pe3 { .write = write; .spad = (top1 + 3); }
}

@kernel checkAddCst config | exec
void checkAddCstRun(void) {
}

@emulate "neg_ofb"
.kernel checkNegOfb direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 7 - top1; }
  .pe1 { .top = top; .write = write; .spad = (7 - top1); }
  .pe2 { .write = write; .spad = 7 - (top1); }
  .pe3 { .write = write; .spad = (7) - top1; }
}

@kernel checkNegOfb config | exec
void checkNegOfbRun(void) {
}

@emulate "add_ofa"
.kernel checkAddOfa direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 5; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + 5; }
  .pe2 { .write = write; .spad = 5 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + 5; }
}

@kernel checkAddOfa config | exec
void checkAddOfaRun(void) {
}

@emulate "subacst"
.kernel checkSubacst direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 5; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, 5); }
  .pe2 { .write = write; .spad = (top0 - top1) + 5; }
  .pe3 { .write = write; .spad = 5 + (top0 - top1); }
}

@kernel checkSubacst config | exec
void checkSubacstRun(void) {
}

@emulate "add_byt"
.kernel checkAddByt direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = addbyt(top1, top0); }
  .pe2 { .write = write; .spad = addbyt( top0 , top1 ); }
  .pe3 { .write = write; .spad = (addbyt(top0, top1)); }
}

@kernel checkAddByt config | exec
void checkAddBytRun(void) {
}

@emulate "sub_byt"
.kernel checkSubByt direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = (subbyt(top0, top1)); }
  .pe2 { .write = write; .spad = subbyt( top0 , top1 ); }
  .pe3 { .write = write; .spad = subbyt(top0,top1); }
}

@kernel checkSubByt config | exec
void checkSubBytRun(void) {
}
