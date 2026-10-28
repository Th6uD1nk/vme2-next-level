[Index](../VMEG.md) · [The kernel](kernel.md) · [Processing elements](pe.md)

# AGU variables

## Contents

- [4.1 Declaring an Agu](#41-declaring-an-agu)
- [4.2 Parameters](#42-parameters)
  - [4.2.1 Common parameters](#421-common-parameters)
  - [4.2.2 inner0](#422-inner0)
  - [4.2.3 Read AGUs](#423-read-agus)
  - [4.2.4 Write AGUs](#424-write-agus)
  - [4.2.5 The mode 2](#425-the-mode-2)
- [4.3 Binding an AGU to a pe](#43-binding-an-agu-to-a-pe)
  - [4.3.1 Sharing an AGU](#431-sharing-an-agu)
- [4.4 Errors](#44-errors)

## 4.1 Declaring an Agu

```c
Agu name = { count: 15 };
Agu(4) other = { count: 15 };
```

**Rules:**

- An `Agu` is declared in a kernel, or in the block of a pe.
- The mode of an AGU is its type: `Agu` and `Agu(4)` are the mode 4, `Agu(2)` is the mode 2. Each mode has its own parameters: [4.2](#42-parameters) for the mode 4, [4.2.5](#425-the-mode-2) for the mode 2. Another mode is an error.
- An AGU written directly in the braces of `.top`, `.base` or `.write` has no type: it is in the mode 4.
- The parameters are written in braces, each one with `:` between its name and its value ([2.2](language.md#22-variables)).
- A value is a number, an `Int`, an expression ([2.5](language.md#25-expressions)) or a name that `vmegc` does not know ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- The values are the **real values of the registers**: nothing is added or removed. `count: 15` is 16 words.
- An `Agu` does nothing until a pe uses it: see [4.3](#43-binding-an-agu-to-a-pe).

## 4.2 Parameters

The parameters of the mode 4, the default mode.

| Parameter | Read AGU (`.top`, `.base`) | Write AGU (`.write`) | Meaning |
|---|---|---|---|
| `count` | required | required | the number of words, minus 1 |
| `offset` | yes | yes | where the AGU starts in the buffer |
| `step` | yes | yes | the distance between two words |
| `inner0` | yes | yes | an inner range ([4.2.2](#422-inner0)) |
| `reverse` | yes | yes | the order of the words is inverted |
| `repeat` | yes | no | the inner range is repeated ([4.2.3](#423-read-agus)) |
| `cyc` | no | yes | a delay in cycles ([4.2.4](#424-write-agus)) |
| `bubbles` | no | yes | words of zero before the data ([4.2.4](#424-write-agus)) |
| `sync` | no | yes | the data can be read by an operation of the same run ([4.2.4](#424-write-agus)) |

The other bits of the format registers are currently not supported.

### 4.2.1 Common parameters

| Parameter | Value | Default |
|---|---|---|
| `count` | the number of words minus 1: `count: 15` is 16 words | required |
| `offset` | the position in the buffer, in words, where the AGU starts. A signed number from -32768 to 32767 | 0 |
| `step` | the distance between two successive words, in words | 1 |
| `reverse` | `true` inverts the order of the words: a read of 16 words gives 15, 14, …, 0, and a write puts the word 0 on the position 15, the word 1 on the 14, and so on | `false` |

```c
Agu t = { count: 15, offset: -16, step: 2, reverse: true };
```

### 4.2.2 inner0

`inner0` describes a range of words inside the AGU. It has its own parameters, `count` and `step`, written in braces.

```c
Agu t = { count: 15, inner0: { count: 15, step: 1 } };
```

| Parameter of `inner0` | Value |
|---|---|
| `count` | the number of words of the range, minus 1. Required |
| `step` | the distance between two words of the range, in words. Required. A `step` of 0 means no range |

- The parameters of `inner0` can not have parameters of their own.
- `inner1` is currently not supported.
- What the range does on its own is currently not documented. With `repeat` it is the range that is repeated, see [4.2.3](#423-read-agus).

### 4.2.3 Read AGUs

A read AGU is bound with `.top` or `.base`. It takes the common parameters and `repeat`.

`repeat: true` repeats the range of `inner0` for as long as the run lasts, whatever the `count` of the AGU. The matrix of the mat4x4 sample is read this way: its 16 words are read again and again while the vectors go by.

```c
Agu matrix = { count: 15, inner0: { count: 15, step: 1 }, repeat: true };
```

**Rules:**

- `repeat` needs `inner0`.
- Currently not supported: `repeat` together with `reverse`.

### 4.2.4 Write AGUs

A write AGU is bound with `.write`. It writes the result of the pe into the buffer of the pe. It takes the common parameters and `cyc`, `bubbles` and `sync`.

```c
Agu w = { count: 15, cyc: 9, bubbles: 5, sync: true };
```

| Parameter | Value |
|---|---|
| `cyc` | the delay of the write, from 0 to 255 (currently not checked): a number, `auto`, or `auto` with a shift, see below. A result computed at the cycle `c` is written on the word `c + 6 - cyc + bubbles`: a larger `cyc` writes earlier |
| `bubbles` | from 0 to 4095. The written stream is shifted by `bubbles` words, and the first ones are zeros |
| `sync` | `true` makes the data readable by an operation of the same run |

- `sync` waits no cycle. For an operation to see the data, the write has to come at least 7 positions after the cycle that computed it, that is `6 - cyc + bubbles >= 7`. This is for you to set with `cyc` and `bubbles`: `vmegc` does not compute it.

`cyc` compensates the time that the operations of the pe need to produce the data. It is written as a number, as `auto`, or as `auto` with a shift:

```c
Agu a = { count: 15, cyc: 9 };
Agu b = { count: 15, cyc: auto };
Agu c = { count: 15, cyc: auto - 1 };
Agu d = { count: 15, cyc: auto + shift };
```

**Explanation of the code above:**

- `auto` lets vmeg work out the number, so that the stream is aligned on the first element that leaves the pe. An operation takes 3 cycles to write its result and the write to the buffer takes 3 more: one operation gives 6, two chained operations give 9. An operation that reads a Staging variable comes after the operation that set it, so the chain goes across the pes. `mac` and `acc` count like the other operations.
- A shift is written after `auto`: `auto - 1`, `auto + 1`, or `auto` plus or minus an `Int` or a macro. It uses the same expressions as the rest of the language, and it is the way to read an element other than the first one, for example the fourth element of each group of a `mac`.

**Rules:**

- `auto` is only accepted in the `cyc` of a write AGU. The pe that owns the AGU needs an operation that leaves it; when an Agu variable is shared, it is the first pe that binds it. `vmegc` warns when another pe that shares it needs a different delay ([7.3](staging-routing.md#73-warnings)).
- The rule is checked for one and two operations. Three chained operations (12) and a Staging variable read by another pe are not yet verified on the hardware.

### 4.2.5 The mode 2

```c
Agu(2) t = { offset: 128, count: 7, step: 1, repeat: true };
Agu(2) w = { offset: 4, count: 15, step: 2, cyc: 6, bubbles: 2, sync: true };
```

| Parameter | Read AGU | Write AGU | Value |
|---|---|---|---|
| `count` | required | required | the number of words minus 1, as in [4.2.1](#421-common-parameters) |
| `offset` | yes | yes | as in [4.2.1](#421-common-parameters) |
| `step` | yes | yes | the distance between two successive words, in words. Default 1 |
| `reverse` | yes | yes | as in [4.2.1](#421-common-parameters) |
| `repeat` | yes | no | the range is read again and again for as long as the run lasts |
| `cyc`, `bubbles`, `sync` | no | yes | as in [4.2.4](#424-write-agus) |

**Explanation of the code above:**

- `t` reads 8 words from the word 128, one after the other, and starts again at the first one until the run ends.
- `w` writes 16 words from the word 4, one word out of two, with the same delay, bubbles and sync as a mode 4 write AGU.

**Rules:**

- In the mode 2, `count` and `step` describe the range itself: there is no `inner0`.
- `repeat` needs nothing else: it repeats the `count + 1` words of the AGU.
- Currently not verified on the hardware in the mode 2: `reverse`, and `cyc`, `bubbles` and `sync` of a write AGU.
- An AGU written directly in the braces of a pe is in the mode 4: for the mode 2, declare an `Agu(2)` variable and bind it.

## 4.3 Binding an AGU to a pe

An AGU is bound to a pe in the block of the pe, with `.top`, `.base` or `.write`:

```c
Agu t = { count: 15 }, w = { count: 15 };

.pe0 { .top = t; .write = w; }
.pe1 { .top = { count: 15 }; }
```

**Rules:**

- `.top` and `.base` bind a read AGU, `.write` binds a write AGU. A pe has one AGU of each of the three.
- The AGU is an `Agu` variable (`.top = t;`), or its parameters written directly in braces (`.top = { count: 15 };`).
- The pe is written `pe0` to `pe3`, or `pe[p]` with a number or a loop variable.
- Each of the three can be set once in a pe.
- An `Agu` variable is bound to one kind only: the same variable cannot be given to `.top` and to `.base`.

### 4.3.1 Sharing an AGU

An `Agu` variable that several pes bind is **one** AGU. It belongs to the first pe that binds it, its parameters are written once, and the other pes read or write through it: they get the same addresses.

```c
Agu t = { count: 15 };
Agu w = { count: 15 };

for p in 0..3 {
  pe[p] { .top = t; .write = w; .spad = top0 + top0; }
}
```

**Rules:**

- Sharing is the way to give the same stream to several pes. With the parameters written directly in each pe, every pe has its own AGU.
- The owner pe is also the pe that `cyc: auto` looks at ([4.2.4](#424-write-agus)).

## 4.4 Errors

The parameters of an `Agu` variable are checked when a pe binds it, so the messages name the pe (`pe0.top`). The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [4.1](#41-declaring-an-agu) | `the Agu variable 'a' is declared twice` | two `Agu` with the same name |
| [4.1](#41-declaring-an-agu) | `'a' is already declared as a Staging variable` | the name belongs to a Staging variable (or `a Transfer variable`) |
| [4.1](#41-declaring-an-agu) | `the Agu mode 3 is not described (2, 4)` | `Agu(n)` with a mode other than 2 and 4 |
| [4.1](#41-declaring-an-agu) | `pe0.top: the mode of an Agu is its type, write Agu(4) or Agu(2)` | `mode` written as a parameter |
| [4.2](#42-parameters) | `pe0.top: 'count' is required` | an AGU without `count` |
| [4.2](#42-parameters) | `pe0.top: unknown parameter 'foo' (count, offset, …)` | a name that is not a parameter of this kind of AGU, the message lists the ones that are |
| [4.2](#42-parameters) | `pe0.top: duplicate parameter 'count'` | the same parameter written twice |
| [4.2](#42-parameters) | `pe0.top: 'count' takes a value, not parameters between braces` | braces given to a parameter that takes a value |
| [4.2.1](#421-common-parameters) | `pe0.top: the offset 40000 is outside -32768 to 32767` | an `offset` that does not fit in 16 bits |
| [4.2.1](#421-common-parameters) | `pe0.top: reverse takes true or false` | `reverse` with another value (same for `repeat` and `sync`) |
| [4.2.2](#422-inner0) | `pe0.top: 'inner0' takes parameters between braces: inner0: { count: 15, step: 1 }` | `inner0` with a value |
| [4.2.2](#422-inner0) | `pe0.top.inner0: unknown parameter 'foo' (count, step)` | a parameter of `inner0` other than `count` and `step` |
| [4.2.2](#422-inner0) | `pe0.top.inner0: duplicate parameter 'count'` | the same parameter of `inner0` written twice |
| [4.2.2](#422-inner0) | `pe0.top.inner0: 'step' is required` | `inner0` without `count` or without `step` |
| [4.2.2](#422-inner0) | `braces cannot be nested more than one level inside the parameters` | braces inside the braces of `inner0` |
| [4.2.3](#423-read-agus) | `pe0.top: repeat needs inner0, the range to repeat` | `repeat` without `inner0` in the mode 4 |
| [4.2.4](#424-write-agus) | `pe0.write: the bubbles 5000 are outside 0 to 4095` | `bubbles` out of range |
| [4.2.4](#424-write-agus) | `pe0.write: auto is only for cyc` | `auto` in a parameter other than `cyc` |
| [4.2.4](#424-write-agus) | `auto is reserved for the cyc of a write AGU` | an `Int` named `auto` |
| [4.2.4](#424-write-agus) | `pe0.write: cyc auto needs an operation in pe0` | `cyc: auto` on a pe without an operation that leaves it |
| [4.2.5](#425-the-mode-2) | `pe0.top: unknown parameter 'inner0' (count, offset, step, reverse, repeat)` | `inner0` in an `Agu(2)` (the message lists the parameters of the mode) |
| [4.3](#43-binding-an-agu-to-a-pe) | `unknown Agu variable 'zzz'` | `.top = zzz;` with a name that is not an `Agu` |
| [4.3](#43-binding-an-agu-to-a-pe) | `pe0.top is already set at line N` | the same AGU kind set twice in a pe |
| [4.3](#43-binding-an-agu-to-a-pe) | `the Agu variable 'a' is already bound to .top, it cannot be bound to .base` | one variable given to two kinds |
| [4.3](#43-binding-an-agu-to-a-pe) | `pe6: processing element out of range (pe0 to pe3)` | a pe number above 3 |
