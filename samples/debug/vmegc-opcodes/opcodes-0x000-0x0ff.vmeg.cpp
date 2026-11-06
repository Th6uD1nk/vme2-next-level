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

@emulate "add_shf"
.kernel checkAddShf direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 3); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 3) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 1 + 2); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 3); }
}

@kernel checkAddShf config | exec
void checkAddShfRun(void) {
}

@emulate "shr_cst_ofa"
.kernel checkShrCstOfa direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 3) + 5; }
  .pe1 { .top = top; .write = write; .spad = 5 + (top1 >> 3); }
  .pe2 { .write = write; .spad = ((top1 >> 3)) + 5; }
  .pe3 { .write = write; .spad = (top1 >> 3) + (2 + 3); }
}

@kernel checkShrCstOfa config | exec
void checkShrCstOfaRun(void) {
}

@emulate "subshr"
.kernel checkSubshr direct {
  Int count = 16 - 1;

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

@emulate "shr_cst_neg_ofa"
.kernel checkShrCstNegOfa direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 5 - (top1 >> 3); }
  .pe1 { .top = top; .write = write; .spad = (5) - (top1 >> 3); }
  .pe2 { .write = write; .spad = (2 + 3) - (top1 >> 3); }
  .pe3 { .write = write; .spad = 5 - ((top1) >> 3); }
}

@kernel checkShrCstNegOfa config | exec
void checkShrCstNegOfaRun(void) {
}

@emulate "shrsub"
.kernel checkShrsub direct {
  Int count = 16 - 1;

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

@emulate "shr_cst_ofs"
.kernel checkShrCstOfs direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 3) - 5; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 3)) - 5; }
  .pe2 { .write = write; .spad = (top1 >> 3) - (2 + 3); }
  .pe3 { .write = write; .spad = ((top1) >> 3) - 5; }
}

@kernel checkShrCstOfs config | exec
void checkShrCstOfsRun(void) {
}

@emulate "add_hib"
.kernel checkAddHib direct {
  Int count = 16 - 1;

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
  Int count = 16 - 1;

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
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 0x4) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? -top1 : (top1); }
}

@kernel checkSelNeg config | exec
void checkSelNegRun(void) {
}

@emulate "sel_neg_slf"
.kernel checkSelNegSlf direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 0x4) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf config | exec
void checkSelNegSlfRun(void) {
}

@emulate "sel_cst"
.kernel checkSelCst direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? 7 : top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? 7 : top1; }
  .pe2 { .write = write; .spad = (top0 & 0x4) ? (3 + 4) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? 7 : (top1); }
}

@kernel checkSelCst config | exec
void checkSelCstRun(void) {
}

@emulate "sel_cst_ofb"
.kernel checkSelCstOfb direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? top1 : 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? top1 : 7; }
  .pe2 { .write = write; .spad = (top0 & 0x4) ? top1 : (3 + 4); }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? (top1) : 7; }
}

@kernel checkSelCstOfb config | exec
void checkSelCstOfbRun(void) {
}

@emulate "sel_ads"
.kernel checkSelAds direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? top1 - 7 : top1 + 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? top1 - 7 : top1 + 7; }
  .pe2 { .write = write; .spad = (top1 & 0x4) ? (top1 - 7) : (top1 + 7); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? top1 - (3 + 4) : top1 + 7; }
}

@kernel checkSelAds config | exec
void checkSelAdsRun(void) {
}

@emulate "sel_ads_inv"
.kernel checkSelAdsInv direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? top1 + 7 : top1 - 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? top1 + 7 : top1 - 7; }
  .pe2 { .write = write; .spad = (top1 & 0x4) ? (top1 + 7) : (top1 - 7); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? top1 + (3 + 4) : top1 - 7; }
}

@kernel checkSelAdsInv config | exec
void checkSelAdsInvRun(void) {
}

@emulate "clamp"
.kernel checkClamp direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, -100, 100); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,-100,100); }
  .pe2 { .write = write; .spad = clamp((top1), -100, 100); }
  .pe3 { .write = write; .spad = clamp(top1, 0 - 100, 50 + 50); }
}

@kernel checkClamp config | exec
void checkClampRun(void) {
}

@emulate "mul_clp"
.kernel checkMulClp direct {
  Int count = 16 - 1;

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
  Int count = 16 - 1;

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
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? 0 : 9; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? 0 : 9; }
  .pe2 { .write = write; .spad = (top1 & 0x4) ? 0 : (3 * 3); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? 0 : 9; }
}

@kernel checkSelCstZer config | exec
void checkSelCstZerRun(void) {
}

@emulate "sel_cst_zer_inv"
.kernel checkSelCstZerInv direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? 9 : 0; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? 9 : 0; }
  .pe2 { .write = write; .spad = (top1 & 0x4) ? (3 * 3) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? 9 : 0; }
}

@kernel checkSelCstZerInv config | exec
void checkSelCstZerInvRun(void) {
}

@emulate "shl_dyn"
.kernel checkShlDyn direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -5 << top1; }
  .pe1 { .top = top; .write = write; .spad = (-5) << top1; }
  .pe2 { .write = write; .spad = (0 - 5) << top1; }
  .pe3 { .write = write; .spad = (-5) << (top1); }
}

@kernel checkShlDyn config | exec
void checkShlDynRun(void) {
}

@emulate "shr_dyn"
.kernel checkShrDyn direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -5 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (-5) >> top1; }
  .pe2 { .write = write; .spad = (0 - 5) >> top1; }
  .pe3 { .write = write; .spad = (-5) >> (top1); }
}

@kernel checkShrDyn config | exec
void checkShrDynRun(void) {
}

@emulate "shl_dyn_u"
.kernel checkShlDynU direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0xc00000 << top1; }
  .pe1 { .top = top; .write = write; .spad = (0xc00000) << top1; }
  .pe2 { .write = write; .spad = (0x800000 + 0x400000) << top1; }
  .pe3 { .write = write; .spad = (0xc00000) << (top1); }
}

@kernel checkShlDynU config | exec
void checkShlDynURun(void) {
}

@emulate "shr_dyn_u"
.kernel checkShrDynU direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0xc00000 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (0xc00000) >> top1; }
  .pe2 { .write = write; .spad = (0x800000 + 0x400000) >> top1; }
  .pe3 { .write = write; .spad = (0xc00000) >> (top1); }
}

@kernel checkShrDynU config | exec
void checkShrDynURun(void) {
}

@emulate "shl_reg"
.kernel checkShlReg direct {
  Int count = 16 - 1;

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
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 3); }
  .pe2 { .write = write; .spad = top1 << (1 + 2); }
  .pe3 { .write = write; .spad = (top1) << 3; }
}

@kernel checkShlCst config | exec
void checkShlCstRun(void) {
}

@emulate "shr_reg"
.kernel checkShrReg direct {
  Int count = 16 - 1;

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
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 3); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 3)); }
  .pe2 { .write = write; .spad = shrcst(top1, 1 + 2); }
  .pe3 { .write = write; .spad = shrcst((top1), 3); }
}

@kernel checkShrCst config | exec
void checkShrCstRun(void) {
}

@emulate "shl_reg_u"
.kernel checkShlRegU direct {
  Int count = 16 - 1;

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
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 3); }
  .pe2 { .write = write; .spad = top1 <<< (1 + 2); }
  .pe3 { .write = write; .spad = (top1) <<< 3; }
}

@kernel checkShlCstU config | exec
void checkShlCstURun(void) {
}

@emulate "shr_reg_u"
.kernel checkShrRegU direct {
  Int count = 16 - 1;

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
  Int count = 16 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 3); }
  .pe2 { .write = write; .spad = top1 >>> (1 + 2); }
  .pe3 { .write = write; .spad = (top1) >>> 3; }
}

@kernel checkShrCstU config | exec
void checkShrCstURun(void) {
}
