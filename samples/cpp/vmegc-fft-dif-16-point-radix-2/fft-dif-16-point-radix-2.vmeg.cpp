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

#include <psptypes.h>
#include <pspctrl.h>
#include <pspdisplay.h>
#include <pspkernel.h>
#include <psppower.h>
#include <pspgu.h>
#include <me-core-mapper/me-core.h>
#include <me-core-mapper/vme-fu-opcodes.h>
#include <debug.h>

PSP_MODULE_INFO("vme-fft", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT(16);

meLibSetSharedUncached32(10);
#define meCounter    (meLibSharedMemory[0])
#define meFFTIndex   (meLibSharedMemory[1])

#define FFT_POINT_COUNT (16)
#define FFT_VALUE_COUNT FFT_POINT_COUNT
#define SAMPLE_SIZE (FFT_VALUE_COUNT * 2)
#define SAMPLE_BYTE_COUNT (FFT_VALUE_COUNT * 2 * 4)

#define Q_FORMAT 20

#define FFT_STAGE_0_STRIDE (FFT_VALUE_COUNT / 2)
#define FFT_TWIDDLE_COUNT (FFT_VALUE_COUNT - 1)
#define FFT_TWIDDLE_BASE_OFFSET (128)

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

volatile Buffer(Q4.20) fftReal0[SAMPLE_SIZE] = {
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  1.0f, 1.0f, 1.0f, 1.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal1[SAMPLE_SIZE] = {
  1.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal2[SAMPLE_SIZE] = {
  0.0f, 0.0f, 0.0f, 0.0f,
  1.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal3[SAMPLE_SIZE] = {
  1.000000f, 0.923880f, 0.707107f, 0.382683f,
  0.000000f, -0.382683f, -0.707107f, -0.923880f,
  -1.000000f, -0.923880f, -0.707107f, -0.382683f,
  0.000000f, 0.382683f, 0.707107f, 0.923880f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal4[SAMPLE_SIZE] = {
  1.0f, 0.7071f, 0.0f, -0.7071f,
  -1.0f, -0.7071f, 0.0f, 0.7071f,
  1.0f, 0.7071f, 0.0f, -0.7071f,
  -1.0f, -0.7071f, 0.0f, 0.7071f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal5[SAMPLE_SIZE] = {
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  1.0f, -1.0f, 1.0f, -1.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal6[SAMPLE_SIZE] = {
  0.000000f, 0.382683f, 0.707107f, 0.923880f,
  1.000000f, 0.923880f, 0.707107f, 0.382683f,
  0.000000f, -0.382683f, -0.707107f, -0.923880f,
  -1.000000f, -0.923880f, -0.707107f, -0.382683f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftReal7[SAMPLE_SIZE] = {
  2.000000f, 1.306563f, 0.000000f, -0.541196f,
  0.000000f, 0.541196f, 0.000000f, -1.306563f,
  -2.000000f, -1.306563f, 0.000000f, 0.541196f,
  0.000000f, -0.541196f, 0.000000f, 1.306563f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer(Q4.20) fftImag[SAMPLE_SIZE] = {
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0.0f, 0.0f, 0.0f, 0.0f,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0,
};

volatile Buffer* fftSignals[8] = {
  fftReal0, fftReal1, fftReal2, fftReal3,
  fftReal4, fftReal5, fftReal6, fftReal7,
};

volatile Buffer* fftStageReal = (volatile u32*)0x40000000;
volatile Buffer* fftStageImag = (volatile u32*)(0x40000000 | (FFT_VALUE_COUNT * 4 * 2));

volatile Memory butterflyConfigs[4];

.kernel butterfly memory {
  .params { int stride; }

  Agu upperTop = { count: FFT_STAGE_0_STRIDE - 1, offset: 0x800 - FFT_STAGE_0_STRIDE };
  Agu lowerTop = { count: FFT_STAGE_0_STRIDE - 1, offset: stride };
  Agu upperWrite = { count: FFT_STAGE_0_STRIDE - 1, offset: 0x800 - FFT_STAGE_0_STRIDE, cyc: 6 };
  Agu lowerWrite = { count: FFT_STAGE_0_STRIDE - 1, cyc: 6 };

  .pe0 {
    .top = upperTop;
    .write = upperWrite;
    .spad = round(top1 + top0) >> 1;
  }

  .pe1 {
    .top = lowerTop;
    .write = lowerWrite;
    .spad = round(top0 - top1);
  }

  .pe2 {
    .top = upperTop;
    .write = upperWrite;
    .spad = round(top3 + top2) >> 1;
  }

  .pe3 {
    .top = lowerTop;
    .write = lowerWrite;
    .spad = round(top2 - top3);
  }
}

volatile Memory lowerLegConfigs[4];

.kernel lowerLeg memory {
  .params { int twiddleOffset; int twiddleCount; }

  Agu(2) twiddles = {
    offset: twiddleOffset,
    count: FFT_STAGE_0_STRIDE - 1,
    inner0: { count: twiddleCount, step: 1 },
    repeat: true
  };
  Agu lowerBase = { count: FFT_STAGE_0_STRIDE - 1 };
  Agu lowerWrite = { count: FFT_STAGE_0_STRIDE - 1, cyc: auto };

  Staging realReal, imagImag, realImag, imagReal;

  .pe0 {
    .top = twiddles;
    .remap = { operator: "*", primary: 0x220 };
    realReal = round(base1 * top0 >> Q_FORMAT);
  }

  .pe1 {
    .base = lowerBase;
    .write = lowerWrite;
    .remap = { operator: "*", primary: 0x220 };
    imagImag = round(base3 * top2 >> Q_FORMAT);
    .spad = round(realReal - imagImag) >> 1;
  }

  .pe2 {
    .top = twiddles;
    .remap = { operator: "*", primary: 0x220 };
    realImag = round(base1 * top2 >> Q_FORMAT);
  }

  .pe3 {
    .base = lowerBase;
    .write = lowerWrite;
    .remap = { operator: "*", primary: 0x220 };
    imagReal = round(base3 * top0 >> Q_FORMAT);
    .spad = round(imagReal + realImag) >> 1;
  }
}

void meLibOnProcess(void) {
  @emulate "fft-4-stages" {
    for s in 0..3 {
      @kernel butterfly build {
        .params = { stride: FFT_STAGE_0_STRIDE >> s };
        .memory = butterflyConfigs[s];
      }

      @kernel lowerLeg build {
        .params = {
          twiddleOffset: FFT_TWIDDLE_BASE_OFFSET + FFT_VALUE_COUNT - (FFT_VALUE_COUNT >> s),
          twiddleCount: (FFT_VALUE_COUNT >> (s + 1)) - 1
        };
        .memory = lowerLegConfigs[s];
      }
    }

    meCoreDcacheWritebackRange((void*)fftTwiddleReal, sizeof(fftTwiddleReal));
    meCoreDcacheWritebackRange((void*)fftTwiddleImag, sizeof(fftTwiddleImag));
    meCoreDcacheWritebackRange((void*)fftImag, SAMPLE_BYTE_COUNT);

    @kernel lowerLeg config {
      .memory = lowerLegConfigs[0];

      Transfer realTwiddles = { memory: fftTwiddleReal, count: FFT_TWIDDLE_COUNT - 1 };
      Transfer imagTwiddles = { memory: fftTwiddleImag, count: FFT_TWIDDLE_COUNT - 1 };

      .load { .transfer = realTwiddles; .scope = global; .offsets { .top0 = FFT_TWIDDLE_BASE_OFFSET; } }
      .load { .transfer = imagTwiddles; .scope = global; .offsets { .top2 = FFT_TWIDDLE_BASE_OFFSET; } }
    }

    while (1) {
      volatile Buffer* signal = fftSignals[meFFTIndex];
      meCoreDcacheWritebackRange((void*)signal, SAMPLE_BYTE_COUNT);

      @kernel butterfly config {
        .memory = butterflyConfigs[0];

        Transfer(Words) realIn = { memory: signal, count: 1, gap: FFT_VALUE_COUNT - 1 + FFT_STAGE_0_STRIDE, step: 0, group: { size: 2 * FFT_STAGE_0_STRIDE - 1, outer: FFT_STAGE_0_STRIDE, inner: 1 } };
        Transfer(Words) imagIn = { memory: fftImag, count: 1, gap: FFT_VALUE_COUNT - 1 + FFT_STAGE_0_STRIDE, step: 0, group: { size: 2 * FFT_STAGE_0_STRIDE - 1, outer: FFT_STAGE_0_STRIDE, inner: 1 } };

        .load { .transfer = realIn; .scope = local; .offsets { .top1 = -FFT_STAGE_0_STRIDE; } }
        .load { .transfer = imagIn; .scope = global; .offsets { .top3 = -FFT_STAGE_0_STRIDE; } }
      }

      @kernel butterfly exec {
        .memory = butterflyConfigs[0];
      }

      @kernel lowerLeg config | exec {
        .memory = lowerLegConfigs[0];
      }

      @unroll
      for (int s = 1; s < 4; s++) {
        @kernel butterfly config {
          .memory = butterflyConfigs[s];

          Transfer realOut = { memory: fftStageReal, count: FFT_VALUE_COUNT - 1 };
          Transfer imagOut = { memory: fftStageImag, count: FFT_VALUE_COUNT - 1 };
          Transfer(Words) realIn = { memory: fftStageReal, count: 1, gap: FFT_VALUE_COUNT - 1 + (FFT_STAGE_0_STRIDE >> s), step: 0, group: { size: 2 * (FFT_STAGE_0_STRIDE >> s) - 1, outer: FFT_STAGE_0_STRIDE >> s, inner: 1 } };
          Transfer(Words) imagIn = { memory: fftStageImag, count: 1, gap: FFT_VALUE_COUNT - 1 + (FFT_STAGE_0_STRIDE >> s), step: 0, group: { size: 2 * (FFT_STAGE_0_STRIDE >> s) - 1, outer: FFT_STAGE_0_STRIDE >> s, inner: 1 } };

          .store { .transfer = realOut; .scope = global; .offsets { .base1 = -FFT_STAGE_0_STRIDE; } }
          .store { .transfer = imagOut; .scope = global; .offsets { .base3 = -FFT_STAGE_0_STRIDE; } }
          .load { .transfer = realIn; .scope = global; .offsets { .top1 = -FFT_STAGE_0_STRIDE; } }
          .load { .transfer = imagIn; .scope = global; .offsets { .top3 = -FFT_STAGE_0_STRIDE; } }
        }

        @kernel butterfly exec {
          .memory = butterflyConfigs[s];
        }

        @kernel lowerLeg config | exec {
          .memory = lowerLegConfigs[s];

          if (s == 3) {
            vmeDebugFillAtWith(0, VME_BASE_BUFF1_WOFF - FFT_STAGE_0_STRIDE);
            vmeDebugFillAtWith(1, VME_BASE_BUFF3_WOFF - FFT_STAGE_0_STRIDE);
          }
        }
      }

      meCounter += 1;
    }
  }
}

int main() {

  vmeDebugSetupBuffers();

  meLibDefaultInit();
  pspDebugScreenInit();
  pspDebugScreenPrintf("16-point-radix-2");

  int up = 1;
  SceCtrlData ctl;
  do {

    sceCtrlPeekBufferPositive(&ctl, 1);

    if (up && (ctl.Buttons & PSP_CTRL_TRIANGLE)) {

      meFFTIndex += meFFTIndex < 7 ? 1 : 0;
      up = 0;
    }

    if (up && (ctl.Buttons & PSP_CTRL_CROSS)) {

      meFFTIndex -= meFFTIndex > 0 ? 1 : 0;
      up = 0;
    }

    if (!(ctl.Buttons)) {
      up = 1;
    }

    pspDebugScreenSetXY(1, 2);
    pspDebugScreenPrintf("meCounter: 0x%08lx    ", meCounter);

    pspDebugScreenSetXY(1, 4);
    pspDebugScreenPrintf("Real parts: ");
    vmeDebugDisplayBufferWithSpace('8', 0, 1, 5);

    pspDebugScreenSetXY(1, 10);
    pspDebugScreenPrintf("Imaginary parts: ");
    vmeDebugDisplayBufferWithSpace('8', 1, 1, 11);

    pspDebugScreenSetXY(1, 18);
    pspDebugScreenPrintf("Stimulus index: %lx", meFFTIndex);

    sceDisplayWaitVblankStart();
  } while (!(ctl.Buttons & PSP_CTRL_HOME));

  vmeDebugTouch();
  vmeDebugDumpBuffers();
  vmeDebugFreeBuffers();

  sceKernelExitGame();
  return 0;
}
