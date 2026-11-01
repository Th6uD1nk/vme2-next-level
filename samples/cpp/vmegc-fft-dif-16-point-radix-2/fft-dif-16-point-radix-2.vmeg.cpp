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

volatile Buffer(Q4.20) fftTwiddleReal[15] = {
  1.0f, 0.9238795f, 0.7071068f, 0.3826834f,
  0.0f, -0.3826834f, -0.7071068f, -0.9238795f,
  1.0f, 0.7071068f, 0.0f, -0.7071068f,
  1.0f, 0.0f, 1.0f,
};

volatile Buffer(Q4.20) fftTwiddleImag[15] = {
  0.0f, -0.3826834f, -0.7071068f, -0.9238795f,
  -1.0f, -0.9238795f, -0.7071068f, -0.3826834f,
  0.0f, -0.7071068f, -1.0f, -0.7071068f,
  0.0f, -1.0f, 0.0f,
};

volatile Buffer(Q4.20) fftReal0[32] = {
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal1[32] = {
  1.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal2[32] = {
  0.0f, 0.0f, 0.0f, 0.0f,
  1.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal3[32] = {
  1.000000f, 0.923880f, 0.707107f, 0.382683f,
  0.000000f, -0.382683f, -0.707107f, -0.923880f,
  -1.000000f, -0.923880f, -0.707107f, -0.382683f,
  0.000000f, 0.382683f, 0.707107f, 0.923880f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal4[32] = {
  1.0f, 0.7071f, 0.0f, -0.7071f,
  -1.0f, -0.7071f, 0.0f, 0.7071f,
  1.0f, 0.7071f, 0.0f, -0.7071f,
  -1.0f, -0.7071f, 0.0f, 0.7071f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal5[32] = {
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal6[32] = {
  0.000000f, 0.382683f, 0.707107f, 0.923880f,
  1.000000f, 0.923880f, 0.707107f, 0.382683f,
  0.000000f, -0.382683f, -0.707107f, -0.923880f,
  -1.000000f, -0.923880f, -0.707107f, -0.382683f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal7[32] = {
  2.000000f, 1.306563f, 0.000000f, -0.541196f,
  0.000000f, 0.541196f, 0.000000f, -1.306563f,
  -2.000000f, -1.306563f, 0.000000f, 0.541196f,
  0.000000f, -0.541196f, 0.000000f, 1.306563f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftImag[32] = {
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftStageReal[32];

volatile Buffer(Q4.20) fftStageImag[32];

.kernel butterfly memory {
  .params { int stride; }

  Agu upperTop = { count: 7, offset: 0x800 - 8 };
  Agu lowerTop = { count: 7, offset: stride };
  Agu upperWrite = { count: 7, offset: 0x800 - 8, cyc: 6 };
  Agu lowerWrite = { count: 7, cyc: 6 };

  .pe0 { .top = upperTop; .write = upperWrite; .spad = round(top1 + top0) >> 1; }
  .pe1 { .top = lowerTop; .write = lowerWrite; .spad = round(top0 - top1); }
  .pe2 { .top = upperTop; .write = upperWrite; .spad = round(top3 + top2) >> 1; }
  .pe3 { .top = lowerTop; .write = lowerWrite; .spad = round(top2 - top3); }
}

.kernel lowerLeg memory {
  .params { int twiddleOffset; int twiddleCount; }

  Agu(2) twiddles = { offset: twiddleOffset, count: twiddleCount, step: 1, repeat: true };
  Agu lowerBase = { count: 7 };
  Agu lowerWrite = { count: 7, cyc: auto };

  Staging realReal, imagImag, realImag, imagReal;

  .pe0 { .top = twiddles; .remap = { operator: "*", primary: 0x220 }; realReal = round(base1 * top0 >> 20); }
  .pe1 { .base = lowerBase; .write = lowerWrite; .remap = { operator: "*", primary: 0x220 }; imagImag = round(base3 * top2 >> 20); .spad = round(realReal - imagImag) >> 1; }
  .pe2 { .top = twiddles; .remap = { operator: "*", primary: 0x220 }; realImag = round(base1 * top2 >> 20); }
  .pe3 { .base = lowerBase; .write = lowerWrite; .remap = { operator: "*", primary: 0x220 }; imagReal = round(base3 * top0 >> 20); .spad = round(imagReal + realImag) >> 1; }
}

void meLibOnProcess(void) {
  @emulate "fft-4-stages" {
    @kernel butterfly build {
      .params = { stride: 8 };
    }
    @kernel butterfly config {
      Transfer(Words) realIn = { memory: fftReal0, count: 1, gap: 23, step: 0, group: { size: 15, outer: 8, inner: 1 } };
      Transfer(Words) imagIn = { memory: fftImag, count: 1, gap: 23, step: 0, group: { size: 15, outer: 8, inner: 1 } };
      .load { .transfer = realIn; .scope = global; .offsets { .top1 = -8; } }
      .load { .transfer = imagIn; .scope = global; .offsets { .top3 = -8; } }
    }
    @kernel butterfly exec {
    }
    @kernel lowerLeg build {
      .params = { twiddleOffset: 128, twiddleCount: 7 };
    }
    @kernel lowerLeg config {
      Transfer realTwiddles = { memory: fftTwiddleReal, count: 14 };
      Transfer imagTwiddles = { memory: fftTwiddleImag, count: 14 };
      .load { .transfer = realTwiddles; .scope = global; .offsets { .top0 = 128; } }
      .load { .transfer = imagTwiddles; .scope = global; .offsets { .top2 = 128; } }
    }
    @kernel lowerLeg exec {
      Transfer realOut = { memory: fftStageReal, count: 15 };
      Transfer imagOut = { memory: fftStageImag, count: 15 };
      .store { .transfer = realOut; .scope = global; .offsets { .base1 = -8; } }
      .store { .transfer = imagOut; .scope = global; .offsets { .base3 = -8; } }
    }
    for s in 1..3 {
      @kernel butterfly build {
        .params = { stride: 8 >> s };
      }
      @kernel butterfly config {
        Transfer(Words) realIn = { memory: fftStageReal, count: 1, gap: 15 + (8 >> s), step: 0, group: { size: 2 * (8 >> s) - 1, outer: 8 >> s, inner: 1 } };
        Transfer(Words) imagIn = { memory: fftStageImag, count: 1, gap: 15 + (8 >> s), step: 0, group: { size: 2 * (8 >> s) - 1, outer: 8 >> s, inner: 1 } };
        .load { .transfer = realIn; .scope = global; .offsets { .top1 = -8; } }
        .load { .transfer = imagIn; .scope = global; .offsets { .top3 = -8; } }
      }
      @kernel butterfly exec {
      }
      @kernel lowerLeg build {
        .params = { twiddleOffset: 144 - (16 >> s), twiddleCount: (8 >> s) - 1 };
      }
      @kernel lowerLeg config {
      }
      @kernel lowerLeg exec {
        Transfer realOut = { memory: fftStageReal, count: 15 };
        Transfer imagOut = { memory: fftStageImag, count: 15 };
        .store { .transfer = realOut; .scope = global; .offsets { .base1 = -8; } }
        .store { .transfer = imagOut; .scope = global; .offsets { .base3 = -8; } }
      }
    }
  }
}
