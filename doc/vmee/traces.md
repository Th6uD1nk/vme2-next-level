[Index](../VMEE.md) · [Running vmee](running.md) · [Running on the PSP with vmeh](vmeh.md)

# Traces

## Contents

- [2.1 The trace file](#21-the-trace-file)
- [2.2 Playing a trace](#22-playing-a-trace)
- [2.3 Errors](#23-errors)

## 2.1 The trace file

A trace is a text file with one event per line. The events are what a program sends to the VME: the writes in the registers and the words of the RAM that the DMAC reads. This is the load of the kernel of [1.2](running.md#12-running-a-kernel), as `vmee --run twice main.vmeg.cpp --trace trace.txt` writes it:

```
M 0x8800000 0x1 0x2 0x3 0x4 0x5 0x6 0x7 0x8
W 0x440ff010 0x48800000
W 0x440ff014 0x7
W 0x440ff018 0x8000
W 0x440ff008 0x40
```

**Explanation of the code above:**

- `M 0x8800000 0x1 … 0x8` puts the 8 words of `input` in the RAM at the address `0x8800000`.
- `W 0x440ff010 0x48800000` writes the RAM address in the register `0x010` of the DMAC, `W 0x440ff014 0x7` the count (the number of words minus 1) in the register `0x014`, and `W 0x440ff018 0x8000` the offset in the scratchpad, in words, in the register `0x018`: `0x8000` is the first word of `TOP_0`.
- `W 0x440ff008 0x40` writes the control register `0x008`, which starts the transfer: `0x40` copies the words of the RAM to the scratchpad.

| Event | Meaning |
|---|---|
| `W 0x<address> 0x<value>` | writes `value` at `address`, in one of the three zones of the VME: the scratchpad from `0x44000000`, the registers of the datapath from `0x440f8000`, the DMAC from `0x440ff000` |
| `M 0x<address> 0x<word> …` | the words of the RAM from `address`, put in the trace before the transfer that reads them |

**Rules:**

- The numbers are hexadecimal, with or without `0x`.
- Everything after a `#` is a comment, and the empty lines are skipped.
- The events are played in the order of the file.
- `--trace` of `--run` writes a file in this format ([1.5](running.md#15---trace)).
