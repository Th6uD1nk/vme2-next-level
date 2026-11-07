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

volatile Buffer in0[256] = {
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff,
  0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff,
  0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff,
  0x2, 0x2, 0x2, 0x2,
  0x2, 0x2, 0x2, 0x2,
  0x2, 0x2, 0x2, 0x2,
  0xfffffffe, 0xfffffffe, 0xfffffffe, 0xfffffffe,
  0xfffffffe, 0xfffffffe, 0xfffffffe, 0xfffffffe,
  0xfffffffe, 0xfffffffe, 0xfffffffe, 0xfffffffe,
  0x7fffff, 0x7fffff, 0x7fffff, 0x7fffff,
  0x7fffff, 0x7fffff, 0x7fffff, 0x7fffff,
  0x7fffff, 0x7fffff, 0x7fffff, 0x7fffff,
  0xff800000, 0xff800000, 0xff800000, 0xff800000,
  0xff800000, 0xff800000, 0xff800000, 0xff800000,
  0xff800000, 0xff800000, 0xff800000, 0xff800000,
  0x555555, 0x555555, 0x555555, 0x555555,
  0x555555, 0x555555, 0x555555, 0x555555,
  0x555555, 0x555555, 0x555555, 0x555555,
  0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa,
  0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa,
  0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa, 0xffaaaaaa,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xffffff00, 0xffffff00, 0xffffff00, 0xffffff00,
  0xffffff00, 0xffffff00, 0xffffff00, 0xffffff00,
  0xffffff00, 0xffffff00, 0xffffff00, 0xffffff00,
  0x1234, 0x1234, 0x1234, 0x1234,
  0x1234, 0x1234, 0x1234, 0x1234,
  0x1234, 0x1234, 0x1234, 0x1234,
  0x1f4d40, 0xffdacb41, 0x85982, 0xffb05643,
  0xff8ab0c4, 0x4c87c5, 0xff8112c6, 0x321807,
  0xff8429c8, 0x2f3e09, 0xffec7b4a, 0xffb66b0b,
  0x29fc8c, 0x13da4d, 0xffce2f0e, 0xffba478f,
  0xf1d10, 0x532c11, 0xfffc8012, 0xff872e93,
  0x296454, 0xffb94fd5, 0x1dd696, 0x76657,
  0xffca7098, 0xffe84059, 0x2a875a, 0x16461b,
  0x1b821c, 0x11add, 0xffe3abde, 0xffcd2c1f,
  0x7da020, 0x47a121, 0x6b9fa2, 0x59d323,
  0xff8f70a4, 0xff888e65, 0xff9b15a6, 0xff8f35a7,
  0xffcd83e8, 0x611d29, 0x64212a, 0x475b6b,
  0x456e2c, 0xfffbff2d, 0x3fd46e, 0xffacf4ef,
  0xffa61f70, 0x60e6f1, 0x50ba72, 0xff868f73,
  0x85f4, 0x469e75, 0xffcc5776, 0xffa2cdf7,
  0xff86ac38, 0xffae7ab9, 0xffc8807a, 0x50057b,
  0x75cfbc, 0xffc48a7d, 0xffe147be, 0x5c43bf,
  0xffe44067, 0xfffa27f3, 0xff89b0d1, 0xffe3d198,
  0xffc649f0, 0xfff8c78c, 0x260a88, 0xff9d80d3,
  0x7b9190, 0x71b534, 0x30233f, 0xffa9c314,
  0xffac26d1, 0xffbe3eaa, 0x49cff, 0xfffb4472,
  0xffd7fe48, 0xffc04d27, 0xfffea135, 0xffd038f9,
  0x2f87de, 0x53c934, 0xffd5114e, 0x6328b0,
  0xffdc0b4a, 0x12fc10, 0xff8136d8, 0x17c3d5,
  0xffcb0d83, 0x127e7e, 0x6af810, 0x731aa4,
  0xffdebd57, 0xfffcf84d, 0x561ed7, 0x16d231,
  0x4dca39, 0x53df3c, 0x360c26, 0xffe1979f,
  0x540356, 0xffee0d69, 0x2e4048, 0xffcbef3b,
  0xffbe620d, 0xa6032, 0xff80d334, 0x2343a7,
};

volatile Buffer in1[256] = {
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x0, 0x1, 0xffffffff, 0x2,
  0xfffffffe, 0x7fffff, 0xff800000, 0x555555,
  0xffaaaaaa, 0xff, 0xffffff00, 0x1234,
  0x4799cb, 0x4675f0, 0x7d6d5, 0x67f6ba,
  0x324b1f, 0xff8ef004, 0x6b39a9, 0xff9a628e,
  0xff9396f3, 0x3ec7d8, 0xff82523d, 0x1176a2,
  0xfffddd07, 0x760aec, 0xffcc32d1, 0xffede636,
  0x49771b, 0xff8bed40, 0xff801525, 0x30d04a,
  0xfff925ef, 0xffc1b594, 0x68b5f9, 0x77c9e,
  0xff939243, 0xffe38528, 0x4c678d, 0x43f8b2,
  0x2abed7, 0xff8f857c, 0x1643a1, 0x2bad46,
  0x300b2b, 0x1a3490, 0x2025b5, 0x6bdf5a,
  0xffa8bd3f, 0xffc9f864, 0x3b6609, 0x5929ae,
  0xfff2a193, 0x7b3d38, 0x50cfdd, 0x6482c2,
  0x2bb6a7, 0x70ddcc, 0xffdd3831, 0xffef7f56,
  0xffcf223b, 0xffca89a0, 0x1295c5, 0x3251ea,
  0x53168f, 0xffec7034, 0xffec1b19, 0xffdc0bbe,
  0xffe9b1a3, 0xfff19b88, 0xff9381ad, 0x7c8dd2,
  0xffb01f37, 0xffb5715c, 0x76ac81, 0xffcb6866,
  0x173c4e, 0x403621, 0xe8a83, 0xff858f2c,
  0x6c219c, 0xffaabed3, 0x6be48b, 0xffa18436,
  0xffcef905, 0x2fa332, 0x71b156, 0x30911b,
  0x65e0d2, 0xff8641cd, 0x402cd2, 0xff994d5f,
  0x62ca86, 0x7f29ff, 0x59d33f, 0xffff6f20,
  0x7f678d, 0x55740a, 0x500d60, 0x7a865e,
  0xff9869c6, 0xffb9a9d6, 0xffea3977, 0x568235,
  0x17c81d, 0xff933af7, 0x7aba31, 0xffad7a4f,
  0x799c1d, 0xffb72660, 0x12f67d, 0x71c773,
  0x63523c, 0xffbb79ee, 0x5aa78d, 0xffcac558,
  0x5a9768, 0x4f2153, 0xffc86441, 0x49e141,
  0x5fbc51, 0x63e5db, 0xffc1ced7, 0x73091a,
};

volatile Buffer in0b0[256] = {
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x101, 0x101, 0x101, 0x101,
};

volatile Buffer in1b0[256] = {
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
};

volatile Buffer in0b1[256] = {
  0x101, 0x101, 0x101, 0x101,
  0x101, 0x101, 0x101, 0x101,
  0x101, 0x101, 0x101, 0x101,
  0x101, 0x101, 0x101, 0x101,
  0x101, 0x101, 0x101, 0x101,
  0x101, 0x101, 0x101, 0x101,
  0x101, 0x101, 0x101, 0x101,
  0x101, 0x101, 0x101, 0x101,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x7f01, 0x7f01, 0x7f01, 0x7f01,
  0x8001, 0x8001, 0x8001, 0x8001,
  0x8001, 0x8001, 0x8001, 0x8001,
  0x8001, 0x8001, 0x8001, 0x8001,
  0x8001, 0x8001, 0x8001, 0x8001,
  0x8001, 0x8001, 0x8001, 0x8001,
  0x8001, 0x8001, 0x8001, 0x8001,
  0x8001, 0x8001, 0x8001, 0x8001,
  0x8001, 0x8001, 0x8001, 0x8001,
  0x8001, 0x8001, 0x8001, 0x8001,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xfe01, 0xfe01, 0xfe01, 0xfe01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0xff01, 0xff01, 0xff01, 0xff01,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x7f, 0x7f, 0x7f, 0x7f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x17f, 0x17f, 0x17f, 0x17f,
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
};

volatile Buffer in1b1[256] = {
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
};

volatile Buffer in0b2[256] = {
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
  0x7f7f, 0x7f7f, 0x7f7f, 0x7f7f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0x807f, 0x807f, 0x807f, 0x807f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xfe7f, 0xfe7f, 0xfe7f, 0xfe7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0xff7f, 0xff7f, 0xff7f, 0xff7f,
  0x80, 0x80, 0x80, 0x80,
  0x80, 0x80, 0x80, 0x80,
  0x80, 0x80, 0x80, 0x80,
  0x80, 0x80, 0x80, 0x80,
  0x80, 0x80, 0x80, 0x80,
  0x80, 0x80, 0x80, 0x80,
  0x80, 0x80, 0x80, 0x80,
  0x80, 0x80, 0x80, 0x80,
  0x80, 0x80, 0x80, 0x80,
  0x180, 0x180, 0x180, 0x180,
  0x180, 0x180, 0x180, 0x180,
  0x180, 0x180, 0x180, 0x180,
  0x180, 0x180, 0x180, 0x180,
  0x180, 0x180, 0x180, 0x180,
  0x180, 0x180, 0x180, 0x180,
  0x180, 0x180, 0x180, 0x180,
  0x180, 0x180, 0x180, 0x180,
  0x180, 0x180, 0x180, 0x180,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x7f80, 0x7f80, 0x7f80, 0x7f80,
  0x8080, 0x8080, 0x8080, 0x8080,
  0x8080, 0x8080, 0x8080, 0x8080,
  0x8080, 0x8080, 0x8080, 0x8080,
};

volatile Buffer in1b2[256] = {
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
};

volatile Buffer in0b3[256] = {
  0x8080, 0x8080, 0x8080, 0x8080,
  0x8080, 0x8080, 0x8080, 0x8080,
  0x8080, 0x8080, 0x8080, 0x8080,
  0x8080, 0x8080, 0x8080, 0x8080,
  0x8080, 0x8080, 0x8080, 0x8080,
  0x8080, 0x8080, 0x8080, 0x8080,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xfe80, 0xfe80, 0xfe80, 0xfe80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0xfe, 0xfe, 0xfe, 0xfe,
  0xfe, 0xfe, 0xfe, 0xfe,
  0xfe, 0xfe, 0xfe, 0xfe,
  0xfe, 0xfe, 0xfe, 0xfe,
  0xfe, 0xfe, 0xfe, 0xfe,
  0xfe, 0xfe, 0xfe, 0xfe,
  0xfe, 0xfe, 0xfe, 0xfe,
  0xfe, 0xfe, 0xfe, 0xfe,
  0xfe, 0xfe, 0xfe, 0xfe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x1fe, 0x1fe, 0x1fe, 0x1fe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x7ffe, 0x7ffe, 0x7ffe, 0x7ffe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0x80fe, 0x80fe, 0x80fe, 0x80fe,
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
};

volatile Buffer in1b3[256] = {
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
};

volatile Buffer in0b4[256] = {
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
  0xfefe, 0xfefe, 0xfefe, 0xfefe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xfffe, 0xfffe, 0xfffe, 0xfffe,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x1ff, 0x1ff, 0x1ff, 0x1ff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x7fff, 0x7fff, 0x7fff, 0x7fff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0x80ff, 0x80ff, 0x80ff, 0x80ff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xfeff, 0xfeff, 0xfeff, 0xfeff,
  0xffff, 0xffff, 0xffff, 0xffff,
  0xffff, 0xffff, 0xffff, 0xffff,
  0xffff, 0xffff, 0xffff, 0xffff,
  0xffff, 0xffff, 0xffff, 0xffff,
  0xffff, 0xffff, 0xffff, 0xffff,
};

volatile Buffer in1b4[256] = {
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
};

volatile Buffer in0b5[256] = {
  0xffff, 0xffff, 0xffff, 0xffff,
  0xffff, 0xffff, 0xffff, 0xffff,
  0xffff, 0xffff, 0xffff, 0xffff,
  0xffff, 0xffff, 0xffff, 0xffff,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x100, 0x100, 0x100, 0x100,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x7f00, 0x7f00, 0x7f00, 0x7f00,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0x8000, 0x8000, 0x8000, 0x8000,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xfe00, 0xfe00, 0xfe00, 0xfe00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0xff00, 0xff00, 0xff00, 0xff00,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
  0x1, 0x1, 0x1, 0x1,
};

volatile Buffer in1b5[256] = {
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
  0xfe, 0x1fe, 0x7ffe, 0x80fe,
  0xfefe, 0xfffe, 0xff, 0x1ff,
  0x7fff, 0x80ff, 0xfeff, 0xffff,
  0x0, 0x100, 0x7f00, 0x8000,
  0xfe00, 0xff00, 0x1, 0x101,
  0x7f01, 0x8001, 0xfe01, 0xff01,
  0x7f, 0x17f, 0x7f7f, 0x807f,
  0xfe7f, 0xff7f, 0x80, 0x180,
  0x7f80, 0x8080, 0xfe80, 0xff80,
};

volatile Buffer in0b6[256] = {
  0x0, 0xffff0000, 0x0, 0xffff0000,
  0x0, 0x10000, 0xff800000, 0xffff0000,
  0x100, 0xffff0100, 0x10100, 0x10100,
  0x100, 0xffff0100, 0xff800100, 0x7f00,
  0x7f00, 0xff807f00, 0xffff7f00, 0x7f00,
  0x17f00, 0xffff7f00, 0xffff8000, 0xffff8000,
  0xffff8000, 0xff808000, 0x8000, 0x8000,
  0x18000, 0xfe00, 0x1fe00, 0xfe00,
  0xfe00, 0xfffffe00, 0x1fe00, 0xfe00,
  0xffffff00, 0xff80ff00, 0xff80ff00, 0xff00,
  0xffffff00, 0xff00, 0xff00, 0xff00,
  0xff800001, 0xff800001, 0xffff0001, 0x1,
  0xffff0001, 0xffff0001, 0x1, 0x10101,
  0xffff0101, 0x101, 0x101, 0xff800101,
  0xffff0101, 0xffff0101, 0x7f01, 0x7f01,
  0xffff7f01, 0xffff7f01, 0xffff7f01, 0xff807f01,
  0x7f01, 0xff808001, 0xff808001, 0xffff8001,
  0xff808001, 0x18001, 0x18001, 0xff808001,
  0xff80fe01, 0xff80fe01, 0xfffffe01, 0xff80fe01,
  0xff80fe01, 0x1fe01, 0xfffffe01, 0xff80fe01,
  0x1ff01, 0xff01, 0xff80ff01, 0xffffff01,
  0xffffff01, 0xff80ff01, 0x1ff01, 0xff80007f,
  0x1007f, 0xff80007f, 0xffff007f, 0xff80007f,
  0x7f, 0xffff007f, 0xff80017f, 0x17f,
  0xff80017f, 0x1017f, 0xff80017f, 0xff80017f,
  0xffff017f, 0xffff7f7f, 0x7f7f, 0xffff7f7f,
  0xff807f7f, 0x17f7f, 0x17f7f, 0xffff7f7f,
  0x1807f, 0xff80807f, 0xff80807f, 0x807f,
  0x1807f, 0xffff807f, 0xffff807f, 0xffff807f,
  0xfe7f, 0xff80fe7f, 0xfffffe7f, 0xfe7f,
  0x1fe7f, 0xff80fe7f, 0xff80fe7f, 0xff7f,
  0x1ff7f, 0xff7f, 0xffffff7f, 0xffffff7f,
  0xff7f, 0xffffff7f, 0xffff0080, 0xff800080,
  0xff800080, 0xffff0080, 0xff800080, 0x10080,
  0x10080, 0xffff0180, 0x10180, 0x10180,
  0x10180, 0xffff0180, 0xff800180, 0x180,
  0xffff7f80, 0x7f80, 0x17f80, 0xffff7f80,
  0x17f80, 0x17f80, 0xffff7f80, 0xff807f80,
  0xffff8080, 0xff808080, 0xffff8080, 0x8080,
  0xffff8080, 0x8080, 0xffff8080, 0xfe80,
  0x1fe80, 0x1fe80, 0xff80fe80, 0xfffffe80,
  0xfffffe80, 0x1fe80, 0xffffff80, 0xff80ff80,
  0xff80, 0xff80, 0xff80, 0xff80,
  0x1ff80, 0x100fe, 0xffff00fe, 0xffff00fe,
  0xffff00fe, 0xfe, 0xff8000fe, 0xff8000fe,
  0xffff01fe, 0xffff01fe, 0x1fe, 0x1fe,
  0x1fe, 0x101fe, 0x101fe, 0x101fe,
  0xff807ffe, 0x7ffe, 0xff807ffe, 0xffff7ffe,
  0xff807ffe, 0xffff7ffe, 0xffff7ffe, 0x80fe,
  0x80fe, 0xffff80fe, 0x80fe, 0x80fe,
  0x80fe, 0x180fe, 0xff80fefe, 0xff80fefe,
  0xfefe, 0xfffffefe, 0xfffffefe, 0xfefe,
  0xfefe, 0xfffe, 0x1fffe, 0xff80fffe,
  0xfffffffe, 0xfffffffe, 0xfffffffe, 0xfffe,
  0xffff00ff, 0x100ff, 0xff, 0x100ff,
  0xff8000ff, 0xff, 0xff8000ff, 0xff,
  0xffff01ff, 0x101ff, 0x1ff, 0x1ff,
  0x1ff, 0xff8001ff, 0xffff01ff, 0xff807fff,
  0xff807fff, 0xff807fff, 0xffff7fff, 0xffff7fff,
  0xffff7fff, 0x17fff, 0x80ff, 0x80ff,
  0xffff80ff, 0xff8080ff, 0xff8080ff, 0x180ff,
  0x80ff, 0xff80feff, 0x1feff, 0x1feff,
  0x1feff, 0xfffffeff, 0xff80feff, 0xfeff,
  0xffff, 0xffff, 0xffff, 0xffffffff,
};

volatile Buffer in1b6[256] = {
  0xffff0000, 0xffffff00, 0x1fe01, 0xffff807f,
  0xffff7f80, 0xffff01fe, 0xffff00ff, 0x1ffff,
  0xff80fe00, 0x18001, 0xffff7f7f, 0x180,
  0x100fe, 0xfffffffe, 0xfeff, 0x8000,
  0x7f01, 0x17f, 0x10080, 0x1ff80,
  0xff80fefe, 0xff8080ff, 0x7f00, 0xffff0101,
  0x7f, 0xffffff7f, 0xfffffe80, 0x80fe,
  0x7fff, 0xffff0100, 0xff800001, 0x1ff01,
  0x1fe7f, 0x18080, 0x17ffe, 0x101ff,
  0x10000, 0xffffff00, 0x1fe01, 0x807f,
  0xff807f80, 0x101fe, 0x100ff, 0xffffffff,
  0x1fe00, 0x8001, 0xffff7f7f, 0xff800180,
  0xffff00fe, 0xfffffffe, 0xfffffeff, 0xffff8000,
  0xffff7f01, 0xffff017f, 0xff800080, 0xffffff80,
  0xfefe, 0x180ff, 0xffff7f00, 0xffff0101,
  0x1007f, 0xffffff7f, 0xfe80, 0x80fe,
  0xffff7fff, 0xffff0100, 0xff800001, 0xff01,
  0xfffffe7f, 0x8080, 0x7ffe, 0xff8001ff,
  0x0, 0x1ff00, 0x1fe01, 0x807f,
  0xff807f80, 0x101fe, 0xffff00ff, 0xffffffff,
  0xff80fe00, 0x18001, 0x17f7f, 0xffff0180,
  0xff8000fe, 0x1fffe, 0xff80feff, 0x18000,
  0xff807f01, 0x17f, 0xff800080, 0xff80ff80,
  0xfefe, 0xffff80ff, 0x7f00, 0x10101,
  0xff80007f, 0xff80ff7f, 0xff80fe80, 0x180fe,
  0x17fff, 0x10100, 0x10001, 0xff01,
  0xff80fe7f, 0xffff8080, 0xff807ffe, 0x101ff,
  0x0, 0x1ff00, 0x1fe01, 0x1807f,
  0x7f80, 0xffff01fe, 0x100ff, 0xffff,
  0x1fe00, 0x18001, 0x17f7f, 0xff800180,
  0xfe, 0xff80fffe, 0xfeff, 0x18000,
  0xff807f01, 0x17f, 0xffff0080, 0x1ff80,
  0xff80fefe, 0x180ff, 0x17f00, 0xffff0101,
  0xffff007f, 0x1ff7f, 0x1fe80, 0x80fe,
  0xff807fff, 0x10100, 0x10001, 0xffffff01,
  0xfe7f, 0xffff8080, 0x7ffe, 0x101ff,
  0x0, 0xffffff00, 0xfffffe01, 0x1807f,
  0x7f80, 0x1fe, 0x100ff, 0x1ffff,
  0xfffffe00, 0x18001, 0xffff7f7f, 0x10180,
  0x100fe, 0xfffe, 0xfffffeff, 0x8000,
  0xff807f01, 0xff80017f, 0xff800080, 0x1ff80,
  0x1fefe, 0xff8080ff, 0x17f00, 0xffff0101,
  0xffff007f, 0x1ff7f, 0x1fe80, 0xff8080fe,
  0xff807fff, 0xff800100, 0xffff0001, 0xffffff01,
  0x1fe7f, 0xff808080, 0x17ffe, 0xffff01ff,
  0xff800000, 0xffffff00, 0x1fe01, 0xffff807f,
  0xff807f80, 0xffff01fe, 0xff, 0xffffffff,
  0xfffffe00, 0xff808001, 0xffff7f7f, 0xffff0180,
  0xffff00fe, 0xfffe, 0xfeff, 0x8000,
  0x7f01, 0x1017f, 0x80, 0xffffff80,
  0x1fefe, 0xffff80ff, 0x7f00, 0xffff0101,
  0xff80007f, 0xffffff7f, 0xfffffe80, 0x80fe,
  0xff807fff, 0x100, 0x10001, 0xff01,
  0xfe7f, 0xff808080, 0xff807ffe, 0x1ff,
  0xffff0000, 0xffffff00, 0xfe01, 0x807f,
  0xffff7f80, 0xffff01fe, 0xff8000ff, 0xffff,
  0xfe00, 0x8001, 0x7f7f, 0xffff0180,
  0xff8000fe, 0xfffffffe, 0xfeff, 0x18000,
  0xffff7f01, 0xffff017f, 0x80, 0xff80ff80,
  0xfefe, 0x80ff, 0x7f00, 0x10101,
  0xffff007f, 0xff80ff7f, 0x1fe80, 0xffff80fe,
  0xff807fff, 0x100, 0xffff0001, 0xff80ff01,
  0x1fe7f, 0xffff8080, 0x7ffe, 0xffff01ff,
  0xff800000, 0xffffff00, 0xfffffe01, 0x1807f,
};

volatile Buffer in0b7[256] = {
  0x4799f0, 0x4675cc, 0x7d6d3, 0x67f69d,
  0x324b27, 0xff8ef00c, 0x6b39ab, 0xff9a6284,
  0xff9396c1, 0x3ec7e4, 0xff825225, 0x117686,
  0xfffddd26, 0x760aca, 0xffcc32fd, 0xffede634,
  0x497701, 0xff8bed75, 0xff801507, 0x30d077,
  0xfff925e8, 0xffc1b58a, 0x68b5f2, 0x77cb9,
  0xff939251, 0xffe3851d, 0x4c679d, 0x43f882,
  0x2abecb, 0xff8f8572, 0x1643a2, 0x2bad73,
  0x300b11, 0x1a34b8, 0x2025be, 0x6bdf55,
  0xffa8bd35, 0xffc9f872, 0x3b6631, 0x5929af,
  0xfff2a1b9, 0x7b3d3b, 0x50cff5, 0x6482e2,
  0x2bb6be, 0x70ddc0, 0xffdd3824, 0xffef7f48,
  0xffcf222b, 0xffca89ae, 0x1295f1, 0x3251c7,
  0x531682, 0xffec7023, 0xffec1b37, 0xffdc0bb2,
  0xffe9b187, 0xfff19b8b, 0xff9381ab, 0x7c8df8,
  0xffb01f39, 0xffb57152, 0x76acbd, 0xffcb686d,
  0x173c4e, 0x403621, 0xe8a83, 0xff858f2c,
  0x6c219c, 0xffaabed3, 0x6be48b, 0xffa18436,
  0xffcef905, 0x2fa332, 0x71b156, 0x30911b,
  0x65e0d2, 0xff8641cd, 0x402cd2, 0xff994d5f,
  0x62ca86, 0x7f29ff, 0x59d33f, 0xffff6f20,
  0x7f678d, 0x55740a, 0x500d60, 0x7a865e,
  0xff9869c6, 0xffb9a9d6, 0xffea3977, 0x568235,
  0x17c81d, 0xff933af7, 0x7aba31, 0xffad7a4f,
  0x799c1d, 0xffb72660, 0x12f67d, 0x71c773,
  0x63523c, 0xffbb79ee, 0x5aa78d, 0xffcac558,
  0x5a9768, 0x4f2153, 0xffc86441, 0x49e141,
  0x5fbc51, 0x63e5db, 0xffc1ced7, 0x73091a,
  0x5092f2, 0xffdacdd5, 0x600cc5, 0xffe60099,
  0x5bf803, 0x2669ee, 0x6c6283, 0xffba71bd,
  0x376a9b, 0xffea6589, 0x30ab24, 0xffdbbfce,
  0x64bfbf, 0xfff69336, 0xff902ebe, 0xffb914bd,
  0xffff8d6a, 0x1e3a3, 0xffc65d39, 0x477329,
  0x63aa38, 0xffb519ea, 0xff87e96e, 0xffe11d5b,
  0x4dabe, 0x382977, 0xffc3507c, 0x5681da,
  0xffd30a6c, 0x478e43, 0x743f84, 0x185d06,
  0xffa9d19a, 0xffc6fa37, 0xff858397, 0x1bf96c,
  0xfff3f017, 0xffd0760f, 0x2f4567, 0xfffbb766,
  0xfff92f4d, 0x581e5, 0x1ac1d9, 0x13b869,
  0xffc6eda6, 0x35487f, 0x6f11a2, 0x39c76f,
  0x572925, 0x9b9c, 0x17a085, 0xffe172c6,
  0xff81245a, 0x4d33bf, 0x615862, 0xffc34b54,
  0xff9db080, 0x32a206, 0x3b1d5f, 0xff8e91f7,
  0xffbbaa4f, 0xffb0a376, 0x177ab9, 0x4b1939,
  0xffef9def, 0x12ff06, 0xffb7d01f, 0x3c1a65,
  0x6a99fd, 0xfffa95b7, 0xffc5ad31, 0x148980,
  0xffb891d2, 0xffdce2f3, 0xffda73f2, 0x234fa0,
  0x38502b, 0xff968815, 0x1bc63f, 0x52acf1,
  0x5189f7, 0xff822240, 0xff84d185, 0x34ecbf,
  0xffce922e, 0xffed7f0b, 0xff8821ad, 0x65213,
  0xffc21711, 0x2e5121, 0x4814a4, 0x465d0a,
  0x39ad9, 0x4c1b55, 0xfff68886, 0x2957d5,
  0xffae4abc, 0xffc4d1c0, 0x66d7fe, 0xffb1d2f2,
  0x1915a5, 0x124393, 0x68e143, 0x574383,
  0xffc09f10, 0x799a21, 0xff85535f, 0x37ae28,
  0xffa6e871, 0xffbc1105, 0x84e2b, 0x63dced,
  0x30a4d2, 0xffffcbe7, 0xffef26e6, 0x4f4a9f,
  0xff897cb1, 0xfff6997e, 0xfff50152, 0x33b11d,
  0x1e72b5, 0x5647b1, 0xffa84c41, 0x269f71,
  0xffdd1f35, 0x4fb5a8, 0xffaef875, 0xffa9ab85,
  0xfff4e149, 0x6f31c7, 0xffa896ec, 0xffd96a96,
  0xfff827b3, 0xffcd5cb4, 0x276739, 0xffc39779,
  0xffbb948f, 0x6a225a, 0x1ee0a, 0xffde0aaa,
  0xffe2b20f, 0xffc9cf1e, 0x63ae6b, 0x7871bc,
};

volatile Buffer in1b7[256] = {
  0x1f4d63, 0xffdacb7a, 0x859a0, 0xffb0567e,
  0xff8ab0e1, 0x4c87ea, 0xff8112f2, 0x32183d,
  0xff8429c7, 0x2f3e39, 0xffec7b6d, 0xffb66b0d,
  0x29fca6, 0x13da78, 0xffce2f16, 0xffba4780,
  0xf1d05, 0x532c12, 0xfffc803a, 0xff872ea7,
  0x29644e, 0xffb94fde, 0x1dd69f, 0x76678,
  0xffca709c, 0xffe84070, 0x2a8763, 0x164600,
  0x1b820b, 0x11ae6, 0xffe3abc8, 0xffcd2c25,
  0x7da021, 0x47a13d, 0x6b9fad, 0x59d322,
  0xff8f70bc, 0xff888e70, 0xff9b15b3, 0xff8f3585,
  0xffcd83da, 0x611d21, 0x642123, 0x475b63,
  0x456e36, 0xfffbff17, 0x3fd47b, 0xffacf4c3,
  0xffa61f79, 0x60e6fd, 0x50ba62, 0xff868f6c,
  0x85f9, 0x469e66, 0xffcc5743, 0xffa2cdf1,
  0xff86ac1f, 0xffae7abd, 0xffc88061, 0x500563,
  0x75cfbd, 0xffc48a7c, 0xffe14799, 0x5c4390,
  0xffe44067, 0xfffa27f3, 0xff89b0d1, 0xffe3d198,
  0xffc649f0, 0xfff8c78c, 0x260a88, 0xff9d80d3,
  0x7b9190, 0x71b534, 0x30233f, 0xffa9c314,
  0xffac26d1, 0xffbe3eaa, 0x49cff, 0xfffb4472,
  0xffd7fe48, 0xffc04d27, 0xfffea135, 0xffd038f9,
  0x2f87de, 0x53c934, 0xffd5114e, 0x6328b0,
  0xffdc0b4a, 0x12fc10, 0xff8136d8, 0x17c3d5,
  0xffcb0d83, 0x127e7e, 0x6af810, 0x731aa4,
  0xffdebd57, 0xfffcf84d, 0x561ed7, 0x16d231,
  0x4dca39, 0x53df3c, 0x360c26, 0xffe1979f,
  0x540356, 0xffee0d69, 0x2e4048, 0xffcbef3b,
  0xffbe620d, 0xa6032, 0xff80d334, 0x2343a7,
  0xffabd00c, 0xffe72179, 0xffc8703d, 0x3ea21a,
  0xffc24924, 0x363f37, 0xffcd25bf, 0x2bfbc2,
  0x22308b, 0x5312d2, 0x2f2a16, 0xffdafe20,
  0xffce62cf, 0x603c84, 0xffebc77c, 0xff861fbe,
  0x40a9c6, 0x743dba, 0xffa909bb, 0x5974f4,
  0x3efb77, 0x5cde3f, 0xfff05632, 0xfff1a989,
  0xffddb7c9, 0xffbcb8bb, 0xffd368ae, 0x1190ed,
  0xff8c890b, 0x1d3e7d, 0xff85c914, 0x46a5a7,
  0xffbe5a1e, 0x4748e0, 0x3e84ed, 0xffc08b3c,
  0x410c0f, 0xffd3118f, 0xffb5233e, 0xff8898b7,
  0x53c278, 0xff869cb6, 0x14b37e, 0x136923,
  0xffde0d38, 0x50fd04, 0xfff49a7c, 0xffd99001,
  0xffe4714d, 0x77324b, 0xfff31154, 0xffeced38,
  0x3556bd, 0xffb556cc, 0xfff27b3a, 0x3876f0,
  0x2d3b63, 0x627323, 0xffc87420, 0xffc270c6,
  0xff88724b, 0xffe8aa4b, 0xff9782fb, 0xffdbf8ff,
  0x4821bd, 0xff8b0542, 0x4b8c33, 0x7b0f75,
  0x2aad5f, 0xffa068ff, 0x4f8420, 0xffb607e5,
  0x12c840, 0x440e6d, 0xffbdb589, 0xff9f896f,
  0xfff5baf6, 0xffc0bb43, 0xffb13d77, 0xffe7dff8,
  0x940f4, 0xffe12b1f, 0xffd7371e, 0xffa7eb04,
  0x2a2687, 0xffa3f6ba, 0xffe9c900, 0xfff651e4,
  0xff9b0c21, 0xfff0c86e, 0x51f690, 0xfff0c0f1,
  0x3f9846, 0xffdfacfd, 0x4141fd, 0xffaa4f02,
  0xd6e47, 0x7eed05, 0x1f052a, 0xfff1e317,
  0xfff0d59e, 0x26bb5f, 0xffe892d9, 0xffc0a980,
  0xffec8c78, 0x19f869, 0xff832083, 0xfff3ee0a,
  0x676c73, 0xffc64967, 0xffba54d2, 0x2c7882,
  0xffbd2a9c, 0x31b70b, 0xffc0ce03, 0x1b8ae3,
  0xffb16ec0, 0x4d2ef4, 0xffef639d, 0x86c33,
  0x448874, 0x218f1, 0xff9ce89f, 0x6e0358,
  0xffaa101a, 0xff88208e, 0xffabb902, 0xfffad227,
  0x7c9b78, 0x645151, 0xff8c3fb6, 0x21c9eb,
  0xff824945, 0xfff89210, 0xffe3d16d, 0x7ec4a,
  0x52a3ad, 0xffc2c8fe, 0x7e4890, 0xffe20766,
  0xffd9e6c1, 0x332de1, 0x6e88e6, 0x3132bf,
};

@emulate "pass"
.kernel checkPass direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1; }
  .pe1 { .top = top; .write = write; .spad = (top1); }
  .pe2 { .write = write; .spad = pass(top1); }
  .pe3 { .write = write; .spad = sat(top1, 31); }
}

@kernel checkPass config | exec
void checkPassRun(void) {
}

@emulate "cst"
.kernel checkCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 5; }
  .pe1 { .top = top; .write = write; .spad = cst(5); }
  .pe2 { .write = write; .spad = (5 + 1) - 1; }
  .pe3 { .write = write; .spad = (5 * 1) | 0; }
}

@kernel checkCst config | exec
void checkCstRun(void) {
}

@emulate "cst_2"
.kernel checkCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0; }
  .pe1 { .top = top; .write = write; .spad = cst(0); }
  .pe2 { .write = write; .spad = (0 + 1) - 1; }
  .pe3 { .write = write; .spad = (0 * 1) | 0; }
}

@kernel checkCst2 config | exec
void checkCst2Run(void) {
}

@emulate "cst_3"
.kernel checkCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1; }
  .pe1 { .top = top; .write = write; .spad = cst(-1); }
  .pe2 { .write = write; .spad = (-1 + 1) - 1; }
  .pe3 { .write = write; .spad = (-1 * 1) | 0; }
}

@kernel checkCst3 config | exec
void checkCst3Run(void) {
}

@emulate "cst_4"
.kernel checkCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607; }
  .pe1 { .top = top; .write = write; .spad = cst(8388607); }
  .pe2 { .write = write; .spad = (8388607 + 1) - 1; }
  .pe3 { .write = write; .spad = (8388607 * 1) | 0; }
}

@kernel checkCst4 config | exec
void checkCst4Run(void) {
}

@emulate "cst_5"
.kernel checkCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608; }
  .pe1 { .top = top; .write = write; .spad = cst(-8388608); }
  .pe2 { .write = write; .spad = (-8388608 + 1) - 1; }
  .pe3 { .write = write; .spad = (-8388608 * 1) | 0; }
}

@kernel checkCst5 config | exec
void checkCst5Run(void) {
}

@emulate "cst_6"
.kernel checkCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 4660; }
  .pe1 { .top = top; .write = write; .spad = cst(4660); }
  .pe2 { .write = write; .spad = (4660 + 1) - 1; }
  .pe3 { .write = write; .spad = (4660 * 1) | 0; }
}

@kernel checkCst6 config | exec
void checkCst6Run(void) {
}

@emulate "cst_7"
.kernel checkCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 16777215; }
  .pe1 { .top = top; .write = write; .spad = cst(16777215); }
  .pe2 { .write = write; .spad = (16777215 + 1) - 1; }
  .pe3 { .write = write; .spad = (16777215 * 1) | 0; }
}

@kernel checkCst7 config | exec
void checkCst7Run(void) {
}

@emulate "cst_8"
.kernel checkCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 4278190083; }
  .pe1 { .top = top; .write = write; .spad = cst(4278190083); }
  .pe2 { .write = write; .spad = (4278190083 + 1) - 1; }
  .pe3 { .write = write; .spad = (4278190083 * 1) | 0; }
}

@kernel checkCst8 config | exec
void checkCst8Run(void) {
}

@emulate "add"
.kernel checkAdd direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1; }
  .pe1 { .top = top; .write = write; .spad = top1 + top0; }
  .pe2 { .write = write; .spad = (top0 + top1); }
  .pe3 { .write = write; .spad = top0 + (top1); }
}

@kernel checkAdd config | exec
void checkAddRun(void) {
}

@emulate "bak_shr"
.kernel checkBakShr direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >> 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 3); }
  .pe2 { .write = write; .spad = top1 >> (1 + 2); }
  .pe3 { .write = write; .spad = (top1) >> 3; }
}

@kernel checkBakShr config | exec
void checkBakShrRun(void) {
}

@emulate "sub"
.kernel checkSub direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1; }
  .pe1 { .top = top; .write = write; .spad = (top0 - top1); }
  .pe2 { .write = write; .spad = top0 - (top1); }
  .pe3 { .write = write; .spad = (top0) - (top1); }
}

@kernel checkSub config | exec
void checkSubRun(void) {
}

@emulate "add_cst"
.kernel checkAddCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 3; }
  .pe1 { .top = top; .write = write; .spad = 3 + top1; }
  .pe2 { .write = write; .spad = (top1) + 3; }
  .pe3 { .write = write; .spad = (top1 + 3); }
}

@kernel checkAddCst config | exec
void checkAddCstRun(void) {
}

@emulate "add_cst_2"
.kernel checkAddCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 0; }
  .pe1 { .top = top; .write = write; .spad = 0 + top1; }
  .pe2 { .write = write; .spad = (top1) + 0; }
  .pe3 { .write = write; .spad = (top1 + 0); }
}

@kernel checkAddCst2 config | exec
void checkAddCst2Run(void) {
}

@emulate "add_cst_3"
.kernel checkAddCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + -1; }
  .pe1 { .top = top; .write = write; .spad = -1 + top1; }
  .pe2 { .write = write; .spad = (top1) + -1; }
  .pe3 { .write = write; .spad = (top1 + -1); }
}

@kernel checkAddCst3 config | exec
void checkAddCst3Run(void) {
}

@emulate "add_cst_4"
.kernel checkAddCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 8388607; }
  .pe1 { .top = top; .write = write; .spad = 8388607 + top1; }
  .pe2 { .write = write; .spad = (top1) + 8388607; }
  .pe3 { .write = write; .spad = (top1 + 8388607); }
}

@kernel checkAddCst4 config | exec
void checkAddCst4Run(void) {
}

@emulate "add_cst_5"
.kernel checkAddCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + -8388608; }
  .pe1 { .top = top; .write = write; .spad = -8388608 + top1; }
  .pe2 { .write = write; .spad = (top1) + -8388608; }
  .pe3 { .write = write; .spad = (top1 + -8388608); }
}

@kernel checkAddCst5 config | exec
void checkAddCst5Run(void) {
}

@emulate "add_cst_6"
.kernel checkAddCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 4660; }
  .pe1 { .top = top; .write = write; .spad = 4660 + top1; }
  .pe2 { .write = write; .spad = (top1) + 4660; }
  .pe3 { .write = write; .spad = (top1 + 4660); }
}

@kernel checkAddCst6 config | exec
void checkAddCst6Run(void) {
}

@emulate "add_cst_7"
.kernel checkAddCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 16777215; }
  .pe1 { .top = top; .write = write; .spad = 16777215 + top1; }
  .pe2 { .write = write; .spad = (top1) + 16777215; }
  .pe3 { .write = write; .spad = (top1 + 16777215); }
}

@kernel checkAddCst7 config | exec
void checkAddCst7Run(void) {
}

@emulate "add_cst_8"
.kernel checkAddCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 + 4278190083; }
  .pe1 { .top = top; .write = write; .spad = 4278190083 + top1; }
  .pe2 { .write = write; .spad = (top1) + 4278190083; }
  .pe3 { .write = write; .spad = (top1 + 4278190083); }
}

@kernel checkAddCst8 config | exec
void checkAddCst8Run(void) {
}

@emulate "neg_ofb"
.kernel checkNegOfb direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 7 - top1; }
  .pe1 { .top = top; .write = write; .spad = (7 - top1); }
  .pe2 { .write = write; .spad = 7 - (top1); }
  .pe3 { .write = write; .spad = (7) - top1; }
}

@kernel checkNegOfb config | exec
void checkNegOfbRun(void) {
}

@emulate "neg_ofb_2"
.kernel checkNegOfb2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0 - top1; }
  .pe1 { .top = top; .write = write; .spad = (0 - top1); }
  .pe2 { .write = write; .spad = 0 - (top1); }
  .pe3 { .write = write; .spad = (0) - top1; }
}

@kernel checkNegOfb2 config | exec
void checkNegOfb2Run(void) {
}

@emulate "neg_ofb_3"
.kernel checkNegOfb3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1 - top1; }
  .pe1 { .top = top; .write = write; .spad = (-1 - top1); }
  .pe2 { .write = write; .spad = -1 - (top1); }
  .pe3 { .write = write; .spad = (-1) - top1; }
}

@kernel checkNegOfb3 config | exec
void checkNegOfb3Run(void) {
}

@emulate "neg_ofb_4"
.kernel checkNegOfb4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607 - top1; }
  .pe1 { .top = top; .write = write; .spad = (8388607 - top1); }
  .pe2 { .write = write; .spad = 8388607 - (top1); }
  .pe3 { .write = write; .spad = (8388607) - top1; }
}

@kernel checkNegOfb4 config | exec
void checkNegOfb4Run(void) {
}

@emulate "neg_ofb_5"
.kernel checkNegOfb5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608 - top1; }
  .pe1 { .top = top; .write = write; .spad = (-8388608 - top1); }
  .pe2 { .write = write; .spad = -8388608 - (top1); }
  .pe3 { .write = write; .spad = (-8388608) - top1; }
}

@kernel checkNegOfb5 config | exec
void checkNegOfb5Run(void) {
}

@emulate "neg_ofb_6"
.kernel checkNegOfb6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 16777215 - top1; }
  .pe1 { .top = top; .write = write; .spad = (16777215 - top1); }
  .pe2 { .write = write; .spad = 16777215 - (top1); }
  .pe3 { .write = write; .spad = (16777215) - top1; }
}

@kernel checkNegOfb6 config | exec
void checkNegOfb6Run(void) {
}

@emulate "neg_ofb_7"
.kernel checkNegOfb7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 4278190083 - top1; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 - top1); }
  .pe2 { .write = write; .spad = 4278190083 - (top1); }
  .pe3 { .write = write; .spad = (4278190083) - top1; }
}

@kernel checkNegOfb7 config | exec
void checkNegOfb7Run(void) {
}

@emulate "add_ofa"
.kernel checkAddOfa direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 5; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + 5; }
  .pe2 { .write = write; .spad = 5 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + 5; }
}

@kernel checkAddOfa config | exec
void checkAddOfaRun(void) {
}

@emulate "add_ofa_2"
.kernel checkAddOfa2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + -1; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + -1; }
  .pe2 { .write = write; .spad = -1 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + -1; }
}

@kernel checkAddOfa2 config | exec
void checkAddOfa2Run(void) {
}

@emulate "add_ofa_3"
.kernel checkAddOfa3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 8388607; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + 8388607; }
  .pe2 { .write = write; .spad = 8388607 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + 8388607; }
}

@kernel checkAddOfa3 config | exec
void checkAddOfa3Run(void) {
}

@emulate "add_ofa_4"
.kernel checkAddOfa4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + -8388608; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + -8388608; }
  .pe2 { .write = write; .spad = -8388608 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + -8388608; }
}

@kernel checkAddOfa4 config | exec
void checkAddOfa4Run(void) {
}

@emulate "add_ofa_5"
.kernel checkAddOfa5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 4660; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + 4660; }
  .pe2 { .write = write; .spad = 4660 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + 4660; }
}

@kernel checkAddOfa5 config | exec
void checkAddOfa5Run(void) {
}

@emulate "add_ofa_6"
.kernel checkAddOfa6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 16777215; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + 16777215; }
  .pe2 { .write = write; .spad = 16777215 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + 16777215; }
}

@kernel checkAddOfa6 config | exec
void checkAddOfa6Run(void) {
}

@emulate "add_ofa_7"
.kernel checkAddOfa7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + top1 + 4278190083; }
  .pe1 { .top = top; .write = write; .spad = (top0 + top1) + 4278190083; }
  .pe2 { .write = write; .spad = 4278190083 + (top0 + top1); }
  .pe3 { .write = write; .spad = top1 + top0 + 4278190083; }
}

@kernel checkAddOfa7 config | exec
void checkAddOfa7Run(void) {
}

@emulate "subacst"
.kernel checkSubacst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 5; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, 5); }
  .pe2 { .write = write; .spad = (top0 - top1) + 5; }
  .pe3 { .write = write; .spad = 5 + (top0 - top1); }
}

@kernel checkSubacst config | exec
void checkSubacstRun(void) {
}

@emulate "subacst_2"
.kernel checkSubacst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + -1; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, -1); }
  .pe2 { .write = write; .spad = (top0 - top1) + -1; }
  .pe3 { .write = write; .spad = -1 + (top0 - top1); }
}

@kernel checkSubacst2 config | exec
void checkSubacst2Run(void) {
}

@emulate "subacst_3"
.kernel checkSubacst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 8388607; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, 8388607); }
  .pe2 { .write = write; .spad = (top0 - top1) + 8388607; }
  .pe3 { .write = write; .spad = 8388607 + (top0 - top1); }
}

@kernel checkSubacst3 config | exec
void checkSubacst3Run(void) {
}

@emulate "subacst_4"
.kernel checkSubacst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + -8388608; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, -8388608); }
  .pe2 { .write = write; .spad = (top0 - top1) + -8388608; }
  .pe3 { .write = write; .spad = -8388608 + (top0 - top1); }
}

@kernel checkSubacst4 config | exec
void checkSubacst4Run(void) {
}

@emulate "subacst_5"
.kernel checkSubacst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 4660; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, 4660); }
  .pe2 { .write = write; .spad = (top0 - top1) + 4660; }
  .pe3 { .write = write; .spad = 4660 + (top0 - top1); }
}

@kernel checkSubacst5 config | exec
void checkSubacst5Run(void) {
}

@emulate "subacst_6"
.kernel checkSubacst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 16777215; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, 16777215); }
  .pe2 { .write = write; .spad = (top0 - top1) + 16777215; }
  .pe3 { .write = write; .spad = 16777215 + (top0 - top1); }
}

@kernel checkSubacst6 config | exec
void checkSubacst6Run(void) {
}

@emulate "subacst_7"
.kernel checkSubacst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - top1 + 4278190083; }
  .pe1 { .top = top; .write = write; .spad = subacst(top0, top1, 4278190083); }
  .pe2 { .write = write; .spad = (top0 - top1) + 4278190083; }
  .pe3 { .write = write; .spad = 4278190083 + (top0 - top1); }
}

@kernel checkSubacst7 config | exec
void checkSubacst7Run(void) {
}

@emulate "add_byt"
.kernel checkAddByt direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = addbyt(top1, top0); }
  .pe2 { .write = write; .spad = addbyt( top0 , top1 ); }
  .pe3 { .write = write; .spad = (addbyt(top0, top1)); }
}

@kernel checkAddByt config | exec
void checkAddBytRun(void) {
}

@emulate "add_byt_set"
.kernel checkAddBytSet direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b0, count };
  Transfer top1Transfer = { memory: in1b0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x038 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x038 }; }
  .pe3 { .write = write; .spad = addbyt(top1, top0); }
}

@kernel checkAddBytSet config | exec
void checkAddBytSetRun(void) {
}

@emulate "add_byt_set_2"
.kernel checkAddBytSet2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b1, count };
  Transfer top1Transfer = { memory: in1b1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x038 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x038 }; }
  .pe3 { .write = write; .spad = addbyt(top1, top0); }
}

@kernel checkAddBytSet2 config | exec
void checkAddBytSet2Run(void) {
}

@emulate "add_byt_set_3"
.kernel checkAddBytSet3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b2, count };
  Transfer top1Transfer = { memory: in1b2, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x038 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x038 }; }
  .pe3 { .write = write; .spad = addbyt(top1, top0); }
}

@kernel checkAddBytSet3 config | exec
void checkAddBytSet3Run(void) {
}

@emulate "add_byt_set_4"
.kernel checkAddBytSet4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b3, count };
  Transfer top1Transfer = { memory: in1b3, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x038 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x038 }; }
  .pe3 { .write = write; .spad = addbyt(top1, top0); }
}

@kernel checkAddBytSet4 config | exec
void checkAddBytSet4Run(void) {
}

@emulate "add_byt_set_5"
.kernel checkAddBytSet5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b4, count };
  Transfer top1Transfer = { memory: in1b4, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x038 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x038 }; }
  .pe3 { .write = write; .spad = addbyt(top1, top0); }
}

@kernel checkAddBytSet5 config | exec
void checkAddBytSet5Run(void) {
}

@emulate "add_byt_set_6"
.kernel checkAddBytSet6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b5, count };
  Transfer top1Transfer = { memory: in1b5, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x038 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x038 }; }
  .pe3 { .write = write; .spad = addbyt(top1, top0); }
}

@kernel checkAddBytSet6 config | exec
void checkAddBytSet6Run(void) {
}

@emulate "add_byt_set_7"
.kernel checkAddBytSet7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b6, count };
  Transfer top1Transfer = { memory: in1b6, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x038 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x038 }; }
  .pe3 { .write = write; .spad = addbyt(top1, top0); }
}

@kernel checkAddBytSet7 config | exec
void checkAddBytSet7Run(void) {
}

@emulate "add_byt_set_8"
.kernel checkAddBytSet8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b7, count };
  Transfer top1Transfer = { memory: in1b7, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x038 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x038 }; }
  .pe3 { .write = write; .spad = addbyt(top1, top0); }
}

@kernel checkAddBytSet8 config | exec
void checkAddBytSet8Run(void) {
}

@emulate "sub_byt"
.kernel checkSubByt direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = (subbyt(top0, top1)); }
  .pe2 { .write = write; .spad = subbyt( top0 , top1 ); }
  .pe3 { .write = write; .spad = subbyt(top0,top1); }
}

@kernel checkSubByt config | exec
void checkSubBytRun(void) {
}

@emulate "sub_byt_set"
.kernel checkSubBytSet direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b0, count };
  Transfer top1Transfer = { memory: in1b0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x03c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x03c }; }
  .pe3 { .write = write; .spad = (subbyt(top0, top1)); }
}

@kernel checkSubBytSet config | exec
void checkSubBytSetRun(void) {
}

@emulate "sub_byt_set_2"
.kernel checkSubBytSet2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b1, count };
  Transfer top1Transfer = { memory: in1b1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x03c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x03c }; }
  .pe3 { .write = write; .spad = (subbyt(top0, top1)); }
}

@kernel checkSubBytSet2 config | exec
void checkSubBytSet2Run(void) {
}

@emulate "sub_byt_set_3"
.kernel checkSubBytSet3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b2, count };
  Transfer top1Transfer = { memory: in1b2, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x03c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x03c }; }
  .pe3 { .write = write; .spad = (subbyt(top0, top1)); }
}

@kernel checkSubBytSet3 config | exec
void checkSubBytSet3Run(void) {
}

@emulate "sub_byt_set_4"
.kernel checkSubBytSet4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b3, count };
  Transfer top1Transfer = { memory: in1b3, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x03c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x03c }; }
  .pe3 { .write = write; .spad = (subbyt(top0, top1)); }
}

@kernel checkSubBytSet4 config | exec
void checkSubBytSet4Run(void) {
}

@emulate "sub_byt_set_5"
.kernel checkSubBytSet5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b4, count };
  Transfer top1Transfer = { memory: in1b4, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x03c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x03c }; }
  .pe3 { .write = write; .spad = (subbyt(top0, top1)); }
}

@kernel checkSubBytSet5 config | exec
void checkSubBytSet5Run(void) {
}

@emulate "sub_byt_set_6"
.kernel checkSubBytSet6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b5, count };
  Transfer top1Transfer = { memory: in1b5, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x03c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x03c }; }
  .pe3 { .write = write; .spad = (subbyt(top0, top1)); }
}

@kernel checkSubBytSet6 config | exec
void checkSubBytSet6Run(void) {
}

@emulate "sub_byt_set_7"
.kernel checkSubBytSet7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b6, count };
  Transfer top1Transfer = { memory: in1b6, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x03c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x03c }; }
  .pe3 { .write = write; .spad = (subbyt(top0, top1)); }
}

@kernel checkSubBytSet7 config | exec
void checkSubBytSet7Run(void) {
}

@emulate "sub_byt_set_8"
.kernel checkSubBytSet8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b7, count };
  Transfer top1Transfer = { memory: in1b7, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = subbyt(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x03c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x03c }; }
  .pe3 { .write = write; .spad = (subbyt(top0, top1)); }
}

@kernel checkSubBytSet8 config | exec
void checkSubBytSet8Run(void) {
}

@emulate "add_shf"
.kernel checkAddShf direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 3); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 3) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (3 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 3); }
}

@kernel checkAddShf config | exec
void checkAddShfRun(void) {
}

@emulate "add_shf_2"
.kernel checkAddShf2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 0); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 0) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (0 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 0); }
}

@kernel checkAddShf2 config | exec
void checkAddShf2Run(void) {
}

@emulate "add_shf_3"
.kernel checkAddShf3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 1); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 1) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (1 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 1); }
}

@kernel checkAddShf3 config | exec
void checkAddShf3Run(void) {
}

@emulate "add_shf_4"
.kernel checkAddShf4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 31); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 31) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (31 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 31); }
}

@kernel checkAddShf4 config | exec
void checkAddShf4Run(void) {
}

@emulate "add_shf_5"
.kernel checkAddShf5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> -1); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> -1) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (-1 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> -1); }
}

@kernel checkAddShf5 config | exec
void checkAddShf5Run(void) {
}

@emulate "add_shf_6"
.kernel checkAddShf6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> -32); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> -32) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (-32 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> -32); }
}

@kernel checkAddShf6 config | exec
void checkAddShf6Run(void) {
}

@emulate "add_shf_7"
.kernel checkAddShf7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 40); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 40) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (40 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 40); }
}

@kernel checkAddShf7 config | exec
void checkAddShf7Run(void) {
}

@emulate "add_shf_8"
.kernel checkAddShf8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 16777215); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 16777215) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (16777215 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 16777215); }
}

@kernel checkAddShf8 config | exec
void checkAddShf8Run(void) {
}

@emulate "add_shf_9"
.kernel checkAddShf9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 + (top1 >> 4278190083); }
  .pe1 { .top = top; .write = write; .spad = (top1 >> 4278190083) + top0; }
  .pe2 { .write = write; .spad = top0 + (top1 >> (4278190083 + 0)); }
  .pe3 { .write = write; .spad = (top0) + ((top1) >> 4278190083); }
}

@kernel checkAddShf9 config | exec
void checkAddShf9Run(void) {
}

@emulate "shr_cst_ofa"
.kernel checkShrCstOfa direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 3) + 5; }
  .pe1 { .top = top; .write = write; .spad = 5 + (top1 >> 3); }
  .pe2 { .write = write; .spad = ((top1 >> 3)) + 5; }
  .pe3 { .write = write; .spad = (top1 >> (3 + 0)) + (5); }
}

@kernel checkShrCstOfa config | exec
void checkShrCstOfaRun(void) {
}

@emulate "shr_cst_ofa_2"
.kernel checkShrCstOfa2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 0) + 0; }
  .pe1 { .top = top; .write = write; .spad = 0 + (top1 >> 0); }
  .pe2 { .write = write; .spad = ((top1 >> 0)) + 0; }
  .pe3 { .write = write; .spad = (top1 >> (0 + 0)) + (0); }
}

@kernel checkShrCstOfa2 config | exec
void checkShrCstOfa2Run(void) {
}

@emulate "shr_cst_ofa_3"
.kernel checkShrCstOfa3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 1) + -1; }
  .pe1 { .top = top; .write = write; .spad = -1 + (top1 >> 1); }
  .pe2 { .write = write; .spad = ((top1 >> 1)) + -1; }
  .pe3 { .write = write; .spad = (top1 >> (1 + 0)) + (-1); }
}

@kernel checkShrCstOfa3 config | exec
void checkShrCstOfa3Run(void) {
}

@emulate "shr_cst_ofa_4"
.kernel checkShrCstOfa4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 31) + 8388607; }
  .pe1 { .top = top; .write = write; .spad = 8388607 + (top1 >> 31); }
  .pe2 { .write = write; .spad = ((top1 >> 31)) + 8388607; }
  .pe3 { .write = write; .spad = (top1 >> (31 + 0)) + (8388607); }
}

@kernel checkShrCstOfa4 config | exec
void checkShrCstOfa4Run(void) {
}

@emulate "shr_cst_ofa_5"
.kernel checkShrCstOfa5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -1) + -8388608; }
  .pe1 { .top = top; .write = write; .spad = -8388608 + (top1 >> -1); }
  .pe2 { .write = write; .spad = ((top1 >> -1)) + -8388608; }
  .pe3 { .write = write; .spad = (top1 >> (-1 + 0)) + (-8388608); }
}

@kernel checkShrCstOfa5 config | exec
void checkShrCstOfa5Run(void) {
}

@emulate "shr_cst_ofa_6"
.kernel checkShrCstOfa6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -32) + 7; }
  .pe1 { .top = top; .write = write; .spad = 7 + (top1 >> -32); }
  .pe2 { .write = write; .spad = ((top1 >> -32)) + 7; }
  .pe3 { .write = write; .spad = (top1 >> (-32 + 0)) + (7); }
}

@kernel checkShrCstOfa6 config | exec
void checkShrCstOfa6Run(void) {
}

@emulate "shr_cst_ofa_7"
.kernel checkShrCstOfa7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 40) + 9; }
  .pe1 { .top = top; .write = write; .spad = 9 + (top1 >> 40); }
  .pe2 { .write = write; .spad = ((top1 >> 40)) + 9; }
  .pe3 { .write = write; .spad = (top1 >> (40 + 0)) + (9); }
}

@kernel checkShrCstOfa7 config | exec
void checkShrCstOfa7Run(void) {
}

@emulate "shr_cst_ofa_8"
.kernel checkShrCstOfa8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 16777215) + 4278190083; }
  .pe1 { .top = top; .write = write; .spad = 4278190083 + (top1 >> 16777215); }
  .pe2 { .write = write; .spad = ((top1 >> 16777215)) + 4278190083; }
  .pe3 { .write = write; .spad = (top1 >> (16777215 + 0)) + (4278190083); }
}

@kernel checkShrCstOfa8 config | exec
void checkShrCstOfa8Run(void) {
}

@emulate "shr_cst_ofa_9"
.kernel checkShrCstOfa9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 4278190083) + 16777215; }
  .pe1 { .top = top; .write = write; .spad = 16777215 + (top1 >> 4278190083); }
  .pe2 { .write = write; .spad = ((top1 >> 4278190083)) + 16777215; }
  .pe3 { .write = write; .spad = (top1 >> (4278190083 + 0)) + (16777215); }
}

@kernel checkShrCstOfa9 config | exec
void checkShrCstOfa9Run(void) {
}

@emulate "subshr"
.kernel checkSubshr direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 3); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 3); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 3); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 3); }
}

@kernel checkSubshr config | exec
void checkSubshrRun(void) {
}

@emulate "subshr_2"
.kernel checkSubshr2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 0); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 0); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 0); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 0); }
}

@kernel checkSubshr2 config | exec
void checkSubshr2Run(void) {
}

@emulate "subshr_3"
.kernel checkSubshr3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 1); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 1); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 1); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 1); }
}

@kernel checkSubshr3 config | exec
void checkSubshr3Run(void) {
}

@emulate "subshr_4"
.kernel checkSubshr4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 31); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 31); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 31); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 31); }
}

@kernel checkSubshr4 config | exec
void checkSubshr4Run(void) {
}

@emulate "subshr_5"
.kernel checkSubshr5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> -1); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, -1); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> -1); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> -1); }
}

@kernel checkSubshr5 config | exec
void checkSubshr5Run(void) {
}

@emulate "subshr_6"
.kernel checkSubshr6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> -32); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, -32); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> -32); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> -32); }
}

@kernel checkSubshr6 config | exec
void checkSubshr6Run(void) {
}

@emulate "subshr_7"
.kernel checkSubshr7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 40); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 40); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 40); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 40); }
}

@kernel checkSubshr7 config | exec
void checkSubshr7Run(void) {
}

@emulate "subshr_8"
.kernel checkSubshr8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 16777215); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 16777215); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 16777215); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 16777215); }
}

@kernel checkSubshr8 config | exec
void checkSubshr8Run(void) {
}

@emulate "subshr_9"
.kernel checkSubshr9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 - (top1 >> 4278190083); }
  .pe1 { .top = top; .write = write; .spad = subshr(top1, top0, 4278190083); }
  .pe2 { .write = write; .spad = (top0) - (top1 >> 4278190083); }
  .pe3 { .write = write; .spad = top0 - ((top1) >> 4278190083); }
}

@kernel checkSubshr9 config | exec
void checkSubshr9Run(void) {
}

@emulate "shr_cst_neg_ofa"
.kernel checkShrCstNegOfa direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 5 - (top1 >> 3); }
  .pe1 { .top = top; .write = write; .spad = (5) - (top1 >> 3); }
  .pe2 { .write = write; .spad = (5 + 0) - (top1 >> 3); }
  .pe3 { .write = write; .spad = 5 - ((top1) >> 3); }
}

@kernel checkShrCstNegOfa config | exec
void checkShrCstNegOfaRun(void) {
}

@emulate "shr_cst_neg_ofa_2"
.kernel checkShrCstNegOfa2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0 - (top1 >> 0); }
  .pe1 { .top = top; .write = write; .spad = (0) - (top1 >> 0); }
  .pe2 { .write = write; .spad = (0 + 0) - (top1 >> 0); }
  .pe3 { .write = write; .spad = 0 - ((top1) >> 0); }
}

@kernel checkShrCstNegOfa2 config | exec
void checkShrCstNegOfa2Run(void) {
}

@emulate "shr_cst_neg_ofa_3"
.kernel checkShrCstNegOfa3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1 - (top1 >> 1); }
  .pe1 { .top = top; .write = write; .spad = (-1) - (top1 >> 1); }
  .pe2 { .write = write; .spad = (-1 + 0) - (top1 >> 1); }
  .pe3 { .write = write; .spad = -1 - ((top1) >> 1); }
}

@kernel checkShrCstNegOfa3 config | exec
void checkShrCstNegOfa3Run(void) {
}

@emulate "shr_cst_neg_ofa_4"
.kernel checkShrCstNegOfa4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607 - (top1 >> 31); }
  .pe1 { .top = top; .write = write; .spad = (8388607) - (top1 >> 31); }
  .pe2 { .write = write; .spad = (8388607 + 0) - (top1 >> 31); }
  .pe3 { .write = write; .spad = 8388607 - ((top1) >> 31); }
}

@kernel checkShrCstNegOfa4 config | exec
void checkShrCstNegOfa4Run(void) {
}

@emulate "shr_cst_neg_ofa_5"
.kernel checkShrCstNegOfa5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608 - (top1 >> -1); }
  .pe1 { .top = top; .write = write; .spad = (-8388608) - (top1 >> -1); }
  .pe2 { .write = write; .spad = (-8388608 + 0) - (top1 >> -1); }
  .pe3 { .write = write; .spad = -8388608 - ((top1) >> -1); }
}

@kernel checkShrCstNegOfa5 config | exec
void checkShrCstNegOfa5Run(void) {
}

@emulate "shr_cst_neg_ofa_6"
.kernel checkShrCstNegOfa6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 7 - (top1 >> -32); }
  .pe1 { .top = top; .write = write; .spad = (7) - (top1 >> -32); }
  .pe2 { .write = write; .spad = (7 + 0) - (top1 >> -32); }
  .pe3 { .write = write; .spad = 7 - ((top1) >> -32); }
}

@kernel checkShrCstNegOfa6 config | exec
void checkShrCstNegOfa6Run(void) {
}

@emulate "shr_cst_neg_ofa_7"
.kernel checkShrCstNegOfa7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 9 - (top1 >> 40); }
  .pe1 { .top = top; .write = write; .spad = (9) - (top1 >> 40); }
  .pe2 { .write = write; .spad = (9 + 0) - (top1 >> 40); }
  .pe3 { .write = write; .spad = 9 - ((top1) >> 40); }
}

@kernel checkShrCstNegOfa7 config | exec
void checkShrCstNegOfa7Run(void) {
}

@emulate "shr_cst_neg_ofa_8"
.kernel checkShrCstNegOfa8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 4278190083 - (top1 >> 16777215); }
  .pe1 { .top = top; .write = write; .spad = (4278190083) - (top1 >> 16777215); }
  .pe2 { .write = write; .spad = (4278190083 + 0) - (top1 >> 16777215); }
  .pe3 { .write = write; .spad = 4278190083 - ((top1) >> 16777215); }
}

@kernel checkShrCstNegOfa8 config | exec
void checkShrCstNegOfa8Run(void) {
}

@emulate "shr_cst_neg_ofa_9"
.kernel checkShrCstNegOfa9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 16777215 - (top1 >> 4278190083); }
  .pe1 { .top = top; .write = write; .spad = (16777215) - (top1 >> 4278190083); }
  .pe2 { .write = write; .spad = (16777215 + 0) - (top1 >> 4278190083); }
  .pe3 { .write = write; .spad = 16777215 - ((top1) >> 4278190083); }
}

@kernel checkShrCstNegOfa9 config | exec
void checkShrCstNegOfa9Run(void) {
}

@emulate "shrsub"
.kernel checkShrsub direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 3) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 3)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 3) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 3) - top0; }
}

@kernel checkShrsub config | exec
void checkShrsubRun(void) {
}

@emulate "shrsub_2"
.kernel checkShrsub2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 0) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 0)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 0) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 0) - top0; }
}

@kernel checkShrsub2 config | exec
void checkShrsub2Run(void) {
}

@emulate "shrsub_3"
.kernel checkShrsub3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 1) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 1)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 1) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 1) - top0; }
}

@kernel checkShrsub3 config | exec
void checkShrsub3Run(void) {
}

@emulate "shrsub_4"
.kernel checkShrsub4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 31) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 31)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 31) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 31) - top0; }
}

@kernel checkShrsub4 config | exec
void checkShrsub4Run(void) {
}

@emulate "shrsub_5"
.kernel checkShrsub5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -1) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> -1)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> -1) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> -1) - top0; }
}

@kernel checkShrsub5 config | exec
void checkShrsub5Run(void) {
}

@emulate "shrsub_6"
.kernel checkShrsub6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -32) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> -32)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> -32) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> -32) - top0; }
}

@kernel checkShrsub6 config | exec
void checkShrsub6Run(void) {
}

@emulate "shrsub_7"
.kernel checkShrsub7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 40) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 40)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 40) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 40) - top0; }
}

@kernel checkShrsub7 config | exec
void checkShrsub7Run(void) {
}

@emulate "shrsub_8"
.kernel checkShrsub8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 16777215) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 16777215)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 16777215) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 16777215) - top0; }
}

@kernel checkShrsub8 config | exec
void checkShrsub8Run(void) {
}

@emulate "shrsub_9"
.kernel checkShrsub9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 4278190083) - top0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 4278190083)) - top0; }
  .pe2 { .write = write; .spad = (top1 >> 4278190083) - (top0); }
  .pe3 { .write = write; .spad = ((top1) >> 4278190083) - top0; }
}

@kernel checkShrsub9 config | exec
void checkShrsub9Run(void) {
}

@emulate "shr_cst_ofs"
.kernel checkShrCstOfs direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 3) - 5; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 3)) - 5; }
  .pe2 { .write = write; .spad = (top1 >> 3) - (5); }
  .pe3 { .write = write; .spad = ((top1) >> 3) - 5; }
}

@kernel checkShrCstOfs config | exec
void checkShrCstOfsRun(void) {
}

@emulate "shr_cst_ofs_2"
.kernel checkShrCstOfs2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 0) - 0; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 0)) - 0; }
  .pe2 { .write = write; .spad = (top1 >> 0) - (0); }
  .pe3 { .write = write; .spad = ((top1) >> 0) - 0; }
}

@kernel checkShrCstOfs2 config | exec
void checkShrCstOfs2Run(void) {
}

@emulate "shr_cst_ofs_3"
.kernel checkShrCstOfs3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 1) - -1; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 1)) - -1; }
  .pe2 { .write = write; .spad = (top1 >> 1) - (-1); }
  .pe3 { .write = write; .spad = ((top1) >> 1) - -1; }
}

@kernel checkShrCstOfs3 config | exec
void checkShrCstOfs3Run(void) {
}

@emulate "shr_cst_ofs_4"
.kernel checkShrCstOfs4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 31) - 8388607; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 31)) - 8388607; }
  .pe2 { .write = write; .spad = (top1 >> 31) - (8388607); }
  .pe3 { .write = write; .spad = ((top1) >> 31) - 8388607; }
}

@kernel checkShrCstOfs4 config | exec
void checkShrCstOfs4Run(void) {
}

@emulate "shr_cst_ofs_5"
.kernel checkShrCstOfs5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -1) - -8388608; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> -1)) - -8388608; }
  .pe2 { .write = write; .spad = (top1 >> -1) - (-8388608); }
  .pe3 { .write = write; .spad = ((top1) >> -1) - -8388608; }
}

@kernel checkShrCstOfs5 config | exec
void checkShrCstOfs5Run(void) {
}

@emulate "shr_cst_ofs_6"
.kernel checkShrCstOfs6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> -32) - 7; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> -32)) - 7; }
  .pe2 { .write = write; .spad = (top1 >> -32) - (7); }
  .pe3 { .write = write; .spad = ((top1) >> -32) - 7; }
}

@kernel checkShrCstOfs6 config | exec
void checkShrCstOfs6Run(void) {
}

@emulate "shr_cst_ofs_7"
.kernel checkShrCstOfs7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 40) - 9; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 40)) - 9; }
  .pe2 { .write = write; .spad = (top1 >> 40) - (9); }
  .pe3 { .write = write; .spad = ((top1) >> 40) - 9; }
}

@kernel checkShrCstOfs7 config | exec
void checkShrCstOfs7Run(void) {
}

@emulate "shr_cst_ofs_8"
.kernel checkShrCstOfs8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 16777215) - 4278190083; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 16777215)) - 4278190083; }
  .pe2 { .write = write; .spad = (top1 >> 16777215) - (4278190083); }
  .pe3 { .write = write; .spad = ((top1) >> 16777215) - 4278190083; }
}

@kernel checkShrCstOfs8 config | exec
void checkShrCstOfs8Run(void) {
}

@emulate "shr_cst_ofs_9"
.kernel checkShrCstOfs9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 >> 4278190083) - 16777215; }
  .pe1 { .top = top; .write = write; .spad = ((top1 >> 4278190083)) - 16777215; }
  .pe2 { .write = write; .spad = (top1 >> 4278190083) - (16777215); }
  .pe3 { .write = write; .spad = ((top1) >> 4278190083) - 16777215; }
}

@kernel checkShrCstOfs9 config | exec
void checkShrCstOfs9Run(void) {
}

@emulate "add_hib"
.kernel checkAddHib direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = addhib(top1, top0); }
  .pe2 { .write = write; .spad = addhib( top0 , top1 ); }
  .pe3 { .write = write; .spad = (addhib(top0, top1)); }
}

@kernel checkAddHib config | exec
void checkAddHibRun(void) {
}

@emulate "add_lob"
.kernel checkAddLob direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = (top1 & 0xff) + (top0 & 0xff); }
  .pe2 { .write = write; .spad = ((top0 & 255)) + ((top1 & 255)); }
  .pe3 { .write = write; .spad = (255 & top0) + (255 & top1); }
}

@kernel checkAddLob config | exec
void checkAddLobRun(void) {
}

@emulate "add_hib_set"
.kernel checkAddHibSet direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b0, count };
  Transfer top1Transfer = { memory: in1b0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x058 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x058 }; }
  .pe3 { .write = write; .spad = addhib(top1, top0); }
}

@kernel checkAddHibSet config | exec
void checkAddHibSetRun(void) {
}

@emulate "add_hib_set_2"
.kernel checkAddHibSet2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b1, count };
  Transfer top1Transfer = { memory: in1b1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x058 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x058 }; }
  .pe3 { .write = write; .spad = addhib(top1, top0); }
}

@kernel checkAddHibSet2 config | exec
void checkAddHibSet2Run(void) {
}

@emulate "add_hib_set_3"
.kernel checkAddHibSet3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b2, count };
  Transfer top1Transfer = { memory: in1b2, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x058 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x058 }; }
  .pe3 { .write = write; .spad = addhib(top1, top0); }
}

@kernel checkAddHibSet3 config | exec
void checkAddHibSet3Run(void) {
}

@emulate "add_hib_set_4"
.kernel checkAddHibSet4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b3, count };
  Transfer top1Transfer = { memory: in1b3, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x058 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x058 }; }
  .pe3 { .write = write; .spad = addhib(top1, top0); }
}

@kernel checkAddHibSet4 config | exec
void checkAddHibSet4Run(void) {
}

@emulate "add_hib_set_5"
.kernel checkAddHibSet5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b4, count };
  Transfer top1Transfer = { memory: in1b4, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x058 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x058 }; }
  .pe3 { .write = write; .spad = addhib(top1, top0); }
}

@kernel checkAddHibSet5 config | exec
void checkAddHibSet5Run(void) {
}

@emulate "add_hib_set_6"
.kernel checkAddHibSet6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b5, count };
  Transfer top1Transfer = { memory: in1b5, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x058 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x058 }; }
  .pe3 { .write = write; .spad = addhib(top1, top0); }
}

@kernel checkAddHibSet6 config | exec
void checkAddHibSet6Run(void) {
}

@emulate "add_hib_set_7"
.kernel checkAddHibSet7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b6, count };
  Transfer top1Transfer = { memory: in1b6, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x058 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x058 }; }
  .pe3 { .write = write; .spad = addhib(top1, top0); }
}

@kernel checkAddHibSet7 config | exec
void checkAddHibSet7Run(void) {
}

@emulate "add_hib_set_8"
.kernel checkAddHibSet8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b7, count };
  Transfer top1Transfer = { memory: in1b7, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = addhib(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x058 }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x058 }; }
  .pe3 { .write = write; .spad = addhib(top1, top0); }
}

@kernel checkAddHibSet8 config | exec
void checkAddHibSet8Run(void) {
}

@emulate "add_lob_set"
.kernel checkAddLobSet direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b0, count };
  Transfer top1Transfer = { memory: in1b0, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x05c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x05c }; }
  .pe3 { .write = write; .spad = (top1 & 255) + (top0 & 255); }
}

@kernel checkAddLobSet config | exec
void checkAddLobSetRun(void) {
}

@emulate "add_lob_set_2"
.kernel checkAddLobSet2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b1, count };
  Transfer top1Transfer = { memory: in1b1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x05c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x05c }; }
  .pe3 { .write = write; .spad = (top1 & 255) + (top0 & 255); }
}

@kernel checkAddLobSet2 config | exec
void checkAddLobSet2Run(void) {
}

@emulate "add_lob_set_3"
.kernel checkAddLobSet3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b2, count };
  Transfer top1Transfer = { memory: in1b2, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x05c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x05c }; }
  .pe3 { .write = write; .spad = (top1 & 255) + (top0 & 255); }
}

@kernel checkAddLobSet3 config | exec
void checkAddLobSet3Run(void) {
}

@emulate "add_lob_set_4"
.kernel checkAddLobSet4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b3, count };
  Transfer top1Transfer = { memory: in1b3, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x05c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x05c }; }
  .pe3 { .write = write; .spad = (top1 & 255) + (top0 & 255); }
}

@kernel checkAddLobSet4 config | exec
void checkAddLobSet4Run(void) {
}

@emulate "add_lob_set_5"
.kernel checkAddLobSet5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b4, count };
  Transfer top1Transfer = { memory: in1b4, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x05c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x05c }; }
  .pe3 { .write = write; .spad = (top1 & 255) + (top0 & 255); }
}

@kernel checkAddLobSet5 config | exec
void checkAddLobSet5Run(void) {
}

@emulate "add_lob_set_6"
.kernel checkAddLobSet6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b5, count };
  Transfer top1Transfer = { memory: in1b5, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x05c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x05c }; }
  .pe3 { .write = write; .spad = (top1 & 255) + (top0 & 255); }
}

@kernel checkAddLobSet6 config | exec
void checkAddLobSet6Run(void) {
}

@emulate "add_lob_set_7"
.kernel checkAddLobSet7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b6, count };
  Transfer top1Transfer = { memory: in1b6, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x05c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x05c }; }
  .pe3 { .write = write; .spad = (top1 & 255) + (top0 & 255); }
}

@kernel checkAddLobSet7 config | exec
void checkAddLobSet7Run(void) {
}

@emulate "add_lob_set_8"
.kernel checkAddLobSet8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0b7, count };
  Transfer top1Transfer = { memory: in1b7, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 255) + (top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = top0 + top1 + 5592405; .remap = { operator: "+", primary: 0x05c }; }
  .pe2 { .write = write; .spad = top0 + (top1 >> 37); .remap = { operator: "+", primary: 0x05c }; }
  .pe3 { .write = write; .spad = (top1 & 255) + (top0 & 255); }
}

@kernel checkAddLobSet8 config | exec
void checkAddLobSet8Run(void) {
}

@emulate "sel_neg"
.kernel checkSelNeg direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 4) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? -top1 : (top1); }
}

@kernel checkSelNeg config | exec
void checkSelNegRun(void) {
}

@emulate "sel_neg_2"
.kernel checkSelNeg2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (0 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 0) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 0)) ? -top1 : (top1); }
}

@kernel checkSelNeg2 config | exec
void checkSelNeg2Run(void) {
}

@emulate "sel_neg_3"
.kernel checkSelNeg3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 1) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 1) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 1)) ? -top1 : (top1); }
}

@kernel checkSelNeg3 config | exec
void checkSelNeg3Run(void) {
}

@emulate "sel_neg_4"
.kernel checkSelNeg4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 8388608) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 8388608) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 8388608)) ? -top1 : (top1); }
}

@kernel checkSelNeg4 config | exec
void checkSelNeg4Run(void) {
}

@emulate "sel_neg_5"
.kernel checkSelNeg5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & -1) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & -1) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & -1)) ? -top1 : (top1); }
}

@kernel checkSelNeg5 config | exec
void checkSelNeg5Run(void) {
}

@emulate "sel_neg_6"
.kernel checkSelNeg6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 5592405) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 5592405) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 5592405)) ? -top1 : (top1); }
}

@kernel checkSelNeg6 config | exec
void checkSelNeg6Run(void) {
}

@emulate "sel_neg_7"
.kernel checkSelNeg7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 16777215) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (16777215 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 16777215) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 16777215)) ? -top1 : (top1); }
}

@kernel checkSelNeg7 config | exec
void checkSelNeg7Run(void) {
}

@emulate "sel_neg_8"
.kernel checkSelNeg8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4278190083) ? -top1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 & top0) ? -top1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 4278190083) ? (-top1) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 4278190083)) ? -top1 : (top1); }
}

@kernel checkSelNeg8 config | exec
void checkSelNeg8Run(void) {
}

@emulate "sel_neg_slf"
.kernel checkSelNegSlf direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 4) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf config | exec
void checkSelNegSlfRun(void) {
}

@emulate "sel_neg_slf_2"
.kernel checkSelNegSlf2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (0 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 0) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 0)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf2 config | exec
void checkSelNegSlf2Run(void) {
}

@emulate "sel_neg_slf_3"
.kernel checkSelNegSlf3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 1) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 1) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 1)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf3 config | exec
void checkSelNegSlf3Run(void) {
}

@emulate "sel_neg_slf_4"
.kernel checkSelNegSlf4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 8388608) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 8388608) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 8388608)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf4 config | exec
void checkSelNegSlf4Run(void) {
}

@emulate "sel_neg_slf_5"
.kernel checkSelNegSlf5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & -1) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & -1) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & -1)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf5 config | exec
void checkSelNegSlf5Run(void) {
}

@emulate "sel_neg_slf_6"
.kernel checkSelNegSlf6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 5592405) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 5592405) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 5592405)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf6 config | exec
void checkSelNegSlf6Run(void) {
}

@emulate "sel_neg_slf_7"
.kernel checkSelNegSlf7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 16777215) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (16777215 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 16777215) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 16777215)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf7 config | exec
void checkSelNegSlf7Run(void) {
}

@emulate "sel_neg_slf_8"
.kernel checkSelNegSlf8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4278190083) ? top1 : -top1; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 & top0) ? top1 : -top1; }
  .pe2 { .write = write; .spad = (top0 & 4278190083) ? top1 : (-top1); }
  .pe3 { .write = write; .spad = ((top0 & 4278190083)) ? (top1) : -top1; }
}

@kernel checkSelNegSlf8 config | exec
void checkSelNegSlf8Run(void) {
}

@emulate "sel_cst"
.kernel checkSelCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? 7 : top1; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? 7 : top1; }
  .pe2 { .write = write; .spad = (top0 & 4) ? (7 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? 7 : (top1); }
}

@kernel checkSelCst config | exec
void checkSelCstRun(void) {
}

@emulate "sel_cst_2"
.kernel checkSelCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0) ? 0 : top1; }
  .pe1 { .top = top; .write = write; .spad = (0 & top0) ? 0 : top1; }
  .pe2 { .write = write; .spad = (top0 & 0) ? (0 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 0)) ? 0 : (top1); }
}

@kernel checkSelCst2 config | exec
void checkSelCst2Run(void) {
}

@emulate "sel_cst_3"
.kernel checkSelCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 1) ? -1 : top1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top0) ? -1 : top1; }
  .pe2 { .write = write; .spad = (top0 & 1) ? (-1 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 1)) ? -1 : (top1); }
}

@kernel checkSelCst3 config | exec
void checkSelCst3Run(void) {
}

@emulate "sel_cst_4"
.kernel checkSelCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 8388608) ? 8388607 : top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top0) ? 8388607 : top1; }
  .pe2 { .write = write; .spad = (top0 & 8388608) ? (8388607 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 8388608)) ? 8388607 : (top1); }
}

@kernel checkSelCst4 config | exec
void checkSelCst4Run(void) {
}

@emulate "sel_cst_5"
.kernel checkSelCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & -1) ? -8388608 : top1; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top0) ? -8388608 : top1; }
  .pe2 { .write = write; .spad = (top0 & -1) ? (-8388608 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & -1)) ? -8388608 : (top1); }
}

@kernel checkSelCst5 config | exec
void checkSelCst5Run(void) {
}

@emulate "sel_cst_6"
.kernel checkSelCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 5592405) ? 4660 : top1; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top0) ? 4660 : top1; }
  .pe2 { .write = write; .spad = (top0 & 5592405) ? (4660 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 5592405)) ? 4660 : (top1); }
}

@kernel checkSelCst6 config | exec
void checkSelCst6Run(void) {
}

@emulate "sel_cst_7"
.kernel checkSelCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 16777215) ? 4278190083 : top1; }
  .pe1 { .top = top; .write = write; .spad = (16777215 & top0) ? 4278190083 : top1; }
  .pe2 { .write = write; .spad = (top0 & 16777215) ? (4278190083 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 16777215)) ? 4278190083 : (top1); }
}

@kernel checkSelCst7 config | exec
void checkSelCst7Run(void) {
}

@emulate "sel_cst_8"
.kernel checkSelCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4278190083) ? 16777215 : top1; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 & top0) ? 16777215 : top1; }
  .pe2 { .write = write; .spad = (top0 & 4278190083) ? (16777215 + 0) : top1; }
  .pe3 { .write = write; .spad = ((top0 & 4278190083)) ? 16777215 : (top1); }
}

@kernel checkSelCst8 config | exec
void checkSelCst8Run(void) {
}

@emulate "sel_cst_ofb"
.kernel checkSelCstOfb direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4) ? top1 : 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top0) ? top1 : 7; }
  .pe2 { .write = write; .spad = (top0 & 4) ? top1 : (7 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 4)) ? (top1) : 7; }
}

@kernel checkSelCstOfb config | exec
void checkSelCstOfbRun(void) {
}

@emulate "sel_cst_ofb_2"
.kernel checkSelCstOfb2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 0) ? top1 : 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top0) ? top1 : 0; }
  .pe2 { .write = write; .spad = (top0 & 0) ? top1 : (0 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 0)) ? (top1) : 0; }
}

@kernel checkSelCstOfb2 config | exec
void checkSelCstOfb2Run(void) {
}

@emulate "sel_cst_ofb_3"
.kernel checkSelCstOfb3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 1) ? top1 : -1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top0) ? top1 : -1; }
  .pe2 { .write = write; .spad = (top0 & 1) ? top1 : (-1 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 1)) ? (top1) : -1; }
}

@kernel checkSelCstOfb3 config | exec
void checkSelCstOfb3Run(void) {
}

@emulate "sel_cst_ofb_4"
.kernel checkSelCstOfb4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 8388608) ? top1 : 8388607; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top0) ? top1 : 8388607; }
  .pe2 { .write = write; .spad = (top0 & 8388608) ? top1 : (8388607 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 8388608)) ? (top1) : 8388607; }
}

@kernel checkSelCstOfb4 config | exec
void checkSelCstOfb4Run(void) {
}

@emulate "sel_cst_ofb_5"
.kernel checkSelCstOfb5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & -1) ? top1 : -8388608; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top0) ? top1 : -8388608; }
  .pe2 { .write = write; .spad = (top0 & -1) ? top1 : (-8388608 + 0); }
  .pe3 { .write = write; .spad = ((top0 & -1)) ? (top1) : -8388608; }
}

@kernel checkSelCstOfb5 config | exec
void checkSelCstOfb5Run(void) {
}

@emulate "sel_cst_ofb_6"
.kernel checkSelCstOfb6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 5592405) ? top1 : 4660; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top0) ? top1 : 4660; }
  .pe2 { .write = write; .spad = (top0 & 5592405) ? top1 : (4660 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 5592405)) ? (top1) : 4660; }
}

@kernel checkSelCstOfb6 config | exec
void checkSelCstOfb6Run(void) {
}

@emulate "sel_cst_ofb_7"
.kernel checkSelCstOfb7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 16777215) ? top1 : 4278190083; }
  .pe1 { .top = top; .write = write; .spad = (16777215 & top0) ? top1 : 4278190083; }
  .pe2 { .write = write; .spad = (top0 & 16777215) ? top1 : (4278190083 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 16777215)) ? (top1) : 4278190083; }
}

@kernel checkSelCstOfb7 config | exec
void checkSelCstOfb7Run(void) {
}

@emulate "sel_cst_ofb_8"
.kernel checkSelCstOfb8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top0 & 4278190083) ? top1 : 16777215; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 & top0) ? top1 : 16777215; }
  .pe2 { .write = write; .spad = (top0 & 4278190083) ? top1 : (16777215 + 0); }
  .pe3 { .write = write; .spad = ((top0 & 4278190083)) ? (top1) : 16777215; }
}

@kernel checkSelCstOfb8 config | exec
void checkSelCstOfb8Run(void) {
}

@emulate "sel_ads"
.kernel checkSelAds direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? top1 - 7 : top1 + 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? top1 - 7 : top1 + 7; }
  .pe2 { .write = write; .spad = (top1 & 4) ? (top1 - 7) : (top1 + 7); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? top1 - (7 + 0) : top1 + 7; }
}

@kernel checkSelAds config | exec
void checkSelAdsRun(void) {
}

@emulate "sel_ads_2"
.kernel checkSelAds2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 0) ? top1 - 0 : top1 + 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top1) ? top1 - 0 : top1 + 0; }
  .pe2 { .write = write; .spad = (top1 & 0) ? (top1 - 0) : (top1 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 0)) ? top1 - (0 + 0) : top1 + 0; }
}

@kernel checkSelAds2 config | exec
void checkSelAds2Run(void) {
}

@emulate "sel_ads_3"
.kernel checkSelAds3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 1) ? top1 - -1 : top1 + -1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top1) ? top1 - -1 : top1 + -1; }
  .pe2 { .write = write; .spad = (top1 & 1) ? (top1 - -1) : (top1 + -1); }
  .pe3 { .write = write; .spad = ((top1 & 1)) ? top1 - (-1 + 0) : top1 + -1; }
}

@kernel checkSelAds3 config | exec
void checkSelAds3Run(void) {
}

@emulate "sel_ads_4"
.kernel checkSelAds4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 8388608) ? top1 - 8388607 : top1 + 8388607; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top1) ? top1 - 8388607 : top1 + 8388607; }
  .pe2 { .write = write; .spad = (top1 & 8388608) ? (top1 - 8388607) : (top1 + 8388607); }
  .pe3 { .write = write; .spad = ((top1 & 8388608)) ? top1 - (8388607 + 0) : top1 + 8388607; }
}

@kernel checkSelAds4 config | exec
void checkSelAds4Run(void) {
}

@emulate "sel_ads_5"
.kernel checkSelAds5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & -1) ? top1 - -8388608 : top1 + -8388608; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top1) ? top1 - -8388608 : top1 + -8388608; }
  .pe2 { .write = write; .spad = (top1 & -1) ? (top1 - -8388608) : (top1 + -8388608); }
  .pe3 { .write = write; .spad = ((top1 & -1)) ? top1 - (-8388608 + 0) : top1 + -8388608; }
}

@kernel checkSelAds5 config | exec
void checkSelAds5Run(void) {
}

@emulate "sel_ads_6"
.kernel checkSelAds6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 5592405) ? top1 - 4660 : top1 + 4660; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top1) ? top1 - 4660 : top1 + 4660; }
  .pe2 { .write = write; .spad = (top1 & 5592405) ? (top1 - 4660) : (top1 + 4660); }
  .pe3 { .write = write; .spad = ((top1 & 5592405)) ? top1 - (4660 + 0) : top1 + 4660; }
}

@kernel checkSelAds6 config | exec
void checkSelAds6Run(void) {
}

@emulate "sel_ads_7"
.kernel checkSelAds7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 16777215) ? top1 - 4278190083 : top1 + 4278190083; }
  .pe1 { .top = top; .write = write; .spad = (16777215 & top1) ? top1 - 4278190083 : top1 + 4278190083; }
  .pe2 { .write = write; .spad = (top1 & 16777215) ? (top1 - 4278190083) : (top1 + 4278190083); }
  .pe3 { .write = write; .spad = ((top1 & 16777215)) ? top1 - (4278190083 + 0) : top1 + 4278190083; }
}

@kernel checkSelAds7 config | exec
void checkSelAds7Run(void) {
}

@emulate "sel_ads_8"
.kernel checkSelAds8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4278190083) ? top1 - 16777215 : top1 + 16777215; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 & top1) ? top1 - 16777215 : top1 + 16777215; }
  .pe2 { .write = write; .spad = (top1 & 4278190083) ? (top1 - 16777215) : (top1 + 16777215); }
  .pe3 { .write = write; .spad = ((top1 & 4278190083)) ? top1 - (16777215 + 0) : top1 + 16777215; }
}

@kernel checkSelAds8 config | exec
void checkSelAds8Run(void) {
}

@emulate "sel_ads_inv"
.kernel checkSelAdsInv direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? top1 + 7 : top1 - 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? top1 + 7 : top1 - 7; }
  .pe2 { .write = write; .spad = (top1 & 4) ? (top1 + 7) : (top1 - 7); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? top1 + (7 + 0) : top1 - 7; }
}

@kernel checkSelAdsInv config | exec
void checkSelAdsInvRun(void) {
}

@emulate "sel_ads_inv_2"
.kernel checkSelAdsInv2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 0) ? top1 + 0 : top1 - 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top1) ? top1 + 0 : top1 - 0; }
  .pe2 { .write = write; .spad = (top1 & 0) ? (top1 + 0) : (top1 - 0); }
  .pe3 { .write = write; .spad = ((top1 & 0)) ? top1 + (0 + 0) : top1 - 0; }
}

@kernel checkSelAdsInv2 config | exec
void checkSelAdsInv2Run(void) {
}

@emulate "sel_ads_inv_3"
.kernel checkSelAdsInv3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 1) ? top1 + -1 : top1 - -1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top1) ? top1 + -1 : top1 - -1; }
  .pe2 { .write = write; .spad = (top1 & 1) ? (top1 + -1) : (top1 - -1); }
  .pe3 { .write = write; .spad = ((top1 & 1)) ? top1 + (-1 + 0) : top1 - -1; }
}

@kernel checkSelAdsInv3 config | exec
void checkSelAdsInv3Run(void) {
}

@emulate "sel_ads_inv_4"
.kernel checkSelAdsInv4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 8388608) ? top1 + 8388607 : top1 - 8388607; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top1) ? top1 + 8388607 : top1 - 8388607; }
  .pe2 { .write = write; .spad = (top1 & 8388608) ? (top1 + 8388607) : (top1 - 8388607); }
  .pe3 { .write = write; .spad = ((top1 & 8388608)) ? top1 + (8388607 + 0) : top1 - 8388607; }
}

@kernel checkSelAdsInv4 config | exec
void checkSelAdsInv4Run(void) {
}

@emulate "sel_ads_inv_5"
.kernel checkSelAdsInv5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & -1) ? top1 + -8388608 : top1 - -8388608; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top1) ? top1 + -8388608 : top1 - -8388608; }
  .pe2 { .write = write; .spad = (top1 & -1) ? (top1 + -8388608) : (top1 - -8388608); }
  .pe3 { .write = write; .spad = ((top1 & -1)) ? top1 + (-8388608 + 0) : top1 - -8388608; }
}

@kernel checkSelAdsInv5 config | exec
void checkSelAdsInv5Run(void) {
}

@emulate "sel_ads_inv_6"
.kernel checkSelAdsInv6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 5592405) ? top1 + 4660 : top1 - 4660; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top1) ? top1 + 4660 : top1 - 4660; }
  .pe2 { .write = write; .spad = (top1 & 5592405) ? (top1 + 4660) : (top1 - 4660); }
  .pe3 { .write = write; .spad = ((top1 & 5592405)) ? top1 + (4660 + 0) : top1 - 4660; }
}

@kernel checkSelAdsInv6 config | exec
void checkSelAdsInv6Run(void) {
}

@emulate "sel_ads_inv_7"
.kernel checkSelAdsInv7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 16777215) ? top1 + 4278190083 : top1 - 4278190083; }
  .pe1 { .top = top; .write = write; .spad = (16777215 & top1) ? top1 + 4278190083 : top1 - 4278190083; }
  .pe2 { .write = write; .spad = (top1 & 16777215) ? (top1 + 4278190083) : (top1 - 4278190083); }
  .pe3 { .write = write; .spad = ((top1 & 16777215)) ? top1 + (4278190083 + 0) : top1 - 4278190083; }
}

@kernel checkSelAdsInv7 config | exec
void checkSelAdsInv7Run(void) {
}

@emulate "sel_ads_inv_8"
.kernel checkSelAdsInv8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4278190083) ? top1 + 16777215 : top1 - 16777215; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 & top1) ? top1 + 16777215 : top1 - 16777215; }
  .pe2 { .write = write; .spad = (top1 & 4278190083) ? (top1 + 16777215) : (top1 - 16777215); }
  .pe3 { .write = write; .spad = ((top1 & 4278190083)) ? top1 + (16777215 + 0) : top1 - 16777215; }
}

@kernel checkSelAdsInv8 config | exec
void checkSelAdsInv8Run(void) {
}

@emulate "clamp"
.kernel checkClamp direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, -100, 100); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,-100,100); }
  .pe2 { .write = write; .spad = clamp((top1), -100, 100); }
  .pe3 { .write = write; .spad = clamp(top1, -100 + 0, 100); }
}

@kernel checkClamp config | exec
void checkClampRun(void) {
}

@emulate "clamp_2"
.kernel checkClamp2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 0, 0); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,0,0); }
  .pe2 { .write = write; .spad = clamp((top1), 0, 0); }
  .pe3 { .write = write; .spad = clamp(top1, 0 + 0, 0); }
}

@kernel checkClamp2 config | exec
void checkClamp2Run(void) {
}

@emulate "clamp_3"
.kernel checkClamp3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, -1, 1); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,-1,1); }
  .pe2 { .write = write; .spad = clamp((top1), -1, 1); }
  .pe3 { .write = write; .spad = clamp(top1, -1 + 0, 1); }
}

@kernel checkClamp3 config | exec
void checkClamp3Run(void) {
}

@emulate "clamp_4"
.kernel checkClamp4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 100, -100); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,100,-100); }
  .pe2 { .write = write; .spad = clamp((top1), 100, -100); }
  .pe3 { .write = write; .spad = clamp(top1, 100 + 0, -100); }
}

@kernel checkClamp4 config | exec
void checkClamp4Run(void) {
}

@emulate "clamp_5"
.kernel checkClamp5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, -8388608, 8388607); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,-8388608,8388607); }
  .pe2 { .write = write; .spad = clamp((top1), -8388608, 8388607); }
  .pe3 { .write = write; .spad = clamp(top1, -8388608 + 0, 8388607); }
}

@kernel checkClamp5 config | exec
void checkClamp5Run(void) {
}

@emulate "clamp_6"
.kernel checkClamp6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 8388607, -8388608); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,8388607,-8388608); }
  .pe2 { .write = write; .spad = clamp((top1), 8388607, -8388608); }
  .pe3 { .write = write; .spad = clamp(top1, 8388607 + 0, -8388608); }
}

@kernel checkClamp6 config | exec
void checkClamp6Run(void) {
}

@emulate "clamp_7"
.kernel checkClamp7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 5, 5); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,5,5); }
  .pe2 { .write = write; .spad = clamp((top1), 5, 5); }
  .pe3 { .write = write; .spad = clamp(top1, 5 + 0, 5); }
}

@kernel checkClamp7 config | exec
void checkClamp7Run(void) {
}

@emulate "clamp_8"
.kernel checkClamp8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 16777215, 4278190083); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,16777215,4278190083); }
  .pe2 { .write = write; .spad = clamp((top1), 16777215, 4278190083); }
  .pe3 { .write = write; .spad = clamp(top1, 16777215 + 0, 4278190083); }
}

@kernel checkClamp8 config | exec
void checkClamp8Run(void) {
}

@emulate "clamp_9"
.kernel checkClamp9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = clamp(top1, 4278190083, 16777215); }
  .pe1 { .top = top; .write = write; .spad = clamp(top1,4278190083,16777215); }
  .pe2 { .write = write; .spad = clamp((top1), 4278190083, 16777215); }
  .pe3 { .write = write; .spad = clamp(top1, 4278190083 + 0, 16777215); }
}

@kernel checkClamp9 config | exec
void checkClamp9Run(void) {
}

@emulate "mul_clp"
.kernel checkMulClp direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = mulclp(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = (mulclp(top0, top1)); }
  .pe2 { .write = write; .spad = mulclp( top0 , top1 ); }
  .pe3 { .write = write; .spad = mulclp(top0,top1); }
}

@kernel checkMulClp config | exec
void checkMulClpRun(void) {
}

@emulate "mul_clp_neg"
.kernel checkMulClpNeg direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = mulclpneg(top0, top1); }
  .pe1 { .top = top; .write = write; .spad = (mulclpneg(top0, top1)); }
  .pe2 { .write = write; .spad = mulclpneg( top0 , top1 ); }
  .pe3 { .write = write; .spad = mulclpneg(top0,top1); }
}

@kernel checkMulClpNeg config | exec
void checkMulClpNegRun(void) {
}

@emulate "sel_cst_zer"
.kernel checkSelCstZer direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? 0 : 7; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? 0 : 7; }
  .pe2 { .write = write; .spad = (top1 & 4) ? 0 : (7 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? 0 : 7; }
}

@kernel checkSelCstZer config | exec
void checkSelCstZerRun(void) {
}

@emulate "sel_cst_zer_2"
.kernel checkSelCstZer2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 0) ? 0 : 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top1) ? 0 : 0; }
  .pe2 { .write = write; .spad = (top1 & 0) ? 0 : (0 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 0)) ? 0 : 0; }
}

@kernel checkSelCstZer2 config | exec
void checkSelCstZer2Run(void) {
}

@emulate "sel_cst_zer_3"
.kernel checkSelCstZer3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 1) ? 0 : -1; }
  .pe1 { .top = top; .write = write; .spad = (1 & top1) ? 0 : -1; }
  .pe2 { .write = write; .spad = (top1 & 1) ? 0 : (-1 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 1)) ? 0 : -1; }
}

@kernel checkSelCstZer3 config | exec
void checkSelCstZer3Run(void) {
}

@emulate "sel_cst_zer_4"
.kernel checkSelCstZer4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 8388608) ? 0 : 8388607; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top1) ? 0 : 8388607; }
  .pe2 { .write = write; .spad = (top1 & 8388608) ? 0 : (8388607 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 8388608)) ? 0 : 8388607; }
}

@kernel checkSelCstZer4 config | exec
void checkSelCstZer4Run(void) {
}

@emulate "sel_cst_zer_5"
.kernel checkSelCstZer5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & -1) ? 0 : -8388608; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top1) ? 0 : -8388608; }
  .pe2 { .write = write; .spad = (top1 & -1) ? 0 : (-8388608 + 0); }
  .pe3 { .write = write; .spad = ((top1 & -1)) ? 0 : -8388608; }
}

@kernel checkSelCstZer5 config | exec
void checkSelCstZer5Run(void) {
}

@emulate "sel_cst_zer_6"
.kernel checkSelCstZer6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 5592405) ? 0 : 4660; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top1) ? 0 : 4660; }
  .pe2 { .write = write; .spad = (top1 & 5592405) ? 0 : (4660 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 5592405)) ? 0 : 4660; }
}

@kernel checkSelCstZer6 config | exec
void checkSelCstZer6Run(void) {
}

@emulate "sel_cst_zer_7"
.kernel checkSelCstZer7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 16777215) ? 0 : 4278190083; }
  .pe1 { .top = top; .write = write; .spad = (16777215 & top1) ? 0 : 4278190083; }
  .pe2 { .write = write; .spad = (top1 & 16777215) ? 0 : (4278190083 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 16777215)) ? 0 : 4278190083; }
}

@kernel checkSelCstZer7 config | exec
void checkSelCstZer7Run(void) {
}

@emulate "sel_cst_zer_8"
.kernel checkSelCstZer8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4278190083) ? 0 : 16777215; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 & top1) ? 0 : 16777215; }
  .pe2 { .write = write; .spad = (top1 & 4278190083) ? 0 : (16777215 + 0); }
  .pe3 { .write = write; .spad = ((top1 & 4278190083)) ? 0 : 16777215; }
}

@kernel checkSelCstZer8 config | exec
void checkSelCstZer8Run(void) {
}

@emulate "sel_cst_zer_inv"
.kernel checkSelCstZerInv direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4) ? 7 : 0; }
  .pe1 { .top = top; .write = write; .spad = (4 & top1) ? 7 : 0; }
  .pe2 { .write = write; .spad = (top1 & 4) ? (7 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 4)) ? 7 : 0; }
}

@kernel checkSelCstZerInv config | exec
void checkSelCstZerInvRun(void) {
}

@emulate "sel_cst_zer_inv_2"
.kernel checkSelCstZerInv2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 0) ? 5 : 0; }
  .pe1 { .top = top; .write = write; .spad = (0 & top1) ? 5 : 0; }
  .pe2 { .write = write; .spad = (top1 & 0) ? (5 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 0)) ? 5 : 0; }
}

@kernel checkSelCstZerInv2 config | exec
void checkSelCstZerInv2Run(void) {
}

@emulate "sel_cst_zer_inv_3"
.kernel checkSelCstZerInv3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 1) ? -1 : 0; }
  .pe1 { .top = top; .write = write; .spad = (1 & top1) ? -1 : 0; }
  .pe2 { .write = write; .spad = (top1 & 1) ? (-1 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 1)) ? -1 : 0; }
}

@kernel checkSelCstZerInv3 config | exec
void checkSelCstZerInv3Run(void) {
}

@emulate "sel_cst_zer_inv_4"
.kernel checkSelCstZerInv4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 8388608) ? 8388607 : 0; }
  .pe1 { .top = top; .write = write; .spad = (8388608 & top1) ? 8388607 : 0; }
  .pe2 { .write = write; .spad = (top1 & 8388608) ? (8388607 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 8388608)) ? 8388607 : 0; }
}

@kernel checkSelCstZerInv4 config | exec
void checkSelCstZerInv4Run(void) {
}

@emulate "sel_cst_zer_inv_5"
.kernel checkSelCstZerInv5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & -1) ? -8388608 : 0; }
  .pe1 { .top = top; .write = write; .spad = (-1 & top1) ? -8388608 : 0; }
  .pe2 { .write = write; .spad = (top1 & -1) ? (-8388608 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & -1)) ? -8388608 : 0; }
}

@kernel checkSelCstZerInv5 config | exec
void checkSelCstZerInv5Run(void) {
}

@emulate "sel_cst_zer_inv_6"
.kernel checkSelCstZerInv6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 5592405) ? 4660 : 0; }
  .pe1 { .top = top; .write = write; .spad = (5592405 & top1) ? 4660 : 0; }
  .pe2 { .write = write; .spad = (top1 & 5592405) ? (4660 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 5592405)) ? 4660 : 0; }
}

@kernel checkSelCstZerInv6 config | exec
void checkSelCstZerInv6Run(void) {
}

@emulate "sel_cst_zer_inv_7"
.kernel checkSelCstZerInv7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 16777215) ? 4278190083 : 0; }
  .pe1 { .top = top; .write = write; .spad = (16777215 & top1) ? 4278190083 : 0; }
  .pe2 { .write = write; .spad = (top1 & 16777215) ? (4278190083 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 16777215)) ? 4278190083 : 0; }
}

@kernel checkSelCstZerInv7 config | exec
void checkSelCstZerInv7Run(void) {
}

@emulate "sel_cst_zer_inv_8"
.kernel checkSelCstZerInv8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = (top1 & 4278190083) ? 16777215 : 0; }
  .pe1 { .top = top; .write = write; .spad = (4278190083 & top1) ? 16777215 : 0; }
  .pe2 { .write = write; .spad = (top1 & 4278190083) ? (16777215 + 0) : 0; }
  .pe3 { .write = write; .spad = ((top1 & 4278190083)) ? 16777215 : 0; }
}

@kernel checkSelCstZerInv8 config | exec
void checkSelCstZerInv8Run(void) {
}

@emulate "shl_dyn"
.kernel checkShlDyn direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -5 << top1; }
  .pe1 { .top = top; .write = write; .spad = (-5) << top1; }
  .pe2 { .write = write; .spad = (-5 + 0) << top1; }
  .pe3 { .write = write; .spad = (-5) << (top1); }
}

@kernel checkShlDyn config | exec
void checkShlDynRun(void) {
}

@emulate "shl_dyn_2"
.kernel checkShlDyn2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0 << top1; }
  .pe1 { .top = top; .write = write; .spad = (0) << top1; }
  .pe2 { .write = write; .spad = (0 + 0) << top1; }
  .pe3 { .write = write; .spad = (0) << (top1); }
}

@kernel checkShlDyn2 config | exec
void checkShlDyn2Run(void) {
}

@emulate "shl_dyn_3"
.kernel checkShlDyn3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 1 << top1; }
  .pe1 { .top = top; .write = write; .spad = (1) << top1; }
  .pe2 { .write = write; .spad = (1 + 0) << top1; }
  .pe3 { .write = write; .spad = (1) << (top1); }
}

@kernel checkShlDyn3 config | exec
void checkShlDyn3Run(void) {
}

@emulate "shl_dyn_4"
.kernel checkShlDyn4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1 << top1; }
  .pe1 { .top = top; .write = write; .spad = (-1) << top1; }
  .pe2 { .write = write; .spad = (-1 + 0) << top1; }
  .pe3 { .write = write; .spad = (-1) << (top1); }
}

@kernel checkShlDyn4 config | exec
void checkShlDyn4Run(void) {
}

@emulate "shl_dyn_5"
.kernel checkShlDyn5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607 << top1; }
  .pe1 { .top = top; .write = write; .spad = (8388607) << top1; }
  .pe2 { .write = write; .spad = (8388607 + 0) << top1; }
  .pe3 { .write = write; .spad = (8388607) << (top1); }
}

@kernel checkShlDyn5 config | exec
void checkShlDyn5Run(void) {
}

@emulate "shl_dyn_6"
.kernel checkShlDyn6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608 << top1; }
  .pe1 { .top = top; .write = write; .spad = (-8388608) << top1; }
  .pe2 { .write = write; .spad = (-8388608 + 0) << top1; }
  .pe3 { .write = write; .spad = (-8388608) << (top1); }
}

@kernel checkShlDyn6 config | exec
void checkShlDyn6Run(void) {
}

@emulate "shr_dyn"
.kernel checkShrDyn direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -5 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (-5) >> top1; }
  .pe2 { .write = write; .spad = (-5 + 0) >> top1; }
  .pe3 { .write = write; .spad = (-5) >> (top1); }
}

@kernel checkShrDyn config | exec
void checkShrDynRun(void) {
}

@emulate "shr_dyn_2"
.kernel checkShrDyn2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 0 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (0) >> top1; }
  .pe2 { .write = write; .spad = (0 + 0) >> top1; }
  .pe3 { .write = write; .spad = (0) >> (top1); }
}

@kernel checkShrDyn2 config | exec
void checkShrDyn2Run(void) {
}

@emulate "shr_dyn_3"
.kernel checkShrDyn3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 1 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (1) >> top1; }
  .pe2 { .write = write; .spad = (1 + 0) >> top1; }
  .pe3 { .write = write; .spad = (1) >> (top1); }
}

@kernel checkShrDyn3 config | exec
void checkShrDyn3Run(void) {
}

@emulate "shr_dyn_4"
.kernel checkShrDyn4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -1 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (-1) >> top1; }
  .pe2 { .write = write; .spad = (-1 + 0) >> top1; }
  .pe3 { .write = write; .spad = (-1) >> (top1); }
}

@kernel checkShrDyn4 config | exec
void checkShrDyn4Run(void) {
}

@emulate "shr_dyn_5"
.kernel checkShrDyn5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388607 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (8388607) >> top1; }
  .pe2 { .write = write; .spad = (8388607 + 0) >> top1; }
  .pe3 { .write = write; .spad = (8388607) >> (top1); }
}

@kernel checkShrDyn5 config | exec
void checkShrDyn5Run(void) {
}

@emulate "shr_dyn_6"
.kernel checkShrDyn6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = -8388608 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (-8388608) >> top1; }
  .pe2 { .write = write; .spad = (-8388608 + 0) >> top1; }
  .pe3 { .write = write; .spad = (-8388608) >> (top1); }
}

@kernel checkShrDyn6 config | exec
void checkShrDyn6Run(void) {
}

@emulate "shl_dyn_u"
.kernel checkShlDynU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 12582912 << top1; }
  .pe1 { .top = top; .write = write; .spad = (12582912) << top1; }
  .pe2 { .write = write; .spad = (12582912 + 0) << top1; }
  .pe3 { .write = write; .spad = (12582912) << (top1); }
}

@kernel checkShlDynU config | exec
void checkShlDynURun(void) {
}

@emulate "shl_dyn_u_2"
.kernel checkShlDynU2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388608 << top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608) << top1; }
  .pe2 { .write = write; .spad = (8388608 + 0) << top1; }
  .pe3 { .write = write; .spad = (8388608) << (top1); }
}

@kernel checkShlDynU2 config | exec
void checkShlDynU2Run(void) {
}

@emulate "shl_dyn_u_3"
.kernel checkShlDynU3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 16777215 << top1; }
  .pe1 { .top = top; .write = write; .spad = (16777215) << top1; }
  .pe2 { .write = write; .spad = (16777215 + 0) << top1; }
  .pe3 { .write = write; .spad = (16777215) << (top1); }
}

@kernel checkShlDynU3 config | exec
void checkShlDynU3Run(void) {
}

@emulate "shl_dyn_u_4"
.kernel checkShlDynU4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388609 << top1; }
  .pe1 { .top = top; .write = write; .spad = (8388609) << top1; }
  .pe2 { .write = write; .spad = (8388609 + 0) << top1; }
  .pe3 { .write = write; .spad = (8388609) << (top1); }
}

@kernel checkShlDynU4 config | exec
void checkShlDynU4Run(void) {
}

@emulate "shl_dyn_u_5"
.kernel checkShlDynU5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 11184810 << top1; }
  .pe1 { .top = top; .write = write; .spad = (11184810) << top1; }
  .pe2 { .write = write; .spad = (11184810 + 0) << top1; }
  .pe3 { .write = write; .spad = (11184810) << (top1); }
}

@kernel checkShlDynU5 config | exec
void checkShlDynU5Run(void) {
}

@emulate "shr_dyn_u"
.kernel checkShrDynU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 12582912 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (12582912) >> top1; }
  .pe2 { .write = write; .spad = (12582912 + 0) >> top1; }
  .pe3 { .write = write; .spad = (12582912) >> (top1); }
}

@kernel checkShrDynU config | exec
void checkShrDynURun(void) {
}

@emulate "shr_dyn_u_2"
.kernel checkShrDynU2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388608 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (8388608) >> top1; }
  .pe2 { .write = write; .spad = (8388608 + 0) >> top1; }
  .pe3 { .write = write; .spad = (8388608) >> (top1); }
}

@kernel checkShrDynU2 config | exec
void checkShrDynU2Run(void) {
}

@emulate "shr_dyn_u_3"
.kernel checkShrDynU3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 16777215 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (16777215) >> top1; }
  .pe2 { .write = write; .spad = (16777215 + 0) >> top1; }
  .pe3 { .write = write; .spad = (16777215) >> (top1); }
}

@kernel checkShrDynU3 config | exec
void checkShrDynU3Run(void) {
}

@emulate "shr_dyn_u_4"
.kernel checkShrDynU4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 8388609 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (8388609) >> top1; }
  .pe2 { .write = write; .spad = (8388609 + 0) >> top1; }
  .pe3 { .write = write; .spad = (8388609) >> (top1); }
}

@kernel checkShrDynU4 config | exec
void checkShrDynU4Run(void) {
}

@emulate "shr_dyn_u_5"
.kernel checkShrDynU5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = 11184810 >> top1; }
  .pe1 { .top = top; .write = write; .spad = (11184810) >> top1; }
  .pe2 { .write = write; .spad = (11184810 + 0) >> top1; }
  .pe3 { .write = write; .spad = (11184810) >> (top1); }
}

@kernel checkShrDynU5 config | exec
void checkShrDynU5Run(void) {
}

@emulate "shl_reg"
.kernel checkShlReg direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << top0; }
  .pe1 { .top = top; .write = write; .spad = (top1 << top0); }
  .pe2 { .write = write; .spad = top1 << (top0); }
  .pe3 { .write = write; .spad = (top1) << (top0); }
}

@kernel checkShlReg config | exec
void checkShlRegRun(void) {
}

@emulate "shl_cst"
.kernel checkShlCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 3); }
  .pe2 { .write = write; .spad = top1 << (3 + 0); }
  .pe3 { .write = write; .spad = (top1) << 3; }
}

@kernel checkShlCst config | exec
void checkShlCstRun(void) {
}

@emulate "shl_cst_2"
.kernel checkShlCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 0; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 0); }
  .pe2 { .write = write; .spad = top1 << (0 + 0); }
  .pe3 { .write = write; .spad = (top1) << 0; }
}

@kernel checkShlCst2 config | exec
void checkShlCst2Run(void) {
}

@emulate "shl_cst_3"
.kernel checkShlCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 1; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 1); }
  .pe2 { .write = write; .spad = top1 << (1 + 0); }
  .pe3 { .write = write; .spad = (top1) << 1; }
}

@kernel checkShlCst3 config | exec
void checkShlCst3Run(void) {
}

@emulate "shl_cst_4"
.kernel checkShlCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 31; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 31); }
  .pe2 { .write = write; .spad = top1 << (31 + 0); }
  .pe3 { .write = write; .spad = (top1) << 31; }
}

@kernel checkShlCst4 config | exec
void checkShlCst4Run(void) {
}

@emulate "shl_cst_5"
.kernel checkShlCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << -1; }
  .pe1 { .top = top; .write = write; .spad = (top1 << -1); }
  .pe2 { .write = write; .spad = top1 << (-1 + 0); }
  .pe3 { .write = write; .spad = (top1) << -1; }
}

@kernel checkShlCst5 config | exec
void checkShlCst5Run(void) {
}

@emulate "shl_cst_6"
.kernel checkShlCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << -32; }
  .pe1 { .top = top; .write = write; .spad = (top1 << -32); }
  .pe2 { .write = write; .spad = top1 << (-32 + 0); }
  .pe3 { .write = write; .spad = (top1) << -32; }
}

@kernel checkShlCst6 config | exec
void checkShlCst6Run(void) {
}

@emulate "shl_cst_7"
.kernel checkShlCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 40; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 40); }
  .pe2 { .write = write; .spad = top1 << (40 + 0); }
  .pe3 { .write = write; .spad = (top1) << 40; }
}

@kernel checkShlCst7 config | exec
void checkShlCst7Run(void) {
}

@emulate "shl_cst_8"
.kernel checkShlCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 16777215; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 16777215); }
  .pe2 { .write = write; .spad = top1 << (16777215 + 0); }
  .pe3 { .write = write; .spad = (top1) << 16777215; }
}

@kernel checkShlCst8 config | exec
void checkShlCst8Run(void) {
}

@emulate "shl_cst_9"
.kernel checkShlCst9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 << 4278190083; }
  .pe1 { .top = top; .write = write; .spad = (top1 << 4278190083); }
  .pe2 { .write = write; .spad = top1 << (4278190083 + 0); }
  .pe3 { .write = write; .spad = (top1) << 4278190083; }
}

@kernel checkShlCst9 config | exec
void checkShlCst9Run(void) {
}

@emulate "shr_reg"
.kernel checkShrReg direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >> top0; }
  .pe1 { .top = top; .write = write; .spad = (top1 >> top0); }
  .pe2 { .write = write; .spad = top1 >> (top0); }
  .pe3 { .write = write; .spad = (top1) >> (top0); }
}

@kernel checkShrReg config | exec
void checkShrRegRun(void) {
}

@emulate "shr_cst"
.kernel checkShrCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 3); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 3)); }
  .pe2 { .write = write; .spad = shrcst(top1, 3 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 3); }
}

@kernel checkShrCst config | exec
void checkShrCstRun(void) {
}

@emulate "shr_cst_2"
.kernel checkShrCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 0); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 0)); }
  .pe2 { .write = write; .spad = shrcst(top1, 0 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 0); }
}

@kernel checkShrCst2 config | exec
void checkShrCst2Run(void) {
}

@emulate "shr_cst_3"
.kernel checkShrCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 1); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 1)); }
  .pe2 { .write = write; .spad = shrcst(top1, 1 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 1); }
}

@kernel checkShrCst3 config | exec
void checkShrCst3Run(void) {
}

@emulate "shr_cst_4"
.kernel checkShrCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 31); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 31)); }
  .pe2 { .write = write; .spad = shrcst(top1, 31 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 31); }
}

@kernel checkShrCst4 config | exec
void checkShrCst4Run(void) {
}

@emulate "shr_cst_5"
.kernel checkShrCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, -1); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, -1)); }
  .pe2 { .write = write; .spad = shrcst(top1, -1 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), -1); }
}

@kernel checkShrCst5 config | exec
void checkShrCst5Run(void) {
}

@emulate "shr_cst_6"
.kernel checkShrCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, -32); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, -32)); }
  .pe2 { .write = write; .spad = shrcst(top1, -32 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), -32); }
}

@kernel checkShrCst6 config | exec
void checkShrCst6Run(void) {
}

@emulate "shr_cst_7"
.kernel checkShrCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 40); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 40)); }
  .pe2 { .write = write; .spad = shrcst(top1, 40 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 40); }
}

@kernel checkShrCst7 config | exec
void checkShrCst7Run(void) {
}

@emulate "shr_cst_8"
.kernel checkShrCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 16777215); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 16777215)); }
  .pe2 { .write = write; .spad = shrcst(top1, 16777215 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 16777215); }
}

@kernel checkShrCst8 config | exec
void checkShrCst8Run(void) {
}

@emulate "shr_cst_9"
.kernel checkShrCst9 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = shrcst(top1, 4278190083); }
  .pe1 { .top = top; .write = write; .spad = (shrcst(top1, 4278190083)); }
  .pe2 { .write = write; .spad = shrcst(top1, 4278190083 + 0); }
  .pe3 { .write = write; .spad = shrcst((top1), 4278190083); }
}

@kernel checkShrCst9 config | exec
void checkShrCst9Run(void) {
}

@emulate "shl_reg_u"
.kernel checkShlRegU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< top0; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< top0); }
  .pe2 { .write = write; .spad = top1 <<< (top0); }
  .pe3 { .write = write; .spad = (top1) <<< (top0); }
}

@kernel checkShlRegU config | exec
void checkShlRegURun(void) {
}

@emulate "shl_cst_u"
.kernel checkShlCstU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 3); }
  .pe2 { .write = write; .spad = top1 <<< (3 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< 3; }
}

@kernel checkShlCstU config | exec
void checkShlCstURun(void) {
}

@emulate "shl_cst_u_2"
.kernel checkShlCstU2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 0; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 0); }
  .pe2 { .write = write; .spad = top1 <<< (0 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< 0; }
}

@kernel checkShlCstU2 config | exec
void checkShlCstU2Run(void) {
}

@emulate "shl_cst_u_3"
.kernel checkShlCstU3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 1; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 1); }
  .pe2 { .write = write; .spad = top1 <<< (1 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< 1; }
}

@kernel checkShlCstU3 config | exec
void checkShlCstU3Run(void) {
}

@emulate "shl_cst_u_4"
.kernel checkShlCstU4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< 31; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< 31); }
  .pe2 { .write = write; .spad = top1 <<< (31 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< 31; }
}

@kernel checkShlCstU4 config | exec
void checkShlCstU4Run(void) {
}

@emulate "shl_cst_u_5"
.kernel checkShlCstU5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< -1; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< -1); }
  .pe2 { .write = write; .spad = top1 <<< (-1 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< -1; }
}

@kernel checkShlCstU5 config | exec
void checkShlCstU5Run(void) {
}

@emulate "shl_cst_u_6"
.kernel checkShlCstU6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 <<< -32; }
  .pe1 { .top = top; .write = write; .spad = (top1 <<< -32); }
  .pe2 { .write = write; .spad = top1 <<< (-32 + 0); }
  .pe3 { .write = write; .spad = (top1) <<< -32; }
}

@kernel checkShlCstU6 config | exec
void checkShlCstU6Run(void) {
}

@emulate "shr_reg_u"
.kernel checkShrRegU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> top0; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> top0); }
  .pe2 { .write = write; .spad = top1 >>> (top0); }
  .pe3 { .write = write; .spad = (top1) >>> (top0); }
}

@kernel checkShrRegU config | exec
void checkShrRegURun(void) {
}

@emulate "shr_cst_u"
.kernel checkShrCstU direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 3; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 3); }
  .pe2 { .write = write; .spad = top1 >>> (3 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> 3; }
}

@kernel checkShrCstU config | exec
void checkShrCstURun(void) {
}

@emulate "shr_cst_u_2"
.kernel checkShrCstU2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 0; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 0); }
  .pe2 { .write = write; .spad = top1 >>> (0 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> 0; }
}

@kernel checkShrCstU2 config | exec
void checkShrCstU2Run(void) {
}

@emulate "shr_cst_u_3"
.kernel checkShrCstU3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 1; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 1); }
  .pe2 { .write = write; .spad = top1 >>> (1 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> 1; }
}

@kernel checkShrCstU3 config | exec
void checkShrCstU3Run(void) {
}

@emulate "shr_cst_u_4"
.kernel checkShrCstU4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> 31; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> 31); }
  .pe2 { .write = write; .spad = top1 >>> (31 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> 31; }
}

@kernel checkShrCstU4 config | exec
void checkShrCstU4Run(void) {
}

@emulate "shr_cst_u_5"
.kernel checkShrCstU5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> -1; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> -1); }
  .pe2 { .write = write; .spad = top1 >>> (-1 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> -1; }
}

@kernel checkShrCstU5 config | exec
void checkShrCstU5Run(void) {
}

@emulate "shr_cst_u_6"
.kernel checkShrCstU6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 >>> -32; }
  .pe1 { .top = top; .write = write; .spad = (top1 >>> -32); }
  .pe2 { .write = write; .spad = top1 >>> (-32 + 0); }
  .pe3 { .write = write; .spad = (top1) >>> -32; }
}

@kernel checkShrCstU6 config | exec
void checkShrCstU6Run(void) {
}

@emulate "and"
.kernel checkAnd direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 & top1; }
  .pe1 { .top = top; .write = write; .spad = top1 & top0; }
  .pe2 { .write = write; .spad = (top0 & top1); }
  .pe3 { .write = write; .spad = top0 & (top1); }
}

@kernel checkAnd config | exec
void checkAndRun(void) {
}

@emulate "and_cst"
.kernel checkAndCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 255; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 255); }
  .pe2 { .write = write; .spad = 255 & top1; }
  .pe3 { .write = write; .spad = (top1 & 255); }
}

@kernel checkAndCst config | exec
void checkAndCstRun(void) {
}

@emulate "and_cst_2"
.kernel checkAndCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 0; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 0); }
  .pe2 { .write = write; .spad = 0 & top1; }
  .pe3 { .write = write; .spad = (top1 & 0); }
}

@kernel checkAndCst2 config | exec
void checkAndCst2Run(void) {
}

@emulate "and_cst_3"
.kernel checkAndCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & -1; }
  .pe1 { .top = top; .write = write; .spad = and(top1, -1); }
  .pe2 { .write = write; .spad = -1 & top1; }
  .pe3 { .write = write; .spad = (top1 & -1); }
}

@kernel checkAndCst3 config | exec
void checkAndCst3Run(void) {
}

@emulate "and_cst_4"
.kernel checkAndCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 8388607; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 8388607); }
  .pe2 { .write = write; .spad = 8388607 & top1; }
  .pe3 { .write = write; .spad = (top1 & 8388607); }
}

@kernel checkAndCst4 config | exec
void checkAndCst4Run(void) {
}

@emulate "and_cst_5"
.kernel checkAndCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 8388608; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 8388608); }
  .pe2 { .write = write; .spad = 8388608 & top1; }
  .pe3 { .write = write; .spad = (top1 & 8388608); }
}

@kernel checkAndCst5 config | exec
void checkAndCst5Run(void) {
}

@emulate "and_cst_6"
.kernel checkAndCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 5592405; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 5592405); }
  .pe2 { .write = write; .spad = 5592405 & top1; }
  .pe3 { .write = write; .spad = (top1 & 5592405); }
}

@kernel checkAndCst6 config | exec
void checkAndCst6Run(void) {
}

@emulate "and_cst_7"
.kernel checkAndCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 16777215; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 16777215); }
  .pe2 { .write = write; .spad = 16777215 & top1; }
  .pe3 { .write = write; .spad = (top1 & 16777215); }
}

@kernel checkAndCst7 config | exec
void checkAndCst7Run(void) {
}

@emulate "and_cst_8"
.kernel checkAndCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 & 4278190083; }
  .pe1 { .top = top; .write = write; .spad = and(top1, 4278190083); }
  .pe2 { .write = write; .spad = 4278190083 & top1; }
  .pe3 { .write = write; .spad = (top1 & 4278190083); }
}

@kernel checkAndCst8 config | exec
void checkAndCst8Run(void) {
}

@emulate "nand"
.kernel checkNand direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 & top1); }
  .pe1 { .top = top; .write = write; .spad = ~(top1 & top0); }
  .pe2 { .write = write; .spad = (~(top0 & top1)); }
  .pe3 { .write = write; .spad = ~(top0 & (top1)); }
}

@kernel checkNand config | exec
void checkNandRun(void) {
}

@emulate "nand_cst"
.kernel checkNandCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 255); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 255); }
  .pe2 { .write = write; .spad = ~(255 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 255)); }
}

@kernel checkNandCst config | exec
void checkNandCstRun(void) {
}

@emulate "nand_cst_2"
.kernel checkNandCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 0); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 0); }
  .pe2 { .write = write; .spad = ~(0 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 0)); }
}

@kernel checkNandCst2 config | exec
void checkNandCst2Run(void) {
}

@emulate "nand_cst_3"
.kernel checkNandCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & -1); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, -1); }
  .pe2 { .write = write; .spad = ~(-1 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & -1)); }
}

@kernel checkNandCst3 config | exec
void checkNandCst3Run(void) {
}

@emulate "nand_cst_4"
.kernel checkNandCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 8388607); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 8388607); }
  .pe2 { .write = write; .spad = ~(8388607 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 8388607)); }
}

@kernel checkNandCst4 config | exec
void checkNandCst4Run(void) {
}

@emulate "nand_cst_5"
.kernel checkNandCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 8388608); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 8388608); }
  .pe2 { .write = write; .spad = ~(8388608 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 8388608)); }
}

@kernel checkNandCst5 config | exec
void checkNandCst5Run(void) {
}

@emulate "nand_cst_6"
.kernel checkNandCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 5592405); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 5592405); }
  .pe2 { .write = write; .spad = ~(5592405 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 5592405)); }
}

@kernel checkNandCst6 config | exec
void checkNandCst6Run(void) {
}

@emulate "nand_cst_7"
.kernel checkNandCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 16777215); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 16777215); }
  .pe2 { .write = write; .spad = ~(16777215 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 16777215)); }
}

@kernel checkNandCst7 config | exec
void checkNandCst7Run(void) {
}

@emulate "nand_cst_8"
.kernel checkNandCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 & 4278190083); }
  .pe1 { .top = top; .write = write; .spad = ~and(top1, 4278190083); }
  .pe2 { .write = write; .spad = ~(4278190083 & top1); }
  .pe3 { .write = write; .spad = (~(top1 & 4278190083)); }
}

@kernel checkNandCst8 config | exec
void checkNandCst8Run(void) {
}

@emulate "or"
.kernel checkOr direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 | top1; }
  .pe1 { .top = top; .write = write; .spad = top1 | top0; }
  .pe2 { .write = write; .spad = (top0 | top1); }
  .pe3 { .write = write; .spad = top0 | (top1); }
}

@kernel checkOr config | exec
void checkOrRun(void) {
}

@emulate "or_cst"
.kernel checkOrCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | 128; }
  .pe1 { .top = top; .write = write; .spad = or(top1, 128); }
  .pe2 { .write = write; .spad = 128 | top1; }
  .pe3 { .write = write; .spad = (top1 | 128); }
}

@kernel checkOrCst config | exec
void checkOrCstRun(void) {
}

@emulate "or_cst_2"
.kernel checkOrCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | 0; }
  .pe1 { .top = top; .write = write; .spad = or(top1, 0); }
  .pe2 { .write = write; .spad = 0 | top1; }
  .pe3 { .write = write; .spad = (top1 | 0); }
}

@kernel checkOrCst2 config | exec
void checkOrCst2Run(void) {
}

@emulate "or_cst_3"
.kernel checkOrCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | -1; }
  .pe1 { .top = top; .write = write; .spad = or(top1, -1); }
  .pe2 { .write = write; .spad = -1 | top1; }
  .pe3 { .write = write; .spad = (top1 | -1); }
}

@kernel checkOrCst3 config | exec
void checkOrCst3Run(void) {
}

@emulate "or_cst_4"
.kernel checkOrCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | 8388607; }
  .pe1 { .top = top; .write = write; .spad = or(top1, 8388607); }
  .pe2 { .write = write; .spad = 8388607 | top1; }
  .pe3 { .write = write; .spad = (top1 | 8388607); }
}

@kernel checkOrCst4 config | exec
void checkOrCst4Run(void) {
}

@emulate "or_cst_5"
.kernel checkOrCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | 8388608; }
  .pe1 { .top = top; .write = write; .spad = or(top1, 8388608); }
  .pe2 { .write = write; .spad = 8388608 | top1; }
  .pe3 { .write = write; .spad = (top1 | 8388608); }
}

@kernel checkOrCst5 config | exec
void checkOrCst5Run(void) {
}

@emulate "or_cst_6"
.kernel checkOrCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | 5592405; }
  .pe1 { .top = top; .write = write; .spad = or(top1, 5592405); }
  .pe2 { .write = write; .spad = 5592405 | top1; }
  .pe3 { .write = write; .spad = (top1 | 5592405); }
}

@kernel checkOrCst6 config | exec
void checkOrCst6Run(void) {
}

@emulate "or_cst_7"
.kernel checkOrCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | 16777215; }
  .pe1 { .top = top; .write = write; .spad = or(top1, 16777215); }
  .pe2 { .write = write; .spad = 16777215 | top1; }
  .pe3 { .write = write; .spad = (top1 | 16777215); }
}

@kernel checkOrCst7 config | exec
void checkOrCst7Run(void) {
}

@emulate "or_cst_8"
.kernel checkOrCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 | 4278190083; }
  .pe1 { .top = top; .write = write; .spad = or(top1, 4278190083); }
  .pe2 { .write = write; .spad = 4278190083 | top1; }
  .pe3 { .write = write; .spad = (top1 | 4278190083); }
}

@kernel checkOrCst8 config | exec
void checkOrCst8Run(void) {
}

@emulate "nor"
.kernel checkNor direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 | top1); }
  .pe1 { .top = top; .write = write; .spad = ~(top1 | top0); }
  .pe2 { .write = write; .spad = (~(top0 | top1)); }
  .pe3 { .write = write; .spad = ~(top0 | (top1)); }
}

@kernel checkNor config | exec
void checkNorRun(void) {
}

@emulate "nor_cst"
.kernel checkNorCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | 128); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, 128); }
  .pe2 { .write = write; .spad = ~(128 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | 128)); }
}

@kernel checkNorCst config | exec
void checkNorCstRun(void) {
}

@emulate "nor_cst_2"
.kernel checkNorCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | 0); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, 0); }
  .pe2 { .write = write; .spad = ~(0 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | 0)); }
}

@kernel checkNorCst2 config | exec
void checkNorCst2Run(void) {
}

@emulate "nor_cst_3"
.kernel checkNorCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | -1); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, -1); }
  .pe2 { .write = write; .spad = ~(-1 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | -1)); }
}

@kernel checkNorCst3 config | exec
void checkNorCst3Run(void) {
}

@emulate "nor_cst_4"
.kernel checkNorCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | 8388607); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, 8388607); }
  .pe2 { .write = write; .spad = ~(8388607 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | 8388607)); }
}

@kernel checkNorCst4 config | exec
void checkNorCst4Run(void) {
}

@emulate "nor_cst_5"
.kernel checkNorCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | 8388608); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, 8388608); }
  .pe2 { .write = write; .spad = ~(8388608 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | 8388608)); }
}

@kernel checkNorCst5 config | exec
void checkNorCst5Run(void) {
}

@emulate "nor_cst_6"
.kernel checkNorCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | 5592405); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, 5592405); }
  .pe2 { .write = write; .spad = ~(5592405 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | 5592405)); }
}

@kernel checkNorCst6 config | exec
void checkNorCst6Run(void) {
}

@emulate "nor_cst_7"
.kernel checkNorCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | 16777215); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, 16777215); }
  .pe2 { .write = write; .spad = ~(16777215 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | 16777215)); }
}

@kernel checkNorCst7 config | exec
void checkNorCst7Run(void) {
}

@emulate "nor_cst_8"
.kernel checkNorCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 | 4278190083); }
  .pe1 { .top = top; .write = write; .spad = ~or(top1, 4278190083); }
  .pe2 { .write = write; .spad = ~(4278190083 | top1); }
  .pe3 { .write = write; .spad = (~(top1 | 4278190083)); }
}

@kernel checkNorCst8 config | exec
void checkNorCst8Run(void) {
}

@emulate "xor"
.kernel checkXor direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top0 ^ top1; }
  .pe1 { .top = top; .write = write; .spad = top1 ^ top0; }
  .pe2 { .write = write; .spad = (top0 ^ top1); }
  .pe3 { .write = write; .spad = top0 ^ (top1); }
}

@kernel checkXor config | exec
void checkXorRun(void) {
}

@emulate "xor_cst"
.kernel checkXorCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ 85; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, 85); }
  .pe2 { .write = write; .spad = 85 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ 85); }
}

@kernel checkXorCst config | exec
void checkXorCstRun(void) {
}

@emulate "xor_cst_2"
.kernel checkXorCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ 0; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, 0); }
  .pe2 { .write = write; .spad = 0 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ 0); }
}

@kernel checkXorCst2 config | exec
void checkXorCst2Run(void) {
}

@emulate "xor_cst_3"
.kernel checkXorCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ -1; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, -1); }
  .pe2 { .write = write; .spad = -1 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ -1); }
}

@kernel checkXorCst3 config | exec
void checkXorCst3Run(void) {
}

@emulate "xor_cst_4"
.kernel checkXorCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ 8388607; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, 8388607); }
  .pe2 { .write = write; .spad = 8388607 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ 8388607); }
}

@kernel checkXorCst4 config | exec
void checkXorCst4Run(void) {
}

@emulate "xor_cst_5"
.kernel checkXorCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ 8388608; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, 8388608); }
  .pe2 { .write = write; .spad = 8388608 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ 8388608); }
}

@kernel checkXorCst5 config | exec
void checkXorCst5Run(void) {
}

@emulate "xor_cst_6"
.kernel checkXorCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ 5592405; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, 5592405); }
  .pe2 { .write = write; .spad = 5592405 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ 5592405); }
}

@kernel checkXorCst6 config | exec
void checkXorCst6Run(void) {
}

@emulate "xor_cst_7"
.kernel checkXorCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ 16777215; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, 16777215); }
  .pe2 { .write = write; .spad = 16777215 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ 16777215); }
}

@kernel checkXorCst7 config | exec
void checkXorCst7Run(void) {
}

@emulate "xor_cst_8"
.kernel checkXorCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 ^ 4278190083; }
  .pe1 { .top = top; .write = write; .spad = xor(top1, 4278190083); }
  .pe2 { .write = write; .spad = 4278190083 ^ top1; }
  .pe3 { .write = write; .spad = (top1 ^ 4278190083); }
}

@kernel checkXorCst8 config | exec
void checkXorCst8Run(void) {
}

@emulate "xnor"
.kernel checkXnor direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top0 ^ top1); }
  .pe1 { .top = top; .write = write; .spad = ~(top1 ^ top0); }
  .pe2 { .write = write; .spad = (~(top0 ^ top1)); }
  .pe3 { .write = write; .spad = ~(top0 ^ (top1)); }
}

@kernel checkXnor config | exec
void checkXnorRun(void) {
}

@emulate "xnor_cst"
.kernel checkXnorCst direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ 85); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, 85); }
  .pe2 { .write = write; .spad = ~(85 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ 85)); }
}

@kernel checkXnorCst config | exec
void checkXnorCstRun(void) {
}

@emulate "xnor_cst_2"
.kernel checkXnorCst2 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ 0); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, 0); }
  .pe2 { .write = write; .spad = ~(0 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ 0)); }
}

@kernel checkXnorCst2 config | exec
void checkXnorCst2Run(void) {
}

@emulate "xnor_cst_3"
.kernel checkXnorCst3 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ -1); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, -1); }
  .pe2 { .write = write; .spad = ~(-1 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ -1)); }
}

@kernel checkXnorCst3 config | exec
void checkXnorCst3Run(void) {
}

@emulate "xnor_cst_4"
.kernel checkXnorCst4 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ 8388607); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, 8388607); }
  .pe2 { .write = write; .spad = ~(8388607 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ 8388607)); }
}

@kernel checkXnorCst4 config | exec
void checkXnorCst4Run(void) {
}

@emulate "xnor_cst_5"
.kernel checkXnorCst5 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ 8388608); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, 8388608); }
  .pe2 { .write = write; .spad = ~(8388608 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ 8388608)); }
}

@kernel checkXnorCst5 config | exec
void checkXnorCst5Run(void) {
}

@emulate "xnor_cst_6"
.kernel checkXnorCst6 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ 5592405); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, 5592405); }
  .pe2 { .write = write; .spad = ~(5592405 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ 5592405)); }
}

@kernel checkXnorCst6 config | exec
void checkXnorCst6Run(void) {
}

@emulate "xnor_cst_7"
.kernel checkXnorCst7 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ 16777215); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, 16777215); }
  .pe2 { .write = write; .spad = ~(16777215 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ 16777215)); }
}

@kernel checkXnorCst7 config | exec
void checkXnorCst7Run(void) {
}

@emulate "xnor_cst_8"
.kernel checkXnorCst8 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~(top1 ^ 4278190083); }
  .pe1 { .top = top; .write = write; .spad = ~xor(top1, 4278190083); }
  .pe2 { .write = write; .spad = ~(4278190083 ^ top1); }
  .pe3 { .write = write; .spad = (~(top1 ^ 4278190083)); }
}

@kernel checkXnorCst8 config | exec
void checkXnorCst8Run(void) {
}

@emulate "tst_em1"
.kernel checkTstEm1 direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 == -1; }
  .pe1 { .top = top; .write = write; .spad = top1 == 0xffffff; }
  .pe2 { .write = write; .spad = (top1 == -1); }
  .pe3 { .write = write; .spad = (top1) == -1; }
}

@kernel checkTstEm1 config | exec
void checkTstEm1Run(void) {
}

@emulate "tst_nnz"
.kernel checkTstNnz direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = top1 != 0; }
  .pe1 { .top = top; .write = write; .spad = (top1 != 0); }
  .pe2 { .write = write; .spad = (top1) != 0; }
  .pe3 { .write = write; .spad = top1 != (0); }
}

@kernel checkTstNnz config | exec
void checkTstNnzRun(void) {
}

@emulate "tst_par"
.kernel checkTstPar direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = parity(top1); }
  .pe1 { .top = top; .write = write; .spad = (parity(top1)); }
  .pe2 { .write = write; .spad = parity( top1 ); }
  .pe3 { .write = write; .spad = parity((top1)); }
}

@kernel checkTstPar config | exec
void checkTstParRun(void) {
}

@emulate "not"
.kernel checkNot direct {
  Int count = 256 - 1;

  Transfer top0Transfer = { memory: in0, count };
  Transfer top1Transfer = { memory: in1, count };

  .load { .transfer = top0Transfer; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = top1Transfer; .scope = global; .offsets { .top1 = 0; } }

  Agu top = { count };
  Agu write = { count, cyc: auto };

  .pe0 { .top = top; .write = write; .spad = ~top1; }
  .pe1 { .top = top; .write = write; .spad = (~top1); }
  .pe2 { .write = write; .spad = ~(top1); }
  .pe3 { .write = write; .spad = (~(top1)); }
}

@kernel checkNot config | exec
void checkNotRun(void) {
}
