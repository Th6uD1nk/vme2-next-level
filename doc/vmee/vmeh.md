[Index](../VMEE.md) · [Traces](traces.md) · [Running on the PSP with vmegt](vmegt.md) · [Memories](memories.md)

# Running on the PSP with vmeh

## Contents

- [3.1 Principle](#31-principle)
  - [3.1.1 Pointers](#311-pointers)
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
- The `@declare` blocks ([2.2.3](../vmeg/language.md#223-the-declare-block)) that serve the calls of the emulation are in the program, so the `Transfer` of a `@declare` and its spreads are played as in `vmee`.
- The program is a vmeg file, translated by `vmegc` like any other.

### 3.1.1 Pointers

A `Buffer*` pointer ([8.1.2](../vmeg/arrays.md#812-buffer-pointers)) that a `.load` or a `.store` of the emulation names is written in the program with its target.

```c
volatile Buffer two[4] = { 10, 20, 30, 40 };
volatile Buffer* stage = (volatile u32*)0x40000000;

.kernel doubler direct {
  Agu top = { count: 3 }, write = { count: 3, cyc: auto };
  .pe0 { .top = top; .write = write; .spad = top0 + top0; }
}

void meLibOnProcess(void) {
  @emulate "pick" {
    volatile Buffer* signal = two;
    @kernel doubler config {
      Transfer in = { memory: signal, count: 3 };
      .load { .transfer = in; .scope = local; .offsets { .top0 = 0; } }
    }
    @kernel doubler exec {
      Transfer out = { memory: stage, count: 3 };
      .store { .transfer = out; .scope = global; .offsets { .base0 = 0; } }
    }
  }
}
```

**Explanation of the code above:**

- `vmeh` writes `volatile Buffer* signal = two;` in the function of the program, and `volatile Buffer* stage = (volatile u32*)0x40000000;` among the globals. The program on the PSP uses the pointers as they are.
- `stage` is a fixed address of the PSP: the `.store` writes there, in the local eDRAM of the Media Engine.

**Rules:**

- The target of a pointer is, as in `vmee` ([1.7.1](running.md#171-pointers)): the array of `--use`; the array that its initializer names alone; or an address made of numbers, operators, words of types and macros of the files.
- A pointer whose initializer is none of these, like `volatile Buffer* signal = table[index];`, stops `vmeh` with `the pointer signal of the @emulate "pick" is initialised with an expression that vmeh cannot write, give it the name of an array`. `--use signal=two` gives it the array `two`.
- `--use pointer=array` gives the array to the pointer, as in `vmee` ([1.7](running.md#17---use)), but only to a pointer: a name that is not a pointer that the emulation names is an error ([3.7](#37-errors)), where `vmee --use` also replaces an array.
- With several emulations ([3.3](#33-several-emulations)), a `--use` goes to the emulations that name that pointer.
- The pointers that the emulation does not name are not written in the program.

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
- `-DVMEH_USE="signal=two"` gives an array to a pointer, as `--use` does ([3.1.1](#311-pointers)). Several pairs are separated with `;`: `-DVMEH_USE="signal=two;stage=other"`.

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

## 3.5 The command vmeh

`vmeh` writes the vmeg file of the program. `cmake` runs it ([3.2](#32-building)); it can also be run alone.

```
vmeh --extract pick -o hw.vmeg.cpp --buffers-words 4 --use signal=two main.vmeg.cpp
```

**Explanation of the code above:**

- `--extract pick` keeps the `@emulate` with the id `pick`. Without it, the program has all the emulations of the files ([3.3](#33-several-emulations)).
- `-o hw.vmeg.cpp` is the file written. It is needed.
- `--buffers-start` and `--buffers-words` choose the window of the buffers ([3.4](#34-the-window-of-the-buffers)).
- `--use signal=two` gives the array `two` to the pointer `signal` ([3.1.1](#311-pointers)).
- `main.vmeg.cpp` is the file with the `@emulate`. Several files can be given, as for `vmee` ([1.3](running.md#13-several-files)).

| `cmake` | `vmeh` |
|---|---|
| `-DVMEH_SOURCE=file` | the input file, a path relative to the root of the project |
| `-DVMEH_ID=id` | `--extract id` |
| `-DVMEH_USE="p=a;q=b"` | `--use p=a --use q=b` |
| `-DVMEH_BUFFERS_START=n` | `--buffers-start n` |
| `-DVMEH_BUFFERS_WORDS=n` | `--buffers-words n` |

**Rules:**

- `vmeh` chooses the emulation by its id and reads the files, the window and `--use` like `vmee` ([1](running.md)), with these differences: `--use` gives an array to a pointer only ([3.1.1](#311-pointers)), and there is no `--list`, `--trace`, `--compat` or `--run`.
- `vmeh` writes a program and does not run it. The program is built with `cmake` and `make` ([3.2](#32-building)) and run on the PSP.

## 3.6 Comparing with vmee

The program writes the base buffers in `log.txt` as `vmee --run` shows them ([1.2](running.md#12-running-a-kernel)): `Buffer: BASE n`, then the words, four per line, each one as `0x%08x`. Both results are read the same way.

```
vmee --run pick main.vmeg.cpp --use signal=two --buffers-words 4
```

```
cmake -DVMEH_SOURCE=main.vmeg.cpp -DVMEH_ID=pick -DVMEH_USE="signal=two" -DVMEH_BUFFERS_WORDS=4 ..
```

**Explanation of the code above:**

- The first command plays the emulation `pick` in `vmee`. The second builds the program for the PSP with the same id, the same array for `signal` and the same window.
- The program is run on the PSP. The `Buffer: BASE n` lines of its `log.txt` are compared with the ones that `vmee` shows.

**Rules:**

- The id, the window and the arrays of `--use` are the same on both sides.
- With several emulations, `log.txt` holds the current one only, and its first line is `Kernel: 001 - id` ([3.3](#33-several-emulations)): that line is not in the output of `vmee`.

## 3.7 Errors

The errors of `cmake` stop the configuration. The errors of `vmeh` are printed as `file: message`, with the exit code 1, and the errors of its command line as `vmeh: error: message`, with the exit code 2. The errors of a kernel or of an array come from `vmegc` ([14](../VMEG.md#14-errors)).

| Section | Message | Cause |
|---|---|---|
| [3.2](#32-building) | `give the vmeg file that has the @emulate, for example: cmake -DVMEH_SOURCE=path/to/file.vmeg.cpp ..` | `cmake` without `-DVMEH_SOURCE` |
| [3.5](#35-the-command-vmeh) | `vmeh: error: the following arguments are required: -o/--output` | `vmeh` without `-o` |
| [3.5](#35-the-command-vmeh) | `file: no such file or directory` | an input file that cannot be read |
| [3.5](#35-the-command-vmeh) | `there is no @emulate in these files` | no `@emulate` in the files |
| [3.5](#35-the-command-vmeh) | `no @emulate with the id 'x' (a, b)` | an id that no mark has; the message lists the ids of the files |
| [3.5](#35-the-command-vmeh) | `the @emulate "id" is in a and b` | the mark is in two of the files |
| [3.5](#35-the-command-vmeh) | `the macro N has two different values in the files of the @emulate` | a `#define` with two values in the files that supply the arrays |
| [3.4](#34-the-window-of-the-buffers) | `the first word of the buffers cannot be negative` | `--buffers-start` below 0 |
| [3.4](#34-the-window-of-the-buffers) | `the number of words of the buffers must be 1 or more` | `--buffers-words` below 1 |
| [3.4](#34-the-window-of-the-buffers) | `the window of the buffers goes past the end of a buffer (2048 words)` | `start + words` above 2048 |
| [3.1.1](#311-pointers) | `the pointer signal of the @emulate "id" is initialised with an expression that vmeh cannot write, give it the name of an array` | a pointer set by an expression, with no `--use` |
| [3.1.1](#311-pointers) | `--use signal=two: signal is not a pointer that the @emulate reads or writes, vmeh gives an array to a pointer only` | a `--use` whose name is not a pointer that the emulation names |
| [3.1.1](#311-pointers) | `vmeh: error: --use takes NAME=NAME, for example --use input=other (got 'x')` | a `--use` that is not two names with `=` between them |
| [3.1.1](#311-pointers) | `vmeh: error: --use: the array a is replaced twice` | two `--use` with the same name before the `=` |
