[Index](../VMEG.md) · [The language](language.md)

# Running vmegc

## Contents

- [1.1 Command line](#11-command-line)
- [1.2 Several files](#12-several-files)
- [1.3 Messages](#13-messages)
- [1.4 --list](#14---list)
- [1.5 --ops](#15---ops)
- [1.6 --compat](#16---compat)
- [1.7 CMake](#17-cmake)
- [1.8 Errors](#18-errors)

## 1.1 Command line

```
python3 vmegc.py main.vmeg.cpp
```

**Explanation of the code above:**

- The input ends with `.vmeg.c` or `.vmeg.cpp`. The output has the same name without `.vmeg`: `main.cpp`, or `main.c` for a `.vmeg.c`.
- The output is written in the current directory, not next to the input.
- `-o` gives the name of the output, and the folders of its path are created if they do not exist. With `-o`, the input can have any name.

```
python3 vmegc.py main.vmeg.cpp -o build/main.cpp
```

## 1.2 Several files

```
python3 vmegc.py kernels.vmeg.cpp main.vmeg.cpp
```

**Rules:**

- The files given in the same command are one project. A kernel defined in one file can be called from another one.
- Each file has its own output, named after it ([1.1](#11-command-line)).
- `-o` goes with a single input file.
- Two inputs cannot give the same output, for example `a/x.vmeg.c` and `b/x.vmeg.c`.
- A `.vmeg.h` is not a source: the buffers are declared in the `.vmeg.c` or `.vmeg.cpp` files.

## 1.3 Messages

```
main.vmeg.cpp: line 12: unknown Agu variable 'u'
main.vmeg.cpp: line 7: warning: pe0 has an operation but no .write is bound in this kernel
```

**Rules:**

- An error stops `vmegc` with the exit code 1. Nothing is written, even for the files that have no error.
- A warning does not stop `vmegc`: the files are written and the exit code is 0. The warnings are printed once all the files are translated.
- The generated code keeps the lines of the `.vmeg` file, so the errors of the C or C++ compiler name the line of the file you wrote.

## 1.4 --list

```
python3 vmegc.py --list main.vmeg.cpp
```

`--list` shows the kernels and the `@kernel` of the files, one line each, and writes nothing:

```
main.vmeg.cpp:34-37: .kernel add memory
main.vmeg.cpp:88-88: @kernel add build, sub build, mul build
main.vmeg.cpp:95-95: @kernel add config | async, sub config | async, mul config | async
```

**Explanation of the code above:**

- A line is the file, the first and the last line of the block, and its header.
- The kernels and their calls are checked before the list: an error of these is shown instead of it.

To see the operations of a kernel, give its name:

```
python3 vmegc.py --list --kernel run main.vmeg.cpp
```

**Explanation of the code above:**

- `--kernel run` keeps the line of the kernel `run` and shows, under it, one line for each operation that the kernel runs.
- The operations are the ones `vmegc` chooses for the kernel, as the option `--compat` ([1.6](#16---compat)) leaves them.

For this kernel, written in `main.vmeg.cpp`:

```c
.kernel run direct {
  Agu t = { count: 15 };
  .pe0 { .top = t; .write = { count: 15 }; .spad = top0 + base0 + 5; }
  .pe1 { .top = t; .write = { count: 15 }; .spad = clamp(top1 & 255, 0, 9); }
}
```

the command prints:

```
main.vmeg.cpp:1-5: .kernel run direct
  pe0  line 3  0x030  a + b + c            a = top0, b = base0, c = 5
  pe1  line 4  0x0c4  x & c                x = top1, c = 255
  pe1  line 4  0x07c  clamp(x, low, high)  x = staging1, low = 0, high = 9
```

**Explanation of the code above:**

- The first line is the line of the kernel, as in the list of the kernels.
- A line under it is one operation: the pe, the line of the file, the opcode, how the opcode is written, then the value given to each of its names.
- `pe1` runs two operations: `x & c`, then `clamp`, which reads the result of the first one (`staging1`).
- A number that is written is shown as it is (`c = 5`). A number that is not written is shown at 0 ([6.2.3](operations.md#623-how-the-opcode-is-chosen)).

**Rules:**

- `--kernel` goes with `--list`.
- The name is the one of a kernel of the files given, which are one project ([1.2](#12-several-files)).
- The `sat` and the shifts written on an operation ([6.4](operations.md#64-sat-and-the-shifts)) are not shown.

## 1.5 --ops

```
python3 vmegc.py --ops
```

`--ops` shows the operations that a pe can run, sorted by opcode, and writes nothing. Each operation is a block: its opcode and how it is written (as an expression, or as a function for the operations that have no other writing), what it does, its other writings (`also written …`), the registers that receive its numbers, and where it can stand in a pe (any position, or the first operation of the pe only). A block ends with `not portable` when the opcode is not usable on every model of the PSP. Under the blocks, the options that `sat`, `>>` and `<<` set on the operation they wrap. The operations are described in [Operations](../VMEG.md#6-operations).

Four of its blocks:

```
0x010: a + b
       the sum of a and b
       position any
       not portable

0x048: a - b + c
       a minus b, plus c
       also written subacst(a, b, c)
       registers c = B
       position any

0x07c: clamp(x, low, high)
       x limited between low and high, x is a buffer, a Staging
       variable or an operation
       registers high = A, low = B
       position any

0x200: a * b
       the product of a and b, shifted by the `>> n` after it
       position first operation of the pe only
```

**Explanation of the code above:**

- The first line of a block is the opcode and how the operation is written. The lines under it say what it does.
- `also written` gives another writing of the same opcode ([6.2.2](operations.md#622-operators-with-a-number)).
- `registers c = B` says that the number `c` is written in the register B. `clamp` writes two numbers, in A and in B.
- `position first operation of the pe only` is for the operations that must be the first one of their pe ([5.3](pe.md#53-operations-in-a-pe)). The other operations can stand anywhere: `position any`.
- `not portable` marks an opcode that does not work on every model of the PSP. `--compat fat` leaves it out ([1.6](#16---compat)).

`--ops` goes alone, without a file or another option.

## 1.6 --compat

```
python3 vmegc.py --compat fat main.vmeg.cpp
```

**Explanation of the code above:**

- `--compat fat` makes `vmegc` leave out the opcodes that do not work on the fat model of the PSP. `--ops` marks them `not portable` ([1.5](#15---ops)).
- An expression that such an opcode covered is done by another opcode, as `a + b` is ([6.2.3](operations.md#623-how-the-opcode-is-chosen)).
- Without `--compat`, every opcode can be chosen.

**Rules:**

- `fat` is the only model accepted. Currently not supported: another model.
- `--compat` goes with the files to translate. `--ops` goes alone ([1.5](#15---ops)).

## 1.7 CMake

`cmake/vmegc.cmake` runs `vmegc` as a step of the build.

```cmake
include(cmake/vmegc.cmake)

add_executable(app)
vmegc_sources(app SOURCES kernels.vmeg.cpp main.vmeg.cpp)
```

**Explanation of the code above:**

- `vmegc_sources(target SOURCES …)` runs `vmegc` on all the files as one project ([1.2](#12-several-files)) and adds the generated files to the target. It needs CMake 3.11.
- The generated files are written in the build directory, named after the sources ([1.1](#11-command-line)). They are generated again when a source changes.
- For a single file that holds a kernel and the call of this kernel, `vmegc_translate` gives the path of the generated file, to use as any source:

```cmake
vmegc_translate(GENERATED_C saturate-clamp.vmeg.c)
add_library(saturate-clamp OBJECT ${GENERATED_C})
```

**Rules:**

- `vmegc` needs `python3`: CMake stops if it does not find it.

To translate with `--compat` ([1.6](#16---compat)), give the model to CMake:

```
cmake -DVMEGC_COMPAT=fat ..
```

**Explanation of the code above:**

- `VMEGC_COMPAT=fat` runs `vmegc` with `--compat fat` on all the files of the build. Empty by default: every opcode can be chosen.
- The files are generated again when `VMEGC_COMPAT` changes.
- `VMEGC_COMPAT` is `fat` or empty: CMake stops with another value.

The `samples` folder has a `CMakeLists.txt` for each sample.

## 1.8 Errors

The errors of the command line start with `vmegc: error:`, left out here. The errors inside a file are described with the part of the language they come from.

| Section | Message | Cause |
|---|---|---|
| [1.1](#11-command-line) | `the input files are required` | no input file |
| [1.1](#11-command-line) | `input must end with .vmeg.c or .vmeg.cpp (or pass -o)` | an input with another name, without `-o` |
| [1.1](#11-command-line) | `file.vmeg.c: no such file or directory` | an input that does not exist (or `is a directory`, or another reason the file cannot be read) |
| [1.2](#12-several-files) | `-o goes with a single input file, every output is written in the current directory` | `-o` with several inputs |
| [1.2](#12-several-files) | `b/x.vmeg.c: the output 'x.c' is already the output of a/x.vmeg.c` | two inputs that give the same output |
| [1.2](#12-several-files) | `a.vmeg.h: a .vmeg.h is not a source, the buffers are declared in .vmeg.c or .vmeg.cpp files` | a `.vmeg.h` given as an input |
| [1.4](#14---list) | `--kernel goes with --list` | `--kernel` without `--list` |
| [1.4](#14---list) | `no kernel 'nope' (run, other)` | a name that is not a kernel of the files. The message names the kernels that exist, or says that there is none |
| [1.5](#15---ops) | `--ops goes alone` | `--ops` with a file or another option |
| [1.6](#16---compat) | `argument --compat: invalid choice: 'slim' (choose from 'fat')` | `--compat` with a model other than `fat` |
| [1.7](#17-cmake) | `vmegc needs python3` | CMake does not find `python3` |
| [1.7](#17-cmake) | `vmegc_sources needs cmake 3.11 or newer` | `vmegc_sources` with an older CMake |
| [1.7](#17-cmake) | `VMEGC_COMPAT must be fat or empty, not 'slim'` | `VMEGC_COMPAT` set to a model other than `fat` |
