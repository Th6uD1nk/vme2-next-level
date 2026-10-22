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

PSP_MODULE_INFO("vme-mat4x4-batch", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();

#define VECTOR_COUNT 16
#define VECTOR_BATCH_WORD_COUNT (VECTOR_COUNT * 4)
#define VECTOR_MAC_WORD_COUNT 16

meLibSetSharedUncached32(10);
#define meCounter    (meLibSharedMemory[1])

volatile Buffer cancelMask[4] = {
  0, 0, 0xffffffff, 0
};

volatile Buffer sharedMat[16] = {
  
  0x00006EDA, 0xFFFFC000, 0x00000000, 0x00000000,
  0x00004000, 0x00006EDA, 0x00000000, 0x00000000,
  0x00000000, 0x00000000, 0x00007FFF, 0x00000000,
  0x00000000, 0x00000000, 0x00000000, 0x00007FFF,
  
  /*
  0x01, 0x00, 0x00, 0x00,
  0x00, 0x01, 0x00, 0x00,
  0x00, 0x00, 0x01, 0x00,
  0x00, 0x00, 0x00, 0x01,
  */
};

volatile Buffer sharedVec[VECTOR_BATCH_WORD_COUNT] = {

  0x00000001, 0x00000002, 0x00000003, 0x00000004,
  0x00000005, 0x00000000, 0x00000000, 0x00000001,
  0x00000000, 0x00000005, 0x00000000, 0x00000001,
  0x0000000A, 0x0000000A, 0x00000001, 0x00000001,
  0xFFFFFFFD, 0x00000004, 0x00000002, 0x00000001,
  0x00000007, 0xFFFFFFFE, 0x00000005, 0x00000001,
  0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x00000001,
  0x00000064, 0x00000000, 0x00000000, 0x00000001,
  
  0x00000000, 0xFFFFFFCE, 0x00000000, 0x00000001,
  0x00000008, 0x00000008, 0x00000008, 0x00000001,
  0xFFFFFFEC, 0x0000000F, 0x00000003, 0x00000001,
  0x00000002, 0x00000002, 0x00000002, 0x00000002,
  0x00000000, 0x00000000, 0x00000000, 0x00000001,
  0xFFFFFF9C, 0xFFFFFF9C, 0x0000000A, 0x00000001,
  0x00000032, 0xFFFFFFE7, 0x00000007, 0x00000001,
  0x00000001, 0x00000002, 0x00000003, 0x00000004,
};

volatile Buffer sharedRes[VECTOR_BATCH_WORD_COUNT] = {0};

.kernel mulMat direct {
  Int count = (1 + VECTOR_COUNT) * 16 - 1;
  Int lost = 12;

  Agu matrix  = { count: 15, inner0: { count: 15, step: 1 }, repeat: true };
  Agu mask    = { count: 3, inner0: { count: 3, step: 1 }, repeat: true };
  Agu vectors = { count, offset: -16 };
  Agu inter   = { count: count + lost };
  Agu write0  = { count: count + lost, bubbles: 5, sync: true };
  Agu write2  = { count: count + lost, bubbles: 1, sync: true };
  Agu write3  = { count, cyc: auto - 1 };

  Staging s0, s1, s2, s3;

  .pe0 { .top = matrix; .base = inter; .write = write0; s0 = mac(top0, top1); }
  .pe1 { .top = vectors; s1 = top2 & s0; }
  .pe2 { .top = mask; .base = inter; .write = write2; s2 = acc(s1); }
  .pe3 { .write = write3; s3 = subacst(s2, base2, 0); .subacst(base0, s3, 0); }
}

void meLibOnProcess(void) {

  @kernel mulMat config {
    Transfer matrixTransfer = { type: words, mode: basic, memory: sharedMat, count: 15 };
    Transfer maskTransfer   = { type: words, mode: basic, memory: cancelMask, count: 3 };
    Transfer vectorTransfer = {
      type: words, mode: extended, memory: sharedVec,
      dims: { count: 63, gap: 0 }, step: 4,
      group: { size: 3, outer: 16, inner: 1 }
    };

    .load { .transfer = matrixTransfer; .scope = global; .offsets { .top0 = 0; } }
    .load { .transfer = maskTransfer; .scope = global; .offsets { .top2 = 0; } }
    for i in 0..3 {
      .load { .transfer = vectorTransfer; .scope = global; .offsets { top[1] = i * 4; } }
    }
  }

  while (1) {

    @kernel mulMat exec {
      Transfer resultTransfer = {
        type: words, mode: extended, memory: sharedRes,
        dims: { count: 63, gap: 3 }, step: 4,
        group: { size: 0, outer: 0, inner: 0 }
      };

      if (meCoreHwMutexTryLock() >= 0) {
        .store { .transfer = resultTransfer; .scope = global; .offsets { .base3 = VECTOR_MAC_WORD_COUNT + 3; } }
        meCoreHwMutexUnlock();
      }
    }

    meLibDelayPipeline();
    meCounter += 1;
  }
}

void displayVectors() {

  while (meLibCallHwMutexTryLock() < 0) {
    sceKernelDelayThread(1);
  }
  
  const u32* const out = (u32*)(0x40000000 | (u32)sharedRes);

  pspDebugScreenSetXY(0, 2);
  pspDebugScreenPrintf("VME Output Vectors:\n");
  
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[0], out[1], out[2], out[3]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[4], out[5], out[6], out[7]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[8], out[9], out[10], out[11]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[12], out[13], out[14], out[15]);
  
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[16], out[17], out[18], out[19]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[20], out[21], out[22], out[23]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[24], out[25], out[26], out[27]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[28], out[29], out[30], out[31]);
  
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[32], out[33], out[34], out[35]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[36], out[37], out[38], out[39]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[40], out[41], out[42], out[43]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[44], out[45], out[46], out[47]);
  
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[48], out[49], out[50], out[51]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[52], out[53], out[54], out[55]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[56], out[57], out[58], out[59]);
  pspDebugScreenPrintf("%08lx, %08lx, %08lx, %08lx\n", out[60], out[61], out[62], out[63]);
  
  meLibCallHwMutexUnlock();
}


int main() {
  
  meLibDefaultInit();
  pspDebugScreenInit();
  
  SceCtrlData ctl;
  do {
    
    sceCtrlPeekBufferPositive(&ctl, 1);
    
    pspDebugScreenSetXY(0, 0);
    pspDebugScreenPrintf("ME Counter: 0x%08lx", meCounter);
    displayVectors();
    
    sceDisplayWaitVblank();
    
  } while (!(ctl.Buttons & PSP_CTRL_HOME));
  
  sceKernelDelayThread(100000);
  
  sceKernelExitGame();
  return 0;
}
