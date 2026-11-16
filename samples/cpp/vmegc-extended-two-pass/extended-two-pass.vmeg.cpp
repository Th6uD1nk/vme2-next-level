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

void meLibOnProcess(void) {
  while (1) {
    meCounter += 1;
  }
}

int main() {
  scePowerSetClockFrequency(333, 333, 166);
  meLibDefaultInit();
  pspDebugScreenInit();

  SceCtrlData ctl;
  do {
    sceCtrlPeekBufferPositive(&ctl, 1);
    pspDebugScreenSetXY(1, 1);
    pspDebugScreenPrintf("Extended two-pass VME sample (meCounter: 0x%lx)", meCounter);
    sceDisplayWaitVblank();
  } while (!(ctl.Buttons & PSP_CTRL_HOME));

  sceKernelDelayThread(100000);
  sceKernelExitGame();
  return 0;
}
