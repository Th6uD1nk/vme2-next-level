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

volatile Buffer bit6MulTopA[16] = {
  0x00080000, 0x00080000, 0x00080000, 0x00080000,
  0x00080000, 0x00080000, 0x00080000, 0x00080000,
  0x00080000, 0x00080000, 0x00080000, 0x00080000,
  0x00080000, 0x00080000, 0x00080000, 0x00080000,
};

volatile Buffer bit6MulBaseA[16] = {
  0xfffffff8, 0xfffffff9, 0xfffffffa, 0xfffffffb,
  0xfffffffc, 0xfffffffd, 0xfffffffe, 0xffffffff,
  0x00000000, 0x00000001, 0x00000002, 0x00000003,
  0x00000004, 0x00000005, 0x00000006, 0x00000007,
};

volatile Buffer bit6MulTopB[16] = {
  0x000b504f, 0xfff4afb1, 0x000ec835, 0xfff9e088,
  0x00100000, 0xfff00000, 0x00080000, 0xfff80000,
  0x00040000, 0xfffc0000, 0x000ddb3d, 0xfff224c3,
  0x00000000, 0x00019999, 0xfffe6667, 0x007ffffe,
};

volatile Buffer bit6MulBaseB[16] = {
  0x00100000, 0x00100000, 0x00080000, 0xffe00000,
  0x00340000, 0xffcc0000, 0x000b504f, 0xfff4afb1,
  0x00055555, 0xfffaaaab, 0x00180000, 0xffe80000,
  0x00200000, 0x00780000, 0xff880000, 0xfff00000,
};

@emulate "fu-bit6-fft-mul"
.kernel checkBit6FftMul direct {
  Int count = 16 - 1;

  Transfer topATransfer = { memory: bit6MulTopA, count };
  Transfer baseATransfer = { memory: bit6MulBaseA, count };
  Transfer topBTransfer = { memory: bit6MulTopB, count };
  Transfer baseBTransfer = { memory: bit6MulBaseB, count };

  .load { .transfer = topATransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; } }
  .load { .transfer = baseATransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; } }
  .load { .transfer = topBTransfer; .scope = global; .offsets { .top2 = 0; .top3 = 0; } }
  .load { .transfer = baseBTransfer; .scope = global; .offsets { .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; .spad = zsm(top0 * base0 >> 20); }
  .pe1 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; .spad = top1 * base1 >> 20; }
  .pe2 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; .spad = zsm(top2 * base2 >> 20); }
  .pe3 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; .spad = top3 * base3 >> 20; }
}

@kernel checkBit6FftMul config | exec
void checkBit6FftMulRun(void) {
}

volatile Buffer bit6LegTop[16] = {
  0x000b504f, 0xfff4afb1, 0x0007ffff, 0xfff80001,
  0x000fffff, 0xfff00001, 0x0037ffff, 0xffc80001,
  0x00000001, 0xffffffff, 0x00000003, 0xfffffffd,
  0x0001e241, 0xfffe1dbf, 0x000f423f, 0xfff0bdc1,
};

volatile Buffer bit6LegBase[16] = {
  0x000b504e, 0x000b504f, 0x00080000, 0xfff7ffff,
  0x00000001, 0xfffffffe, 0x00380000, 0x0037ffff,
  0x00000000, 0x00000000, 0x00000002, 0xfffffffe,
  0x0001e240, 0x0001e241, 0x000f4240, 0xfff0bdc0,
};

@emulate "fu-bit6-fft-legs"
.kernel checkBit6FftLegs direct {
  Int count = 16 - 1;

  Transfer topTransfer = { memory: bit6LegTop, count };
  Transfer baseTransfer = { memory: bit6LegBase, count };

  .load { .transfer = topTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; .top2 = 0; .top3 = 0; } }
  .load { .transfer = baseTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(top0 + base0 >> 1); }
  .pe1 { .top = top; .base = base; .write = write; .spad = top1 + base1 >> 1; }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(top2 - base2 >> 1); }
  .pe3 { .top = top; .base = base; .write = write; .spad = top3 - base3 >> 1; }
}

@kernel checkBit6FftLegs config | exec
void checkBit6FftLegsRun(void) {
}

@emulate "fu-bit6-fft-noshift"
.kernel checkBit6FftNoShift direct {
  Int count = 16 - 1;

  Transfer topTransfer = { memory: bit6LegTop, count };
  Transfer baseTransfer = { memory: bit6LegBase, count };

  .load { .transfer = topTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; .top2 = 0; .top3 = 0; } }
  .load { .transfer = baseTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(top0 + base0); }
  .pe1 { .top = top; .base = base; .write = write; .spad = top1 + base1; }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(top2 - base2); }
  .pe3 { .top = top; .base = base; .write = write; .spad = top3 - base3; }
}

@kernel checkBit6FftNoShift config | exec
void checkBit6FftNoShiftRun(void) {
}

volatile Buffer bit6ChainTop0[16] = {
  0x00080000, 0xfff80000, 0x00180000, 0xffe80000,
  0x000b504f, 0xfff4afb1, 0x00040000, 0xfffc0000,
  0x00100000, 0xfff00000, 0x00055555, 0xfffaaaab,
  0x0013c0ca, 0xffec3f36, 0x00019999, 0xfffe6667,
};

volatile Buffer bit6ChainBase0[16] = {
  0x00100000, 0x00100000, 0x00080000, 0x00080000,
  0x0016a09e, 0x0016a09e, 0x000c0000, 0x000c0000,
  0x00140000, 0x00140000, 0x000aaaaa, 0x000aaaaa,
  0x000e6666, 0x000e6666, 0xffee6667, 0x00119999,
};

volatile Buffer bit6ChainTop1[16] = {
  0x00080000, 0x00040000, 0xfff80000, 0xfffc0000,
  0x00100000, 0x000ddb3d, 0xfff224c3, 0x00019999,
  0x00055555, 0x00180000, 0xffe80000, 0x000b504f,
  0xfff4afb1, 0x000ffffe, 0xfff00002, 0x00000000,
};

volatile Buffer bit6ChainBase1[16] = {
  0x00080000, 0x00100000, 0x00100000, 0x00080000,
  0x000c0000, 0x000c0000, 0x00140000, 0x00140000,
  0x0016a09e, 0x000e6666, 0x000e6666, 0x00119999,
  0x00119999, 0x000553f7, 0x000553f7, 0x00100000,
};

@emulate "fu-bit6-fft-chain"
.kernel checkBit6FftChain direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: bit6ChainTop0, count };
  Transfer base0Transfer = { memory: bit6ChainBase0, count };
  Transfer top1Transfer = { memory: bit6ChainTop1, count };
  Transfer base1Transfer = { memory: bit6ChainBase1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; .top2 = 0; } }
  .load { .transfer = base0Transfer; .scope = global; .offsets { .base0 = 16; .base2 = 16; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; .top3 = 0; } }
  .load { .transfer = base1Transfer; .scope = global; .offsets { .base1 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  Staging onReal, onImag, offReal, offImag;

  .pe0 { .top = top; .base = base; .remap = { operator: "*", primary: 0x220 }; onReal = zsm(top0 * base0 >> 20); }
  .pe1 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; onImag = zsm(top1 * base1 >> 20); .spad = zsm(onReal - onImag >> 1); }
  .pe2 { .top = top; .base = base; .remap = { operator: "*", primary: 0x220 }; offReal = top2 * base2 >> 20; }
  .pe3 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; offImag = top3 * base3 >> 20; .spad = offReal - offImag >> 1; }
}

@kernel checkBit6FftChain config | exec
void checkBit6FftChainRun(void) {
}

@emulate "fu-bit6-fft-chain-split"
.kernel checkBit6FftChainSplit direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: bit6ChainTop0, count };
  Transfer base0Transfer = { memory: bit6ChainBase0, count };
  Transfer top1Transfer = { memory: bit6ChainTop1, count };
  Transfer base1Transfer = { memory: bit6ChainBase1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; .top2 = 0; } }
  .load { .transfer = base0Transfer; .scope = global; .offsets { .base0 = 16; .base2 = 16; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; .top3 = 0; } }
  .load { .transfer = base1Transfer; .scope = global; .offsets { .base1 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  Staging firstReal, firstImag, secondReal, secondImag;

  .pe0 { .top = top; .base = base; .remap = { operator: "*", primary: 0x220 }; firstReal = zsm(top0 * base0 >> 20); }
  .pe1 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; firstImag = zsm(top1 * base1 >> 20); .spad = firstReal - firstImag >> 1; }
  .pe2 { .top = top; .base = base; .remap = { operator: "*", primary: 0x220 }; secondReal = top2 * base2 >> 20; }
  .pe3 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; secondImag = top3 * base3 >> 20; .spad = zsm(secondReal - secondImag >> 1); }
}

@kernel checkBit6FftChainSplit config | exec
void checkBit6FftChainSplitRun(void) {
}

volatile Buffer bit6RampPos[16] = {
  0x00000000, 0x00000001, 0x00000002, 0x00000003,
  0x00000004, 0x00000005, 0x00000006, 0x00000007,
  0x00000008, 0x00000009, 0x0000000a, 0x0000000b,
  0x0000000c, 0x0000000d, 0x0000000e, 0x0000000f,
};

volatile Buffer bit6RampNeg[16] = {
  0x00000000, 0xffffffff, 0xfffffffe, 0xfffffffd,
  0xfffffffc, 0xfffffffb, 0xfffffffa, 0xfffffff9,
  0xfffffff8, 0xfffffff7, 0xfffffff6, 0xfffffff5,
  0xfffffff4, 0xfffffff3, 0xfffffff2, 0xfffffff1,
};

@emulate "fu-bit6-shift-2"
.kernel checkBit6Shift2 direct {
  Int count = 16 - 1;

  Transfer posTransfer = { memory: bit6RampPos, count };
  Transfer negTransfer = { memory: bit6RampNeg, count };
  Transfer zeroTransfer = { memory: bit6Base0, count };

  .load { .transfer = posTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; } }
  .load { .transfer = negTransfer; .scope = global; .offsets { .top2 = 0; .top3 = 0; } }
  .load { .transfer = zeroTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(top0 + base0 >> 2); }
  .pe1 { .top = top; .base = base; .write = write; .spad = top1 + base1 >> 2; }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(top2 + base2 >> 2); }
  .pe3 { .top = top; .base = base; .write = write; .spad = top3 + base3 >> 2; }
}

@kernel checkBit6Shift2 config | exec
void checkBit6Shift2Run(void) {
}

@emulate "fu-bit6-shift-3"
.kernel checkBit6Shift3 direct {
  Int count = 16 - 1;

  Transfer posTransfer = { memory: bit6RampPos, count };
  Transfer negTransfer = { memory: bit6RampNeg, count };
  Transfer zeroTransfer = { memory: bit6Base0, count };

  .load { .transfer = posTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; } }
  .load { .transfer = negTransfer; .scope = global; .offsets { .top2 = 0; .top3 = 0; } }
  .load { .transfer = zeroTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(top0 + base0 >> 3); }
  .pe1 { .top = top; .base = base; .write = write; .spad = top1 + base1 >> 3; }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(top2 + base2 >> 3); }
  .pe3 { .top = top; .base = base; .write = write; .spad = top3 + base3 >> 3; }
}

@kernel checkBit6Shift3 config | exec
void checkBit6Shift3Run(void) {
}

volatile Buffer bit6Shift8Pos[16] = {
  0x00000000, 0x00000001, 0x0000007f, 0x00000080,
  0x00000081, 0x000000ff, 0x00000100, 0x00000101,
  0x0000017f, 0x00000180, 0x00000181, 0x000001ff,
  0x00000200, 0x00000201, 0x00000280, 0x000003e8,
};

volatile Buffer bit6Shift8Neg[16] = {
  0x00000000, 0xffffffff, 0xffffff81, 0xffffff80,
  0xffffff7f, 0xffffff01, 0xffffff00, 0xfffffeff,
  0xfffffe81, 0xfffffe80, 0xfffffe7f, 0xfffffe01,
  0xfffffe00, 0xfffffdff, 0xfffffd80, 0xfffffc18,
};

@emulate "fu-bit6-shift-8"
.kernel checkBit6Shift8 direct {
  Int count = 16 - 1;

  Transfer posTransfer = { memory: bit6Shift8Pos, count };
  Transfer negTransfer = { memory: bit6Shift8Neg, count };
  Transfer zeroTransfer = { memory: bit6Base0, count };

  .load { .transfer = posTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; } }
  .load { .transfer = negTransfer; .scope = global; .offsets { .top2 = 0; .top3 = 0; } }
  .load { .transfer = zeroTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(top0 + base0 >> 8); }
  .pe1 { .top = top; .base = base; .write = write; .spad = top1 + base1 >> 8; }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(top2 + base2 >> 8); }
  .pe3 { .top = top; .base = base; .write = write; .spad = top3 + base3 >> 8; }
}

@kernel checkBit6Shift8 config | exec
void checkBit6Shift8Run(void) {
}

volatile Buffer bit6LimitAddTop[16] = {
  0x007fffff, 0x007fffff, 0x007ffffe, 0x007ffffd,
  0x007fffff, 0x007fffff, 0x00000001, 0xff800000,
  0xff800000, 0xff800001, 0xff800000, 0xff800002,
  0xff800000, 0x00400000, 0x003fffff, 0xffc00000,
};

volatile Buffer bit6LimitAddBase[16] = {
  0x007fffff, 0x007ffffe, 0x007fffff, 0x007fffff,
  0x00000001, 0x00000000, 0x007fffff, 0xff800000,
  0xff800001, 0xff800000, 0x00000001, 0xff800001,
  0xffffffff, 0x00400000, 0x00400001, 0xffc00000,
};

volatile Buffer bit6LimitMulTop[16] = {
  0x007fffff, 0x007fffff, 0xff800000, 0xff800000,
  0x00400000, 0xffc00000, 0x002d413d, 0x002d413c,
  0x002d413d, 0xffd2bec3, 0x00100000, 0xfff00000,
  0x007fffff, 0x00000001, 0xffffffff, 0x00123456,
};

volatile Buffer bit6LimitMulBase[16] = {
  0x007fffff, 0xff800000, 0xff800000, 0x007fffff,
  0x00400000, 0x00400000, 0x002d413d, 0x002d413c,
  0xffd2bec3, 0xffd2bec3, 0x00100000, 0x00100000,
  0x007fffff, 0x007fffff, 0x007fffff, 0xffedcbaa,
};

@emulate "fu-bit6-limits"
.kernel checkBit6Limits direct {
  Int count = 16 - 1;

  Transfer addTopTransfer = { memory: bit6LimitAddTop, count };
  Transfer addBaseTransfer = { memory: bit6LimitAddBase, count };
  Transfer mulTopTransfer = { memory: bit6LimitMulTop, count };
  Transfer mulBaseTransfer = { memory: bit6LimitMulBase, count };

  .load { .transfer = addTopTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; } }
  .load { .transfer = addBaseTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; } }
  .load { .transfer = mulTopTransfer; .scope = global; .offsets { .top2 = 0; .top3 = 0; } }
  .load { .transfer = mulBaseTransfer; .scope = global; .offsets { .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(top0 + base0 >> 1); }
  .pe1 { .top = top; .base = base; .write = write; .spad = top1 + base1 >> 1; }
  .pe2 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; .spad = zsm(top2 * base2 >> 20); }
  .pe3 { .top = top; .base = base; .write = write; .remap = { operator: "*", primary: 0x220 }; .spad = top3 * base3 >> 20; }
}

@kernel checkBit6Limits config | exec
void checkBit6LimitsRun(void) {
}

volatile Buffer bit6SatShift1[16] = {
  0x000007fe, 0x000007ff, 0x00000800, 0x00000801,
  0x00000802, 0x00000ffd, 0x00000ffe, 0x00000fff,
  0x00001000, 0x00001001, 0xfffff801, 0xfffff800,
  0xfffff7ff, 0xfffff7fe, 0xfffff001, 0xffffefff,
};

volatile Buffer bit6SatShift2[16] = {
  0x000007fe, 0x000007ff, 0x00000800, 0x00000802,
  0x00000803, 0x00001ffb, 0x00001ffc, 0x00001ffd,
  0x00001ffe, 0x00001fff, 0x00002000, 0xfffff800,
  0xfffff7ff, 0xfffff7fd, 0xffffe000, 0xffffdffe,
};

@emulate "fu-bit6-limits-sat"
.kernel checkBit6LimitsSat direct {
  Int count = 16 - 1;

  Transfer shift1Transfer = { memory: bit6SatShift1, count };
  Transfer shift2Transfer = { memory: bit6SatShift2, count };
  Transfer zeroTransfer = { memory: bit6Base0, count };

  .load { .transfer = shift1Transfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; } }
  .load { .transfer = shift2Transfer; .scope = global; .offsets { .top2 = 0; .top3 = 0; } }
  .load { .transfer = zeroTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(sat(top0 + base0, 12) >> 1); }
  .pe1 { .top = top; .base = base; .write = write; .spad = sat(top1 + base1, 12) >> 1; }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(sat(top2 + base2, 12) >> 2); }
  .pe3 { .top = top; .base = base; .write = write; .spad = sat(top3 + base3, 12) >> 2; }
}

@kernel checkBit6LimitsSat config | exec
void checkBit6LimitsSatRun(void) {
}

@emulate "fu-bit6-sub-ofb-k0"
.kernel checkBit6SubOfbK0 direct {
  Int count = 16 - 1;

  Transfer topTransfer = { memory: bit6LegTop, count };
  Transfer baseTransfer = { memory: bit6LegBase, count };

  .load { .transfer = topTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; .top2 = 0; .top3 = 0; } }
  .load { .transfer = baseTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(top0 - base0 + 7); }
  .pe1 { .top = top; .base = base; .write = write; .spad = top1 - base1 + 7; }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(subacst(top2, base2, -7)); }
  .pe3 { .top = top; .base = base; .write = write; .spad = subacst(top3, base3, -7); }
}

@kernel checkBit6SubOfbK0 config | exec
void checkBit6SubOfbK0Run(void) {
}

@emulate "fu-bit6-sub-ofb-k1"
.kernel checkBit6SubOfbK1 direct {
  Int count = 16 - 1;

  Transfer topTransfer = { memory: bit6LegTop, count };
  Transfer baseTransfer = { memory: bit6LegBase, count };

  .load { .transfer = topTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; .top2 = 0; .top3 = 0; } }
  .load { .transfer = baseTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(subacst(top0, base0, 7) >> 1); }
  .pe1 { .top = top; .base = base; .write = write; .spad = subacst(top1, base1, 7) >> 1; }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(subacst(top2, base2, -7) >> 1); }
  .pe3 { .top = top; .base = base; .write = write; .spad = subacst(top3, base3, -7) >> 1; }
}

@kernel checkBit6SubOfbK1 config | exec
void checkBit6SubOfbK1Run(void) {
}

@emulate "fu-bit6-sub-inv-k0"
.kernel checkBit6SubInvK0 direct {
  Int count = 16 - 1;

  Transfer topTransfer = { memory: bit6LegTop, count };
  Transfer baseTransfer = { memory: bit6LegBase, count };

  .load { .transfer = topTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; .top2 = 0; .top3 = 0; } }
  .load { .transfer = baseTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .remap = { operator: "+", primary: 0x034 }; .spad = zsm(subacst(top0, base0, 7)); }
  .pe1 { .top = top; .base = base; .write = write; .remap = { operator: "+", primary: 0x034 }; .spad = subacst(top1, base1, 7); }
  .pe2 { .top = top; .base = base; .write = write; .remap = { operator: "+", primary: 0x034 }; .spad = zsm(subacst(top2, base2, -7)); }
  .pe3 { .top = top; .base = base; .write = write; .remap = { operator: "+", primary: 0x034 }; .spad = subacst(top3, base3, -7); }
}

@kernel checkBit6SubInvK0 config | exec
void checkBit6SubInvK0Run(void) {
}

@emulate "fu-bit6-sub-inv-k1"
.kernel checkBit6SubInvK1 direct {
  Int count = 16 - 1;

  Transfer topTransfer = { memory: bit6LegTop, count };
  Transfer baseTransfer = { memory: bit6LegBase, count };

  .load { .transfer = topTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; .top2 = 0; .top3 = 0; } }
  .load { .transfer = baseTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .remap = { operator: "+", primary: 0x034 }; .spad = zsm(subacst(top0, base0, 7) >> 1); }
  .pe1 { .top = top; .base = base; .write = write; .remap = { operator: "+", primary: 0x034 }; .spad = subacst(top1, base1, 7) >> 1; }
  .pe2 { .top = top; .base = base; .write = write; .remap = { operator: "+", primary: 0x034 }; .spad = zsm(subacst(top2, base2, -7) >> 1); }
  .pe3 { .top = top; .base = base; .write = write; .remap = { operator: "+", primary: 0x034 }; .spad = subacst(top3, base3, -7) >> 1; }
}

@kernel checkBit6SubInvK1 config | exec
void checkBit6SubInvK1Run(void) {
}

@emulate "fu-bit6-sub-shr-a"
.kernel checkBit6SubShrA direct {
  Int count = 16 - 1;

  Transfer topTransfer = { memory: bit6LegTop, count };
  Transfer baseTransfer = { memory: bit6LegBase, count };

  .load { .transfer = topTransfer; .scope = global; .offsets { .top0 = 0; .top1 = 0; .top2 = 0; .top3 = 0; } }
  .load { .transfer = baseTransfer; .scope = global; .offsets { .base0 = 16; .base1 = 16; .base2 = 16; .base3 = 16; } }

  Agu top = { count };
  Agu base = { count, offset: 16 };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .base = base; .write = write; .spad = zsm(subshr(top0, base0, 2)); }
  .pe1 { .top = top; .base = base; .write = write; .spad = subshr(top1, base1, 2); }
  .pe2 { .top = top; .base = base; .write = write; .spad = zsm(subshr(top2, base2, 2) >> 1); }
  .pe3 { .top = top; .base = base; .write = write; .spad = subshr(top3, base3, 2) >> 1; }
}

@kernel checkBit6SubShrA config | exec
void checkBit6SubShrARun(void) {
}
