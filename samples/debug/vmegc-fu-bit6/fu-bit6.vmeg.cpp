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

volatile Buffer bit6Top0[16] = {
  0xfffffff8, 0xfffffff9, 0xfffffffa, 0xfffffffb,
  0xfffffffc, 0xfffffffd, 0xfffffffe, 0xffffffff,
  0, 1, 2, 3,
  4, 5, 6, 7,
};

volatile Buffer bit6Base0[16] = {
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer bit6Top1[16] = {
  1, 3, 5, 7,
  9, 11, 13, 15,
  0xffffffff, 0xfffffffd, 0xfffffffb, 0xfffffff9,
  0xfffffff7, 0xfffffff5, 0xfffffff3, 0xfffffff1,
};

volatile Buffer bit6Base1[16] = {
  0, 2, 4, 6,
  8, 10, 12, 14,
  0, 0xfffffffe, 0xfffffffc, 0xfffffffa,
  0xfffffff8, 0xfffffff6, 0xfffffff4, 0xfffffff2,
};

volatile Buffer bit6Top2[16] = {
  0x7ffffe, 0x7fffff, 0xff800000, 0xff800001,
  0x400000, 0xffc00000, 0x123456, 0xffedcbaa,
  1, 0xffffffff, 3, 0xfffffffd,
  5, 0xfffffffb, 0, 0,
};

volatile Buffer bit6Base2[16] = {
  1, 1, 0xffffffff, 0xffffffff,
  0x3fffff, 0xffc00001, 0x654321, 0xff9abcdf,
  1, 0xffffffff, 1, 0xffffffff,
  1, 0xffffffff, 0, 1,
};

volatile Buffer bit6Top3[16] = {
  0, 1, 0xffffffff, 2,
  0xfffffffe, 3, 0xfffffffd, 4,
  0xfffffffc, 5, 0xfffffffb, 6,
  0xfffffffa, 7, 0xfffffff9, 8,
};

volatile Buffer bit6Base3[16] = {
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1,
};

@emulate "fu-bit6-on"
.kernel checkBit6On direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: bit6Top0, count };
  Transfer top1Transfer = { memory: bit6Top1, count };
  Transfer top2Transfer = { memory: bit6Top2, count };
  Transfer top3Transfer = { memory: bit6Top3, count };
  Transfer base0Transfer = { memory: bit6Base0, count };
  Transfer base1Transfer = { memory: bit6Base1, count };
  Transfer base2Transfer = { memory: bit6Base2, count };
  Transfer base3Transfer = { memory: bit6Base3, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }
  .load { .transfer = top2Transfer; .scope = global; .offsets { .top2 = 0; } }
  .load { .transfer = top3Transfer; .scope = global; .offsets { .top3 = 0; } }
  .load { .transfer = base0Transfer; .scope = global; .offsets { .base0 = 16; } }
  .load { .transfer = base1Transfer; .scope = global; .offsets { .base1 = 16; } }
  .load { .transfer = base2Transfer; .scope = global; .offsets { .base2 = 16; } }
  .load { .transfer = base3Transfer; .scope = global; .offsets { .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(top0 + base0 >> 1); }
  .pe1 { .top = top; .base = base; .write = write; .spad = zsm(top1 - base1 >> 1); }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(top2 + base2 >> 2); }
  .pe3 { .top = top; .base = base; .write = write; .spad = zsm(top3 * base3 >> 4); }
}

@kernel checkBit6On config | exec
void checkBit6OnRun(void) {
}

@emulate "fu-bit6-off"
.kernel checkBit6Off direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: bit6Top0, count };
  Transfer top1Transfer = { memory: bit6Top1, count };
  Transfer top2Transfer = { memory: bit6Top2, count };
  Transfer top3Transfer = { memory: bit6Top3, count };
  Transfer base0Transfer = { memory: bit6Base0, count };
  Transfer base1Transfer = { memory: bit6Base1, count };
  Transfer base2Transfer = { memory: bit6Base2, count };
  Transfer base3Transfer = { memory: bit6Base3, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }
  .load { .transfer = top2Transfer; .scope = global; .offsets { .top2 = 0; } }
  .load { .transfer = top3Transfer; .scope = global; .offsets { .top3 = 0; } }
  .load { .transfer = base0Transfer; .scope = global; .offsets { .base0 = 16; } }
  .load { .transfer = base1Transfer; .scope = global; .offsets { .base1 = 16; } }
  .load { .transfer = base2Transfer; .scope = global; .offsets { .base2 = 16; } }
  .load { .transfer = base3Transfer; .scope = global; .offsets { .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = top0 + base0 >> 1; }
  .pe1 { .top = top; .base = base; .write = write; .spad = top1 - base1 >> 1; }
  .pe2 { .top = top; .base = base; .write = write; .spad = top2 + base2 >> 2; }
  .pe3 { .top = top; .base = base; .write = write; .spad = top3 * base3 >> 4; }
}

@kernel checkBit6Off config | exec
void checkBit6OffRun(void) {
}
