[Index](../VMEG.md) · [The kernel](kernel.md) · [Processing elements](pe.md)

# AGU variables

## Contents

- [4.1 Declaring an Agu](#41-declaring-an-agu)
- [4.2 Parameters](#42-parameters)
  - [4.2.1 Common parameters](#421-common-parameters)
  - [4.2.2 inner0](#422-inner0)
  - [4.2.3 Read AGUs](#423-read-agus)
  - [4.2.4 Write AGUs](#424-write-agus)
- [4.3 Binding an AGU to a pe](#43-binding-an-agu-to-a-pe)
  - [4.3.1 Sharing an AGU](#431-sharing-an-agu)
- [4.4 Errors](#44-errors)

## 4.1 Declaring an Agu

```c
Agu name = { count: 15 };
```

- An `Agu` is declared in a kernel, or in the block of a pe.
- The parameters are written in braces, each one with `:` between its name and its value ([2.2](language.md#22-variables)).
- A value is a number, an `Int`, an expression ([2.5](language.md#25-expressions)) or a name that `vmegc` does not know ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- The values are the **real values of the registers**: nothing is added or removed. `count: 15` is 16 words.
- An `Agu` does nothing until a pe uses it: see [4.3](#43-binding-an-agu-to-a-pe).

## 4.2 Parameters

| Parameter | Read AGU (`.top`, `.base`) | Write AGU (`.write`) | Meaning |
|---|---|---|---|
| `count` | required | required | the number of words, minus 1 |
| `offset` | yes | yes | where the AGU starts in the buffer |
| `mode` | yes | yes | the mode of the AGU |
| `step` | yes | yes | the distance between two words |
| `inner0` | yes | yes | an inner range ([4.2.2](#422-inner0)) |
| `reverse` | yes | yes | the order of the words is inverted |
| `repeat` | yes | no | the inner range is repeated ([4.2.3](#423-read-agus)) |
| `cyc` | no | yes | a delay in cycles ([4.2.4](#424-write-agus)) |
| `bubbles` | no | yes | words of zero before the data ([4.2.4](#424-write-agus)) |
| `sync` | no | yes | the data can be read by a FU of the same run ([4.2.4](#424-write-agus)) |

### 4.2.1 Common parameters

| Parameter | Value | Default |
|---|---|---|
| `count` | the number of words minus 1: `count: 15` is 16 words | required |
| `offset` | the position in the buffer, in words, where the AGU starts. A signed number from -32768 to 32767 | 0 |
| `step` | the distance between two successive words, in words | 1 |
| `mode` | the mode of the AGU, a number. Currently only the mode 4 is described: the address of the word `i` is `offset + i * step` | 4 |
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

- `repeat` needs `inner0`.
- It works in the mode 4, the default mode.
- It does not work together with `reverse`: `vmegc` does not check it.

### 4.2.4 Write AGUs

A write AGU is bound with `.write`. It writes the result of the pe into the buffer of the pe. It takes the common parameters and `cyc`, `bubbles` and `sync`.

```c
Agu w = { count: 15, cyc: 9, bubbles: 5, sync: true };
```

| Parameter | Value |
|---|---|
| `cyc` | the delay of the write, from 0 to 255 (currently not checked): a number, `auto`, or `auto` with a shift, see below. A result computed at the cycle `c` is written on the word `c + 6 - cyc + bubbles`: a larger `cyc` writes earlier |
| `bubbles` | from 0 to 4095. The written stream is shifted by `bubbles` words, and the first ones are zeros |
| `sync` | `true` makes the data readable by a FU of the same run |

- `sync` waits no cycle. For a FU to see the data, the write has to come at least 7 positions after the cycle that computed it, that is `6 - cyc + bubbles >= 7`. This is for you to set with `cyc` and `bubbles`: `vmegc` does not compute it.

`cyc` compensates the time that the FUs of the pe need to produce the data. It is written as a number, as `auto`, or as `auto` with a shift:

```c
Agu a = { count: 15, cyc: 9 };
Agu b = { count: 15, cyc: auto };
Agu c = { count: 15, cyc: auto - 1 };
Agu d = { count: 15, cyc: auto + shift };
```

- `auto` lets vmeg work out the number, so that the stream is aligned on the first element that leaves the pe. A FU takes 3 cycles to write its result and the write to the buffer takes 3 more: one FU gives 6, two chained FUs give 9. A FU that reads a Staging variable comes after the FU that set it, so the chain goes across the pes. `mac` and `acc` count like the other FUs.
- A shift is written after `auto`: `auto - 1`, `auto + 1`, or `auto` plus or minus an `Int` or a macro. It uses the same expressions as the rest of the language, and it is the way to read an element other than the first one, for example the fourth element of each group of a `mac`.
- `auto` is only accepted in the `cyc` of a write AGU. The pe that owns the AGU needs an operation that leaves it; when an Agu variable is shared, it is the first pe that binds it.
- The rule is checked for one and two FUs. Three chained FUs (12) and a Staging variable read by another pe are not yet verified on the hardware.
