# vmeg

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
| 8 | [Arrays](#8-arrays) | the `Buffer` keyword, global and local arrays |
| 9 | [Transfers](#9-transfers) | `Transfer`, `.load`, `.store`, the generated functions |
| 10 | [Calling a kernel](#10-calling-a-kernel) | `@kernel` and the actions `build`, `config`, `exec`, `async` |
| 11 | [Blocks](#11-blocks) | the vmeg statements inside a `@kernel` block |
| 12 | [meLibOnProcess](#12-melibonprocess) | the start of the function of the Media Engine |
| 13 | [Emulation](#13-emulation) | `@emulate`, how a kernel is played (see also [VMEE](VMEE.md)) |
| 14 | [Errors](#14-errors) | every message of `vmegc`, by cause |
| 15 | [Limits](#15-limits) | what is not available yet |
| 16 | [Reference](#16-reference) | the whole syntax on one page |

## 1. Running vmegc

Details: [Running vmegc](vmeg/running.md)

## 2. The language

Details: [The language](vmeg/language.md)

## 3. The kernel

Details: [The kernel](vmeg/kernel.md)

## 4. AGU variables

Details: [AGU variables](vmeg/agu.md)

## 5. Processing elements

Details: [Processing elements](vmeg/pe.md)

## 6. Operations

Details: [Operations](vmeg/operations.md)

## 7. Staging, routing and warnings

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

## 15. Limits

Details: [Limits](vmeg/limits.md)

## 16. Reference

Details: [Reference](vmeg/reference.md)
