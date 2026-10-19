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
#include <pspctrl.h>
#include <pspdisplay.h>
#include <pspkernel.h>
#include <psppower.h>
#include <me-core-mapper/me-core.h>
#include <me-core-mapper/vme-fu-opcodes.h>
#include <debug.h>

PSP_MODULE_INFO("vme-sat", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT(32);

meLibSetSharedUncached32(10);
#define meCounter    (meLibSharedMemory[1])

#define SHARED_BASE_0_INPUT_OFFSET 32

volatile Buffer sharedTop0[16] = {
  0x10, 0x11, 0x12, 0x13,
  0x14, 0x15, 0x16, 0x17,
  0x18, 0x19, 0x1a, 0x1b,
  0x1c, 0x1d, 0x1e, 0x1f,
};

volatile Buffer sharedTop1[16] = {
  0x20, 0x21, 0x22, 0x23,
  0x24, 0x25, 0x26, 0x27,
  0x28, 0x29, 0x2a, 0x2b,
  0x2c, 0x2d, 0x2e, 0x2f,
};

volatile Buffer sharedTop2[16] = {
  0x30, 0x31, 0x32, 0x33,
  0x34, 0x35, 0x36, 0x37,
  0x38, 0x39, 0x3a, 0x3b,
  0x3c, 0x3d, 0x3e, 0x3f,
};

volatile Buffer sharedTop3[16] = {
  0x40, 0x41, 0x42, 0x43,
  0x44, 0x45, 0x46, 0x47,
  0x48, 0x49, 0x4a, 0x4b,
  0x4c, 0x4d, 0x4e, 0x4f,
};

volatile Buffer sharedBase0[16] = {
  0x01, 0x10, 0x01, (0x7fffff + 0x02),
  0x01, 0x20, 0x01, (0x7fffff + 0x02),
  0x01, 0x30, 0x01, (0x7fffff + 0x02),
  0x01, 0x40, 0x01, (0x7fffff + 0x02),
};

kernel runContext direct {
  
  global buffers {
    top0, 16 words, from sharedTop0;
    top1, 16 words, from sharedTop1;
    top2, 16 words, from sharedTop2;
    top3, 16 words, from sharedTop3;
    base0, 16 words, at SHARED_BASE_0_INPUT_OFFSET, from sharedBase0;
  }

  const count = 16 - 1;

  Agu top   = { count };
  Agu base  = { count, offset: SHARED_BASE_0_INPUT_OFFSET };
  Agu write = { count, cyc: 0x09 };

  for p in 0..3 {
    pe[p] {
      .top = top;
      .write = write;
      .clamp(sat(top[p] + base0, 7), 0, 0x7fffff);
    }
  }

  pe0 { .base = base; }
}

void meLibOnProcess(void) {

  @kernel runContext {
    vmeDebugFillWith(VME_BASE_BUFFERS);
  }

  while (1) {
    meCounter += 1;
  }
}

int main() {
  
  scePowerSetClockFrequency(333, 333, 166);
  vmeDebugSetupBuffers();

  meLibDefaultInit();

  pspDebugScreenInit();
  SceCtrlData ctl;
  do {
    sceCtrlPeekBufferPositive(&ctl, 1);

    {
      const int x = 1;
      const int y = 1;

      pspDebugScreenSetXY(x, y);
      pspDebugScreenPrintf("Result of the 4 Processing Elements:");

      pspDebugScreenSetXY(x, y + 2);
      pspDebugScreenPrintf("BASE_0:");
      vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, VME_DBG_IDX_BASE_0, x, y + 3);

      pspDebugScreenSetXY(x + 34, y + 2);
      pspDebugScreenPrintf("BASE_1:");
      vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, VME_DBG_IDX_BASE_1, x + 34, y + 3);

      pspDebugScreenSetXY(x, y + 12);
      pspDebugScreenPrintf("BASE_2:");
      vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, VME_DBG_IDX_BASE_2, x, y + 13);

      pspDebugScreenSetXY(x + 34, y + 12);
      pspDebugScreenPrintf("BASE_3:");
      vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, VME_DBG_IDX_BASE_3, x + 34, y + 13);
    }

    pspDebugScreenSetXY(1, 24);
    pspDebugScreenPrintf("meCounter: 0x%lx", meCounter);

    sceDisplayWaitVblank();

  } while (!(ctl.Buttons & PSP_CTRL_HOME));

  sceKernelDelayThread(100000);

  vmeDebugTouch();
  vmeDebugDumpBuffers();
  vmeDebugFreeBuffers();

  sceKernelExitGame();
  return 0;
}
