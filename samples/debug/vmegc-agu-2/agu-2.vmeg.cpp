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

volatile Buffer aguTable[32] = {
  1, 2, 3, 4,
  5, 6, 7, 8,
  9, 10, 11, 12,
  13, 14, 15, 16,
  17, 18, 19, 20,
  21, 22, 23, 24,
  25, 26, 27, 28,
  29, 30, 31, 32,
};

@emulate "agu2-c7-r4"
.kernel probeAgu2C7R4 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C7R4 config | exec
void probeAgu2C7R4Run(void) {
}

@emulate "agu2-c5-r4"
.kernel probeAgu2C5R4 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { count: 5, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C5R4 config | exec
void probeAgu2C5R4Run(void) {
}

@emulate "agu2-c3-r8"
.kernel probeAgu2C3R8 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { count: 3, inner0: { count: 7, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C3R8 config | exec
void probeAgu2C3R8Run(void) {
}

@emulate "agu2-c0-r4"
.kernel probeAgu2C0R4 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { count: 0, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C0R4 config | exec
void probeAgu2C0R4Run(void) {
}

@emulate "agu2-c15-r4"
.kernel probeAgu2C15R4 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { count: 15, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C15R4 config | exec
void probeAgu2C15R4Run(void) {
}

@emulate "agu2-c7-r4-s2"
.kernel probeAgu2C7R4S2 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { count: 7, inner0: { count: 3, step: 2 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C7R4S2 config | exec
void probeAgu2C7R4S2Run(void) {
}

@emulate "agu2-c7-r4-no-repeat"
.kernel probeAgu2C7R4NoRepeat direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { count: 7, inner0: { count: 3, step: 1 } };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C7R4NoRepeat config | exec
void probeAgu2C7R4NoRepeatRun(void) {
}

@emulate "agu2-c7-no-inner"
.kernel probeAgu2C7NoInner direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { count: 7 };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C7NoInner config | exec
void probeAgu2C7NoInnerRun(void) {
}

@emulate "agu2-c7-r4-offset3"
.kernel probeAgu2C7R4Offset3 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu(2) read = { offset: 3, count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu2C7R4Offset3 config | exec
void probeAgu2C7R4Offset3Run(void) {
}

@emulate "agu4-c7-r4"
.kernel probeAgu4C7R4 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu read = { count: 7, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu4C7R4 config | exec
void probeAgu4C7R4Run(void) {
}

@emulate "agu4-c5-r4"
.kernel probeAgu4C5R4 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu read = { count: 5, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu4C5R4 config | exec
void probeAgu4C5R4Run(void) {
}

@emulate "agu4-c0-r4"
.kernel probeAgu4C0R4 direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu read = { count: 0, inner0: { count: 3, step: 1 }, repeat: true };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu4C0R4 config | exec
void probeAgu4C0R4Run(void) {
}

@emulate "agu4-c7-no-inner"
.kernel probeAgu4C7NoInner direct {
  Transfer tableTransfer = { memory: aguTable, count: 31 };

  .load { .transfer = tableTransfer; .scope = global; .offsets { .top0 = 0; } }

  Agu read = { count: 7 };
  Agu write = { count: 23, cyc: auto };

  .pe0 { .top = read; .write = write; .spad = top0 | top0; }
}

@kernel probeAgu4C7NoInner config | exec
void probeAgu4C7NoInnerRun(void) {
}
