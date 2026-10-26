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
