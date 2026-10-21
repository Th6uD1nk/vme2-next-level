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
#include <vme-ext.h>
#include <debug.h>

PSP_MODULE_INFO("vme-ctx", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT(32);

meLibSetSharedUncached32(10);
#define meCounter    (meLibSharedMemory[0])

// (back[n] + front[n]) >> k
.kernel add memory {
  Agu t = { count: 31 }, b = { count: 31 }, w = { count: 31, cyc: 6 };
  .pe0 { .top = t; .base = b; .write = w; .base0 + top0; }
}

// (front[n] - back[n]) >> k
.kernel sub memory {
  Agu t = { count: 31 }, b = { count: 31 }, w = { count: 31, cyc: 6 };
  .pe1 { .top = t; .base = b; .write = w; .subshr(base1, top0, 0); }
  .pe0 { .top = t; }
}

// (back[n] * front[n]) >> k
.kernel mul memory {
  Agu t = { count: 31 }, b = { count: 31 }, w = { count: 31, cyc: 6 };
  .pe2 { .top = t; .base = b; .write = w; .base2 * top0; }
  .pe0 { .top = t; }
}

void setupScratchpadData() {

  {
    vmeExtRow4u32* const data = (vmeExtRow4u32*)VME_TOP_BUFFER_0;
    data[0].row = {0x01, 0x02, 0x03, 0x04};
    data[1].row = {0x05, 0x06, 0x07, 0x08};
    data[2].row = {0x09, 0x0a, 0x0b, 0x0c};
    data[3].row = {0x0d, 0x0e, 0x0f, 0x10};
  }

  {
    vmeExtRow4u32* const add = (vmeExtRow4u32*)VME_BASE_BUFFER_0;
    add[0].row = {0x10, 0x0f, 0x0e, 0x0d};
    add[1].row = {0x0c, 0x0b, 0x0a, 0x09};
    add[2].row = {0x08, 0x07, 0x06, 0x05};
    add[3].row = {0x04, 0x03, 0x02, 0x01};
  }

  {
    vmeExtRow4u32* const sub = (vmeExtRow4u32*)VME_BASE_BUFFER_1;
    sub[0].row = {0x01, 0x01, 0x01, 0x01};
    sub[1].row = {0x05, 0x05, 0x05, 0x05};
    sub[2].row = {0x05, 0x05, 0x05, 0x05};
    sub[3].row = {0x09, 0x09, 0x09, 0x09};
  }

  {
    vmeExtRow4u32* const mul = (vmeExtRow4u32*)VME_BASE_BUFFER_2;
    mul[0].row = {0x01, 0x02, 0x01, 0x02};
    mul[1].row = {0x01, 0x02, 0x01, 0x02};
    mul[2].row = {0x01, 0x02, 0x01, 0x02};
    mul[3].row = {0x01, 0x02, 0x01, 0x02};
  }
}

@kernel add build, sub build, mul build
void meLibOnProcess(void) {

  vmeLibEnable();
  setupScratchpadData();
  vmeLibDisable();

  @kernel add config | async, sub config | async, mul config | async {
    vmeDebugFillWith(VME_BASE_BUFFERS);
    vmeDebugCopy(VME_DBG_IDX_TOP_0);
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
      pspDebugScreenPrintf("Result of 3 different VME contexts executed one after the other:");
      
      pspDebugScreenSetXY(x, y + 2);
      pspDebugScreenPrintf("BASE_0:");
      vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, VME_DBG_IDX_BASE_0, x, y + 3);

      pspDebugScreenSetXY(x + 34, y + 2);
      pspDebugScreenPrintf("BASE_1:");
      vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, VME_DBG_IDX_BASE_1, x + 34, y + 3);
      
      pspDebugScreenSetXY(x, y + 12);
      pspDebugScreenPrintf("BASE_2:");
      vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, VME_DBG_IDX_BASE_2, x, y + 13);
    }
  
    pspDebugScreenSetXY(1, 24);
    pspDebugScreenPrintf("meCounter: 0x%lx", meCounter);
    
    sceDisplayWaitVblank();
    
  } while (!(ctl.Buttons & PSP_CTRL_HOME));
  
  sceKernelDelayThread(100000);
  
  vmeDebugTouch();
  vmeDebugDumpBuffers();
  vmeDebugDumpBuffer(VME_DBG_IDX_TOP_0, "TOP_0");
  vmeDebugFreeBuffers();
  
  sceKernelExitGame();
  return 0;
}
