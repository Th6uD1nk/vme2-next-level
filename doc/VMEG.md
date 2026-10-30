# vmeg

**vmeg** is a language for the PSP Virtual Mobile Engine (VME), the small reconfigurable chip of the Media Engine. You write a kernel as a graph of buffers, address generators and processing elements, **inside your own C or C++ file**, next to the rest of your code. The **g** stands for *graph* and for *generator*.

**vmegc** is the compiler. It runs as a step of your **CMake build**, or from the command line: it replaces the vmeg blocks with plain C or C++ that drives the VME, leaves the rest of the file as it is, and your toolchain builds the result as usual.

A quick example, a kernel that adds two buffers and the function that runs it:

```c
// main.vmeg.cpp
.kernel add direct {
  Agu t = { count: 15 }, b = { count: 15 }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .base = b; .write = w; .spad = top0 + base0; }
}

@kernel add config | exec
void run(void) {
}
```

And the CMake lines that build it:

```cmake
include(cmake/vmegc.cmake)
add_executable(app)
vmegc_sources(app SOURCES main.vmeg.cpp)
```

## Contents

| | Page | What it covers |
|---|---|---|
| 1 | [Running vmegc](#1-running-vmegc) | the command line, several files, CMake, `--list`, `--ops` |
| 2 | [The language](#2-the-language) | the dot, the variables, the accesses by index, `Int`, numbers and macros |
| 3 | [The kernel](#3-the-kernel) | `.kernel`, the modes `direct` and `memory` |
| 4 | [AGU variables](#4-agu-variables) | `Agu`, its parameters, the bindings |
| 5 | [Processing elements](#5-processing-elements) | `.pe0` to `.pe3`, `pe[i]` |
| 6 | [Operations](#6-operations) | the operators and the functions of a pe, `sat`, the shifts |
| 7 | [Staging, routing and warnings](#7-staging-routing-and-warnings) | `Staging`, the derived routing, the warnings |
| 8 | [Arrays](#8-arrays) | the `Buffer` keyword, global and local arrays, the `Memory` keyword |
| 9 | [Transfers](#9-transfers) | `Transfer`, `.load`, `.store`, the generated functions |
| 10 | [Calling a kernel](#10-calling-a-kernel) | `@kernel` and the actions `build`, `config`, `exec`, `async` |
| 11 | [Blocks](#11-blocks) | the vmeg statements inside a `@kernel` block |
| 12 | [meLibOnProcess](#12-melibonprocess) | the start of the function of the Media Engine |
| 13 | [Emulation](#13-emulation) | `@emulate`, how a kernel is played (see also [VMEE](VMEE.md)) |
| 14 | [Errors](#14-errors) | every message of `vmegc`, by cause |
| 15 | [Reference](#15-reference) | the whole syntax on one page |

## 1. Running vmegc

`vmegc` reads one or several `.vmeg.c` or `.vmeg.cpp` files and writes, for each one, a plain C or C++ file. It runs from the command line, or as a step of a CMake build.

Details: [Running vmegc](vmeg/running.md)

## 2. The language

A vmeg file is C or C++ with a few extra constructs, written in three forms: attributes with a leading dot (`.kernel`, `.pe0`, `.load`), typed variables without a dot (`Agu`, `Staging`, `Transfer`, `Int`), and accesses by index (`pe[1]`, `top[2]`). A number comes from a literal, from an `Int` or from a macro of the file.

Details: [The language](vmeg/language.md)

## 3. The kernel

A kernel is the description of what the VME computes: `.kernel name mode { … }`. Its body holds the address generators, the processing elements and the transfers. The mode says where its registers are written: `direct` writes them in the VME, `memory` writes them in a context in RAM that is sent to the VME.

Details: [The kernel](vmeg/kernel.md)

## 4. AGU variables

An AGU (address generator) says which words of a buffer a processing element reads or writes, and in which order. `Agu name = { count: 15 };` declares one, and a pe uses it once it is bound with `.top`, `.base` or `.write`.

A write AGU also takes `cyc`, the delay of the write: a number, or `auto` to let vmeg work it out, with an optional shift (`cyc: auto - 1`).

Details: [AGU variables](vmeg/agu.md)

## 5. Processing elements

The VME has four processing elements, `pe0` to `pe3`. A pe reads its data through its read AGUs, runs its operations and writes the result through its write AGU. A kernel describes each pe in a block: `.pe0 { … }`.

Details: [Processing elements](vmeg/pe.md)

## 6. Operations

A pe computes with operators (`+`, `-`, `*`, `&`, `|`, `^`, `~`) and with functions (`clamp`, `mac`, `acc`, `subacst`, `subshr`, `and`, `or`, `xor`). `sat` and the shifts `>>` and `<<` adjust the operation they wrap. These are the operations currently supported, the list is not complete. `vmegc --ops` shows the table of all of them.

Details: [Operations](vmeg/operations.md)

## 7. Staging, routing and warnings

A `Staging` variable keeps the result of an operation in a pe, so that another operation can read it. `vmegc` works out by itself how the AGUs and the results are connected, from the bindings and the operations, and it warns when something is likely wrong, such as a buffer that is read without an AGU.

Details: [Staging, routing and warnings](vmeg/staging-routing.md)

## 8. Arrays

Details: [Arrays](vmeg/arrays.md)

## 9. Transfers

Details: [Transfers](vmeg/transfers.md)

## 10. Calling a kernel

Details: [Calling a kernel](vmeg/calling.md)

## 11. Blocks

Details: [Blocks](vmeg/blocks.md)

## 12. meLibOnProcess

Details: [meLibOnProcess](vmeg/on-process.md)

## 13. Emulation

Details: [Emulation](vmeg/emulation.md)

## 14. Errors

Details: [Errors](vmeg/errors.md)

## 15. Reference

Details: [Reference](vmeg/reference.md)
