[Index](../VMEE.md) · [Traces](traces.md)

# Running vmee

## Contents

- [1.1 Marking a kernel](#11-marking-a-kernel)
- [1.2 Running a kernel](#12-running-a-kernel)
- [1.3 Several files](#13-several-files)
- [1.4 The window of the buffers](#14-the-window-of-the-buffers)
- [1.5 --trace](#15---trace)
- [1.6 --compat](#16---compat)
- [1.7 --use](#17---use)
  - [1.7.1 Pointers](#171-pointers)
- [1.8 --list](#18---list)
- [1.9 Errors](#19-errors)

## 1.1 Marking a kernel

```c
@emulate "twice"
.kernel twice direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}
```

**Explanation of the code above:**

- `@emulate "twice"` marks the kernel `twice`. The emulator is asked for the kernel by this id.
- `vmegc` does not write the mark in the C or C++ file.

**Rules:**

- The mark is written right above the `.kernel`. The id is made of letters, digits, `-` and `_`, between double quotes, and is unique in the file.
- The mark has a second form, `@emulate "id" { … }`, which surrounds calls of kernels written in a function. The rules of both forms are in [Emulation](../vmeg/emulation.md).

## 1.2 Running a kernel

```c
volatile Buffer input[8] = { 1, 2, 3, 4, 5, 6, 7, 8 };

@emulate "twice"
.kernel twice direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  Transfer in = { memory: input, count: 7 };
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

@kernel twice config | exec
void run(void) {
}
```

```
vmee --run twice main.vmeg.cpp --buffers-words 8
```

shows:

```
Buffer: BASE 0
0x00000002, 0x00000004, 0x00000006, 0x00000008,
0x0000000a, 0x0000000c, 0x0000000e, 0x00000010,
```

followed by the same lines for `BASE 1` to `BASE 3`.

**Explanation of the code above:**

- `--run twice` plays the kernel marked `twice`. `vmee` is the command of `./install.sh`, `python3 vmeemu.py` is the same command.
- The result is written like `vmeDebugDumpBuffers` does on the PSP: `Buffer: BASE n`, then the words of the buffer, four per line, each one as `0x%08x`.
- The `.load` copies `input` to `TOP_0` before the kernel runs. The kernel adds each word to itself and writes the result in `BASE_0`.

**Rules:**

- The kernel is `direct` or `memory`. A memory kernel gives the same result as a direct one.
- With the mark above a `.kernel`, the emulator plays the definition of the kernel as `config | exec` (with `build` first for a `memory` kernel).
- With the block `@emulate "id" { … }`, the emulator plays the calls in the order written, each one with its actions: a call with `config` alone configures the kernel and runs nothing.
- A call does the `.load` of its kernel first and its `.store` last, whatever the actions are, and the vmeg statements written in the body of the call (`.load`, `.store`) come after its actions, the way `vmegc` generates them ([10.5](../vmeg/calling.md#105-uploads-and-downloads-around-the-run), [11.3](../vmeg/blocks.md#113-the-vmeg-statements-of-a-block)). The arrays they use must be declared in the files ([1.3](#13-several-files)).
- The variables of a `@declare` ([2.2.3](../vmeg/language.md#223-the-declare-block)) that serve the calls are used as in the program: a `Transfer` of a `@declare` and its spreads ([9.1.2](../vmeg/transfers.md#912-the-spread)) are played with their values.
- The VME is reset once, before the first call. A call starts from the state that the previous one left in the scratchpad, and the arrays that a `.store` has written are what the `.load` of the next calls read.
- Only the four base buffers are shown. A `.store` does not show its array: read the result in the buffer it comes from.
- The RAM starts as an image of zeros. A word that no array and no earlier `.store` has written reads 0. The local eDRAM of the Media Engine is the first 4 MB of the addresses (2 MB on the phat, 4 MB on the slim, the larger size is used): the words never written there are read with no message, and above `0x400000` with the warning of [1.9](#19-errors). An address is taken on its 29 low bits, so `0x40000000` and `0x0` are the same word.
- The kernel is built into a small host program with `g++ -m32` and the library of the submodule `me-core-mapper`. `--run` needs `g++` with 32 bit support, and the submodule must not be empty (`git submodule update --init me-core-mapper`).
- The host program is run once for each call, and the events it writes are played by the emulator, one call after the other. Each run is stopped after 60 seconds.

## 1.3 Several files

When the arrays of the kernel are defined in other files, all the files are given in the same command:

```c
// data.vmeg.cpp
volatile Buffer input[8] = { 1, 2, 3, 4, 5, 6, 7, 8 };
```

```c
// main.vmeg.cpp
extern volatile Buffer input[8];

@emulate "twice"
.kernel twice direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  Transfer in = { memory: input, count: 7 };
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}
```

```
vmee --run twice main.vmeg.cpp data.vmeg.cpp
```

**Explanation of the code above:**

- `input` is declared `extern` in `main.vmeg.cpp` and defined in `data.vmeg.cpp`. The command gives both files, and the result is the one of [1.2](#12-running-a-kernel).

**Rules:**

- The file that has the `@emulate "id"` is found among the files. It is an error if no file has it, or if two files have it.
- A `.scope = global` array that this file declares `extern`, or does not declare, is taken from the file that defines it. It is an error if no file defines it.
- A `.scope = local` array (the default) is taken from the function marked `@kernel name` that calls the kernel, in any of the files.
- The `#define` of the files that supply the arrays are used too. A macro with two different values is an error.
- Only `--run` takes several files.

## 1.4 The window of the buffers

`--buffers-start N` and `--buffers-words N` choose the words shown for each base buffer: `N` words from the word `start`. The defaults are 0 and 32.

```
vmee --run twice main.vmeg.cpp --buffers-start 2 --buffers-words 4
```

shows, for the kernel of [1.2](#12-running-a-kernel):

```
Buffer: BASE 0
0x00000006, 0x00000008, 0x0000000a, 0x0000000c,
```

followed by the same lines for `BASE 1` to `BASE 3`.

**Rules:**

- The window stays inside a buffer of 2048 words: `start + words` is 2048 at most.
- The number of words is 1 or more.
- A number of words that is not a multiple of 4 gives a shorter last line.
- `vmeh` has the same options ([3](vmeh.md)), and the log of the PSP has the same format.

## 1.5 --trace

```
vmee --run twice main.vmeg.cpp --trace trace.txt
```

`--trace` also writes the events of the run to a file, in the format of [Traces](traces.md). It goes with `--run`.

## 1.6 --compat

```
vmee --run twice main.vmeg.cpp --compat fat
```

`--compat fat` generates the code of the kernel with the opcodes that work on the fat PSP, the way `vmegc --compat fat` does ([1.6](../vmeg/running.md#16---compat)): the addition uses `0x030` and not `0x010`, for example. Without it the code is the default one. It goes with `--run`.

## 1.7 --use

```c
volatile Buffer input[8] = { 1, 2, 3, 4, 5, 6, 7, 8 };
volatile Buffer other[8] = { 10, 20, 30, 40, 50, 60, 70, 80 };

@emulate "twice"
.kernel twice direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  Transfer in = { memory: input, count: 7 };
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

@kernel twice config | exec
void run(void) {
}
```

```
vmee --run twice main.vmeg.cpp --use input=other --buffers-words 8
```

shows:

```
Buffer: BASE 0
0x00000014, 0x00000028, 0x0000003c, 0x00000050,
0x00000064, 0x00000078, 0x0000008c, 0x000000a0,
```

followed by the same lines for `BASE 1` to `BASE 3`.

**Explanation of the code above:**

- `--use input=other` plays the emulation with the array `other` in place of the array `input`. The `.load` of `in` reads `other`, so the kernel adds each of its words to itself: 20, 40, 60, … 160.
- Without the option the same command shows 2, 4, 6, … 16.

**Rules:**

- `--use A=B` can be written several times, one for each array to replace. An array is replaced once.
- `A` is an array or a pointer `Buffer*` ([1.7.1](#171-pointers)) that a `.load` or a `.store` of the emulation names. Everywhere the emulation names `A`, in a load or in a store, it reads or writes `B`.
- `B` is an array defined in the files of the command ([1.3](#13-several-files)). It has the same size as `A`.
- The array `A` is not read nor written by the run.
- In an emulation with several calls ([1.2](#12-running-a-kernel)), a store to `A` goes to `B`, and a later load of `A` reads it there.
- `--use` goes with `--run`. It does not change the kernel, the file or the program for the PSP.

### 1.7.1 Pointers

A `Buffer*` pointer ([8.1.2](../vmeg/arrays.md#812-buffer-pointers)) that a `.load` or a `.store` of the emulation names is given an array before the first call.

```c
volatile Buffer one[4] = { 1, 2, 3, 4 };
volatile Buffer two[4] = { 10, 20, 30, 40 };
volatile Buffer* table[2] = { one, two };
volatile Buffer* stage = (volatile u32*)0x40000000;

.kernel doubler direct {
  Agu top = { count: 3 }, write = { count: 3, cyc: auto };
  .pe0 { .top = top; .write = write; .spad = top0 + top0; }
}

void meLibOnProcess(void) {
  @emulate "pick" {
    while (1) {
      volatile Buffer* signal = table[index];
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
}
```

```
vmee --run pick main.vmeg.cpp --use signal=two --buffers-words 4
```

shows:

```
Buffer: BASE 0
0x00000014, 0x00000028, 0x0000003c, 0x00000050,
```

followed by the same lines for `BASE 1` to `BASE 3`.

**Explanation of the code above:**

- `signal` is set from a table with `index`, a value that the emulator does not know. `--use signal=two` gives it the array `two`, so the kernel doubles 10, 20, 30, 40.
- Without `--use` the pointer reads zeros: the command writes `warning: the pointer signal is not bound to an array, it reads zeros: give it one with --use signal=array`, and the buffer shows zeros.
- `stage` is set on a fixed address. The `.store` that names it writes the RAM at that address, with no `--use` and no warning.

**Rules:**

- The pointers that the emulation names are the ones that get an array. A pointer that it does not name is left alone.
- A pointer is looked for in the files ([1.3](#13-several-files)) and in the function that holds the block, in the block or in a block that contains it.
- The array of a pointer is, in this order: the array of `--use`; the array that its initializer names alone, as in `volatile Buffer* p = a;`; otherwise none.
- An initializer that is an address is kept as the address of the pointer: it is made of numbers, the operators `( ) + - * / | & ^ ~ % < >`, the words of types (`u8` to `u64`, `s8` to `s64`, `int`, `unsigned`, `signed`, `long`, `short`, `char`, `void`, `volatile`, `const`), and macros of the files, with at least one number or one macro.
- A pointer with no array and no address reads zeros, and a store to it goes to an internal array of 2048 words, the same for all of these pointers. The warning is written once for each pointer.
- The address is the one of the RAM image of the emulator ([1.2](#12-running-a-kernel)): `0x40000000` is the start of the local eDRAM.

## 1.8 --list

```
vmee --list main.vmeg.cpp
```

`--list` shows the emulations of the file and writes nothing else: no kernel is played. An emulation is an `@emulate`, in either form: the mark above a `.kernel`, or the block `@emulate "id" { … }` ([1.1](#11-marking-a-kernel)). For this file:

```c
volatile Buffer input[16];

@emulate "add-test"
.kernel add direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  Transfer in = { memory: input, count: 15 };
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

.kernel twice direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 * top0; }
}

void meLibOnProcess(void) {
  @emulate "both" {
    @kernel add config | exec {
    }
    @kernel twice config | exec {
    }
  }
}
```

the listing is:

```
emulate "add-test": kernel add (direct, lines 4-9)
  global loads:
    TOP_0   16 words  from input
  local loads: none
emulate "both": kernels add, twice (lines 17-22)
  calls:
    add  config | exec
    twice  config | exec
  global loads:
    TOP_0   16 words  from input
  local loads: none

defines of the file:
```

**Explanation of the code above:**

- `add-test` is the mark on `add`: its line gives the kernel, its mode and the lines of the kernel.
- `both` is the block: its line gives the kernels it calls and the lines of the block, and `calls:` gives the calls in their order, with their actions.
- `TOP_0   16 words  from input` says that the buffer `TOP_0` receives 16 words of `input`, by a `.load`. The `.store` of the kernels are listed the same way, under `global stores` and `local stores`.
- The last line, `defines of the file:`, is followed by the `#define` of the file.

**Rules:**

- `--kernel NAME` keeps the emulations that use the kernel `NAME`: `--kernel twice` keeps `both`.
- `--full` lists the eight buffers, `TOP_0` to `TOP_3` and `BASE_0` to `BASE_3`, of each emulation, and shows `not linked` for those that no `.load` fills.
- `--kernel` and `--full` go with `--list`. `--run` does not.
- A line is marked with `<--` when something is likely wrong, as in this listing of two `.load` that overlap, that go past the end of a buffer and that use a name with no `#define`:

```
    TOP_1   16 words  at 0x7f8  from a  <-- goes past the end of the buffer (0x800 words)
    TOP_0   16 words  at 8  from b  <-- overlaps TOP_0 at 0 (words 8-15)
    TOP_2   16 words  at RIGHT  from b  <-- 'RIGHT' has no #define in this file
```

- The fourth mark is `'name' is not declared with Buffer`, for a source array that is not a `Buffer`.
- Only one file is given to `--list`.
- Currently not supported: a block that calls a kernel defined in another file than the block.

## 1.9 Errors

The errors of the command line are printed as `vmeemu: error: message`, with the exit code 2. The other errors are printed as `file: message`, with the exit code 1. The errors of a kernel or of an array come from `vmegc` and are described with the part of the language they come from ([14](../VMEG.md#14-errors)).

| Section | Message | Cause |
|---|---|---|
| [1.2](#12-running-a-kernel) | `no @emulate with the id 'x' (a, b)` | an id that no mark has; the message lists the ids of the file, or says that there is no `@emulate` |
| [1.2](#12-running-a-kernel) | `[Errno 2] No such file or directory: 'file'` | an input file that cannot be read |
| [1.2](#12-running-a-kernel) | `the library folder … lacks …, the submodule is probably empty (git submodule update --init me-core-mapper)` | the submodule `me-core-mapper` is empty |
| [1.2](#12-running-a-kernel) | `g++ is needed to build the host program and was not found` | no `g++` |
| [1.2](#12-running-a-kernel) | `the host program does not build:` | the host program written for the kernel does not compile; the output of `g++` follows |
| [1.2](#12-running-a-kernel) | `the host program did not finish in 60 seconds` | the host program runs for more than 60 seconds |
| [1.2](#12-running-a-kernel) | `the host program failed with the exit code N:` | the host program ends with an error; its error output follows |
| [1.3](#13-several-files) | `several files go only with --run` | several files without `--run` |
| [1.3](#13-several-files) | `the @emulate "id" is in a and b` | the mark is in two of the files |
| [1.3](#13-several-files) | `the array x of the @emulate "id" is declared extern and no file defines it` | a global array declared `extern` that no file defines |
| [1.3](#13-several-files) | `the array x of the @emulate "id" is defined in no file` | an array of a `.load` or of a `.store` that no file declares |
| [1.3](#13-several-files) | `the Memory x of the @emulate "id" is defined in no file` | a `Memory` named by `.memory` that no file declares |
| [1.3](#13-several-files) | `the macro N has two different values in the files of the @emulate "id"` | a `#define` with two values in the files that supply the arrays |
| [1.4](#14-the-window-of-the-buffers) | `the first word of the buffers cannot be negative` | `--buffers-start` below 0 |
| [1.4](#14-the-window-of-the-buffers) | `the number of words of the buffers must be 1 or more` | `--buffers-words` below 1 |
| [1.4](#14-the-window-of-the-buffers) | `the window of the buffers goes past the end of a buffer (2048 words)` | `start + words` above 2048 |
| [1.5](#15---trace) | `--trace goes with --run` | `--trace` without `--run` |
| [1.6](#16---compat) | `--compat goes with --run` | `--compat` without `--run` |
| [1.7](#17---use) | `--use goes with --run` | `--use` without `--run` |
| [1.7](#17---use) | `--use takes NAME=NAME, for example --use input=other (got 'x')` | a `--use` that is not two names with `=` between them |
| [1.7](#17---use) | `--use: the array a is replaced twice` | two `--use` with the same array before the `=` |
| [1.7](#17---use) | `--use a=b: the array a is not read or written by the @emulate "id"` | `a` is not named by a `.load` or a `.store` of the emulation |
| [1.7](#17---use) | `--use a=b: the array b is defined in no file` | `b` is declared in no file of the command |
| [1.7](#17---use) | `--use a=b: the two arrays must have the same size` | the sizes differ; the message is in the output of `g++` that follows `the host program does not build:` |
| [1.8](#18---list) | `--kernel and --full go with --list` | `--kernel` or `--full` without `--list` |
| [1.8](#18---list) | `--run does not go with --list` | the two options together |
| [1.8](#18---list) | `no @emulate on the kernel 'k' (a, b)` | `--kernel` with a kernel that no emulation uses; the message lists the kernels that are used |
| [1.8](#18---list) | `the kernel q of the @emulate "far" is not defined in this file` | a block that calls a kernel defined in another file |
| [1.2](#12-running-a-kernel) | `warning: N words never written are read as 0 outside the eDRAM, the first at 0xA` | a transfer reads words that nothing wrote, from the address `0x400000` up |
| [1.7.1](#171-pointers) | `warning: the pointer p is not bound to an array, it reads zeros: give it one with --use p=array` | a pointer that the emulation names, with no `--use`, no array in its initializer and no address |
| [1.8](#18---list) | `warning: there is no @emulate in this file` | the file has no `@emulate`; the listing is still written |
| [1.8](#18---list) | `warning: emulate "x": the kernel k has no buffer` | the kernel has no `.load` and no `.store`; the message names all the kernels of a block |
