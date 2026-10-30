[Index](../VMEE.md) · [Traces](traces.md) · [Memories](memories.md)

# Running on the PSP with vmeh

## Contents

- [3.1 Principle](#31-principle)
- [3.2 Building](#32-building)
- [3.3 Several emulations](#33-several-emulations)
- [3.4 The window of the buffers](#34-the-window-of-the-buffers)
- [3.5 The command vmeh](#35-the-command-vmeh)
- [3.6 Comparing with vmee](#36-comparing-with-vmee)
- [3.7 Errors](#37-errors)

## 3.1 Principle

`vmeh` writes the program that runs the kernels marked with `@emulate` ([1.1](running.md#11-marking-a-kernel)) on the PSP. The program plays the same calls as `vmee --run` ([1.2](running.md#12-running-a-kernel)): the `@kernel` of the mark with its actions, or the calls of the block `@emulate "id" { … }`.

When the last call is over, the program writes the base buffers in the file `log.txt`, in the format that `vmee --run` shows. The two results are made to be compared.

**Rules:**

- The calls of a block are played in the order written, with their `.params` and `.memory`.
- The vmeg statements written in the body of a call (`.load`, `.store`) are done before the buffers are written, and follow the same rules as in `vmee` ([1.2](running.md#12-running-a-kernel)).
- The program is a vmeg file, translated by `vmegc` like any other.

## 3.2 Building

```
cd samples/vmeh
mkdir build && cd build
cmake -DVMEH_SOURCE=samples/c/saturate-clamp.vmeg.c ..
make
```

**Explanation of the code above:**

- `-DVMEH_SOURCE` is the vmeg file with the `@emulate`, a path relative to the root of the project.
- `cmake` runs `vmeh.py` on the file and writes `hw.vmeg.cpp` in `build`. `make` translates it with `vmegc` ([1.7](../vmeg/running.md#17-cmake)) and builds the program.
- The EBOOT is in `build`.

**Rules:**

- The build needs the PSP toolchain, `PSPDEV` set, like the other samples.
- With one `@emulate`, the program runs it, writes `log.txt` in the folder of the EBOOT and exits. It shows nothing on the screen.
- `-DVMEH_SOURCE` is needed: without it `cmake` stops with an error ([3.7](#37-errors)).
