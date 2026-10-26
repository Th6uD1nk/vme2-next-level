#include <me-core-mapper/me-core.h>
#include <me-core-mapper/vme-fu-opcodes.h>

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

@emulate "saturate-clamp"
.kernel runContext direct {
  Int count = 16 - 1;

  Transfer top0Transfer = { type: words, mode: basic, memory: sharedTop0, count };
  Transfer top1Transfer = { type: words, mode: basic, memory: sharedTop1, count };
  Transfer top2Transfer = { type: words, mode: basic, memory: sharedTop2, count };
  Transfer top3Transfer = { type: words, mode: basic, memory: sharedTop3, count };
  Transfer base0Transfer = { type: words, mode: basic, memory: sharedBase0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }
  .load { .transfer = top2Transfer; .scope = global; .offsets { .top2 = 0; } }
  .load { .transfer = top3Transfer; .scope = global; .offsets { .top3 = 0; } }
  .load { .transfer = base0Transfer; .scope = global; .offsets { .base0 = SHARED_BASE_0_INPUT_OFFSET; } }

  Agu top   = { count };
  Agu base  = { count, offset: SHARED_BASE_0_INPUT_OFFSET };
  Agu write = { count, cyc: auto };

  for p in 0..3 {
    pe[p] {
      .top = top;
      .write = write;
      .spad = clamp(sat(top[p] + base0, 7), 0, 0x7fffff);
    }
  }

  .pe0 { .base = base; }
}

@kernel runContext config | exec
void run(void) {
}
