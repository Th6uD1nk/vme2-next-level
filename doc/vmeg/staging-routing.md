[Index](../VMEG.md) · [Operations](operations.md) · [Arrays](arrays.md)

# Staging, routing and warnings

This page explains how a result is kept in a pe, what `vmegc` connects by itself, and what it warns about.

## Contents

- [7.1 Staging variables](#71-staging-variables)
- [7.2 The routing](#72-the-routing)
- [7.3 Warnings](#73-warnings)
- [7.4 Errors](#74-errors)

## 7.1 Staging variables

A `Staging` variable keeps the result of an operation in a pe. Another operation reads it by its name, in the same pe or in another one.

```c
Staging s;

.pe0 { s = top0 + top1; }
.pe1 { .top2 - s; }
.pe2 { .s + top3; }
```

**Explanation of the code above:**

- `Staging s;` declares the variable, in the kernel or in the block of a pe. Several can be declared at once: `Staging a, b;` ([2.2](language.md#22-variables)).
- `s = top0 + top1;` sets it: the operation runs in `pe0` and its result stays there. An operation kept in a `Staging` variable is written without a dot.
- `.top2 - s;` and `.s + top3;` read it: the result of `pe0` is an operand of the operations of `pe1` and `pe2`.

**Rules:**

- A `Staging` variable is set once, and set before it is read: the statements are read in order.
- It is read like a buffer, as an operand of an operator or of a function ([6.1](operations.md#61-operands-and-results)).
- The operation that sets it counts in the pe ([5.3](pe.md#53-operations-in-a-pe)).

## 7.2 The routing

Each pe has its own buffers, `topN` and `baseN`, and a result that leaves on its own write. The buffers are filled by the read AGUs bound in the pe (`.top` and `.base`), and the result is written by the write AGU of the pe (`.write`). An operation can read the buffers of any pe.

```c
Agu t = { count: 15 };

.pe0 { .top = t; .write = { count: 15 }; .top0 + top1; }
.pe1 { .top = t; }
```

**Explanation of the code above:**

- `pe0` reads `top0`, which its own `.top` fills, and `top1`, which is filled by the `.top` of `pe1`.
- The two pes share the `Agu` variable `t` ([4.3.1](agu.md#431-sharing-an-agu)): they read the same words.
- Without `.top = t;` in `pe1`, `top1` would not be filled and it would read zero ([7.3](#73-warnings)).

**Rules:**

- `vmegc` connects the AGUs, the buffers and the results from the bindings and the operations. Nothing is written for it.
- A buffer `topN` or `baseN` needs the AGU `.top` or `.base` bound in `peN`.
- The result of a pe leaves on its write AGU. A result kept in a `Staging` variable stays in the pe.
- The registers of the interconnect that are written by hand are `xpcr` and `skew` ([3.4](kernel.md#34-interconnect-registers)).

## 7.3 Warnings

`vmegc` warns when something is likely wrong in a kernel. A warning does not stop it: the files are written ([1.3](running.md#13-messages)).

```c
.kernel k direct {
  Agu t = { count: 15 };
  .pe0 { .top = t; .top0 + top1; }
}
```

```
main.vmeg.c: line 3: warning: top1 is read but no .top is bound in pe1 of this kernel
main.vmeg.c: line 3: warning: pe0 has an operation but no .write is bound in this kernel
```

**Explanation of the code above:**

- `pe0` reads `top1`, but this kernel binds no `.top` in `pe1`.
- `pe0` has an operation that leaves, but this kernel binds no `.write` in `pe0`.

**Rules:**

- A warning is about the kernel only. An AGU that the kernel does not bind can be set by another kernel in a direct kernel, which keeps the registers it does not write; a memory kernel sets them to 0 ([3.2](kernel.md#32-modes)).

| Warning | Cause |
|---|---|
| `top1 is read but no .top is bound in pe1 of this kernel` | a buffer `topN` or `baseN` read by an operation, with no `.top` or `.base` bound in `peN` ([7.2](#72-the-routing)) |
| `pe0 has an operation but no .write is bound in this kernel` | the operation that leaves a pe, with no `.write` bound in this pe |
| `pe1 shares the write Agu 'w' with pe0 but its operations need another delay, cyc: auto follows pe0` | a write `Agu` with `cyc: auto` bound in several pes whose operations need different delays: the delay is the one of the first pe ([4.2.4](agu.md#424-write-agus)) |

## 7.4 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [7.1](#71-staging-variables) | `the Staging variable 's' is declared twice` | two `Staging` with the same name |
| [7.1](#71-staging-variables) | `'a' is already declared as an Agu variable` | a `Staging` named like an `Agu` (or `a Transfer variable`) |
| [7.1](#71-staging-variables) | `'a' is already declared as a Staging variable` | an `Agu` or a `Transfer` named like a `Staging` |
| [7.1](#71-staging-variables) | `unknown Staging variable 'zz'` | `zz = …;` in a pe, with a name that is not declared |
| [7.1](#71-staging-variables) | `'a' is an Agu variable, only a Staging variable can receive an operation` | an operation assigned to an `Agu` |
| [7.1](#71-staging-variables) | `the Staging variable 's' is already set at line N` | a `Staging` set twice |
| [7.1](#71-staging-variables) | `the Staging variable 's' is read before it is set` | a `Staging` read before the statement that sets it |
