kernel runContext direct {
  global buffers {
    top0, 16 words, from sharedTop0;
    top1, 16 words, from sharedTop1;
    top2, 16 words, from sharedTop2;
    top3, 16 words, from sharedTop3;
    base0, 16 words, at SHARED_BASE_0_INPUT_OFFSET, from sharedBase0;
  }

  icn top = 0, write = 0, base = 0x4440;

  const count = 16 - 1;

  for p in 0..3 {
    pe[p].out = clamp(sat(top[p] + base0, 7), 0, 0x7fffff);
  }

  pe0.top   = { count };
  pe0.base  = { count, offset: SHARED_BASE_0_INPUT_OFFSET };
  pe0.write = { count, cyc: 0x09 };
}
