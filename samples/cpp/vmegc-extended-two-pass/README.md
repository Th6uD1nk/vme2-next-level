# Extended Two-Pass VME Sample

Demonstrates an `extended` VME kernel (`twoPass`) executing across two hardware passes using virtual PEs `pe[0..7]` and split scratchpad halves (`0x000` for pass 1, `0x400` word offset for pass 2).

## Overview

1. Global `.load` statements transfer `pass1In0`..`pass1In3` (16 words each) into `.top0`..`.top3` and `pass2In0`..`pass2In3` into `.top4`..`.top7` (`+ 0x400`).
2. Pass 1 (`for i in 0..3`) reads `top[i]` and writes `s[i] = top[i] + (i + 1)` to cross-pass staging registers `Staging s[4]`.
3. Between passes, `vmegc` emits `vmeLibProcessAsync();` and `_vmeLibStart();` to queue Pass 1 and switch to delta Pass 2 registers.
4. Pass 2 (`for i in 4..7`) reads `top[i] + s[i - 4]` and writes the 16 results to `BASE_0`..`BASE_3` high halves (`+ 0x400`), before the caller closes with `vmeLibProcessAsync();` and `vmeLibFinishAsync();`.
5. Global `.store` statements copy `.base4`..`.base7` into `out0`..`out3`, while `meLibOnProcess` copies the high scratchpad halves for on-screen hex display and `./log.txt` dump on exit (`HOME`).

## Build

```bash
cmake -B build -S .
cmake --build build
```

This produces `build/EBOOT.PBP`. On exit, `./log.txt` starts each buffer with `0x0066` (`102`), `0x00cc` (`204`), `0x0132` (`306`), and `0x0198` (`408`).
