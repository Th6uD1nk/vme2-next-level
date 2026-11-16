#include <pspctrl.h>
#include <pspdisplay.h>
#include <pspkernel.h>
#include <psppower.h>

#include <me-core-mapper/me-core.h>
#include <me-core-mapper/vme-fu-opcodes.h>
#include <vme-ext.h>
#include <debug.h>

PSP_MODULE_INFO("vme-extended-two-pass", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT(16);

meLibSetSharedUncached32(1);
#define meCounter (meLibSharedMemory[0])

volatile Buffer pass1In0[16] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };
volatile Buffer pass1In1[16] = { 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32 };
volatile Buffer pass1In2[16] = { 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48 };
volatile Buffer pass1In3[16] = { 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64 };

volatile Buffer pass2In0[16] = { 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115 };
volatile Buffer pass2In1[16] = { 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215 };
volatile Buffer pass2In2[16] = { 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315 };
volatile Buffer pass2In3[16] = { 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415 };

volatile Buffer out0[16] = { 0 };
volatile Buffer out1[16] = { 0 };
volatile Buffer out2[16] = { 0 };
volatile Buffer out3[16] = { 0 };

@emulate "two-pass"
.kernel twoPass extended {
  Staging s[4];
  Transfer p1[4] = {
    { memory: pass1In0, count: 15 }, { memory: pass1In1, count: 15 },
    { memory: pass1In2, count: 15 }, { memory: pass1In3, count: 15 }
  };
  Transfer p2[4] = {
    { memory: pass2In0, count: 15 }, { memory: pass2In1, count: 15 },
    { memory: pass2In2, count: 15 }, { memory: pass2In3, count: 15 }
  };
  Transfer dst[4] = {
    { memory: out0, count: 15 }, { memory: out1, count: 15 },
    { memory: out2, count: 15 }, { memory: out3, count: 15 }
  };
  .load { .transfer = p1[0]; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = p1[1]; .scope = global; .offsets { .top1 = 0; } }
  .load { .transfer = p1[2]; .scope = global; .offsets { .top2 = 0; } }
  .load { .transfer = p1[3]; .scope = global; .offsets { .top3 = 0; } }
  .load { .transfer = p2[0]; .scope = global; .offsets { .top4 = 0; } }
  .load { .transfer = p2[1]; .scope = global; .offsets { .top5 = 0; } }
  .load { .transfer = p2[2]; .scope = global; .offsets { .top6 = 0; } }
  .load { .transfer = p2[3]; .scope = global; .offsets { .top7 = 0; } }
  for i in 0..3 {
    pe[i] {
      .top = { count: 15 };
      s[i] = top[i] + (i + 1);
    }
  }
  for i in 4..7 {
    pe[i] {
      .top = { count: 15 };
      .write = { count: 15, cyc: auto };
      .spad = top[i] + s[i - 4];
    }
  }
  .store { .transfer = dst[0]; .scope = global; .offsets { .base4 = 0; } }
  .store { .transfer = dst[1]; .scope = global; .offsets { .base5 = 0; } }
  .store { .transfer = dst[2]; .scope = global; .offsets { .base6 = 0; } }
  .store { .transfer = dst[3]; .scope = global; .offsets { .base7 = 0; } }
}

void meLibOnProcess(void) {
  @kernel twoPass config | exec {
    for (int i = 0; i < 4; ++i) vmeDebugFillAtWith(i, VME_BASE_BUFF0_WOFF + i * 0x800 + 0x400);
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
    pspDebugScreenSetXY(1, 1);
    pspDebugScreenPrintf("Extended two-pass VME sample (meCounter: 0x%lx)", meCounter);
    for (int i = 0; i < 4; ++i) vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, i, (i & 1) ? 35 : 1, (i >> 1) ? 9 : 3);
    sceDisplayWaitVblank();
  } while (!(ctl.Buttons & PSP_CTRL_HOME));

  sceKernelDelayThread(100000);
  vmeDebugTouch();
  vmeDebugDumpBuffers();
  vmeDebugFreeBuffers();
  sceKernelExitGame();
  return 0;
}
