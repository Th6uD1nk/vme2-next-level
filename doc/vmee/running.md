[Index](../VMEE.md) · [Traces](traces.md)

# Running vmee

## Contents

- [1.1 Marking a kernel](#11-marking-a-kernel)
- [1.2 Running a kernel](#12-running-a-kernel)
- [1.3 Several files](#13-several-files)
- [1.4 The window of the buffers](#14-the-window-of-the-buffers)
- [1.5 --trace](#15---trace)
- [1.6 --compat](#16---compat)
- [1.7 --list](#17---list)
- [1.8 Errors](#18-errors)

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

- The kernel is `direct` or `memory`. A memory kernel gives the same result as a direct one. The emulator plays the definition of the kernel as `config | exec`: the actions of a `@kernel` call, `build` and `async` among them, are not played.
- The `.load` of the kernel are played before the run, the `.store` after it, the way `vmegc` generates them for a call. The arrays they use must be declared in the files ([1.3](#13-several-files)).
- Only the `.load` and the `.store` written in the `.kernel` are played. Currently not supported: the ones written in the block of a `@kernel` call.
- Only the four base buffers are shown. A `.store` does not show its array: read the result in the buffer it comes from.
- The kernel is built into a small host program with `g++ -m32` and the library of the submodule `me-core-mapper`. `--run` needs `g++` with 32 bit support, and the submodule must not be empty (`git submodule update --init me-core-mapper`).
- The host program is run, and the events it writes are played by the emulator. The run is stopped after 60 seconds.

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

## 1.7 --list

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
