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

meLibSetSharedUncached32(1);
#define meCounter (meLibSharedMemory[0])

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
