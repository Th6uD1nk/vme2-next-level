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

## 3.3 Several emulations

```c
@emulate "add"
.kernel add direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

@emulate "sub"
.kernel sub direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 - top0; }
}
```

**Explanation of the code above:**

- The file has two `@emulate`. The program built by `vmeh` has both of them.
- The screen shows the number and the id of the current one, `001 - add` first. The first one runs at the start.
- Left and Right go to the previous and to the next one. They stop at the first and at the last one, and each emulation runs when it is reached.
- `log.txt` holds the dump of the current emulation only: each new run replaces it. Its first line is `Kernel: 001 - add`, followed by the buffers in the format of [1.2](running.md#12-running-a-kernel).

**Rules:**

- `-DVMEH_ID=id` keeps only the `@emulate` with that id: `cmake -DVMEH_SOURCE=… -DVMEH_ID=sub ..` builds a program with `sub` alone, which behaves as in [3.2](#32-building).
- With one `@emulate`, the program shows nothing and does not wait for a button ([3.2](#32-building)).

## 3.4 The window of the buffers

The window is the words of each base buffer that the program writes in `log.txt`, as `--buffers-start` and `--buffers-words` choose them for `vmee` ([1.4](running.md#14-the-window-of-the-buffers)).

```
cmake -DVMEH_SOURCE=samples/c/saturate-clamp.vmeg.c -DVMEH_BUFFERS_START=2 -DVMEH_BUFFERS_WORDS=4 ..
```

```
start: 2
count: 4
```

**Explanation of the code above:**

- `-DVMEH_BUFFERS_START` and `-DVMEH_BUFFERS_WORDS` give the first word and the number of words. The defaults are 0 and 32, as in `vmee`.
- With several `@emulate` ([3.3](#33-several-emulations)), the program reads the window at the start from `config.txt`, next to `log.txt`, with the lines `start:` and `count:`. The window can be changed without building the program again.
- When `config.txt` is not there, or has no such line, the values given to `cmake` are used.

**Rules:**

- The window has the limits of [1.4](running.md#14-the-window-of-the-buffers): `start + words` is 2048 at most, and the number of words is 1 or more. `cmake` stops with an error if the values it gets are out of these limits ([3.7](#37-errors)). The values of `config.txt` are not checked.
- With one `@emulate`, only the options of `cmake` apply: the program does not read `config.txt`.
