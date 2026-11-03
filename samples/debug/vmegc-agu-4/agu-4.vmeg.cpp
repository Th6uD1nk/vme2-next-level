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

volatile Buffer aguTableA[32] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32 };
volatile Buffer aguTableB[32] = { 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200 };

@declare {
  Transfer tableA = { memory: aguTableA, count: 31 };
  Transfer tableB = { memory: aguTableB, count: 31 };
}

@emulate "agu4-c7-add"
.kernel probeAgu4C7Add direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7 };
  Agu readBase = { count: 7 };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 + base0; }
}

@kernel probeAgu4C7Add config | exec
void probeAgu4C7AddRun(void) {
}

@emulate "agu4-c7-sub"
.kernel probeAgu4C7Sub direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7 };
  Agu readBase = { count: 7 };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 - base0; }
}

@kernel probeAgu4C7Sub config | exec
void probeAgu4C7SubRun(void) {
}

@emulate "agu4-c7-mul"
.kernel probeAgu4C7Mul direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7 };
  Agu readBase = { count: 7 };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 * base0; }
}

@kernel probeAgu4C7Mul config | exec
void probeAgu4C7MulRun(void) {
}

@emulate "agu4-c7-mac"
.kernel probeAgu4C7Mac direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7 };
  Agu readBase = { count: 7 };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = mac(top0, base0); }
}

@kernel probeAgu4C7Mac config | exec
void probeAgu4C7MacRun(void) {
}

@emulate "agu4-c7-acc"
.kernel probeAgu4C7Acc direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  Agu readTop = { count: 7 };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .write = write; .spad = acc(top0); }
}

@kernel probeAgu4C7Acc config | exec
void probeAgu4C7AccRun(void) {
}

@emulate "agu4-c7-r4-add"
.kernel probeAgu4C7R4Add direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 3, step: 1 } };
  Agu readBase = { count: 7, inner0: { count: 3, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 + base0; }
}

@kernel probeAgu4C7R4Add config | exec
void probeAgu4C7R4AddRun(void) {
}

@emulate "agu4-c7-r4-sub"
.kernel probeAgu4C7R4Sub direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 3, step: 1 } };
  Agu readBase = { count: 7, inner0: { count: 3, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 - base0; }
}

@kernel probeAgu4C7R4Sub config | exec
void probeAgu4C7R4SubRun(void) {
}

@emulate "agu4-c7-r4-mul"
.kernel probeAgu4C7R4Mul direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 3, step: 1 } };
  Agu readBase = { count: 7, inner0: { count: 3, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 * base0; }
}

@kernel probeAgu4C7R4Mul config | exec
void probeAgu4C7R4MulRun(void) {
}

@emulate "agu4-c7-r4-mac"
.kernel probeAgu4C7R4Mac direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 3, step: 1 } };
  Agu readBase = { count: 7, inner0: { count: 3, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = mac(top0, base0); }
}

@kernel probeAgu4C7R4Mac config | exec
void probeAgu4C7R4MacRun(void) {
}

@emulate "agu4-c7-r4-acc"
.kernel probeAgu4C7R4Acc direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 3, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .write = write; .spad = acc(top0); }
}

@kernel probeAgu4C7R4Acc config | exec
void probeAgu4C7R4AccRun(void) {
}

@emulate "agu4-c7-rep-add"
.kernel probeAgu4C7RepAdd direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, repeat: true };
  Agu readBase = { count: 7, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 + base0; }
}

@kernel probeAgu4C7RepAdd config | exec
void probeAgu4C7RepAddRun(void) {
}

@emulate "agu4-c7-rep-sub"
.kernel probeAgu4C7RepSub direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, repeat: true };
  Agu readBase = { count: 7, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 - base0; }
}

@kernel probeAgu4C7RepSub config | exec
void probeAgu4C7RepSubRun(void) {
}

@emulate "agu4-c7-rep-mul"
.kernel probeAgu4C7RepMul direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, repeat: true };
  Agu readBase = { count: 7, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 * base0; }
}

@kernel probeAgu4C7RepMul config | exec
void probeAgu4C7RepMulRun(void) {
}

@emulate "agu4-c7-rep-mac"
.kernel probeAgu4C7RepMac direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, repeat: true };
  Agu readBase = { count: 7, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = mac(top0, base0); }
}

@kernel probeAgu4C7RepMac config | exec
void probeAgu4C7RepMacRun(void) {
}

@emulate "agu4-c7-rep-acc"
.kernel probeAgu4C7RepAcc direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  Agu readTop = { count: 7, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .write = write; .spad = acc(top0); }
}

@kernel probeAgu4C7RepAcc config | exec
void probeAgu4C7RepAccRun(void) {
}

@emulate "agu4-c7-i7-add"
.kernel probeAgu4C7I7Add direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 } };
  Agu readBase = { count: 7, inner0: { count: 7, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 + base0; }
}

@kernel probeAgu4C7I7Add config | exec
void probeAgu4C7I7AddRun(void) {
}

@emulate "agu4-c7-i7-sub"
.kernel probeAgu4C7I7Sub direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 } };
  Agu readBase = { count: 7, inner0: { count: 7, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 - base0; }
}

@kernel probeAgu4C7I7Sub config | exec
void probeAgu4C7I7SubRun(void) {
}

@emulate "agu4-c7-i7-mul"
.kernel probeAgu4C7I7Mul direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 } };
  Agu readBase = { count: 7, inner0: { count: 7, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 * base0; }
}

@kernel probeAgu4C7I7Mul config | exec
void probeAgu4C7I7MulRun(void) {
}

@emulate "agu4-c7-i7-mac"
.kernel probeAgu4C7I7Mac direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 } };
  Agu readBase = { count: 7, inner0: { count: 7, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = mac(top0, base0); }
}

@kernel probeAgu4C7I7Mac config | exec
void probeAgu4C7I7MacRun(void) {
}

@emulate "agu4-c7-i7-acc"
.kernel probeAgu4C7I7Acc direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 } };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .write = write; .spad = acc(top0); }
}

@kernel probeAgu4C7I7Acc config | exec
void probeAgu4C7I7AccRun(void) {
}

@emulate "agu4-c7-i7-rep-add"
.kernel probeAgu4C7I7RepAdd direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu readBase = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 + base0; }
}

@kernel probeAgu4C7I7RepAdd config | exec
void probeAgu4C7I7RepAddRun(void) {
}

@emulate "agu4-c7-i7-rep-sub"
.kernel probeAgu4C7I7RepSub direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu readBase = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 - base0; }
}

@kernel probeAgu4C7I7RepSub config | exec
void probeAgu4C7I7RepSubRun(void) {
}

@emulate "agu4-c7-i7-rep-mul"
.kernel probeAgu4C7I7RepMul direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu readBase = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 * base0; }
}

@kernel probeAgu4C7I7RepMul config | exec
void probeAgu4C7I7RepMulRun(void) {
}

@emulate "agu4-c7-i7-rep-mac"
.kernel probeAgu4C7I7RepMac direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu readBase = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = mac(top0, base0); }
}

@kernel probeAgu4C7I7RepMac config | exec
void probeAgu4C7I7RepMacRun(void) {
}

@emulate "agu4-c7-i7-rep-acc"
.kernel probeAgu4C7I7RepAcc direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 7, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .write = write; .spad = acc(top0); }
}

@kernel probeAgu4C7I7RepAcc config | exec
void probeAgu4C7I7RepAccRun(void) {
}

@emulate "agu4-c7-r4-rep-add"
.kernel probeAgu4C7R4RepAdd direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu readBase = { count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 + base0; }
}

@kernel probeAgu4C7R4RepAdd config | exec
void probeAgu4C7R4RepAddRun(void) {
}

@emulate "agu4-c7-r4-rep-sub"
.kernel probeAgu4C7R4RepSub direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu readBase = { count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 - base0; }
}

@kernel probeAgu4C7R4RepSub config | exec
void probeAgu4C7R4RepSubRun(void) {
}

@emulate "agu4-c7-r4-rep-mul"
.kernel probeAgu4C7R4RepMul direct {
  .load { .transfer = tableA; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tableB; .scope = global; .offsets { .base0 = 0; } }
  Agu readTop = { count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu readBase = { count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };
  .pe0 { .top = readTop; .base = readBase; .write = write; .spad = top0 * base0; }
}

@kernel probeAgu4C7R4RepMul config | exec
void probeAgu4C7R4RepMulRun(void) {
}
