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
