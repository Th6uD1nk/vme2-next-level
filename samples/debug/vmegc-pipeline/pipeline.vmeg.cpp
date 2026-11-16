#include <pspctrl.h>
#include <pspdisplay.h>
#include <pspkernel.h>
#include <psppower.h>
#include <me-core-mapper/me-core.h>
#include <me-core-mapper/vme-fu-opcodes.h>
#include <vme-ext.h>
#include <debug.h>

PSP_MODULE_INFO("vme-pipeline", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);
ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT(16);
meLibSetSharedUncached32(1);
#define meCounter (meLibSharedMemory[0])

volatile Buffer in0[16] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };
volatile Buffer in1[16] = { 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32 };
volatile Buffer in2[16] = { 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48 };
volatile Buffer in3[16] = { 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64 };

volatile Buffer out0[16] = { 0 };
volatile Buffer out1[16] = { 0 };
volatile Buffer out2[16] = { 0 };
volatile Buffer out3[16] = { 0 };

@emulate "slot-dag"
.kernel pipeSlotDag pipeline {
  Transfer ta = { memory: in0, count: 15 }, tb = { memory: in1, count: 15 };
  Transfer dst = { memory: out0, count: 15 };
  .load { .transfer = ta; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tb; .scope = global; .offsets { .base0 = 0; } }
  .flow {
    .count = 15;
    Slot tap = (base0 & 0xff) >> 1;
    .slot = (top0 & 0xff) + tap;
    .slot = slot * 2;
    for i in 0..6 { .slot = slot + 1; }
    .slot = slot + tap;
  }
  .store { .transfer = dst; .scope = global; }
}

@emulate "four-pass"
.kernel pipeFourPass pipeline {
  Transfer tc = { memory: in2, count: 15 }, td = { memory: in3, count: 15 };
  Transfer dst = { memory: out1, count: 15 };
  .load { .transfer = tc; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = td; .scope = global; .offsets { .top1 = 0; } }
  .flow {
    .count = 15;
    Slot stage[2];
    stage[0] = (top0 & 0x3f) + 3;
    stage[1] = (top1 >> 1) + 5;
    .slot = stage[0] + stage[1];
    .slot = slot * 2;
    for i in 0..19 { .slot = slot + 1; }
    .slot = slot + stage[0];
  }
  .store { .transfer = dst; .scope = global; }
}

void meLibOnProcess(void) {
  @kernel pipeSlotDag config | exec, pipeFourPass config | exec {
    meCoreMemcpy((void*)&vmeDebugBuffers[0], (void*)out0, 64);
    meCoreMemcpy((void*)&vmeDebugBuffers[16], (void*)out1, 64);
  }
  while (1) meCounter += 1;
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
    pspDebugScreenPrintf("Pipeline VME sample (meCounter: 0x%lx)", meCounter);
    for (int i = 0; i < 4; ++i) vmeDebugDisplayBuffer(VME_DEBUG_DIGIT_4, i, (i & 1) ? 35 : 1, (i >> 1) ? 9 : 3);
    sceDisplayWaitVblank();
  } while (!(ctl.Buttons & PSP_CTRL_HOME));
  sceKernelDelayThread(100000);
  vmeDebugTouch();
  vmeDebugDumpBuffers();
  vmeDebugFreeBuffers();
  sceKernelExitGame();
}
