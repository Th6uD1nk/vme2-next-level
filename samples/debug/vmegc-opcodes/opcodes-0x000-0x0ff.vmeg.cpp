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

volatile Buffer in0[256] = {
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff,
  0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff,
  0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff,
  0x2, 0x2, 0x2, 0x2,
  0x2, 0x2, 0x2, 0x2,
  0x2, 0x2, 0x2, 0x2,
  0xfffffffe, 0xfffffffe, 0xfffffffe, 0xfffffffe,
  0xfffffffe, 0xfffffffe, 0xfffffffe, 0xfffffffe,
  0xfffffffe, 0xfffffffe, 0xfffffffe, 0xfffffffe,
  0x7fffff, 0x7fffff, 0x7fffff, 0x7fffff,
  0x7fffff, 0x7fffff, 0x7fffff, 0x7fffff,
  0x7fffff, 0x7fffff, 0x7fffff, 0x7fffff,
  0xff800000, 0xff800000, 0xff800000, 0xff800000,
  0xff800000, 0xff800000, 0xff800000, 0xff800000,
  0xff800000, 0xff800000, 0xff800000, 0xff800000,
  0x555555, 0x555555, 0x555555, 0x555555,
  0x555555, 0x555555, 0x555555, 0x555555,
  0x555555, 0x555555, 0x555555, 0x555555,
  0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa,
  0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa,
  0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xffffff00, 0xffffff00, 0xffffff00, 0xffffff00,
  0xffffff00, 0xffffff00, 0xffffff00, 0xffffff00,
  0xffffff00, 0xffffff00, 0xffffff00, 0xffffff00,
  0x1234, 0x1234, 0x1234, 0x1234,
  0x1234, 0x1234, 0x1234, 0x1234,
  0x1234, 0x1234, 0x1234, 0x1234,
  0x1f4d40, 0xffdacb41, 0x85982, 0xffb05643,
  0xff8ab0c4, 0x4c87c5, 0xff8112c6, 0x321807,
  0xff8429c8, 0x2f3e09, 0xffec7b4a, 0xffb66b0b,
  0x29fc8c, 0x13da4d, 0xffce2f0e, 0xffba478f,
  0xf1d10, 0x532c11, 0xfffc8012, 0xff872e93,
  0x296454, 0xffb94fd5, 0x1dd696, 0x76657,
  0xffca7098, 0xffe84059, 0x2a875a, 0x16461b,
  0x1b821c, 0x11add, 0xffe3abde, 0xffcd2c1f,
  0x7da020, 0x47a121, 0x6b9fa2, 0x59d323,
  0xff8f70a4, 0xff888e65, 0xff9b15a6, 0xff8f35a7,
  0xffcd83e8, 0x611d29, 0x64212a, 0x475b6b,
  0x456e2c, 0xfffbff2d, 0x3fd46e, 0xffacf4ef,
  0xffa61f70, 0x60e6f1, 0x50ba72, 0xff868f73,
  0x85f4, 0x469e75, 0xffcc5776, 0xffa2cdf7,
  0xff86ac38, 0xffae7ab9, 0xffc8807a, 0x50057b,
  0x75cfbc, 0xffc48a7d, 0xffe147be, 0x5c43bf,
  0xffe44067, 0xfffa27f3, 0xff89b0d1, 0xffe3d198,
  0xffc649f0, 0xfff8c78c, 0x260a88, 0xff9d80d3,
  0x7b9190, 0x71b534, 0x30233f, 0xffa9c314,
  0xffac26d1, 0xffbe3eaa, 0x49cff, 0xfffb4472,
  0xffd7fe48, 0xffc04d27, 0xfffea135, 0xffd038f9,
  0x2f87de, 0x53c934, 0xffd5114e, 0x6328b0,
  0xffdc0b4a, 0x12fc10, 0xff8136d8, 0x17c3d5,
  0xffcb0d83, 0x127e7e, 0x6af810, 0x731aa4,
  0xffdebd57, 0xfffcf84d, 0x561ed7, 0x16d231,
  0x4dca39, 0x53df3c, 0x360c26, 0xffe1979f,
  0x540356, 0xffee0d69, 0x2e4048, 0xffcbef3b,
  0xffbe620d, 0xa6032, 0xff80d334, 0x2343a7,
};

volatile Buffer in1[256] = {
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x4799cb, 0x4675f0, 0x7d6d5, 0x67f6ba,
  0x324b1f, 0xff8ef004, 0x6b39a9, 0xff9a628e,
  0xff9396f3, 0x3ec7d8, 0xff82523d, 0x1176a2,
  0xfffddd07, 0x760aec, 0xffcc32d1, 0xffede636,
  0x49771b, 0xff8bed40, 0xff801525, 0x30d04a,
  0xfff925ef, 0xffc1b594, 0x68b5f9, 0x77c9e,
  0xff939243, 0xffe38528, 0x4c678d, 0x43f8b2,
  0x2abed7, 0xff8f857c, 0x1643a1, 0x2bad46,
  0x300b2b, 0x1a3490, 0x2025b5, 0x6bdf5a,
  0xffa8bd3f, 0xffc9f864, 0x3b6609, 0x5929ae,
  0xfff2a193, 0x7b3d38, 0x50cfdd, 0x6482c2,
  0x2bb6a7, 0x70ddcc, 0xffdd3831, 0xffef7f56,
  0xffcf223b, 0xffca89a0, 0x1295c5, 0x3251ea,
  0x53168f, 0xffec7034, 0xffec1b19, 0xffdc0bbe,
  0xffe9b1a3, 0xfff19b88, 0xff9381ad, 0x7c8dd2,
  0xffb01f37, 0xffb5715c, 0x76ac81, 0xffcb6866,
  0x173c4e, 0x403621, 0xe8a83, 0xff858f2c,
  0x6c219c, 0xffaabed3, 0x6be48b, 0xffa18436,
  0xffcef905, 0x2fa332, 0x71b156, 0x30911b,
  0x65e0d2, 0xff8641cd, 0x402cd2, 0xff994d5f,
  0x62ca86, 0x7f29ff, 0x59d33f, 0xffff6f20,
  0x7f678d, 0x55740a, 0x500d60, 0x7a865e,
  0xff9869c6, 0xffb9a9d6, 0xffea3977, 0x568235,
  0x17c81d, 0xff933af7, 0x7aba31, 0xffad7a4f,
  0x799c1d, 0xffb72660, 0x12f67d, 0x71c773,
  0x63523c, 0xffbb79ee, 0x5aa78d, 0xffcac558,
  0x5a9768, 0x4f2153, 0xffc86441, 0x49e141,
  0x5fbc51, 0x63e5db, 0xffc1ced7, 0x73091a,
};

@emulate "pass"
.kernel checkPass direct {
  Int count = 256 - 1;

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
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 5; }
  .pe1 { .top = top; .write = write; .spad = cst(5); }
  .pe2 { .write = write; .spad = (5 + 1) - 1; }
  .pe3 { .write = write; .spad = (5 * 1) | 0; }
}

@kernel checkCst config | exec
void checkCstRun(void) {
}

@emulate "cst_2"
.kernel checkCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0; }
  .pe1 { .top = top; .write = write; .spad = cst(0); }
  .pe2 { .write = write; .spad = (0 + 1) - 1; }
  .pe3 { .write = write; .spad = (0 * 1) | 0; }
}

@kernel checkCst2 config | exec
void checkCst2Run(void) {
}

@emulate "cst_3"
.kernel checkCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1; }
  .pe1 { .top = top; .write = write; .spad = cst(-1); }
  .pe2 { .write = write; .spad = (-1 + 1) - 1; }
  .pe3 { .write = write; .spad = (-1 * 1) | 0; }
}

@kernel checkCst3 config | exec
void checkCst3Run(void) {
}

@emulate "cst_4"
.kernel checkCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607; }
  .pe1 { .top = top; .write = write; .spad = cst(8388607); }
  .pe2 { .write = write; .spad = (8388607 + 1) - 1; }
  .pe3 { .write = write; .spad = (8388607 * 1) | 0; }
}

@kernel checkCst4 config | exec
void checkCst4Run(void) {
}

@emulate "cst_5"
.kernel checkCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608; }
  .pe1 { .top = top; .write = write; .spad = cst(-8388608); }
  .pe2 { .write = write; .spad = (-8388608 + 1) - 1; }
  .pe3 { .write = write; .spad = (-8388608 * 1) | 0; }
}

@kernel checkCst5 config | exec
void checkCst5Run(void) {
}

@emulate "cst_6"
.kernel checkCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 4660; }
  .pe1 { .top = top; .write = write; .spad = cst(4660); }
  .pe2 { .write = write; .spad = (4660 + 1) - 1; }
  .pe3 { .write = write; .spad = (4660 * 1) | 0; }
}

@kernel checkCst6 config | exec
void checkCst6Run(void) {
}

@emulate "add"
.kernel checkAdd direct {
  Int count = 256 - 1;

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
  Int count = 256 - 1;

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
  Int count = 256 - 1;

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
  Int count = 256 - 1;

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

@emulate "add_cst_2"
.kernel checkAddCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 0; }
  .pe1 { .top = top; .write = write; .spad = 0 + top1; }
  .pe2 { .write = write; .spad = (top1) + 0; }
  .pe3 { .write = write; .spad = (top1 + 0); }
}

@kernel checkAddCst2 config | exec
void checkAddCst2Run(void) {
}

@emulate "add_cst_3"
.kernel checkAddCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + -1; }
  .pe1 { .top = top; .write = write; .spad = -1 + top1; }
  .pe2 { .write = write; .spad = (top1) + -1; }
  .pe3 { .write = write; .spad = (top1 + -1); }
}

@kernel checkAddCst3 config | exec
void checkAddCst3Run(void) {
}

@emulate "add_cst_4"
.kernel checkAddCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 8388607; }
  .pe1 { .top = top; .write = write; .spad = 8388607 + top1; }
  .pe2 { .write = write; .spad = (top1) + 8388607; }
  .pe3 { .write = write; .spad = (top1 + 8388607); }
}

@kernel checkAddCst4 config | exec
void checkAddCst4Run(void) {
}

@emulate "add_cst_5"
.kernel checkAddCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + -8388608; }
  .pe1 { .top = top; .write = write; .spad = -8388608 + top1; }
  .pe2 { .write = write; .spad = (top1) + -8388608; }
  .pe3 { .write = write; .spad = (top1 + -8388608); }
}

@kernel checkAddCst5 config | exec
void checkAddCst5Run(void) {
}

@emulate "add_cst_6"
.kernel checkAddCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 4660; }
  .pe1 { .top = top; .write = write; .spad = 4660 + top1; }
  .pe2 { .write = write; .spad = (top1) + 4660; }
  .pe3 { .write = write; .spad = (top1 + 4660); }
}

@kernel checkAddCst6 config | exec
void checkAddCst6Run(void) {
}

@emulate "neg_ofb"
.kernel checkNegOfb direct {
  Int count = 256 - 1;

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

@emulate "neg_ofb_2"
.kernel checkNegOfb2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0 - top1; }
  .pe1 { .top = top; .write = write; .spad = (0 - top1); }
  .pe2 { .write = write; .spad = 0 - (top1); }
  .pe3 { .write = write; .spad = (0) - top1; }
}

@kernel checkNegOfb2 config | exec
void checkNegOfb2Run(void) {
}

@emulate "neg_ofb_3"
.kernel checkNegOfb3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1 - top1; }
  .pe1 { .top = top; .write = write; .spad = (-1 - top1); }
  .pe2 { .write = write; .spad = -1 - (top1); }
  .pe3 { .write = write; .spad = (-1) - top1; }
}

@kernel checkNegOfb3 config | exec
void checkNegOfb3Run(void) {
}

@emulate "neg_ofb_4"
.kernel checkNegOfb4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607 - top1; }
  .pe1 { .top = top; .write = write; .spad = (8388607 - top1); }
  .pe2 { .write = write; .spad = 8388607 - (top1); }
  .pe3 { .write = write; .spad = (8388607) - top1; }
}

@kernel checkNegOfb4 config | exec
void checkNegOfb4Run(void) {
}

@emulate "neg_ofb_5"
.kernel checkNegOfb5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608 - top1; }
  .pe1 { .top = top; .write = write; .spad = (-8388608 - top1); }
  .pe2 { .write = write; .spad = -8388608 - (top1); }
  .pe3 { .write = write; .spad = (-8388608) - top1; }
}

@kernel checkNegOfb5 config | exec
void checkNegOfb5Run(void) {
}

@emulate "add_ofa"
.kernel checkAddOfa direct {
  Int count = 256 - 1;

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

@emulate "add_ofa_2"
.kernel checkAddOfa2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + -1; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + -1; }
  .pe2 { .write = write; .spad = -1 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + -1; }
}

@kernel checkAddOfa2 config | exec
void checkAddOfa2Run(void) {
}

@emulate "add_ofa_3"
.kernel checkAddOfa3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 8388607; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + 8388607; }
  .pe2 { .write = write; .spad = 8388607 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + 8388607; }
}

@kernel checkAddOfa3 config | exec
void checkAddOfa3Run(void) {
}

@emulate "add_ofa_4"
.kernel checkAddOfa4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + -8388608; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + -8388608; }
  .pe2 { .write = write; .spad = -8388608 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + -8388608; }
}

@kernel checkAddOfa4 config | exec
void checkAddOfa4Run(void) {
}

@emulate "add_ofa_5"
.kernel checkAddOfa5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 4660; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + 4660; }
  .pe2 { .write = write; .spad = 4660 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + 4660; }
}

@kernel checkAddOfa5 config | exec
void checkAddOfa5Run(void) {
}

@emulate "subacst"
.kernel checkSubacst direct {
  Int count = 256 - 1;

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

@emulate "subacst_2"
.kernel checkSubacst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + -1; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, -1); }
  .pe2 { .write = write; .spad = (top0 - top1) + -1; }
  .pe3 { .write = write; .spad = -1 + (top0 - top1); }
}

@kernel checkSubacst2 config | exec
void checkSubacst2Run(void) {
}

@emulate "subacst_3"
.kernel checkSubacst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 8388607; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, 8388607); }
  .pe2 { .write = write; .spad = (top0 - top1) + 8388607; }
  .pe3 { .write = write; .spad = 8388607 + (top0 - top1); }
}

@kernel checkSubacst3 config | exec
void checkSubacst3Run(void) {
}

@emulate "subacst_4"
.kernel checkSubacst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + -8388608; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, -8388608); }
  .pe2 { .write = write; .spad = (top0 - top1) + -8388608; }
  .pe3 { .write = write; .spad = -8388608 + (top0 - top1); }
}

@kernel checkSubacst4 config | exec
void checkSubacst4Run(void) {
}

@emulate "subacst_5"
.kernel checkSubacst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 4660; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, 4660); }
  .pe2 { .write = write; .spad = (top0 - top1) + 4660; }
  .pe3 { .write = write; .spad = 4660 + (top0 - top1); }
}

@kernel checkSubacst5 config | exec
void checkSubacst5Run(void) {
}

@emulate "add_byt"
.kernel checkAddByt direct {
  Int count = 256 - 1;

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
  Int count = 256 - 1;

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

@emulate "add_shf"
.kernel checkAddShf direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 3); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 3) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (3 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 3); }
}

@kernel checkAddShf config | exec
void checkAddShfRun(void) {
}

@emulate "add_shf_2"
.kernel checkAddShf2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 0); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 0) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (0 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 0); }
}

@kernel checkAddShf2 config | exec
void checkAddShf2Run(void) {
}

@emulate "add_shf_3"
.kernel checkAddShf3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 1); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 1) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (1 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 1); }
}

@kernel checkAddShf3 config | exec
void checkAddShf3Run(void) {
}

@emulate "add_shf_4"
.kernel checkAddShf4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 31); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 31) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (31 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 31); }
}

@kernel checkAddShf4 config | exec
void checkAddShf4Run(void) {
}

@emulate "add_shf_5"
.kernel checkAddShf5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> -1); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> -1) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (-1 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> -1); }
}

@kernel checkAddShf5 config | exec
void checkAddShf5Run(void) {
}

@emulate "add_shf_6"
.kernel checkAddShf6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> -32); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> -32) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (-32 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> -32); }
}

@kernel checkAddShf6 config | exec
void checkAddShf6Run(void) {
}

@emulate "add_shf_7"
.kernel checkAddShf7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 40); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 40) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (40 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 40); }
}

@kernel checkAddShf7 config | exec
void checkAddShf7Run(void) {
}

@emulate "shr_cst_ofa"
.kernel checkShrCstOfa direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 3) + 5; }
  .pe1 { .top = top; .write = write; .spad = 5 + (top1 >> 3); }
  .pe2 { .write = write; .spad = ((top1 >> 3)) + 5; }
  .pe3 { .write = write; .spad = (top1 >> (3 + 0)) + (5); }
}

@kernel checkShrCstOfa config | exec
void checkShrCstOfaRun(void) {
}

@emulate "shr_cst_ofa_2"
.kernel checkShrCstOfa2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 0) + 0; }
  .pe1 { .top = top; .write = write; .spad = 0 + (top1 >> 0); }
  .pe2 { .write = write; .spad = ((top1 >> 0)) + 0; }
  .pe3 { .write = write; .spad = (top1 >> (0 + 0)) + (0); }
}

@kernel checkShrCstOfa2 config | exec
void checkShrCstOfa2Run(void) {
}

@emulate "shr_cst_ofa_3"
.kernel checkShrCstOfa3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 1) + -1; }
  .pe1 { .top = top; .write = write; .spad = -1 + (top1 >> 1); }
  .pe2 { .write = write; .spad = ((top1 >> 1)) + -1; }
  .pe3 { .write = write; .spad = (top1 >> (1 + 0)) + (-1); }
}

@kernel checkShrCstOfa3 config | exec
void checkShrCstOfa3Run(void) {
}

@emulate "shr_cst_ofa_4"
.kernel checkShrCstOfa4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 31) + 8388607; }
  .pe1 { .top = top; .write = write; .spad = 8388607 + (top1 >> 31); }
  .pe2 { .write = write; .spad = ((top1 >> 31)) + 8388607; }
  .pe3 { .write = write; .spad = (top1 >> (31 + 0)) + (8388607); }
}

@kernel checkShrCstOfa4 config | exec
void checkShrCstOfa4Run(void) {
}

@emulate "shr_cst_ofa_5"
.kernel checkShrCstOfa5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -1) + -8388608; }
  .pe1 { .top = top; .write = write; .spad = -8388608 + (top1 >> -1); }
  .pe2 { .write = write; .spad = ((top1 >> -1)) + -8388608; }
  .pe3 { .write = write; .spad = (top1 >> (-1 + 0)) + (-8388608); }
}

@kernel checkShrCstOfa5 config | exec
void checkShrCstOfa5Run(void) {
}

@emulate "shr_cst_ofa_6"
.kernel checkShrCstOfa6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -32) + 7; }
  .pe1 { .top = top; .write = write; .spad = 7 + (top1 >> -32); }
  .pe2 { .write = write; .spad = ((top1 >> -32)) + 7; }
  .pe3 { .write = write; .spad = (top1 >> (-32 + 0)) + (7); }
}

@kernel checkShrCstOfa6 config | exec
void checkShrCstOfa6Run(void) {
}

@emulate "shr_cst_ofa_7"
.kernel checkShrCstOfa7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 40) + 9; }
  .pe1 { .top = top; .write = write; .spad = 9 + (top1 >> 40); }
  .pe2 { .write = write; .spad = ((top1 >> 40)) + 9; }
  .pe3 { .write = write; .spad = (top1 >> (40 + 0)) + (9); }
}

@kernel checkShrCstOfa7 config | exec
void checkShrCstOfa7Run(void) {
}

@emulate "subshr"
.kernel checkSubshr direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 3); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 3); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 3); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 3); }
}

@kernel checkSubshr config | exec
void checkSubshrRun(void) {
}

@emulate "subshr_2"
.kernel checkSubshr2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 0); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 0); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 0); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 0); }
}

@kernel checkSubshr2 config | exec
void checkSubshr2Run(void) {
}

@emulate "subshr_3"
.kernel checkSubshr3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 1); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 1); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 1); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 1); }
}

@kernel checkSubshr3 config | exec
void checkSubshr3Run(void) {
}

@emulate "subshr_4"
.kernel checkSubshr4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 31); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 31); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 31); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 31); }
}

@kernel checkSubshr4 config | exec
void checkSubshr4Run(void) {
}

@emulate "subshr_5"
.kernel checkSubshr5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> -1); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, -1); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> -1); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> -1); }
}

@kernel checkSubshr5 config | exec
void checkSubshr5Run(void) {
}

@emulate "subshr_6"
.kernel checkSubshr6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> -32); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, -32); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> -32); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> -32); }
}

@kernel checkSubshr6 config | exec
void checkSubshr6Run(void) {
}

@emulate "subshr_7"
.kernel checkSubshr7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 40); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 40); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 40); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 40); }
}

@kernel checkSubshr7 config | exec
void checkSubshr7Run(void) {
}

@emulate "shr_cst_neg_ofa"
.kernel checkShrCstNegOfa direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 5 - (top1 >> 3); }
  .pe1 { .top = top; .write = write; .spad = (5) - (top1 >> 3); }
  .pe2 { .write = write; .spad = (5 + 0) - (top1 >> 3); }
  .pe3 { .write = write; .spad = 5 - ((top1) >> 3); }
}

@kernel checkShrCstNegOfa config | exec
void checkShrCstNegOfaRun(void) {
}

@emulate "shr_cst_neg_ofa_2"
.kernel checkShrCstNegOfa2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0 - (top1 >> 0); }
  .pe1 { .top = top; .write = write; .spad = (0) - (top1 >> 0); }
  .pe2 { .write = write; .spad = (0 + 0) - (top1 >> 0); }
  .pe3 { .write = write; .spad = 0 - ((top1) >> 0); }
}

@kernel checkShrCstNegOfa2 config | exec
void checkShrCstNegOfa2Run(void) {
}

@emulate "shr_cst_neg_ofa_3"
.kernel checkShrCstNegOfa3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1 - (top1 >> 1); }
  .pe1 { .top = top; .write = write; .spad = (-1) - (top1 >> 1); }
  .pe2 { .write = write; .spad = (-1 + 0) - (top1 >> 1); }
  .pe3 { .write = write; .spad = -1 - ((top1) >> 1); }
}

@kernel checkShrCstNegOfa3 config | exec
void checkShrCstNegOfa3Run(void) {
}

@emulate "shr_cst_neg_ofa_4"
.kernel checkShrCstNegOfa4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607 - (top1 >> 31); }
  .pe1 { .top = top; .write = write; .spad = (8388607) - (top1 >> 31); }
  .pe2 { .write = write; .spad = (8388607 + 0) - (top1 >> 31); }
  .pe3 { .write = write; .spad = 8388607 - ((top1) >> 31); }
}

@kernel checkShrCstNegOfa4 config | exec
void checkShrCstNegOfa4Run(void) {
}

@emulate "shr_cst_neg_ofa_5"
.kernel checkShrCstNegOfa5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608 - (top1 >> -1); }
  .pe1 { .top = top; .write = write; .spad = (-8388608) - (top1 >> -1); }
  .pe2 { .write = write; .spad = (-8388608 + 0) - (top1 >> -1); }
  .pe3 { .write = write; .spad = -8388608 - ((top1) >> -1); }
}

@kernel checkShrCstNegOfa5 config | exec
void checkShrCstNegOfa5Run(void) {
}

@emulate "shr_cst_neg_ofa_6"
.kernel checkShrCstNegOfa6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 7 - (top1 >> -32); }
  .pe1 { .top = top; .write = write; .spad = (7) - (top1 >> -32); }
  .pe2 { .write = write; .spad = (7 + 0) - (top1 >> -32); }
  .pe3 { .write = write; .spad = 7 - ((top1) >> -32); }
}

@kernel checkShrCstNegOfa6 config | exec
void checkShrCstNegOfa6Run(void) {
}

@emulate "shr_cst_neg_ofa_7"
.kernel checkShrCstNegOfa7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 9 - (top1 >> 40); }
  .pe1 { .top = top; .write = write; .spad = (9) - (top1 >> 40); }
  .pe2 { .write = write; .spad = (9 + 0) - (top1 >> 40); }
  .pe3 { .write = write; .spad = 9 - ((top1) >> 40); }
}

@kernel checkShrCstNegOfa7 config | exec
void checkShrCstNegOfa7Run(void) {
}

@emulate "shrsub"
.kernel checkShrsub direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 3) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 3)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 3) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 3) - top0; }
}

@kernel checkShrsub config | exec
void checkShrsubRun(void) {
}

@emulate "shrsub_2"
.kernel checkShrsub2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 0) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 0)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 0) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 0) - top0; }
}

@kernel checkShrsub2 config | exec
void checkShrsub2Run(void) {
}

@emulate "shrsub_3"
.kernel checkShrsub3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 1) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 1)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 1) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 1) - top0; }
}

@kernel checkShrsub3 config | exec
void checkShrsub3Run(void) {
}

@emulate "shrsub_4"
.kernel checkShrsub4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 31) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 31)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 31) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 31) - top0; }
}

@kernel checkShrsub4 config | exec
void checkShrsub4Run(void) {
}

@emulate "shrsub_5"
.kernel checkShrsub5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -1) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> -1)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> -1) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> -1) - top0; }
}

@kernel checkShrsub5 config | exec
void checkShrsub5Run(void) {
}

@emulate "shrsub_6"
.kernel checkShrsub6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -32) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> -32)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> -32) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> -32) - top0; }
}

@kernel checkShrsub6 config | exec
void checkShrsub6Run(void) {
}

@emulate "shrsub_7"
.kernel checkShrsub7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 40) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 40)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 40) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 40) - top0; }
}

@kernel checkShrsub7 config | exec
void checkShrsub7Run(void) {
}

@emulate "shr_cst_ofs"
.kernel checkShrCstOfs direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 3) - 5; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 3)) - 5; }
  .pe2 { .write = write; .spad = (top1 >> 3) - (5); }
  .pe3 { .write = write; .spad = ((top1) >> 3) - 5; }
}

@kernel checkShrCstOfs config | exec
void checkShrCstOfsRun(void) {
}

@emulate "shr_cst_ofs_2"
.kernel checkShrCstOfs2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 0) - 0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 0)) - 0; }
  .pe2 { .write = write; .spad = (top1 >> 0) - (0); }
  .pe3 { .write = write; .spad = ((top1) >> 0) - 0; }
}

@kernel checkShrCstOfs2 config | exec
void checkShrCstOfs2Run(void) {
}

@emulate "shr_cst_ofs_3"
.kernel checkShrCstOfs3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 1) - -1; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 1)) - -1; }
  .pe2 { .write = write; .spad = (top1 >> 1) - (-1); }
  .pe3 { .write = write; .spad = ((top1) >> 1) - -1; }
}

@kernel checkShrCstOfs3 config | exec
void checkShrCstOfs3Run(void) {
}

@emulate "shr_cst_ofs_4"
.kernel checkShrCstOfs4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 31) - 8388607; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 31)) - 8388607; }
  .pe2 { .write = write; .spad = (top1 >> 31) - (8388607); }
  .pe3 { .write = write; .spad = ((top1) >> 31) - 8388607; }
}

@kernel checkShrCstOfs4 config | exec
void checkShrCstOfs4Run(void) {
}

@emulate "shr_cst_ofs_5"
.kernel checkShrCstOfs5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -1) - -8388608; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> -1)) - -8388608; }
  .pe2 { .write = write; .spad = (top1 >> -1) - (-8388608); }
  .pe3 { .write = write; .spad = ((top1) >> -1) - -8388608; }
}

@kernel checkShrCstOfs5 config | exec
void checkShrCstOfs5Run(void) {
}

@emulate "shr_cst_ofs_6"
.kernel checkShrCstOfs6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -32) - 7; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> -32)) - 7; }
  .pe2 { .write = write; .spad = (top1 >> -32) - (7); }
  .pe3 { .write = write; .spad = ((top1) >> -32) - 7; }
}

@kernel checkShrCstOfs6 config | exec
void checkShrCstOfs6Run(void) {
}

@emulate "shr_cst_ofs_7"
.kernel checkShrCstOfs7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 40) - 9; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 40)) - 9; }
  .pe2 { .write = write; .spad = (top1 >> 40) - (9); }
  .pe3 { .write = write; .spad = ((top1) >> 40) - 9; }
}

@kernel checkShrCstOfs7 config | exec
void checkShrCstOfs7Run(void) {
}

@emulate "add_hib"
.kernel checkAddHib direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = addhib(top1, top0); }
  .pe2 { .write = write; .spad = addhib( top0 , top1 ); }
  .pe3 { .write = write; .spad = (addhib(top0, top1)); }
}

@kernel checkAddHib config | exec
void checkAddHibRun(void) {
}

@emulate "add_lob"
.kernel checkAddLob direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = (top1 & 0xff) + (top0 & 0xff); }
  .pe2 { .write = write; .spad = ((top0 & 255)) + ((top1 & 255)); }
  .pe3 { .write = write; .spad = (255 & top0) + (255 & top1); }
}

@kernel checkAddLob config | exec
void checkAddLobRun(void) {
}

@emulate "sel_neg"
.kernel checkSelNeg direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 4) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? -top1 : (top1); }
}

@kernel checkSelNeg config | exec
void checkSelNegRun(void) {
}

@emulate "sel_neg_2"
.kernel checkSelNeg2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (0 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 0) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 0)) ? -top1 : (top1); }
}

@kernel checkSelNeg2 config | exec
void checkSelNeg2Run(void) {
}

@emulate "sel_neg_3"
.kernel checkSelNeg3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 1) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 1) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 1)) ? -top1 : (top1); }
}

@kernel checkSelNeg3 config | exec
void checkSelNeg3Run(void) {
}

@emulate "sel_neg_4"
.kernel checkSelNeg4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 8388608) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 8388608) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 8388608)) ? -top1 : (top1); }
}

@kernel checkSelNeg4 config | exec
void checkSelNeg4Run(void) {
}

@emulate "sel_neg_5"
.kernel checkSelNeg5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & -1) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & -1) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & -1)) ? -top1 : (top1); }
}

@kernel checkSelNeg5 config | exec
void checkSelNeg5Run(void) {
}

@emulate "sel_neg_6"
.kernel checkSelNeg6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 5592405) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 5592405) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 5592405)) ? -top1 : (top1); }
}

@kernel checkSelNeg6 config | exec
void checkSelNeg6Run(void) {
}

@emulate "sel_neg_slf"
.kernel checkSelNegSlf direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 4) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf config | exec
void checkSelNegSlfRun(void) {
}

@emulate "sel_neg_slf_2"
.kernel checkSelNegSlf2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (0 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 0) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 0)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf2 config | exec
void checkSelNegSlf2Run(void) {
}

@emulate "sel_neg_slf_3"
.kernel checkSelNegSlf3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 1) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 1) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 1)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf3 config | exec
void checkSelNegSlf3Run(void) {
}

@emulate "sel_neg_slf_4"
.kernel checkSelNegSlf4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 8388608) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 8388608) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 8388608)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf4 config | exec
void checkSelNegSlf4Run(void) {
}

@emulate "sel_neg_slf_5"
.kernel checkSelNegSlf5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & -1) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & -1) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & -1)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf5 config | exec
void checkSelNegSlf5Run(void) {
}

@emulate "sel_neg_slf_6"
.kernel checkSelNegSlf6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 5592405) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 5592405) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 5592405)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf6 config | exec
void checkSelNegSlf6Run(void) {
}

@emulate "sel_cst"
.kernel checkSelCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? 7 : top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? 7 : top1; }
  .pe2 { .write = write; .spad = (top0 & 4) ? (7 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? 7 : (top1); }
}

@kernel checkSelCst config | exec
void checkSelCstRun(void) {
}

@emulate "sel_cst_2"
.kernel checkSelCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0) ? 0 : top1; }
  .pe1 { .top = top; .write = write; .spad = (0 & top0) ? 0 : top1; }
  .pe2 { .write = write; .spad = (top0 & 0) ? (0 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 0)) ? 0 : (top1); }
}

@kernel checkSelCst2 config | exec
void checkSelCst2Run(void) {
}

@emulate "sel_cst_3"
.kernel checkSelCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 1) ? -1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top0) ? -1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 1) ? (-1 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 1)) ? -1 : (top1); }
}

@kernel checkSelCst3 config | exec
void checkSelCst3Run(void) {
}

@emulate "sel_cst_4"
.kernel checkSelCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 8388608) ? 8388607 : top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top0) ? 8388607 : top1; }
  .pe2 { .write = write; .spad = (top0 & 8388608) ? (8388607 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 8388608)) ? 8388607 : (top1); }
}

@kernel checkSelCst4 config | exec
void checkSelCst4Run(void) {
}

@emulate "sel_cst_5"
.kernel checkSelCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & -1) ? -8388608 : top1; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top0) ? -8388608 : top1; }
  .pe2 { .write = write; .spad = (top0 & -1) ? (-8388608 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & -1)) ? -8388608 : (top1); }
}

@kernel checkSelCst5 config | exec
void checkSelCst5Run(void) {
}

@emulate "sel_cst_6"
.kernel checkSelCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 5592405) ? 4660 : top1; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top0) ? 4660 : top1; }
  .pe2 { .write = write; .spad = (top0 & 5592405) ? (4660 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 5592405)) ? 4660 : (top1); }
}

@kernel checkSelCst6 config | exec
void checkSelCst6Run(void) {
}

@emulate "sel_cst_ofb"
.kernel checkSelCstOfb direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? top1 : 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? top1 : 7; }
  .pe2 { .write = write; .spad = (top0 & 4) ? top1 : (7 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? (top1) : 7; }
}

@kernel checkSelCstOfb config | exec
void checkSelCstOfbRun(void) {
}

@emulate "sel_cst_ofb_2"
.kernel checkSelCstOfb2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0) ? top1 : 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top0) ? top1 : 0; }
  .pe2 { .write = write; .spad = (top0 & 0) ? top1 : (0 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 0)) ? (top1) : 0; }
}

@kernel checkSelCstOfb2 config | exec
void checkSelCstOfb2Run(void) {
}

@emulate "sel_cst_ofb_3"
.kernel checkSelCstOfb3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 1) ? top1 : -1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top0) ? top1 : -1; }
  .pe2 { .write = write; .spad = (top0 & 1) ? top1 : (-1 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 1)) ? (top1) : -1; }
}

@kernel checkSelCstOfb3 config | exec
void checkSelCstOfb3Run(void) {
}

@emulate "sel_cst_ofb_4"
.kernel checkSelCstOfb4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 8388608) ? top1 : 8388607; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top0) ? top1 : 8388607; }
  .pe2 { .write = write; .spad = (top0 & 8388608) ? top1 : (8388607 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 8388608)) ? (top1) : 8388607; }
}

@kernel checkSelCstOfb4 config | exec
void checkSelCstOfb4Run(void) {
}

@emulate "sel_cst_ofb_5"
.kernel checkSelCstOfb5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & -1) ? top1 : -8388608; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top0) ? top1 : -8388608; }
  .pe2 { .write = write; .spad = (top0 & -1) ? top1 : (-8388608 + 0); }
  .pe3 { .write = write; .spad = ((top0 & -1)) ? (top1) : -8388608; }
}

@kernel checkSelCstOfb5 config | exec
void checkSelCstOfb5Run(void) {
}

@emulate "sel_cst_ofb_6"
.kernel checkSelCstOfb6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 5592405) ? top1 : 4660; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top0) ? top1 : 4660; }
  .pe2 { .write = write; .spad = (top0 & 5592405) ? top1 : (4660 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 5592405)) ? (top1) : 4660; }
}

@kernel checkSelCstOfb6 config | exec
void checkSelCstOfb6Run(void) {
}

@emulate "sel_ads"
.kernel checkSelAds direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? top1 - 7 : top1 + 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? top1 - 7 : top1 + 7; }
  .pe2 { .write = write; .spad = (top1 & 4) ? (top1 - 7) : (top1 + 7); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? top1 - (7 + 0) : top1 + 7; }
}

@kernel checkSelAds config | exec
void checkSelAdsRun(void) {
}

@emulate "sel_ads_2"
.kernel checkSelAds2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 0) ? top1 - 0 : top1 + 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top1) ? top1 - 0 : top1 + 0; }
  .pe2 { .write = write; .spad = (top1 & 0) ? (top1 - 0) : (top1 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 0)) ? top1 - (0 + 0) : top1 + 0; }
}

@kernel checkSelAds2 config | exec
void checkSelAds2Run(void) {
}

@emulate "sel_ads_3"
.kernel checkSelAds3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 1) ? top1 - -1 : top1 + -1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top1) ? top1 - -1 : top1 + -1; }
  .pe2 { .write = write; .spad = (top1 & 1) ? (top1 - -1) : (top1 + -1); }
  .pe3 { .write = write; .spad = ((top1 & 1)) ? top1 - (-1 + 0) : top1 + -1; }
}

@kernel checkSelAds3 config | exec
void checkSelAds3Run(void) {
}

@emulate "sel_ads_4"
.kernel checkSelAds4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 8388608) ? top1 - 8388607 : top1 + 8388607; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top1) ? top1 - 8388607 : top1 + 8388607; }
  .pe2 { .write = write; .spad = (top1 & 8388608) ? (top1 - 8388607) : (top1 + 8388607); }
  .pe3 { .write = write; .spad = ((top1 & 8388608)) ? top1 - (8388607 + 0) : top1 + 8388607; }
}

@kernel checkSelAds4 config | exec
void checkSelAds4Run(void) {
}

@emulate "sel_ads_5"
.kernel checkSelAds5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & -1) ? top1 - -8388608 : top1 + -8388608; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top1) ? top1 - -8388608 : top1 + -8388608; }
  .pe2 { .write = write; .spad = (top1 & -1) ? (top1 - -8388608) : (top1 + -8388608); }
  .pe3 { .write = write; .spad = ((top1 & -1)) ? top1 - (-8388608 + 0) : top1 + -8388608; }
}

@kernel checkSelAds5 config | exec
void checkSelAds5Run(void) {
}

@emulate "sel_ads_6"
.kernel checkSelAds6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 5592405) ? top1 - 4660 : top1 + 4660; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top1) ? top1 - 4660 : top1 + 4660; }
  .pe2 { .write = write; .spad = (top1 & 5592405) ? (top1 - 4660) : (top1 + 4660); }
  .pe3 { .write = write; .spad = ((top1 & 5592405)) ? top1 - (4660 + 0) : top1 + 4660; }
}

@kernel checkSelAds6 config | exec
void checkSelAds6Run(void) {
}

@emulate "sel_ads_inv"
.kernel checkSelAdsInv direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? top1 + 7 : top1 - 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? top1 + 7 : top1 - 7; }
  .pe2 { .write = write; .spad = (top1 & 4) ? (top1 + 7) : (top1 - 7); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? top1 + (7 + 0) : top1 - 7; }
}

@kernel checkSelAdsInv config | exec
void checkSelAdsInvRun(void) {
}

@emulate "sel_ads_inv_2"
.kernel checkSelAdsInv2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 0) ? top1 + 0 : top1 - 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top1) ? top1 + 0 : top1 - 0; }
  .pe2 { .write = write; .spad = (top1 & 0) ? (top1 + 0) : (top1 - 0); }
  .pe3 { .write = write; .spad = ((top1 & 0)) ? top1 + (0 + 0) : top1 - 0; }
}

@kernel checkSelAdsInv2 config | exec
void checkSelAdsInv2Run(void) {
}

@emulate "sel_ads_inv_3"
.kernel checkSelAdsInv3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 1) ? top1 + -1 : top1 - -1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top1) ? top1 + -1 : top1 - -1; }
  .pe2 { .write = write; .spad = (top1 & 1) ? (top1 + -1) : (top1 - -1); }
  .pe3 { .write = write; .spad = ((top1 & 1)) ? top1 + (-1 + 0) : top1 - -1; }
}

@kernel checkSelAdsInv3 config | exec
void checkSelAdsInv3Run(void) {
}

@emulate "sel_ads_inv_4"
.kernel checkSelAdsInv4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 8388608) ? top1 + 8388607 : top1 - 8388607; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top1) ? top1 + 8388607 : top1 - 8388607; }
  .pe2 { .write = write; .spad = (top1 & 8388608) ? (top1 + 8388607) : (top1 - 8388607); }
  .pe3 { .write = write; .spad = ((top1 & 8388608)) ? top1 + (8388607 + 0) : top1 - 8388607; }
}

@kernel checkSelAdsInv4 config | exec
void checkSelAdsInv4Run(void) {
}

@emulate "sel_ads_inv_5"
.kernel checkSelAdsInv5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & -1) ? top1 + -8388608 : top1 - -8388608; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top1) ? top1 + -8388608 : top1 - -8388608; }
  .pe2 { .write = write; .spad = (top1 & -1) ? (top1 + -8388608) : (top1 - -8388608); }
  .pe3 { .write = write; .spad = ((top1 & -1)) ? top1 + (-8388608 + 0) : top1 - -8388608; }
}

@kernel checkSelAdsInv5 config | exec
void checkSelAdsInv5Run(void) {
}

@emulate "sel_ads_inv_6"
.kernel checkSelAdsInv6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 5592405) ? top1 + 4660 : top1 - 4660; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top1) ? top1 + 4660 : top1 - 4660; }
  .pe2 { .write = write; .spad = (top1 & 5592405) ? (top1 + 4660) : (top1 - 4660); }
  .pe3 { .write = write; .spad = ((top1 & 5592405)) ? top1 + (4660 + 0) : top1 - 4660; }
}

@kernel checkSelAdsInv6 config | exec
void checkSelAdsInv6Run(void) {
}

@emulate "clamp"
.kernel checkClamp direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, -100, 100); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,-100,100); }
  .pe2 { .write = write; .spad = clamp((top1), -100, 100); }
  .pe3 { .write = write; .spad = clamp(top1, -100 + 0, 100); }
}

@kernel checkClamp config | exec
void checkClampRun(void) {
}

@emulate "clamp_2"
.kernel checkClamp2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 0, 0); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,0,0); }
  .pe2 { .write = write; .spad = clamp((top1), 0, 0); }
  .pe3 { .write = write; .spad = clamp(top1, 0 + 0, 0); }
}

@kernel checkClamp2 config | exec
void checkClamp2Run(void) {
}

@emulate "clamp_3"
.kernel checkClamp3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, -1, 1); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,-1,1); }
  .pe2 { .write = write; .spad = clamp((top1), -1, 1); }
  .pe3 { .write = write; .spad = clamp(top1, -1 + 0, 1); }
}

@kernel checkClamp3 config | exec
void checkClamp3Run(void) {
}

@emulate "clamp_4"
.kernel checkClamp4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 100, -100); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,100,-100); }
  .pe2 { .write = write; .spad = clamp((top1), 100, -100); }
  .pe3 { .write = write; .spad = clamp(top1, 100 + 0, -100); }
}

@kernel checkClamp4 config | exec
void checkClamp4Run(void) {
}

@emulate "clamp_5"
.kernel checkClamp5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, -8388608, 8388607); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,-8388608,8388607); }
  .pe2 { .write = write; .spad = clamp((top1), -8388608, 8388607); }
  .pe3 { .write = write; .spad = clamp(top1, -8388608 + 0, 8388607); }
}

@kernel checkClamp5 config | exec
void checkClamp5Run(void) {
}

@emulate "clamp_6"
.kernel checkClamp6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 8388607, -8388608); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,8388607,-8388608); }
  .pe2 { .write = write; .spad = clamp((top1), 8388607, -8388608); }
  .pe3 { .write = write; .spad = clamp(top1, 8388607 + 0, -8388608); }
}

@kernel checkClamp6 config | exec
void checkClamp6Run(void) {
}

@emulate "clamp_7"
.kernel checkClamp7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 5, 5); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,5,5); }
  .pe2 { .write = write; .spad = clamp((top1), 5, 5); }
  .pe3 { .write = write; .spad = clamp(top1, 5 + 0, 5); }
}

@kernel checkClamp7 config | exec
void checkClamp7Run(void) {
}

@emulate "mul_clp"
.kernel checkMulClp direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = mulclp(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = (mulclp(top0, top1)); }
  .pe2 { .write = write; .spad = mulclp( top0 , top1 ); }
  .pe3 { .write = write; .spad = mulclp(top0,top1); }
}

@kernel checkMulClp config | exec
void checkMulClpRun(void) {
}

@emulate "mul_clp_neg"
.kernel checkMulClpNeg direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = mulclpneg(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = (mulclpneg(top0, top1)); }
  .pe2 { .write = write; .spad = mulclpneg( top0 , top1 ); }
  .pe3 { .write = write; .spad = mulclpneg(top0,top1); }
}

@kernel checkMulClpNeg config | exec
void checkMulClpNegRun(void) {
}

@emulate "sel_cst_zer"
.kernel checkSelCstZer direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? 0 : 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? 0 : 7; }
  .pe2 { .write = write; .spad = (top1 & 4) ? 0 : (7 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? 0 : 7; }
}

@kernel checkSelCstZer config | exec
void checkSelCstZerRun(void) {
}

@emulate "sel_cst_zer_2"
.kernel checkSelCstZer2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 0) ? 0 : 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top1) ? 0 : 0; }
  .pe2 { .write = write; .spad = (top1 & 0) ? 0 : (0 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 0)) ? 0 : 0; }
}

@kernel checkSelCstZer2 config | exec
void checkSelCstZer2Run(void) {
}

@emulate "sel_cst_zer_3"
.kernel checkSelCstZer3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 1) ? 0 : -1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top1) ? 0 : -1; }
  .pe2 { .write = write; .spad = (top1 & 1) ? 0 : (-1 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 1)) ? 0 : -1; }
}

@kernel checkSelCstZer3 config | exec
void checkSelCstZer3Run(void) {
}

@emulate "sel_cst_zer_4"
.kernel checkSelCstZer4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 8388608) ? 0 : 8388607; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top1) ? 0 : 8388607; }
  .pe2 { .write = write; .spad = (top1 & 8388608) ? 0 : (8388607 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 8388608)) ? 0 : 8388607; }
}

@kernel checkSelCstZer4 config | exec
void checkSelCstZer4Run(void) {
}

@emulate "sel_cst_zer_5"
.kernel checkSelCstZer5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & -1) ? 0 : -8388608; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top1) ? 0 : -8388608; }
  .pe2 { .write = write; .spad = (top1 & -1) ? 0 : (-8388608 + 0); }
  .pe3 { .write = write; .spad = ((top1 & -1)) ? 0 : -8388608; }
}

@kernel checkSelCstZer5 config | exec
void checkSelCstZer5Run(void) {
}

@emulate "sel_cst_zer_6"
.kernel checkSelCstZer6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 5592405) ? 0 : 4660; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top1) ? 0 : 4660; }
  .pe2 { .write = write; .spad = (top1 & 5592405) ? 0 : (4660 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 5592405)) ? 0 : 4660; }
}

@kernel checkSelCstZer6 config | exec
void checkSelCstZer6Run(void) {
}

@emulate "sel_cst_zer_inv"
.kernel checkSelCstZerInv direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? 7 : 0; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? 7 : 0; }
  .pe2 { .write = write; .spad = (top1 & 4) ? (7 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? 7 : 0; }
}

@kernel checkSelCstZerInv config | exec
void checkSelCstZerInvRun(void) {
}

@emulate "sel_cst_zer_inv_2"
.kernel checkSelCstZerInv2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 0) ? 5 : 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top1) ? 5 : 0; }
  .pe2 { .write = write; .spad = (top1 & 0) ? (5 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 0)) ? 5 : 0; }
}

@kernel checkSelCstZerInv2 config | exec
void checkSelCstZerInv2Run(void) {
}

@emulate "sel_cst_zer_inv_3"
.kernel checkSelCstZerInv3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 1) ? -1 : 0; }
  .pe1 { .top = top; .write = write; .spad = (1 & top1) ? -1 : 0; }
  .pe2 { .write = write; .spad = (top1 & 1) ? (-1 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 1)) ? -1 : 0; }
}

@kernel checkSelCstZerInv3 config | exec
void checkSelCstZerInv3Run(void) {
}

@emulate "sel_cst_zer_inv_4"
.kernel checkSelCstZerInv4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 8388608) ? 8388607 : 0; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top1) ? 8388607 : 0; }
  .pe2 { .write = write; .spad = (top1 & 8388608) ? (8388607 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 8388608)) ? 8388607 : 0; }
}

@kernel checkSelCstZerInv4 config | exec
void checkSelCstZerInv4Run(void) {
}

@emulate "sel_cst_zer_inv_5"
.kernel checkSelCstZerInv5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & -1) ? -8388608 : 0; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top1) ? -8388608 : 0; }
  .pe2 { .write = write; .spad = (top1 & -1) ? (-8388608 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & -1)) ? -8388608 : 0; }
}

@kernel checkSelCstZerInv5 config | exec
void checkSelCstZerInv5Run(void) {
}

@emulate "sel_cst_zer_inv_6"
.kernel checkSelCstZerInv6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 5592405) ? 4660 : 0; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top1) ? 4660 : 0; }
  .pe2 { .write = write; .spad = (top1 & 5592405) ? (4660 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 5592405)) ? 4660 : 0; }
}

@kernel checkSelCstZerInv6 config | exec
void checkSelCstZerInv6Run(void) {
}

@emulate "shl_dyn"
.kernel checkShlDyn direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -5 << top1; }
  .pe1 { .top = top; .write = write; .spad = (-5) << top1; }
  .pe2 { .write = write; .spad = (-5 + 0) << top1; }
  .pe3 { .write = write; .spad = (-5) << (top1); }
}

@kernel checkShlDyn config | exec
void checkShlDynRun(void) {
}

@emulate "shl_dyn_2"
.kernel checkShlDyn2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0 << top1; }
  .pe1 { .top = top; .write = write; .spad = (0) << top1; }
  .pe2 { .write = write; .spad = (0 + 0) << top1; }
  .pe3 { .write = write; .spad = (0) << (top1); }
}

@kernel checkShlDyn2 config | exec
void checkShlDyn2Run(void) {
}

@emulate "shl_dyn_3"
.kernel checkShlDyn3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 1 << top1; }
  .pe1 { .top = top; .write = write; .spad = (1) << top1; }
  .pe2 { .write = write; .spad = (1 + 0) << top1; }
  .pe3 { .write = write; .spad = (1) << (top1); }
}

@kernel checkShlDyn3 config | exec
void checkShlDyn3Run(void) {
}

@emulate "shl_dyn_4"
.kernel checkShlDyn4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1 << top1; }
  .pe1 { .top = top; .write = write; .spad = (-1) << top1; }
  .pe2 { .write = write; .spad = (-1 + 0) << top1; }
  .pe3 { .write = write; .spad = (-1) << (top1); }
}

@kernel checkShlDyn4 config | exec
void checkShlDyn4Run(void) {
}

@emulate "shl_dyn_5"
.kernel checkShlDyn5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607 << top1; }
  .pe1 { .top = top; .write = write; .spad = (8388607) << top1; }
  .pe2 { .write = write; .spad = (8388607 + 0) << top1; }
  .pe3 { .write = write; .spad = (8388607) << (top1); }
}

@kernel checkShlDyn5 config | exec
void checkShlDyn5Run(void) {
}

@emulate "shl_dyn_6"
.kernel checkShlDyn6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608 << top1; }
  .pe1 { .top = top; .write = write; .spad = (-8388608) << top1; }
  .pe2 { .write = write; .spad = (-8388608 + 0) << top1; }
  .pe3 { .write = write; .spad = (-8388608) << (top1); }
}

@kernel checkShlDyn6 config | exec
void checkShlDyn6Run(void) {
}

@emulate "shr_dyn"
.kernel checkShrDyn direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -5 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (-5) >> top1; }
  .pe2 { .write = write; .spad = (-5 + 0) >> top1; }
  .pe3 { .write = write; .spad = (-5) >> (top1); }
}

@kernel checkShrDyn config | exec
void checkShrDynRun(void) {
}

@emulate "shr_dyn_2"
.kernel checkShrDyn2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (0) >> top1; }
  .pe2 { .write = write; .spad = (0 + 0) >> top1; }
  .pe3 { .write = write; .spad = (0) >> (top1); }
}

@kernel checkShrDyn2 config | exec
void checkShrDyn2Run(void) {
}

@emulate "shr_dyn_3"
.kernel checkShrDyn3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 1 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (1) >> top1; }
  .pe2 { .write = write; .spad = (1 + 0) >> top1; }
  .pe3 { .write = write; .spad = (1) >> (top1); }
}

@kernel checkShrDyn3 config | exec
void checkShrDyn3Run(void) {
}

@emulate "shr_dyn_4"
.kernel checkShrDyn4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (-1) >> top1; }
  .pe2 { .write = write; .spad = (-1 + 0) >> top1; }
  .pe3 { .write = write; .spad = (-1) >> (top1); }
}

@kernel checkShrDyn4 config | exec
void checkShrDyn4Run(void) {
}

@emulate "shr_dyn_5"
.kernel checkShrDyn5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (8388607) >> top1; }
  .pe2 { .write = write; .spad = (8388607 + 0) >> top1; }
  .pe3 { .write = write; .spad = (8388607) >> (top1); }
}

@kernel checkShrDyn5 config | exec
void checkShrDyn5Run(void) {
}

@emulate "shr_dyn_6"
.kernel checkShrDyn6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (-8388608) >> top1; }
  .pe2 { .write = write; .spad = (-8388608 + 0) >> top1; }
  .pe3 { .write = write; .spad = (-8388608) >> (top1); }
}

@kernel checkShrDyn6 config | exec
void checkShrDyn6Run(void) {
}

@emulate "shl_dyn_u"
.kernel checkShlDynU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 12582912 << top1; }
  .pe1 { .top = top; .write = write; .spad = (12582912) << top1; }
  .pe2 { .write = write; .spad = (12582912 + 0) << top1; }
  .pe3 { .write = write; .spad = (12582912) << (top1); }
}

@kernel checkShlDynU config | exec
void checkShlDynURun(void) {
}

@emulate "shl_dyn_u_2"
.kernel checkShlDynU2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388608 << top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608) << top1; }
  .pe2 { .write = write; .spad = (8388608 + 0) << top1; }
  .pe3 { .write = write; .spad = (8388608) << (top1); }
}

@kernel checkShlDynU2 config | exec
void checkShlDynU2Run(void) {
}

@emulate "shl_dyn_u_3"
.kernel checkShlDynU3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 16777215 << top1; }
  .pe1 { .top = top; .write = write; .spad = (16777215) << top1; }
  .pe2 { .write = write; .spad = (16777215 + 0) << top1; }
  .pe3 { .write = write; .spad = (16777215) << (top1); }
}

@kernel checkShlDynU3 config | exec
void checkShlDynU3Run(void) {
}

@emulate "shl_dyn_u_4"
.kernel checkShlDynU4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388609 << top1; }
  .pe1 { .top = top; .write = write; .spad = (8388609) << top1; }
  .pe2 { .write = write; .spad = (8388609 + 0) << top1; }
  .pe3 { .write = write; .spad = (8388609) << (top1); }
}

@kernel checkShlDynU4 config | exec
void checkShlDynU4Run(void) {
}

@emulate "shl_dyn_u_5"
.kernel checkShlDynU5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 11184810 << top1; }
  .pe1 { .top = top; .write = write; .spad = (11184810) << top1; }
  .pe2 { .write = write; .spad = (11184810 + 0) << top1; }
  .pe3 { .write = write; .spad = (11184810) << (top1); }
}

@kernel checkShlDynU5 config | exec
void checkShlDynU5Run(void) {
}

@emulate "shr_dyn_u"
.kernel checkShrDynU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 12582912 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (12582912) >> top1; }
  .pe2 { .write = write; .spad = (12582912 + 0) >> top1; }
  .pe3 { .write = write; .spad = (12582912) >> (top1); }
}

@kernel checkShrDynU config | exec
void checkShrDynURun(void) {
}

@emulate "shr_dyn_u_2"
.kernel checkShrDynU2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388608 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608) >> top1; }
  .pe2 { .write = write; .spad = (8388608 + 0) >> top1; }
  .pe3 { .write = write; .spad = (8388608) >> (top1); }
}

@kernel checkShrDynU2 config | exec
void checkShrDynU2Run(void) {
}

@emulate "shr_dyn_u_3"
.kernel checkShrDynU3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 16777215 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (16777215) >> top1; }
  .pe2 { .write = write; .spad = (16777215 + 0) >> top1; }
  .pe3 { .write = write; .spad = (16777215) >> (top1); }
}

@kernel checkShrDynU3 config | exec
void checkShrDynU3Run(void) {
}

@emulate "shr_dyn_u_4"
.kernel checkShrDynU4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388609 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (8388609) >> top1; }
  .pe2 { .write = write; .spad = (8388609 + 0) >> top1; }
  .pe3 { .write = write; .spad = (8388609) >> (top1); }
}

@kernel checkShrDynU4 config | exec
void checkShrDynU4Run(void) {
}

@emulate "shr_dyn_u_5"
.kernel checkShrDynU5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 11184810 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (11184810) >> top1; }
  .pe2 { .write = write; .spad = (11184810 + 0) >> top1; }
  .pe3 { .write = write; .spad = (11184810) >> (top1); }
}

@kernel checkShrDynU5 config | exec
void checkShrDynU5Run(void) {
}

@emulate "shl_reg"
.kernel checkShlReg direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << top0; }
  .pe1 { .top = top; .write = write; .spad = (top1 << top0); }
  .pe2 { .write = write; .spad = top1 << (top0); }
  .pe3 { .write = write; .spad = (top1) << (top0); }
}

@kernel checkShlReg config | exec
void checkShlRegRun(void) {
}

@emulate "shl_cst"
.kernel checkShlCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 3); }
  .pe2 { .write = write; .spad = top1 << (3 + 0); }
  .pe3 { .write = write; .spad = (top1) << 3; }
}

@kernel checkShlCst config | exec
void checkShlCstRun(void) {
}

@emulate "shl_cst_2"
.kernel checkShlCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 0; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 0); }
  .pe2 { .write = write; .spad = top1 << (0 + 0); }
  .pe3 { .write = write; .spad = (top1) << 0; }
}

@kernel checkShlCst2 config | exec
void checkShlCst2Run(void) {
}

@emulate "shl_cst_3"
.kernel checkShlCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 1; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 1); }
  .pe2 { .write = write; .spad = top1 << (1 + 0); }
  .pe3 { .write = write; .spad = (top1) << 1; }
}

@kernel checkShlCst3 config | exec
void checkShlCst3Run(void) {
}

@emulate "shl_cst_4"
.kernel checkShlCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 31; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 31); }
  .pe2 { .write = write; .spad = top1 << (31 + 0); }
  .pe3 { .write = write; .spad = (top1) << 31; }
}

@kernel checkShlCst4 config | exec
void checkShlCst4Run(void) {
}

@emulate "shl_cst_5"
.kernel checkShlCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << -1; }
  .pe1 { .top = top; .write = write; .spad = (top1 << -1); }
  .pe2 { .write = write; .spad = top1 << (-1 + 0); }
  .pe3 { .write = write; .spad = (top1) << -1; }
}

@kernel checkShlCst5 config | exec
void checkShlCst5Run(void) {
}

@emulate "shl_cst_6"
.kernel checkShlCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << -32; }
  .pe1 { .top = top; .write = write; .spad = (top1 << -32); }
  .pe2 { .write = write; .spad = top1 << (-32 + 0); }
  .pe3 { .write = write; .spad = (top1) << -32; }
}

@kernel checkShlCst6 config | exec
void checkShlCst6Run(void) {
}

@emulate "shl_cst_7"
.kernel checkShlCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 40; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 40); }
  .pe2 { .write = write; .spad = top1 << (40 + 0); }
  .pe3 { .write = write; .spad = (top1) << 40; }
}

@kernel checkShlCst7 config | exec
void checkShlCst7Run(void) {
}

@emulate "shr_reg"
.kernel checkShrReg direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >> top0; }
  .pe1 { .top = top; .write = write; .spad = (top1 >> top0); }
  .pe2 { .write = write; .spad = top1 >> (top0); }
  .pe3 { .write = write; .spad = (top1) >> (top0); }
}

@kernel checkShrReg config | exec
void checkShrRegRun(void) {
}

@emulate "shr_cst"
.kernel checkShrCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 3); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 3)); }
  .pe2 { .write = write; .spad = shrcst(top1, 3 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 3); }
}

@kernel checkShrCst config | exec
void checkShrCstRun(void) {
}

@emulate "shr_cst_2"
.kernel checkShrCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 0); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 0)); }
  .pe2 { .write = write; .spad = shrcst(top1, 0 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 0); }
}

@kernel checkShrCst2 config | exec
void checkShrCst2Run(void) {
}

@emulate "shr_cst_3"
.kernel checkShrCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 1); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 1)); }
  .pe2 { .write = write; .spad = shrcst(top1, 1 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 1); }
}

@kernel checkShrCst3 config | exec
void checkShrCst3Run(void) {
}

@emulate "shr_cst_4"
.kernel checkShrCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 31); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 31)); }
  .pe2 { .write = write; .spad = shrcst(top1, 31 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 31); }
}

@kernel checkShrCst4 config | exec
void checkShrCst4Run(void) {
}

@emulate "shr_cst_5"
.kernel checkShrCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, -1); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, -1)); }
  .pe2 { .write = write; .spad = shrcst(top1, -1 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), -1); }
}

@kernel checkShrCst5 config | exec
void checkShrCst5Run(void) {
}

@emulate "shr_cst_6"
.kernel checkShrCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, -32); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, -32)); }
  .pe2 { .write = write; .spad = shrcst(top1, -32 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), -32); }
}

@kernel checkShrCst6 config | exec
void checkShrCst6Run(void) {
}

@emulate "shr_cst_7"
.kernel checkShrCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 40); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 40)); }
  .pe2 { .write = write; .spad = shrcst(top1, 40 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 40); }
}

@kernel checkShrCst7 config | exec
void checkShrCst7Run(void) {
}

@emulate "shl_reg_u"
.kernel checkShlRegU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< top0; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< top0); }
  .pe2 { .write = write; .spad = top1 <<< (top0); }
  .pe3 { .write = write; .spad = (top1) <<< (top0); }
}

@kernel checkShlRegU config | exec
void checkShlRegURun(void) {
}

@emulate "shl_cst_u"
.kernel checkShlCstU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 3); }
  .pe2 { .write = write; .spad = top1 <<< (3 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< 3; }
}

@kernel checkShlCstU config | exec
void checkShlCstURun(void) {
}

@emulate "shl_cst_u_2"
.kernel checkShlCstU2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 0; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 0); }
  .pe2 { .write = write; .spad = top1 <<< (0 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< 0; }
}

@kernel checkShlCstU2 config | exec
void checkShlCstU2Run(void) {
}

@emulate "shl_cst_u_3"
.kernel checkShlCstU3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 1; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 1); }
  .pe2 { .write = write; .spad = top1 <<< (1 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< 1; }
}

@kernel checkShlCstU3 config | exec
void checkShlCstU3Run(void) {
}

@emulate "shl_cst_u_4"
.kernel checkShlCstU4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 31; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 31); }
  .pe2 { .write = write; .spad = top1 <<< (31 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< 31; }
}

@kernel checkShlCstU4 config | exec
void checkShlCstU4Run(void) {
}

@emulate "shl_cst_u_5"
.kernel checkShlCstU5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< -1; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< -1); }
  .pe2 { .write = write; .spad = top1 <<< (-1 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< -1; }
}

@kernel checkShlCstU5 config | exec
void checkShlCstU5Run(void) {
}

@emulate "shl_cst_u_6"
.kernel checkShlCstU6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< -32; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< -32); }
  .pe2 { .write = write; .spad = top1 <<< (-32 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< -32; }
}

@kernel checkShlCstU6 config | exec
void checkShlCstU6Run(void) {
}

@emulate "shr_reg_u"
.kernel checkShrRegU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> top0; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> top0); }
  .pe2 { .write = write; .spad = top1 >>> (top0); }
  .pe3 { .write = write; .spad = (top1) >>> (top0); }
}

@kernel checkShrRegU config | exec
void checkShrRegURun(void) {
}

@emulate "shr_cst_u"
.kernel checkShrCstU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 3); }
  .pe2 { .write = write; .spad = top1 >>> (3 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> 3; }
}

@kernel checkShrCstU config | exec
void checkShrCstURun(void) {
}

@emulate "shr_cst_u_2"
.kernel checkShrCstU2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 0; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 0); }
  .pe2 { .write = write; .spad = top1 >>> (0 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> 0; }
}

@kernel checkShrCstU2 config | exec
void checkShrCstU2Run(void) {
}

@emulate "shr_cst_u_3"
.kernel checkShrCstU3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 1; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 1); }
  .pe2 { .write = write; .spad = top1 >>> (1 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> 1; }
}

@kernel checkShrCstU3 config | exec
void checkShrCstU3Run(void) {
}

@emulate "shr_cst_u_4"
.kernel checkShrCstU4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 31; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 31); }
  .pe2 { .write = write; .spad = top1 >>> (31 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> 31; }
}

@kernel checkShrCstU4 config | exec
void checkShrCstU4Run(void) {
}

@emulate "shr_cst_u_5"
.kernel checkShrCstU5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> -1; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> -1); }
  .pe2 { .write = write; .spad = top1 >>> (-1 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> -1; }
}

@kernel checkShrCstU5 config | exec
void checkShrCstU5Run(void) {
}

@emulate "shr_cst_u_6"
.kernel checkShrCstU6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> -32; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> -32); }
  .pe2 { .write = write; .spad = top1 >>> (-32 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> -32; }
}

@kernel checkShrCstU6 config | exec
void checkShrCstU6Run(void) {
}

@emulate "and"
.kernel checkAnd direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 & top1; }
  .pe1 { .top = top; .write = write; .spad = top1 & top0; }
  .pe2 { .write = write; .spad = (top0 & top1); }
  .pe3 { .write = write; .spad = top0 & (top1); }
}

@kernel checkAnd config | exec
void checkAndRun(void) {
}

@emulate "and_cst"
.kernel checkAndCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 255; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 255); }
  .pe2 { .write = write; .spad = 255 & top1; }
  .pe3 { .write = write; .spad = (top1 & 255); }
}

@kernel checkAndCst config | exec
void checkAndCstRun(void) {
}

@emulate "and_cst_2"
.kernel checkAndCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 0; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 0); }
  .pe2 { .write = write; .spad = 0 & top1; }
  .pe3 { .write = write; .spad = (top1 & 0); }
}

@kernel checkAndCst2 config | exec
void checkAndCst2Run(void) {
}

@emulate "and_cst_3"
.kernel checkAndCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & -1; }
  .pe1 { .top = top; .write = write; .spad = and(top1, -1); }
  .pe2 { .write = write; .spad = -1 & top1; }
  .pe3 { .write = write; .spad = (top1 & -1); }
}

@kernel checkAndCst3 config | exec
void checkAndCst3Run(void) {
}

@emulate "and_cst_4"
.kernel checkAndCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 8388607; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 8388607); }
  .pe2 { .write = write; .spad = 8388607 & top1; }
  .pe3 { .write = write; .spad = (top1 & 8388607); }
}

@kernel checkAndCst4 config | exec
void checkAndCst4Run(void) {
}

@emulate "and_cst_5"
.kernel checkAndCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 8388608; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 8388608); }
  .pe2 { .write = write; .spad = 8388608 & top1; }
  .pe3 { .write = write; .spad = (top1 & 8388608); }
}

@kernel checkAndCst5 config | exec
void checkAndCst5Run(void) {
}

@emulate "and_cst_6"
.kernel checkAndCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 5592405; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 5592405); }
  .pe2 { .write = write; .spad = 5592405 & top1; }
  .pe3 { .write = write; .spad = (top1 & 5592405); }
}

@kernel checkAndCst6 config | exec
void checkAndCst6Run(void) {
}

@emulate "nand"
.kernel checkNand direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 & top1); }
  .pe1 { .top = top; .write = write; .spad = ~(top1 & top0); }
  .pe2 { .write = write; .spad = (~(top0 & top1)); }
  .pe3 { .write = write; .spad = ~(top0 & (top1)); }
}

@kernel checkNand config | exec
void checkNandRun(void) {
}

@emulate "nand_cst"
.kernel checkNandCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 255); }
  .pe2 { .write = write; .spad = ~(255 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 255)); }
}

@kernel checkNandCst config | exec
void checkNandCstRun(void) {
}

@emulate "nand_cst_2"
.kernel checkNandCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 0); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 0); }
  .pe2 { .write = write; .spad = ~(0 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 0)); }
}

@kernel checkNandCst2 config | exec
void checkNandCst2Run(void) {
}

@emulate "nand_cst_3"
.kernel checkNandCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & -1); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, -1); }
  .pe2 { .write = write; .spad = ~(-1 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & -1)); }
}

@kernel checkNandCst3 config | exec
void checkNandCst3Run(void) {
}

@emulate "nand_cst_4"
.kernel checkNandCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 8388607); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 8388607); }
  .pe2 { .write = write; .spad = ~(8388607 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 8388607)); }
}

@kernel checkNandCst4 config | exec
void checkNandCst4Run(void) {
}

@emulate "nand_cst_5"
.kernel checkNandCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 8388608); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 8388608); }
  .pe2 { .write = write; .spad = ~(8388608 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 8388608)); }
}

@kernel checkNandCst5 config | exec
void checkNandCst5Run(void) {
}

@emulate "nand_cst_6"
.kernel checkNandCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 5592405); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 5592405); }
  .pe2 { .write = write; .spad = ~(5592405 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 5592405)); }
}

@kernel checkNandCst6 config | exec
void checkNandCst6Run(void) {
}

@emulate "or"
.kernel checkOr direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 | top1; }
  .pe1 { .top = top; .write = write; .spad = top1 | top0; }
  .pe2 { .write = write; .spad = (top0 | top1); }
  .pe3 { .write = write; .spad = top0 | (top1); }
}

@kernel checkOr config | exec
void checkOrRun(void) {
}

@emulate "or_cst"
.kernel checkOrCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | 0x80; }
  .pe1 { .top = top; .write = write; .spad = or(top1, 0x80); }
  .pe2 { .write = write; .spad = 0x80 | top1; }
  .pe3 { .write = write; .spad = (top1 | 128); }
}

@kernel checkOrCst config | exec
void checkOrCstRun(void) {
}

@emulate "nor"
.kernel checkNor direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 | top1); }
  .pe1 { .top = top; .write = write; .spad = ~(top1 | top0); }
  .pe2 { .write = write; .spad = (~(top0 | top1)); }
  .pe3 { .write = write; .spad = ~(top0 | (top1)); }
}

@kernel checkNor config | exec
void checkNorRun(void) {
}

@emulate "nor_cst"
.kernel checkNorCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | 0x80); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, 0x80); }
  .pe2 { .write = write; .spad = ~(0x80 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | 128)); }
}

@kernel checkNorCst config | exec
void checkNorCstRun(void) {
}

@emulate "xor"
.kernel checkXor direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 ^ top1; }
  .pe1 { .top = top; .write = write; .spad = top1 ^ top0; }
  .pe2 { .write = write; .spad = (top0 ^ top1); }
  .pe3 { .write = write; .spad = top0 ^ (top1); }
}

@kernel checkXor config | exec
void checkXorRun(void) {
}

@emulate "xor_cst"
.kernel checkXorCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ 0x55; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, 0x55); }
  .pe2 { .write = write; .spad = 0x55 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ 85); }
}

@kernel checkXorCst config | exec
void checkXorCstRun(void) {
}

@emulate "xnor"
.kernel checkXnor direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 ^ top1); }
  .pe1 { .top = top; .write = write; .spad = ~(top1 ^ top0); }
  .pe2 { .write = write; .spad = (~(top0 ^ top1)); }
  .pe3 { .write = write; .spad = ~(top0 ^ (top1)); }
}

@kernel checkXnor config | exec
void checkXnorRun(void) {
}

@emulate "xnor_cst"
.kernel checkXnorCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ 0x55); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, 0x55); }
  .pe2 { .write = write; .spad = ~(0x55 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ 85)); }
}

@kernel checkXnorCst config | exec
void checkXnorCstRun(void) {
}

@emulate "tst_em1"
.kernel checkTstEm1 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 == -1; }
  .pe1 { .top = top; .write = write; .spad = top1 == 0xffffff; }
  .pe2 { .write = write; .spad = (top1 == -1); }
  .pe3 { .write = write; .spad = (top1) == -1; }
}

@kernel checkTstEm1 config | exec
void checkTstEm1Run(void) {
}

@emulate "tst_nnz"
.kernel checkTstNnz direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 != 0; }
  .pe1 { .top = top; .write = write; .spad = (top1 != 0); }
  .pe2 { .write = write; .spad = (top1) != 0; }
  .pe3 { .write = write; .spad = top1 != (0); }
}

@kernel checkTstNnz config | exec
void checkTstNnzRun(void) {
}

@emulate "tst_par"
.kernel checkTstPar direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = parity(top1); }
  .pe1 { .top = top; .write = write; .spad = (parity(top1)); }
  .pe2 { .write = write; .spad = parity( top1 ); }
  .pe3 { .write = write; .spad = parity((top1)); }
}

@kernel checkTstPar config | exec
void checkTstParRun(void) {
}

@emulate "not"
.kernel checkNot direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~top1; }
  .pe1 { .top = top; .write = write; .spad = (~top1); }
  .pe2 { .write = write; .spad = ~(top1); }
  .pe3 { .write = write; .spad = (~(top1)); }
}

@kernel checkNot config | exec
void checkNotRun(void) {
}
