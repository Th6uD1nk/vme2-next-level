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
#include <debug.h>

PSP_MODULE_INFO("vme-fft", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT(16);

meLibSetSharedUncached32(10);
#define meCounter    (meLibSharedMemory[0])
#define meFFTIndex   (meLibSharedMemory[1])

void meLibOnProcess(void) {
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
