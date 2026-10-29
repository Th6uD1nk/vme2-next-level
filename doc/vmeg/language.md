[Index](../VMEG.md) · [Running vmegc](running.md) · [The kernel](kernel.md)

# The language

## Contents

- [2.1 Attributes](#21-attributes)
- [2.2 Variables](#22-variables)
  - [2.2.1 Declaring several at once](#221-declaring-several-at-once)
  - [2.2.2 Names](#222-names)
- [2.3 Accesses by index](#23-accesses-by-index)
- [2.4 Int](#24-int)
- [2.5 Expressions](#25-expressions)
- [2.6 Numbers, macros and unknown names](#26-numbers-macros-and-unknown-names)
  - [2.6.1 Trusted macros](#261-trusted-macros)
- [2.7 Loops](#27-loops)
- [2.8 Synonyms](#28-synonyms)
- [2.9 Errors](#29-errors)

## 2.1 Attributes

An attribute is a named member of a kernel. It starts with a dot. Its content is either a block `{ }` or a value given with `=`.

| Attribute | Opens | Page |
|---|---|---|
| `.kernel name mode { }` | a kernel | [The kernel](kernel.md) |
| `.pe0 { }` to `.pe3 { }` | a processing element | [Processing elements](pe.md) |
| `.load { }`, `.store { }` | a DMAC transfer | [Transfers](transfers.md) |
| `.offsets { }` | the scratchpad offsets of a transfer | [Transfers](transfers.md) |

A member of an attribute has one of two forms: `.member = variable;` or `.member { … }`. The operation of a pe whose result leaves on the write is the member `.spad` (`.spad = top0 + base0;`); an operation kept in a `Staging` variable is set by its name (`s = top0 + base0;`). A variable can be replaced by its fields written in place.

```c
.pe0 { .top = t; .write = { count: 15 }; .spad = top0 + base0; }
.load { .transfer = in; .scope = global; }
```

The member of an attribute can also be written after it: `.pe0.top = t;` is the same as `.pe0 { .top = t; }`.

> **Support is incomplete.** In the same way that a block can stand for a variable (`.top = { count: 15 }` instead of `.top = t`), a variable should be able to stand for a block, and every member should accept both. Today only the bindings of a pe (`.top`, `.base`, `.write`) accept both. `.transfer` takes a variable only, and `.pe0`, `.load`, `.store` and `.offsets` take a block only.

## 2.2 Variables

A variable has a type and starts with no dot. `Agu`, `Transfer` and `Int` are declared with `=`; `Staging` has no initializer. The fields of an initializer are separated from their value with `:`.

| Type | Declares | Example |
|---|---|---|
| `Agu` | an address generator | `Agu t = { count: 15 };` |
| `Staging` | a result kept in the pe | `Staging s;` |
| `Transfer` | a DMAC transfer | `Transfer in = { memory: a, count: 15 };` |
| `Int` | a number known at compile time | `Int n = 16 - 1;` |

`Agu` and `Transfer` can take a kind in parentheses, which gives them their own fields: `Agu(2) t = { count: 15 };` ([4.1](agu.md#41-declaring-an-agu)) and `Transfer(Words) in = { memory: a, count: 15, step: 4 };` ([9.1](transfers.md#91-the-transfer-variable)).

### 2.2.1 Declaring several at once

A variable is declared by its own statement, or together with others of the same type, each one with its own initializer. Both forms give the same result.

```c
Staging a;
Staging b;
Agu x = { count: 3 };
Agu y = { count: 7 };
Int n = 1;
Int m = n + 1;
```

```c
Staging a, b;
Agu x = { count: 3 }, y = { count: 7 };
Int n = 1, m = n + 1;
```

### 2.2.2 Names

`Agu`, `Staging`, `Transfer` and `Int` share one set of names: a name is declared once, whatever its type. A variable is declared before the statement that uses it, in the kernel or in the block where it is used.

## 2.3 Accesses by index

An access by index starts with no dot: `pe[p]`, `top[t]`, `base[b]`. The index is a number from 0 to 3, or an `Int`, a loop variable or an expression of those.

| Written | Same as |
|---|---|
| `pe[1] { … }` | `.pe1 { … }` |
| `pe[1].top = t;` | `.pe1.top = t;` |
| `top[2] = 8;` in a `.offsets` | `.top2 = 8;` |

```c
for p in 0..3 {
  pe[p] { .top = t; .spad = top0 + top0; }
}
```

## 2.4 Int

`Int name = expression;` names a number known at compile time. It writes no code. Where the name is used, its number is used instead: in the fields of an `Agu` or of a `Transfer`, in the offsets, in an index, in the bounds of a loop, in another `Int`.

```c
Int last = 3;
Agu x = { count: last };
for p in 0..last {
  pe[p] { .top = x; .spad = top0 + top0; }
}
```

An `Int` can be written in a kernel, in a `@kernel` block and in the body of a loop. How an expression is computed is in [2.5](#25-expressions), and what happens when a part of it is not known in [2.6](#26-numbers-macros-and-unknown-names).

## 2.5 Expressions

An expression between numbers uses these operators, from the strongest to the weakest. Operators of the same level group from the left.

| Level | Operators |
|---|---|
| 1 | `-` (negation), `~` (complement), parentheses |
| 2 | `*` |
| 3 | `+` `-` |
| 4 | `<<` `>>` |
| 5 | `&` |
| 6 | `^` |
| 7 | `\|` |

| Written | Value |
|---|---|
| `1 + 2 * 3` | `7` |
| `(1 + 2) * 3` | `9` |
| `10 - 2 - 3` | `5` |
| `1 << 2 + 1` | `8` |
| `6 & 3 + 1` | `4` |
| `1 \| 6 & 3` | `3` |
| `5 ^ 3 & 1` | `4` |
| `~5` | `-6` |
| `0xff & ~0xf` | `240` |

The operands are numbers, `Int` names, loop variables and macros ([2.6](#26-numbers-macros-and-unknown-names)). A number is written in decimal (`15`), in hexadecimal (`0x0f`) or in binary (`0b1111`). `true` is `1` and `false` is `0`.

Between numbers, `<<` and `>>` are the plain C shifts. On the result of an operation of a pe they apply to that result, see [Operations](operations.md).

Currently not supported: `/`, `%` and the comparisons.

## 2.6 Numbers, macros and unknown names

A value is a **number** when everything it uses is known: literals, `Int` names, loop variables and the trusted macros of the file ([2.6.1](#261-trusted-macros)). `vmegc` computes it and writes the number.

When one part is not known (a macro of a header, a variable of the function, a macro that is not trusted), the **whole expression** is copied as C text between parentheses. The known parts are replaced by their value. The C compiler then computes it.

| Written | Generated |
|---|---|
| `count: N - 1`, with `#define N 16` before the kernel | `0xf` |
| `count: N - 1`, `N` not known | `(N - 1)` |
| `count: N + HEADER`, with `#define N 16` before the kernel | `(16 + HEADER)` |
| `count: HEADER` | `HEADER` |
| `Int n = HEADER * 2;` then `count: n + 1` | `((HEADER * 2) + 1)` |

The text is copied in the fields of an `Agu` and of a `Transfer`, in the offsets and in an `Int`. In the function generated for a transfer, each unknown name of the text becomes a parameter, see [Transfers](transfers.md).

Where a register needs a constant, an unknown part is an error: the constants of the functions of a pe and the shifts (each one is listed in [Operations](operations.md)), an index, the bounds of a loop.

### 2.6.1 Trusted macros

A macro of the file is trusted when all of these are true:

- it is defined **once** in the file;
- it is defined **before** the kernel or the block that uses it;
- it is **outside** any `#if`, `#ifdef`, `#ifndef` and `#else`;
- it has **no parameters**;
- it is never `#undef`ed;
- its body is a number or an expression whose parts are known, which includes other trusted macros.

A macro that is not trusted is an unknown name.

| Case | `count: N - 1` gives |
|---|---|
| `#define N 16` | `0xf` |
| `#define A 4`, `#define B (A * 2)`, then `B - 1` | `7` |
| `N` defined after the kernel | `(N - 1)` |
| `N` defined twice | `(N - 1)` |
| `N` defined inside `#ifdef` | `(N - 1)` |
| `N` defined, then `#undef N` | `(N - 1)` |
| `#define N (3 + )`, a body that is not an expression | `(N - 1)` |

## 2.7 Loops

`for p in a..b { … }` repeats its body for each value of `p` from `a` to `b`, both included. `vmegc` unrolls it: the body is written once per turn. The bounds are numbers ([2.6](#26-numbers-macros-and-unknown-names)). When `a` is above `b` the body is not written. Loops can be nested. Their body can hold `Int`, `.load` and `.store`, in a kernel as well as in a `@kernel` block, and pe blocks in a kernel.

```c
for p in 0..1 {
  pe[p] { .top = t; .spad = top0 + top0; }
}
```

writes the same as `pe[0] { .top = t; .spad = top0 + top0; }` followed by `pe[1] { .top = t; .spad = top0 + top0; }`.

This is not the C `for (…)`, which stays C code.

An `Int` declared in the body is computed again at each turn. An `Agu`, a `Staging` or a `Transfer` declared in the body is declared again at each turn, which fails at the second one: currently, declare it before the loop.

## 2.8 Synonyms

`context` is a synonym of `kernel`.

| Written | Same as |
|---|---|
| `.context name mode { }` | `.kernel name mode { }` |
| `@context name config` above a function | `@kernel name config` above a function |

The block form `@context name config { }` inside a function is currently not supported, use `@kernel`.

## 2.9 Errors

| Section | Message | Cause |
|---|---|---|
| [2.2](#22-variables) | `expected '='` | an `Agu`, a `Transfer` or an `Int` declared without initializer |
| [2.2](#22-variables) | `expected ';'` | a `Staging` declared with an initializer |
| [2.2.2](#222-names) | `the Agu variable 'x' is declared twice` | a name declared twice with the same type (the message names the type) |
| [2.2.2](#222-names) | `'x' is already declared as an Agu variable` | a name declared again with another type |
| [2.2.2](#222-names) | `unknown Agu variable 't'` | a variable used before its declaration or where it is not visible (the message names the type) |
| [2.3](#23-accesses-by-index) | `pe4: processing element out of range (pe0 to pe3)` | a pe index above 3 |
| [2.3](#23-accesses-by-index) | `top[...]: buffer index must be a number from 0 to 3` | a buffer index outside 0 to 3 |
| [2.4](#24-int) | `'n' is defined twice` | two `Int` with the same name in the same kernel or block |
| [2.5](#25-expressions) | `invalid number '010'` | a number with a leading zero |
| [2.6](#26-numbers-macros-and-unknown-names) | `processing element index must be a number` | an unknown part in the index of a pe |
| [2.6](#26-numbers-macros-and-unknown-names) | `for p: bounds must be numbers` | an unknown part in the bounds of a loop |
| [2.6](#26-numbers-macros-and-unknown-names) | `'call' expression not supported here` | a macro with parameters used like a function, `F(3)`: currently not supported |
| [2.7](#27-loops) | `the Agu variable 'x' is declared twice` | an `Agu`, a `Staging` or a `Transfer` declared in the body of a loop with two turns or more (currently not supported) |
| [2.8](#28-synonyms) | `inside a function only '@kernel name { ... }' is accepted` | the block form of `@context` |
