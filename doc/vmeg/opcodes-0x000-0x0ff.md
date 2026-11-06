[Index](../VMEG.md) · [Operations](operations.md)

# The opcodes 0x000 to 0x0ff

This page lists, by lot of 16 opcodes, the operations of the range 0x000-0x0ff that `vmegc` writes: how each one is written in vmeg and what it computes.

## Contents

- [6.6.1 How to read the tables](#661-how-to-read-the-tables)
- [6.6.2 Lot 1: 0x000 to 0x00f](#662-lot-1-0x000-to-0x00f)

## 6.6.1 How to read the tables

Each lot of 16 opcodes has its table. A row is one operation.

| Column | Content |
|---|---|
| Opcode | the number of the opcode that `vmegc` writes. The four numbers of a group, such as 0x010 to 0x013, give the same word on the PSP: the table gives the first one |
| Written | the way to write the operation in a pe. The names `a`, `b`, `x`, `c` and `n` are the ones used in the Result column |
| Result | what the operation computes for each word read |
| k | what the shift `>> n` written after the operation does to it ([6.4](operations.md#64-sat-and-the-shifts)) |

**Rules:**

- A word read or written is a signed number of 24 bits. A result that does not fit in 24 bits keeps its 24 low bits.
- In a write of two operands, `a` is the first operand and `b` the second: `a - b` subtracts `b` from `a`.
- A row marked `not written` is an opcode that `vmegc` does not write: the Result column says what it gives.
- The list shown by `vmegc --ops` has the opcodes that `vmegc` writes, sorted by opcode.

## 6.6.2 Lot 1: 0x000 to 0x00f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x000 | not written | zero for every input | ignored |
| 0x004 | `x`, `pass(x)` | `x` as it is | ignored |
| 0x008 | not written | the same word as 0x004 | ignored |
| 0x00c | `c`, `cst(c)` | the number `c`, whatever the operands are | ignored |

```c
.pe0 { .spad = pass(top1); }
.pe1 { .spad = 5; }
.pe2 { .spad = cst(5); }
```

**Explanation of the code above:**

- `pe0` copies `top1`. `x` is a buffer or a `Staging` variable ([6.3.7](operations.md#637-pass)).
- `pe1` and `pe2` write the number 5. The number is known at compile time, and it can be an expression of numbers such as `10 - 5`.

**Rules:**

- The shift of the operation is ignored: `pass(x) >> n` and `cst(c) >> n` give the same words as `pass(x)` and `cst(c)`. A shift written on a number alone, `5 >> 2`, is computed at compile time.

