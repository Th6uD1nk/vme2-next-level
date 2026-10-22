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
