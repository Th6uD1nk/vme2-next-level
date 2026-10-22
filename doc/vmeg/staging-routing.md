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
