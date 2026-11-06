[Index](../VMEG.md) · [Operations](operations.md)

# The opcodes 0x000 to 0x0ff

This page lists, by lot of 16 opcodes, the operations of the range 0x000-0x0ff that `vmegc` writes: how each one is written in vmeg and what it computes.

## Contents

- [6.6.1 How to read the tables](#661-how-to-read-the-tables)

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
- The list shown by `vmegc --ops` is the same list, sorted by opcode.
