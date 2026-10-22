[Index](../VMEG.md) · [The language](language.md)

# Running vmegc

## Contents

- [1.1 Command line](#11-command-line)
- [1.2 Several files](#12-several-files)
- [1.3 Messages](#13-messages)
- [1.4 --list](#14---list)
- [1.5 --ops](#15---ops)
- [1.6 CMake](#16-cmake)
- [1.7 Errors](#17-errors)

## 1.1 Command line

```
python3 vmegc.py main.vmeg.cpp
```

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

- The files given in the same command are one project. A kernel defined in one file can be called from another one.
- Each file has its own output, named after it ([1.1](#11-command-line)).
- `-o` goes with a single input file.
- Two inputs cannot give the same output, for example `a/x.vmeg.c` and `b/x.vmeg.c`.
- A `.vmeg.h` is not a source: the buffers are declared in the `.vmeg.c` or `.vmeg.cpp` files.

## 1.3 Messages

```
main.vmeg.cpp: line 12: unknown Agu variable 'u'
main.vmeg.cpp: line 7: warning: pe0 has an operation but no .write is bound, its result stays in the staging
```

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

- A line is the file, the first and the last line of the block, and its header.
- The kernels and their calls are checked before the list: an error of these is shown instead of it.

## 1.5 --ops

```
python3 vmegc.py --ops
```

`--ops` shows the table of the operations that a pe can run, and writes nothing. For each operation: how it is written, its opcode, the buffers or Staging variables it reads (`front`, `back`, or only `back`), and the FUs that can run it (any FU, or the primary one only). Under the table, the fields that `sat`, `>>` and `<<` set on the operation they wrap. The operations are described in [Operations](../VMEG.md#6-operations).

`--ops` goes alone, without a file or another option.
