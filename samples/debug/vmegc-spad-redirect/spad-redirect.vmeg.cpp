#include <pspctrl.h>
#include <pspdisplay.h>
#include <pspkernel.h>
#include <psppower.h>
#include <me-core-mapper/me-core.h>
#include <me-core-mapper/vme-fu-opcodes.h>
#include <debug.h>

PSP_MODULE_INFO("vme-spad-redirect", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT(16);

meLibSetSharedUncached32(10);
#define meCounter (meLibSharedMemory[1])

volatile Buffer sharedTop0[16] = {
  0x1, 0x2, 0x3, 0x4,
  0x5, 0x6, 0x7, 0x8,
  0x9, 0xa, 0xb, 0xc,
  0xd, 0xe, 0xf, 0x10,
};

volatile Buffer sharedTop1[16] = {
  0x10, 0x20, 0x30, 0x40,
  0x50, 0x60, 0x70, 0x80,
  0x90, 0xa0, 0xb0, 0xc0,
  0xd0, 0xe0, 0xf0, 0x100,
};

volatile Buffer sharedTop2[16] = {
  0x100, 0x200, 0x300, 0x400,
  0x500, 0x600, 0x700, 0x800,
  0x900, 0xa00, 0xb00, 0xc00,
  0xd00, 0xe00, 0xf00, 0x1000,
};

volatile Buffer sharedTop3[16] = {
  0x1000, 0x2000, 0x3000, 0x4000,
  0x5000, 0x6000, 0x7000, 0x8000,
  0x9000, 0xa000, 0xb000, 0xc000,
  0xd000, 0xe000, 0xf000, 0x10000,
};

volatile Buffer sharedFill[16] = {
  0x5555, 0x5555, 0x5555, 0x5555,
  0x5555, 0x5555, 0x5555, 0x5555,
  0x5555, 0x5555, 0x5555, 0x5555,
  0x5555, 0x5555, 0x5555, 0x5555,
};

@emulate "spad-redirect"
.kernel runSpadRedirect direct {
  Int count = 16 - 1;

  Transfer t0 = { memory: sharedTop0, count };
  Transfer t3 = { memory: sharedTop3, count };
  Transfer tf = { memory: sharedFill, count };

  .load { .transfer = t0; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = t3; .scope = global; .offsets { .top3 = 0; } }
  .load { .transfer = tf; .scope = global; .offsets { .base0 = 0; .base1 = 0; .base2 = 0; .base3 = 0; } }

  Agu top = { count };

  .pe0 {
    .top = top;
    .write = { count, cyc: auto };
    .spad[2] = top0 + 1;
  }

  .pe3 {
    .top = top;
    .write = { count, cyc: auto };
    .spad[0] = top3 + 2;
  }
}

@kernel runSpadRedirect config | exec
void runSpadRedirectRun(void) {
}

@emulate "rotate"
.kernel runRotateSpad direct {
  Int count = 16 - 1;

  Transfer in[4] = {
    { memory: sharedTop0, count },
    { memory: sharedTop1, count },
    { memory: sharedTop2, count },
    { memory: sharedTop3, count }
  };

  for p in 0..3 {
    .load { .transfer = in[p]; .scope = global; .offsets { top[p] = 0; } }
    pe[p] {
      .top = { count };
      .write = { count, cyc: auto };
      .spad[(p + 1) % 4] = top[p] + 10;
    }
  }
}

@kernel runRotateSpad config | exec
void runRotateSpadRun(void) {
}

void meLibOnProcess(void) {
  meCoreDcacheWritebackInvalidateAll();
  meLibExceptionHandlerInit(0);
  vmeLibEnable();
  vmeLibWipe();

  {
    vmeLibStart();
    runSpadRedirectRun();
    vmeLibFinish();
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
      pspDebugScreenPrintf("Result of the 4 Processing Elements (Spad Redirect):");

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
