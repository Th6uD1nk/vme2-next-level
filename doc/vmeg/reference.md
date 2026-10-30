[Index](../VMEG.md) · [Errors](errors.md)

# Reference

The syntax and the technical elements of vmeg, with the section that describes each one.

## Contents

- [15.1 Command line](#151-command-line)
- [15.2 Language](#152-language)
- [15.3 Kernel](#153-kernel)
- [15.4 Agu](#154-agu)
- [15.5 Processing element](#155-processing-element)
- [15.6 Operations](#156-operations)
- [15.7 Staging](#157-staging)
- [15.8 Arrays](#158-arrays)
- [15.9 Transfers](#159-transfers)
- [15.10 Call of a kernel](#1510-call-of-a-kernel)
- [15.11 Blocks](#1511-blocks)
- [15.12 Other](#1512-other)

## 15.1 Command line

| Element | Section |
|---|---|
| `python3 vmegc.py file.vmeg.cpp` | [1.1](running.md#11-command-line) |
| `-o` | [1.1](running.md#11-command-line) |
| several files | [1.2](running.md#12-several-files) |
| `--list`, `--kernel` | [1.4](running.md#14---list) |
| `--ops` | [1.5](running.md#15---ops) |
| `--compat fat` | [1.6](running.md#16---compat) |
| `vmegc_sources`, `vmegc_translate` | [1.7](running.md#17-cmake) |

## 15.2 Language

| Element | Section |
|---|---|
| `.name { }`, `.name = value;`, `.pe0.top = t;` | [2.1](language.md#21-attributes) |
| `Agu`, `Staging`, `Transfer`, `Int` | [2.2](language.md#22-variables) |
| `Agu(2)`, `Transfer(Words)`, `Buffer(Q8.8)` | [2.2](language.md#22-variables) |
| `a, b` (several declarations at once) | [2.2.1](language.md#221-declaring-several-at-once) |
| `pe[i]`, `top[i]`, `base[i]` | [2.3](language.md#23-accesses-by-index) |
| `Int name = expression;` | [2.4](language.md#24-int) |
| expressions | [2.5](language.md#25-expressions) |
| macros, unknown names | [2.6](language.md#26-numbers-macros-and-unknown-names) |
| `for p in a..b { }` | [2.7](language.md#27-loops) |
| `.context`, `@context` | [2.8](language.md#28-synonyms) |

## 15.3 Kernel

| Element | Section |
|---|---|
| `.kernel name mode { }` | [3.1](kernel.md#31-header) |
| `direct`, `memory` | [3.2](kernel.md#32-modes) |
| statements of the body | [3.3.1](kernel.md#331-statements) |
| `.params { }` | [3.3.4](kernel.md#334-parameters) |
| `icn xpcr = …, skew = …;` | [3.4](kernel.md#34-interconnect-registers) |

## 15.4 Agu

| Element | Section |
|---|---|
| `Agu name = { };`, `Agu(4)` | [4.1](agu.md#41-declaring-an-agu) |
| `count`, `offset`, `step`, `reverse` | [4.2.1](agu.md#421-common-parameters) |
| `inner0` | [4.2.2](agu.md#422-inner0) |
| `repeat` | [4.2.3](agu.md#423-read-agus) |
| `cyc`, `auto`, `bubbles`, `sync` | [4.2.4](agu.md#424-write-agus) |
| `Agu(2)` | [4.2.5](agu.md#425-the-mode-2) |
| `.top`, `.base`, `.write` | [4.3](agu.md#43-binding-an-agu-to-a-pe) |
| an `Agu` shared by several pes | [4.3.1](agu.md#431-sharing-an-agu) |

## 15.5 Processing element

| Element | Section |
|---|---|
| `.pe0` to `.pe3`, `pe[p]` | [5.1](pe.md#51-the-pe-block) |
| `.spad = …;`, `s = …;` | [5.2](pe.md#52-what-a-block-holds) |
| two operations in a pe | [5.3](pe.md#53-operations-in-a-pe) |
| `.remap` | [5.4](pe.md#54-remapping-an-opcode) |

## 15.6 Operations

| Element | Section |
|---|---|
| `top0` to `top3`, `base0` to `base3` | [6.1](operations.md#61-operands-and-results) |
| `+`, `-`, `*`, `&`, `\|`, `^` | [6.2](operations.md#62-operators) |
| `~` | [6.2.1](operations.md#621-the-complement) |
| an operator with a number | [6.2.2](operations.md#622-operators-with-a-number) |
| the choice of the opcode | [6.2.3](operations.md#623-how-the-opcode-is-chosen) |
| `clamp` | [6.3.1](operations.md#631-clamp) |
| `subacst` | [6.3.2](operations.md#632-subacst) |
| `subshr` | [6.3.3](operations.md#633-subshr) |
| `mac` | [6.3.4](operations.md#634-mac) |
| `acc` | [6.3.5](operations.md#635-acc) |
| `and`, `or`, `xor` | [6.3.6](operations.md#636-and-or-and-xor) |
| `sat`, `>>`, `<<` | [6.4](operations.md#64-sat-and-the-shifts) |

## 15.7 Staging

| Element | Section |
|---|---|
| `Staging name;` | [7.1](staging-routing.md#71-staging-variables) |
| the routing | [7.2](staging-routing.md#72-the-routing) |
| the warnings | [7.3](staging-routing.md#73-warnings) |

## 15.8 Arrays

| Element | Section |
|---|---|
| `volatile Buffer name[n];` | [8.1](arrays.md#81-the-buffer-keyword) |
| `Buffer(Qm.n)` | [8.1.1](arrays.md#811-the-q-format) |
| global arrays | [8.2](arrays.md#82-global-arrays) |
| local arrays | [8.3](arrays.md#83-local-arrays) |
| `static`, `extern` | [8.4](arrays.md#84-arrays-in-several-files) |
| `volatile Memory name[n];` | [8.5](arrays.md#85-memory-configs) |

## 15.9 Transfers

| Element | Section |
|---|---|
| `Transfer name = { };` | [9.1](transfers.md#91-the-transfer-variable) |
| `Transfer(Words)`, `Transfer(Halves)`, `Transfer(Bytes)` | [9.2](transfers.md#92-the-extended-mode) |
| `memory`, `count`, `gap`, `step`, `group` | [9.2.1](transfers.md#921-the-fields) |
| `group.size`, `group.outer`, `group.inner` | [9.2.3](transfers.md#923-the-group) |
| `step: 0` | [9.2.4](transfers.md#924-step-0) |
| `.load { }`, `.store { }`, `.transfer`, `.scope` | [9.3](transfers.md#93-load-and-store) |
| `.offsets { }`, `.top0` to `.base3` | [9.4](transfers.md#94-the-offsets) |
| unknown names | [9.5](transfers.md#95-unknown-names-in-a-transfer) |

## 15.10 Call of a kernel

| Element | Section |
|---|---|
| `@kernel name actions` above a function | [10.1](calling.md#101-the-call-of-a-kernel) |
| `build`, `config`, `exec`, `async` | [10.2](calling.md#102-the-actions) |
| `config \| exec` | [10.3](calling.md#103-several-actions-in-one-call) |
| `@kernel a …, b …` | [10.4](calling.md#104-several-kernels-in-one-call) |
| uploads and downloads | [10.5](calling.md#105-uploads-and-downloads-around-the-run) |

## 15.11 Blocks

| Element | Section |
|---|---|
| `@kernel name actions { }` | [11.1](blocks.md#111-the-block-form) |
| the C code of a block | [11.2](blocks.md#112-the-c-code-of-a-block) |
| the vmeg statements of a block | [11.3](blocks.md#113-the-vmeg-statements-of-a-block) |
| `.params = { }`, `.params { }` | [11.3.1](blocks.md#1131-the-params-of-a-call) |
| `.memory` | [11.3.2](blocks.md#1132-the-memory-config-of-a-call) |
| blocks in a row | [11.4](blocks.md#114-blocks-in-a-row) |

## 15.12 Other

| Element | Section |
|---|---|
| `meLibOnProcess` | [12.1](on-process.md#121-the-function-of-the-media-engine) |
| what `vmegc` writes at its start | [12.2](on-process.md#122-what-vmegc-writes-at-its-start) |
| a call on `meLibOnProcess` | [12.3](on-process.md#123-a-call-on-melibonprocess) |
| `@emulate "id"` | [13.1](emulation.md#131-the-emulate-mark) |
| the rules of the mark | [13.2](emulation.md#132-the-rules-of-the-mark) |
| `@emulate` on a block | [13.3](emulation.md#133-the-block-form) |
