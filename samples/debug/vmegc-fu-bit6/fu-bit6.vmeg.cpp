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
  -8, -7, -6, -5,
  -4, -3, -2, -1,
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
  -1, -3, -5, -7,
  -9, -11, -13, -15,
};

volatile Buffer bit6Base1[16] = {
  0, 2, 4, 6,
  8, 10, 12, 14,
  0, -2, -4, -6,
  -8, -10, -12, -14,
};

volatile Buffer bit6Top2[16] = {
  0x7ffffe, 0x7fffff, -0x800000, -0x7fffff,
  0x400000, -0x400000, 0x123456, -0x123456,
  1, -1, 3, -3,
  5, -5, 0, 0,
};

volatile Buffer bit6Base2[16] = {
  1, 1, -1, -1,
  0x3fffff, -0x3fffff, 0x654321, -0x654321,
  1, -1, 1, -1,
  1, -1, 0, 1,
};

volatile Buffer bit6Top3[16] = {
  0, 1, -1, 2,
  -2, 3, -3, 4,
  -4, 5, -5, 6,
  -6, 7, -7, 8,
};

volatile Buffer bit6Base3[16] = {
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1,
  1, 1, 1, 1,
};

@emulate "fu-bit6-on"
.kernel checkBit6On direct {
}

@kernel checkBit6On config | exec
void checkBit6OnRun(void) {
}

@emulate "fu-bit6-off"
.kernel checkBit6Off direct {
}

@kernel checkBit6Off config | exec
void checkBit6OffRun(void) {
}
