[Index](../VMEG.md) · [Operations](operations.md)

# The opcodes 0x000 to 0x0ff

This page lists, by lot of 16 opcodes, the operations of the range 0x000-0x0ff that `vmegc` writes: how each one is written in vmeg and what it computes.

## Contents

- [6.6.1 How to read the tables](#661-how-to-read-the-tables)
- [6.6.2 Lot 1: 0x000 to 0x00f](#662-lot-1-0x000-to-0x00f)
- [6.6.3 Lot 2: 0x010 to 0x01f](#663-lot-2-0x010-to-0x01f)
- [6.6.4 Lot 3: 0x020 to 0x02f](#664-lot-3-0x020-to-0x02f)
- [6.6.5 Lot 4: 0x030 to 0x03f](#665-lot-4-0x030-to-0x03f)
- [6.6.6 Lot 5: 0x040 to 0x04f](#666-lot-5-0x040-to-0x04f)

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

## 6.6.3 Lot 2: 0x010 to 0x01f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x010 | `a + b` | `a + b` | kept |
| 0x014 | `x >> n` | `x` shifted to the right by `n` | kept |
| 0x018 | `a - b` | `a - b` | kept |
| 0x01c | not written | the same word as 0x014 | kept |

```c
.pe0 { .spad = top0 + top1; }
.pe1 { .spad = top1 >> 3; }
.pe2 { .spad = top0 - top1 >> 1; }
```

**Explanation of the code above:**

- `pe0` adds `top0` and `top1`.
- `pe1` shifts `top1` to the right by 3. `x` is a buffer or a `Staging` variable, and `n` is a number from 0 to 63. The shift keeps the sign: it is an arithmetic shift.
- `pe2` subtracts `top1` from `top0`, then shifts the difference to the right by 1.

**Rules:**

- With `k` kept, the shift written after the operation is applied to the exact result, before the 24 low bits are kept.
- `pass(x) >> n` is not the shift of `x`: it is the opcode 0x004, which ignores the shift ([6.6.2](#662-lot-1-0x000-to-0x00f)). `x >> n` on a buffer is the opcode 0x014.
- With `--compat fat`, `a + b` is written with the opcode 0x030 and its number at 0 ([6.2.3](operations.md#623-how-the-opcode-is-chosen)).

## 6.6.4 Lot 3: 0x020 to 0x02f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x020 | not written | the same word as 0x010 | kept |
| 0x024 | `x + c` | `x + c` | kept |
| 0x028 | not written | the same word as 0x018 | kept |
| 0x02c | `c - x` | `c - x` | kept |

```c
.pe0 { .spad = top1 + 3; }
.pe1 { .spad = 7 - top1; }
.pe2 { .spad = (top1 + 3) >> 1; }
```

**Explanation of the code above:**

- `pe0` adds the number 3 to `top1`. The number can be written on either side: `3 + top1` is the same operation.
- `pe1` subtracts `top1` from the number 7. `0 - top1` is the opposite of `top1`.
- `pe2` adds 3 to `top1`, then shifts the sum to the right by 1.

**Rules:**

- `x` is a buffer or a `Staging` variable. The number `c` is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- With `k` kept, the shift written after the operation is applied to the exact result, before the 24 low bits are kept.

## 6.6.5 Lot 4: 0x030 to 0x03f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x030 | `a + b + c` | `(a + b) + c` | ignored |
| 0x034 | `a - b + c`, `subacst(a, b, c)` | `(a - b) + c` | ignored |
| 0x038 | `addbyt(a, b)` | the byte 0 of `a` plus the byte 0 of `b` plus the byte 1 of `a` plus the byte 1 of `b` | ignored |
| 0x03c | `subbyt(a, b)` | the byte 0 of `a` minus the byte 0 of `b`, plus the byte 1 of `a` minus the byte 1 of `b` | ignored |

```c
.pe0 { .spad = top0 + top1 + 5; }
.pe1 { .spad = top0 - top1 + 5; }
.pe2 { .spad = addbyt(top0, top1); }
.pe3 { .spad = subbyt(top0, top1); }
```

**Explanation of the code above:**

- `pe0` adds `top0`, `top1` and the number 5. The number can be written on either side: `5 + (top0 + top1)` is the same operation.
- `pe1` subtracts `top1` from `top0`, then adds the number 5.
- `pe2` adds the two low bytes of `top0` and `top1` and the two bytes that follow them.
- `pe3` does the same with differences: the difference of the low bytes plus the difference of the bytes that follow.

**Rules:**

- The byte 0 of a word is its 8 low bits, the byte 1 is the next 8 bits. The bits above are not used.
- `a` and `b` are buffers or `Staging` variables. The number `c` is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- The shift written after one of these operations is not applied.

## 6.6.6 Lot 5: 0x040 to 0x04f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x040 | `b + (a >> n)` | `b + (a >> n)` | ignored |
| 0x044 | `(x >> n) + c` | `(x >> n) + c` | ignored |
| 0x048 | `b - (a >> n)`, `subshr(a, b, n)` | `b - (a >> n)` | ignored |
| 0x04c | `c - (x >> n)` | `c - (x >> n)` | ignored |

```c
.pe0 { .spad = top0 + (top1 >> 3); }
.pe1 { .spad = (top1 >> 3) + 5; }
.pe2 { .spad = top0 - (top1 >> 3); }
.pe3 { .spad = 5 - (top1 >> 3); }
```

**Explanation of the code above:**

- `pe0` adds `top0` and `top1` shifted to the right by 3.
- `pe1` adds the number 5 to `top1` shifted to the right by 3.
- `pe2` subtracts `top1` shifted to the right by 3 from `top0`. `subshr(top1, top0, 3)` is the same operation.
- `pe3` subtracts `top1` shifted to the right by 3 from the number 5.

**Rules:**

- `a`, `b` and `x` are buffers or `Staging` variables, and the numbers `c` and `n` are known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- The shift `>> n` is a part of these operations: `n` is a number written in a register of the pe, and it is not the shift `k` of the operation.
- The amount `n` is read as a signed number of 6 bits: from 0 to 31 it shifts to the right with the sign kept, from -32 to -1 it shifts to the left. Only the 6 low bits of `n` count.
- The shift written after one of these operations is not applied.
- `x >> n` alone is the opcode 0x014 ([6.6.3](#663-lot-2-0x010-to-0x01f)).

