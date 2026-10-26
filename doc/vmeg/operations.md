[Index](../VMEG.md) · [Processing elements](pe.md) · [Staging, routing and warnings](staging-routing.md)

# Operations

This page presents the operations currently supported. The list is not complete.

## Contents

- [6.1 Operands and results](#61-operands-and-results)
- [6.2 Operators](#62-operators)
  - [6.2.1 The complement](#621-the-complement)
  - [6.2.2 Operators with a number](#622-operators-with-a-number)
  - [6.2.3 How the opcode is chosen](#623-how-the-opcode-is-chosen)
- [6.3 Functions](#63-functions)
  - [6.3.1 clamp](#631-clamp)
  - [6.3.2 subacst](#632-subacst)
  - [6.3.3 subshr](#633-subshr)
  - [6.3.4 mac](#634-mac)
  - [6.3.5 acc](#635-acc)
  - [6.3.6 and, or and xor](#636-and-or-and-xor)
- [6.4 sat and the shifts](#64-sat-and-the-shifts)
- [6.5 Errors](#65-errors)

## 6.1 Operands and results

An operation reads buffers (`top0` to `top3`, `base0` to `base3`) or `Staging` variables ([Staging](staging-routing.md)). The numbers that some of them take, such as the bounds of `clamp`, are known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).

- The result of the operation that leaves the pe goes out on the write AGU; an operation written as `s = …;` keeps its result in the `Staging` variable `s` ([5.2](pe.md#52-what-a-block-holds)).
- An operation can wrap another one: `clamp(top0 + top1, 0, 255)`. Each operation counts in the pe ([5.3](pe.md#53-operations-in-a-pe)).

| Operation | Opcode | Reads | Result |
|---|---|---|---|
| `a + b` | `0x010` | two operands | `a + b` |
| `a + b + c` | `0x030` | two operands and a number | `(a + b) + c` |
| `x + c` | `0x024` | one operand and a number | `x + c` |
| `a - b` | `0x018` | two operands | `a - b` |
| `a - b + c`, `subacst(a, b, c)` | `0x048` | two operands and a number | `(a - b) + c` |
| `b - (a >> n)`, `subshr(a, b, n)` | `0x050` | two operands and a number | `b - (a >> n)` |
| `a * b` | `0x200` | two operands | `(a * b) >> k`, where `k` is the shift written after it ([6.4](#64-sat-and-the-shifts)) |
| `a & b` | `0x0c0` | two operands | the bitwise and |
| `a \| b` | `0x0d0` | two operands | the bitwise or |
| `a ^ b` | `0x0e0` | two operands | the bitwise exclusive or |
| `~x` | `0x0fc` | one operand | the bitwise complement of `x` |
| `~(a & b)` | `0x0c8` | two operands | the complement of the bitwise and, one operation |
| `~(a \| b)` | `0x0d8` | two operands | the complement of the bitwise or, one operation |
| `x & c`, `and(x, c)` | `0x0c4` | one operand and a number | `x & c` |
| `x \| c`, `or(x, c)` | `0x0d4` | one operand and a number | `x \| c` |
| `x ^ c`, `xor(x, c)` | `0x0e4` | one operand and a number | `x ^ c` |
| `~(x & c)`, `~and(x, c)` | `0x0cc` | one operand and a number | the complement of the bitwise and, one operation |
| `~(x \| c)`, `~or(x, c)` | `0x0dc` | one operand and a number | the complement of the bitwise or, one operation |
| `~(x ^ c)`, `~xor(x, c)` | `0x0ec` | one operand and a number | the complement of the bitwise exclusive or, one operation |
| `clamp(x, low, high)` | `0x07c` | one operand and two numbers | `x` limited between `low` and `high` |
| `mac(a, b)` | `0x240` | two operands | a running inner product |
| `acc(x)` | `0x250` | one operand | a running sum |

- `mul`, `mac` and `acc` must be the first operation of the pe ([5.3](pe.md#53-operations-in-a-pe)).
- `acc` reads a buffer or a `Staging` variable only. `clamp`, `~x` and the operations with `x` also read an operation.
- An operation with two writings gives the same result with either one.

## 6.2 Operators

The operators `+`, `-`, `*`, `&`, `|` and `^` take two operands, each one a buffer or a `Staging` variable. Another operation is refused: keep the first result in a `Staging` variable, or wrap it in a function such as `clamp`. A number is written in the forms of [6.2.2](#622-operators-with-a-number).

```c
.pe0 { .spad = top0 + base0; }
.pe1 { .spad = top1 - base1; }
.pe2 { .spad = top2 * base2 >> 8; }
.pe3 { .spad = top3 & base3; }
```

**Explanation of the code above:**

- `a + b` adds the two operands.
- `a - b` subtracts `b` from `a`.
- `a * b` multiplies them. A shift written after the product, `a * b >> 8`, is applied to the product ([6.4](#64-sat-and-the-shifts)).
- `a & b` is the bitwise and.

The bitwise or and exclusive or are written `|` and `^`:

```c
.pe0 { .spad = top0 | base0; }
.pe1 { .spad = top1 ^ base1; }
```

**Explanation of the code above:**

- `a | b` is the bitwise or of the two operands.
- `a ^ b` is the bitwise exclusive or of the two operands.

An operand can be the `Staging` variable of another operation:

```c
Staging s;

.pe0 { s = top0 + top1; .spad = top2 - s; }
```

### 6.2.1 The complement

`~` complements the bits of what follows it: a buffer, a `Staging` variable, or an operation between parentheses. Between numbers, `~` is the plain C complement ([2.5](language.md#25-expressions)).

```c
.pe0 { .spad = ~top0; }
.pe1 { .spad = ~(top1 & base1); }
.pe2 { .spad = ~(top2 + base2); }
.pe3 { .spad = ~(top3 ^ base3); }
```

**Explanation of the code above:**

- `~top0` is one operation: the complement of a buffer.
- `~(top1 & base1)` is **one** operation: the hardware has a single operation for the complement of an and.
- `~(top2 + base2)` and `~(top3 ^ base3)` are **two** operations: the sum or the exclusive or, then the complement. The hardware has no single operation for them.

**Rules:**

- `~` is one operation when its content is written as one of the operations of the table below, with no `sat` and no shift. Otherwise it is a second operation, applied to the result of its content.
- A `sat` or a shift belongs to the operation it wraps: `~sat(a & b, 7)` is two operations.
- The operations that the hardware combines with a complement:

| Written | Opcode |
|---|---|
| `~(a & b)` | `0x0c8` |
| `~(a \| b)` | `0x0d8` |
| `~(x & c)`, `~and(x, c)` | `0x0cc` |
| `~(x \| c)`, `~or(x, c)` | `0x0dc` |
| `~(x ^ c)`, `~xor(x, c)` | `0x0ec` |

`x` can be an operation: `~and(top0 + top1, 255)` is two operations, the sum and then the complement combined with the and. A pe holds two operations at most ([5.3](pe.md#53-operations-in-a-pe)), so `~and(clamp(top0 + top1, 0, 9), 255)` needs three and is refused.

### 6.2.2 Operators with a number

Some operators take a number besides their operands. The operation holds the number in a register of the pe.

```c
.pe0 { .spad = top0 + base0 + 5; }
.pe1 { .spad = top1 - base1 + 3; }
.pe2 { .spad = base2 - (top2 >> 2); }
.pe3 { .spad = (top3 + base3) & 0xff; }
```

**Explanation of the code above:**

- `top0 + base0 + 5` adds the number to the sum: `(top0 + base0) + 5`.
- `top1 - base1 + 3` adds the number to the difference.
- `base2 - (top2 >> 2)` subtracts `top2` shifted to the right by 2 from `base2`. The shift cannot be negative.
- `(top3 + base3) & 0xff` keeps the low byte of the sum. `pe3` holds two operations: the sum, then the and.

| Written | Also written as a function |
|---|---|
| `a + b + c` | |
| `x + c` | |
| `a - b + c` | `subacst(a, b, c)` ([6.3.2](#632-subacst)) |
| `b - (a >> n)` | `subshr(a, b, n)` ([6.3.3](#633-subshr)) |
| `x & c` | `and(x, c)` ([6.3.6](#636-and-or-and-xor)) |
| `x \| c` | `or(x, c)` |
| `x ^ c` | `xor(x, c)` |
| `~(x & c)` | `~and(x, c)` ([6.2.1](#621-the-complement)) |
| `~(x \| c)` | `~or(x, c)` |
| `~(x ^ c)` | `~xor(x, c)` |

**Rules:**

- The number is known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- `x` is a buffer, a `Staging` variable or an operation. `a` and `b` are buffers or `Staging` variables.
- The number can be written on either side of `+`, `&`, `|` and `^`: `255 & top1` is the same as `top1 & 255`, and `5 + (top0 + base0)` the same as `(top0 + base0) + 5`.
- The grouping is the one written: `5 + top0 + base0` is `(5 + top0) + base0` and is refused. Write `5 + (top0 + base0)`.
- A number with a single operand is covered for the sum only: `top0 + 1` is `x + c`. `top0 * 5` and `top0 - 1` are refused, no operation of the table takes a single operand and a number for them.

### 6.2.3 How the opcode is chosen

An expression can be covered by more than one opcode. `vmegc` reads what is written and takes the opcode that covers all of it with the fewest operands and numbers. The operations inside it count too.

| Written | Opcode | Why |
|---|---|---|
| `a + b` | `0x010` | the sum of two operands, nothing else to give |
| `a + 1` | `0x024` | the opcode that takes one operand and a number |
| `a + b + 5` | `0x030` | one operation, instead of the sum and then the number |
| `~(a & b)` | `0x0c8` | one operation, instead of the and and then the complement |

**Rules:**

- A number that is not written is 0. The opcode `0x030`, which takes a number with the sum, can do `a + b` with its number at 0.
- With two opcodes at the same count, the first one in the list given by `--ops` ([1.5](running.md#15---ops)) is taken.
- The option `--compat fat` ([1.6](running.md#16---compat)) leaves out the opcodes that `--ops` marks `not portable`. `a + b` then uses `0x030`, with its number at 0.
- The opcodes chosen for a kernel are listed by `--list --kernel` ([1.4](running.md#14---list)).

## 6.3 Functions

A function is written like an operator, with its operands between parentheses. The numbers it takes are known at compile time.

### 6.3.1 clamp

`clamp(x, low, high)` limits `x` between `low` and `high`. `x` is a buffer, a `Staging` variable or an operation.

```c
Staging s;

.pe0 { .spad = clamp(top0, 0, 255); }
.pe1 { .spad = clamp(top0 + base0, 0, 255); }
.pe2 { s = top0 + base0; .spad = clamp(s, -5, 5); }
```

### 6.3.2 subacst

`subacst(a, b, c)` computes `(a - b) + c`. `a` and `b` are buffers or `Staging` variables, `c` is a number. It can also be written as an expression, `a - b + c` ([6.2.2](#622-operators-with-a-number)).

```c
.pe0 { .spad = subacst(top0, base0, 16); }
```

### 6.3.3 subshr

`subshr(a, b, n)` computes `b - (a >> n)`. `a` and `b` are buffers or `Staging` variables, `n` is a number that cannot be negative. It can also be written as an expression, `b - (a >> n)` ([6.2.2](#622-operators-with-a-number)).

```c
.pe0 { .spad = subshr(top0, base0, 2); }
```

The sign of the result and the place of `n` are not yet verified on the hardware.

### 6.3.4 mac

`mac(a, b)` is a running inner product: at each word it adds `a * b` to the sum of the previous words. The result is a ramp of partial sums, and the result of a product of 4 elements is the 4th word of each group of 4. `a` and `b` are buffers or `Staging` variables.

```c
Staging s;

.pe0 { s = mac(top0, top1); }
```

**Rules:**

- A shift written after it, `mac(top0, top1) >> 4`, is applied to the result ([6.4](#64-sat-and-the-shifts)).
- It must be the first operation of the pe ([5.3](pe.md#53-operations-in-a-pe)).

### 6.3.5 acc

`acc(x)` is a running sum: each word adds `x` to the previous ones. For the words 1 2 3 4 it gives 1 3 6 10. `x` is a buffer or a `Staging` variable.

```c
Staging s;

.pe0 { s = mac(top0, top1); }
.pe1 { .spad = acc(s); }
```

**Rules:**

- It must be the first operation of the pe ([5.3](pe.md#53-operations-in-a-pe)).
- The `mat4x4` sample reads the 4th word of each group of a `mac`, with `cyc: auto - 1` ([4.2.4](agu.md#424-write-agus)).

### 6.3.6 and, or and xor

`and(x, c)`, `or(x, c)` and `xor(x, c)` give the bitwise and, or and exclusive or of `x` and a number `c`. `x` is a buffer, a `Staging` variable or an operation, `c` is a number. They are also written as the operators with a number, `x & c`, `x | c` and `x ^ c` ([6.2.2](#622-operators-with-a-number)).

```c
.pe0 { .spad = and(top0, 0xff); }
.pe1 { .spad = or(top1, 0x80); }
.pe2 { .spad = xor(top2, 0x55); }
.pe3 { .spad = and(top3 + base3, 0xff); }
```

**Explanation of the code above:**

- `pe0` keeps the low byte of `top0`.
- `pe1` sets the bit 7 of `top1`.
- `pe2` inverts the bits of `top2` that are set in `0x55`.
- `pe3` holds two operations: the sum, then the and with `0xff`.

**Rules:**

- The number is known at compile time, like the numbers of the other functions.
- The complement of these functions is one operation: `~and(x, c)`, `~or(x, c)` and `~xor(x, c)`, or `~(x & c)`, `~(x | c)` and `~(x ^ c)` ([6.2.1](#621-the-complement)).

## 6.4 sat and the shifts

`sat` and the shifts are not operations of their own: they set the saturation and the shift of the operation they wrap.

```c
.pe0 { .spad = sat(top0 + base0, 7); }
.pe1 { .spad = top1 + base1 >> 2; }
.pe2 { .spad = sat(top2 + base2, 7) >> 2; }
.pe3 { .spad = top3 + base3 << 4; }
```

| Form | Meaning |
|---|---|
| `sat(op, bits)` | limits the result of `op` to `bits` bits, signed: from `-2^(bits-1)` to `2^(bits-1)-1`. `bits` is from 0 to 31, and 0 means no saturation |
| `op >> n` | shifts the result of `op` to the right by `n`, from 0 to 63 |
| `op << n` | the rotary shift by `n`, from 0 to 63 |

- `sat` and the shifts wrap an operation: `sat(top0, 7)` and `top0 >> 2` are refused.
- An operation takes one `sat` and one shift. When both are used, the shift goes after the `sat`: `sat(x, 7) >> 2`.
- A shift after a product, `a * b >> 8`, is the shift of the product ([6.2](#62-operators)).
- Currently not supported: the signed zero option.

## 6.5 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [6.1](#61-operands-and-results) | `an operand must be a buffer (top0 to top3, base0 to base3) or a Staging variable` | an operand of a function that is a number or another operation, as in `mac(top0 + base0, base1)` or `subacst(5, base0, 1)` |
| [6.2.3](#623-how-the-opcode-is-chosen) | `no opcode covers this expression` | an expression with operators that no opcode covers: an operand that is another operation, as in `top0 + base0 + top1`, or a number with a single operand outside the sum, as in `top0 * 5` or `top0 - 1` ([6.2.2](#622-operators-with-a-number)) |
| [6.1](#61-operands-and-results) | `the Staging variable 's' is read before it is set` | a `Staging` variable read before the statement that sets it |
| [6.1](#61-operands-and-results) | `clamp low must be a number` | a bound, a constant or a shift that is not a number known at compile time. The message names it: `clamp high`, `subacst c`, `subshr n`, `and c`, `or c`, `xor c`, `sat bits`, `the shift` |
| [6.2](#62-operators) | `expected ';'` | an operator that is not supported, such as `/` |
| [6.2](#62-operators) | `an operation is expected (an addition, sat or clamp)` | a statement that leaves, with a buffer alone instead of an operation |
| [6.3.1](#631-clamp) | `clamp takes 3 arguments (x, low, high)` | `clamp` with another number of arguments |
| [6.3.2](#632-subacst) | `subacst takes 3 arguments (a, b, c)` | `subacst` with another number of arguments |
| [6.3.3](#633-subshr) | `subshr takes 3 arguments (a, b, n)` | `subshr` with another number of arguments |
| [6.3.3](#633-subshr) | `subshr n cannot be less than 0` | a negative `n` |
| [6.3.4](#634-mac) | `mac takes 2 arguments (a, b)` | `mac` with another number of arguments |
| [6.3.5](#635-acc) | `acc takes 1 argument (x)` | `acc` with another number of arguments |
| [6.3.5](#635-acc) | `acc takes a buffer or a Staging variable` | an operation inside `acc` |
| [6.3.6](#636-and-or-and-xor) | `and takes 2 arguments (x, c)` | `and`, `or` or `xor` with another number of arguments (the message names the one used) |
| [6.3](#63-functions) | `unknown operation 'foo' (sat, subacst, subshr, and, or, xor, clamp, mac, acc)` | a function that does not exist |
| [6.4](#64-sat-and-the-shifts) | `sat takes 2 arguments (value, bits)` | `sat` with another number of arguments |
| [6.4](#64-sat-and-the-shifts) | `sat bits out of range (0 to 31)` | `bits` above 31 |
| [6.4](#64-sat-and-the-shifts) | `sat must wrap an operation` | `sat` on a buffer or a `Staging` variable |
| [6.4](#64-sat-and-the-shifts) | `an operation takes only one sat` | two `sat` on the same operation |
| [6.4](#64-sat-and-the-shifts) | `the shift goes after the sat: sat(x, n) >> k` | a shift inside the `sat` |
| [6.4](#64-sat-and-the-shifts) | `a shift must wrap an operation` | `>>` or `<<` on a buffer or a `Staging` variable |
| [6.4](#64-sat-and-the-shifts) | `the shift must be 0 to 63` | a shift above 63 |
| [6.4](#64-sat-and-the-shifts) | `an operation takes only one shift` | two shifts on the same operation |
