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
- [6.6.7 Lot 6: 0x050 to 0x05f](#667-lot-6-0x050-to-0x05f)
- [6.6.8 Lot 7: 0x060 to 0x06f](#668-lot-7-0x060-to-0x06f)
- [6.6.9 Lot 8: 0x070 to 0x07f](#669-lot-8-0x070-to-0x07f)
- [6.6.10 Lot 9: 0x080 to 0x08f](#6610-lot-9-0x080-to-0x08f)
- [6.6.11 Lot 10: 0x090 to 0x09f](#6611-lot-10-0x090-to-0x09f)
- [6.6.12 Lot 11: 0x0a0 to 0x0af](#6612-lot-11-0x0a0-to-0x0af)
- [6.6.13 Lot 12: 0x0b0 to 0x0bf](#6613-lot-12-0x0b0-to-0x0bf)
- [6.6.14 Lot 13: 0x0c0 to 0x0cf](#6614-lot-13-0x0c0-to-0x0cf)
- [6.6.15 Lot 14: 0x0d0 to 0x0df](#6615-lot-14-0x0d0-to-0x0df)
- [6.6.16 Lot 15: 0x0e0 to 0x0ef](#6616-lot-15-0x0e0-to-0x0ef)

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

## 6.6.7 Lot 6: 0x050 to 0x05f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x050 | `(a >> n) - b` | `(a >> n) - b` | ignored |
| 0x054 | `(x >> n) - c`, `x - c` | `(x >> n) - c` | ignored |
| 0x058 | `addhib(a, b)` | the byte 1 of `a` plus the byte 1 of `b` | ignored, except that 1 doubles the result |
| 0x05c | `(a & 255) + (b & 255)` | the byte 0 of `a` plus the byte 0 of `b` | ignored, except that 1 doubles the result |

```c
.pe0 { .spad = (top1 >> 3) - top0; }
.pe1 { .spad = (top1 >> 3) - 5; }
.pe2 { .spad = addhib(top0, top1); }
.pe3 { .spad = (top0 & 255) + (top1 & 255); }
```

**Explanation of the code above:**

- `pe0` subtracts `top0` from `top1` shifted to the right by 3.
- `pe1` subtracts the number 5 from `top1` shifted to the right by 3.
- `pe2` adds the byte 1 of `top0` and the byte 1 of `top1`.
- `pe3` adds the byte 0 of `top0` and the byte 0 of `top1`. The opcode is found from the writing with `& 255` on both operands, `& 0xff` is the same.

**Rules:**

- `a`, `b` and `x` are buffers or `Staging` variables, and the numbers `c` and `n` are known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- The amount `n` of 0x050 and 0x054 is read as in the lot 5 ([6.6.6](#666-lot-5-0x040-to-0x04f)).
- `x - c` is written with the opcode 0x054 and its amount `n` at 0: `top1 - 5` and `(top1 >> 0) - 5` are the same operation.
- The byte 0 and the byte 1 of a word are the ones of the lot 4 ([6.6.5](#665-lot-4-0x030-to-0x03f)).
- A shift written after 0x050 or 0x054 is not applied. After 0x058 or 0x05c, a shift of 1 doubles the result, and the other values are not applied.

## 6.6.8 Lot 7: 0x060 to 0x06f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x060 | `(f & a) ? -x : x` | `-x` when `f & a` is not zero, `x` otherwise | ignored |
| 0x064 | `(f & a) ? x : -x` | `x` when `f & a` is not zero, `-x` otherwise | ignored |
| 0x068 | `(f & a) ? b : x` | the number `b` when `f & a` is not zero, `x` otherwise | ignored |
| 0x06c | `(f & a) ? x : b` | `x` when `f & a` is not zero, the number `b` otherwise | ignored |

```c
.pe0 { .spad = (top0 & 4) ? -top1 : top1; }
.pe1 { .spad = (top0 & 4) ? top1 : -top1; }
.pe2 { .spad = (top0 & 4) ? 7 : top1; }
.pe3 { .spad = (top0 & 4) ? top1 : 7; }
```

**Explanation of the code above:**

- The four writings test the bit 2 of `top0` (the mask 4) and choose between `top1`, its opposite and the number 7.
- `pe0` gives the opposite of `top1` when the bit is set, `pe1` when it is not set.
- `pe2` gives 7 when the bit is set and `top1` otherwise, `pe3` the reverse.

**Rules:**

- The condition of the choice `c ? y : z` is `f & a`, with a number `a`: it is true when the result is not zero. The mask can be written on either side, `(4 & top0)`. Another condition gives the error `no opcode covers this expression`.
- `f` and `x` are buffers or `Staging` variables, `f` is the first operand and `x` the second. The numbers `a` and `b` are known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- The shift written after one of these operations is not applied.

## 6.6.9 Lot 8: 0x070 to 0x07f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x070 | `(x & a) ? x - b : x + b` | `x - b` when `x & a` is not zero, `x + b` otherwise | ignored, except that 1 doubles `x` |
| 0x074 | `(x & a) ? x + b : x - b` | `x + b` when `x & a` is not zero, `x - b` otherwise | ignored, except that 1 doubles `x` |
| 0x078 | not written | the first operand when it is negative, the smaller of the two operands otherwise | ignored |
| 0x07c | `clamp(x, low, high)` | `x` limited between `low` and `high` | ignored |

```c
.pe0 { .spad = (top1 & 4) ? top1 - 7 : top1 + 7; }
.pe1 { .spad = (top1 & 4) ? top1 + 7 : top1 - 7; }
.pe2 { .spad = clamp(top1, -100, 100); }
```

**Explanation of the code above:**

- `pe0` subtracts 7 from `top1` when the bit 2 of `top1` is set, and adds 7 otherwise.
- `pe1` does the reverse.
- `pe2` limits `top1` between -100 and 100.

**Rules:**

- `x` is a buffer or a `Staging` variable, and the numbers `a`, `b`, `low` and `high` are known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- The mask is tested on `x` itself: the writing has the same operand at the three places, and another combination gives the error `no opcode covers this expression`.
- A shift of 1 written after 0x070 or 0x074 doubles `x` before `b` is added or subtracted. The other values of the shift are not applied.
- When `low` is above `high`, `clamp` gives `high`.
- 0x078 is not written by `vmegc`: what the PSP gives for it is not a plain minimum, and its tests are not finished.

## 6.6.10 Lot 9: 0x080 to 0x08f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x080 | `mulclp(f, x)` | `x * f` when `f` is from -2 to 2, zero otherwise | ignored |
| 0x084 | `mulclpneg(f, x)` | `-(x * f)` when `f` is from -2 to 2, zero otherwise | ignored |
| 0x088 | `(x & a) ? 0 : b` | zero when `x & a` is not zero, the number `b` otherwise | ignored |
| 0x08c | `(x & a) ? b : 0` | the number `b` when `x & a` is not zero, zero otherwise | ignored |

```c
.pe0 { .spad = mulclp(top0, top1); }
.pe1 { .spad = mulclpneg(top0, top1); }
.pe2 { .spad = (top1 & 4) ? 0 : 9; }
.pe3 { .spad = (top1 & 4) ? 9 : 0; }
```

**Explanation of the code above:**

- `pe0` multiplies `top1` by `top0` when `top0` is -2, -1, 0, 1 or 2, and gives zero for any other value of `top0`.
- `pe1` does the same with the opposite of the product.
- `pe2` gives zero when the bit 2 of `top1` is set, and the number 9 otherwise. `pe3` gives the reverse.

**Rules:**

- `f` and `x` are buffers or `Staging` variables, `f` is the first operand and `x` the second. The numbers `a` and `b` are known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- The mask of 0x088 and 0x08c is tested on `x` itself, and the zero of the writing is the number 0. Another combination gives the error `no opcode covers this expression`.
- The shift written after one of these operations is not applied.

## 6.6.11 Lot 10: 0x090 to 0x09f

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x090 | `c << x`, with `c` from -0x800000 to 0x7fffff | the number `c` shifted to the left by `x`, the sign is kept when it shifts to the right | ignored |
| 0x094 | `c >> x`, with `c` from -0x800000 to 0x7fffff | the number `c` shifted to the right by `x`, the sign is kept | ignored |
| 0x098 | `c << x`, with `c` from 0x800000 to 0xffffff | the number `c` as an unsigned number of 24 bits shifted to the left by `x`, without the sign when it shifts to the right | ignored |
| 0x09c | `c >> x`, with `c` from 0x800000 to 0xffffff | the number `c` as an unsigned number of 24 bits shifted to the right by `x`, without the sign | ignored |

```c
.pe0 { .spad = -5 << top1; }
.pe1 { .spad = -5 >> top1; }
.pe2 { .spad = 0xc00000 << top1; }
.pe3 { .spad = 0xc00000 >> top1; }
```

**Explanation of the code above:**

- The number is shifted by the words of `top1`: each word gives the amount of the shift for the word written.
- `pe0` and `pe1` shift the number -5, `pe2` and `pe3` shift the number 0xc00000.

**Rules:**

- The amount `x` is a buffer or a `Staging` variable read as a signed number of 6 bits: from 0 to 31 the shift goes in the direction of the operator, from -32 to -1 it goes the other way. Only the 6 low bits of the word count.
- The number `c` is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)). `vmegc` takes the opcode from its value: from -0x800000 to 0x7fffff it is 0x090 or 0x094, from 0x800000 to 0xffffff it is 0x098 or 0x09c.
- The two forms give the same word for a left shift. They differ for a right shift of a number whose bit 23 is set: the first form keeps the sign, the second one does not.
- Another value of `c` gives the error `no opcode covers this expression: a number shifted by a buffer must be from -0x800000 to 0xffffff`.
- The shift written after one of these operations is not applied.

## 6.6.12 Lot 11: 0x0a0 to 0x0af

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x0a0 | `a << b` | `a` shifted to the left by `b`, the sign is kept when it shifts to the right | ignored |
| 0x0a4 | `x << c` | `x` shifted to the left by `c`, the sign is kept when it shifts to the right | ignored |
| 0x0a8 | `a >> b` | `a` shifted to the right by `b`, the sign is kept | ignored |
| 0x0ac | `shrcst(x, c)` | `x` shifted to the right by `c`, the sign is kept | ignored |

```c
.pe0 { .spad = top1 << top0; }
.pe1 { .spad = top1 << 3; }
.pe2 { .spad = top1 >> top0; }
.pe3 { .spad = shrcst(top1, 3); }
```

**Explanation of the code above:**

- `pe0` shifts `top1` to the left by the words of `top0`: each word of `top0` is the amount of the shift for the word written.
- `pe1` shifts `top1` to the left by 3.
- `pe2` shifts `top1` to the right by the words of `top0`.
- `pe3` shifts `top1` to the right by 3.

**Rules:**

- `a`, `b` and `x` are buffers or `Staging` variables, and the number `c` is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)). With two operands, the second one is the amount of the shift.
- The amount is read as a signed number of 6 bits: from 0 to 31 the shift goes in the direction of the operator, from -32 to -1 it goes the other way. Only the 6 low bits count.
- `x >> n` written with a number is the opcode 0x014, where the amount `n` goes from 0 to 63 ([6.6.3](#663-lot-2-0x010-to-0x01f)). `shrcst(x, c)` reads `c` as a signed number of 6 bits.
- The shift written after one of these operations is not applied.

## 6.6.13 Lot 12: 0x0b0 to 0x0bf

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x0b0 | `a <<< b` | `a` as an unsigned number of 24 bits shifted to the left by `b`, without the sign when it shifts to the right | ignored |
| 0x0b4 | `x <<< c` | `x` as an unsigned number of 24 bits shifted to the left by `c`, without the sign when it shifts to the right | ignored |
| 0x0b8 | `a >>> b` | `a` as an unsigned number of 24 bits shifted to the right by `b`, without the sign | ignored |
| 0x0bc | `x >>> c` | `x` as an unsigned number of 24 bits shifted to the right by `c`, without the sign | ignored |

```c
.pe0 { .spad = top1 <<< top0; }
.pe1 { .spad = top1 <<< 3; }
.pe2 { .spad = top1 >>> top0; }
.pe3 { .spad = top1 >>> 3; }
```

**Explanation of the code above:**

- `pe0` shifts `top1` to the left by the words of `top0`, and `pe1` by 3. The left shift gives the same word as the one of [6.6.12](#6612-lot-11-0x0a0-to-0x0af).
- `pe2` shifts `top1` to the right by the words of `top0`, and `pe3` by 3. The bits that come in on the left are zeros, where `>>` repeats the sign.

**Rules:**

- `a`, `b` and `x` are buffers or `Staging` variables, and the number `c` is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)). With two operands, the second one is the amount of the shift.
- The amount is read as a signed number of 6 bits: from 0 to 31 the shift goes in the direction of the operator, from -32 to -1 it goes the other way. Only the 6 low bits of a word count.
- A number `c` outside the range -32 to 31 gives the error `no opcode covers this expression`.
- The shift written after one of these operations is not applied.

## 6.6.14 Lot 13: 0x0c0 to 0x0cf

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x0c0 | `a & b` | the bitwise and of `a` and `b` | ignored |
| 0x0c4 | `x & c`, `and(x, c)` | the bitwise and of `x` and `c` | ignored |
| 0x0c8 | `~(a & b)` | the complement of the bitwise and of `a` and `b` | ignored |
| 0x0cc | `~(x & c)`, `~and(x, c)` | the complement of the bitwise and of `x` and `c` | ignored |

```c
.pe0 { .spad = top0 & top1; }
.pe1 { .spad = top1 & 0xff; }
.pe2 { .spad = ~(top0 & top1); }
.pe3 { .spad = ~(top1 & 0xff); }
```

**Explanation of the code above:**

- `pe0` keeps the bits that are set in both `top0` and `top1`.
- `pe1` keeps the low byte of `top1`.
- `pe2` and `pe3` give the complement of the result of `pe0` and `pe1`, in one operation.

**Rules:**

- `a`, `b` and `x` are buffers or `Staging` variables, and the number `c` is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)). The number can be written on either side: `0xff & top1` is the same operation.
- The complement written around the and is one operation, not two ([6.2.1](operations.md#621-the-complement)).
- The shift written after one of these operations is not applied.

## 6.6.15 Lot 14: 0x0d0 to 0x0df

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x0d0 | `a \| b` | the bitwise or of `a` and `b` | ignored |
| 0x0d4 | `x \| c`, `or(x, c)` | the bitwise or of `x` and `c` | ignored |
| 0x0d8 | `~(a \| b)` | the complement of the bitwise or of `a` and `b` | ignored |
| 0x0dc | `~(x \| c)`, `~or(x, c)` | the complement of the bitwise or of `x` and `c` | ignored |

```c
.pe0 { .spad = top0 | top1; }
.pe1 { .spad = top1 | 0x80; }
.pe2 { .spad = ~(top0 | top1); }
.pe3 { .spad = ~(top1 | 0x80); }
```

**Explanation of the code above:**

- `pe0` keeps the bits that are set in `top0` or in `top1`.
- `pe1` sets the bit 7 of `top1`.
- `pe2` and `pe3` give the complement of the result of `pe0` and `pe1`, in one operation.

**Rules:**

- `a`, `b` and `x` are buffers or `Staging` variables, and the number `c` is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)). The number can be written on either side: `0x80 | top1` is the same operation.
- The complement written around the or is one operation, not two ([6.2.1](operations.md#621-the-complement)).
- The shift written after one of these operations is not applied.

## 6.6.16 Lot 15: 0x0e0 to 0x0ef

| Opcode | Written | Result | k |
|---|---|---|---|
| 0x0e0 | `a ^ b` | the bitwise exclusive or of `a` and `b` | ignored |
| 0x0e4 | `x ^ c`, `xor(x, c)` | the bitwise exclusive or of `x` and `c` | ignored |
| 0x0e8 | `~(a ^ b)` | the complement of the bitwise exclusive or of `a` and `b` | ignored |
| 0x0ec | `~(x ^ c)`, `~xor(x, c)` | the complement of the bitwise exclusive or of `x` and `c` | ignored |

```c
.pe0 { .spad = top0 ^ top1; }
.pe1 { .spad = top1 ^ 0x55; }
.pe2 { .spad = ~(top0 ^ top1); }
.pe3 { .spad = ~(top1 ^ 0x55); }
```

**Explanation of the code above:**

- `pe0` keeps the bits that are set in `top0` or in `top1` but not in both.
- `pe1` inverts the bits of `top1` that are set in the number 0x55.
- `pe2` and `pe3` give the complement of the result of `pe0` and `pe1`, in one operation.

**Rules:**

- `a`, `b` and `x` are buffers or `Staging` variables, and the number `c` is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)). The number can be written on either side: `0x55 ^ top1` is the same operation.
- The complement written around the exclusive or is one operation, not two ([6.2.1](operations.md#621-the-complement)).
- The shift written after one of these operations is not applied.

