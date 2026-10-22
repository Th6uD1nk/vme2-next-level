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

A member of an attribute has one of two forms: `.member = variable;` or `.member { … }`. An operation of a pe starts with a dot too. A variable can be replaced by its fields written in place.

```c
.pe0 { .top = t; .write = { count: 15 }; .top0 + base0; }
.load { .transfer = in; .scope = global; }
```

The member of an attribute can also be written after it: `.pe0.top = t;` is the same as `.pe0 { .top = t; }`.

> **Support is incomplete.** In the same way that a block can stand for a variable (`.top = { count: 15 }` instead of `.top = t`), a variable should be able to stand for a block, and every member should accept both. Today only the bindings of a pe (`.top`, `.base`, `.write`) accept both. `.transfer` takes a variable only, and `.pe0`, `.load`, `.store` and `.offsets` take a block only.

## 2.2 Variables

A variable has a type and starts with no dot. `Agu`, `Transfer` and `Int` are declared with `=`; `Staging` has no initializer. The fields of an initializer are separated from their value with `:`.

| Type | Declares | Example |
|---|---|---|
| `Agu` | an address generator | `Agu t = { count: 15 };` |
| `Staging` | a result kept in the FU | `Staging s;` |
| `Transfer` | a DMAC transfer | `Transfer in = { type: words, mode: basic, memory: a, count: 15 };` |
| `Int` | a number known at compile time | `Int n = 16 - 1;` |

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
  pe[p] { .top = t; .top0 + top0; }
}
```

| Error | Cause |
|---|---|
| `pe4: processing element out of range (pe0 to pe3)` | a pe index above 3 |
| `top[...]: buffer index must be a number from 0 to 3` | a buffer index outside 0 to 3 |

## 2.4 Int

`Int name = expression;` names a number known at compile time. It writes no code. Where the name is used, its number is used instead: in the fields of an `Agu` or of a `Transfer`, in the offsets, in an index, in the bounds of a loop, in another `Int`.

```c
Int last = 3;
Agu x = { count: last };
for p in 0..last {
  pe[p] { .top = x; .top0 + top0; }
}
```

An `Int` can be written in a kernel, in a `@kernel` block and in the body of a loop. How an expression is computed is in [2.5](#25-expressions), and what happens when a part of it is not known in [2.6](#26-numbers-macros-and-unknown-names).

| Error | Cause |
|---|---|
| `'n' is defined twice` | two `Int` with the same name in the same kernel or block |
