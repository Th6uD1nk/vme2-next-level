# Pipeline VME Sample

Demonstrates two `pipeline` VME kernels (`pipeSlotDag` and `pipeFourPass`) using `.flow`, `.count`, `.slot`, named `Slot` variables, `Slot` arrays, and automatic `.store` target resolution across multi-pass execution.

## Overview

1. `pipeSlotDag` (`@emulate "slot-dag"`) loads `in0` into `.top0` and `in1` into `.base0`, computes `Slot tap = (base0 & 0xff) >> 1;`, chains linear `.slot` steps and a `for i in 0..6` loop across 3 hardware passes, and stores the final pass output into `out0`.
2. `pipeFourPass` (`@emulate "four-pass"`) loads `in2` into `.top0` and `in3` into `.top1`, populates `Slot stage[2]`, chains linear `.slot` steps and a `for i in 0..19` loop across 4 hardware passes (`2 pass / 2 pass` balanced pairs), and stores the final pass output into `out1`.
3. `meLibOnProcess` executes both kernels and copies `out0` and `out1` into `vmeDebugBuffers` for on-screen display and `./log.txt` dump on exit (`HOME`).

## Build

```bash
cmake -B build -S .
cmake --build build
```

## Check (PSP vs `vmee`)

```bash
python3 samples/debug/vmegc-pipeline/check.py
```
