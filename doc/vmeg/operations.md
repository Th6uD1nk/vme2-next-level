[Index](../VMEG.md) · [Processing elements](pe.md) · [Staging, routing and warnings](staging-routing.md)

# Operations

This page presents the operations currently supported. The list is not complete.

## Contents

- [6.1 Operands and results](#61-operands-and-results)
- [6.2 Operators](#62-operators)
- [6.3 Functions](#63-functions)
  - [6.3.1 clamp](#631-clamp)
  - [6.3.2 subacst](#632-subacst)
  - [6.3.3 subshr](#633-subshr)
  - [6.3.4 mac](#634-mac)
  - [6.3.5 acc](#635-acc)
- [6.4 sat and the shifts](#64-sat-and-the-shifts)
- [6.5 Errors](#65-errors)

## 6.1 Operands and results

An operation reads buffers (`top0` to `top3`, `base0` to `base3`) or `Staging` variables ([Staging](staging-routing.md)). The numbers that some of them take, such as the bounds of `clamp`, are known at compile time ([2.6](language.md#26-numbers-macros-and-unknown-names)).

- The result of the operation that leaves the pe goes out on the write AGU; an operation written as `s = …;` keeps its result in the `Staging` variable `s` ([5.2](pe.md#52-what-a-block-holds)).
- An operation can wrap another one: `clamp(top0 + top1, 0, 255)`. Each operation counts in the pe ([5.3](pe.md#53-operations-in-a-pe)).

| Operation | Opcode | Reads | Result |
|---|---|---|---|
| `a + b` | `0x010` | two operands | `a + b` |
| `a - b` | `0x018` | two operands | `a - b` |
| `subacst(a, b, c)` | `0x048` | two operands and a number | `(a - b) + c` |
| `subshr(a, b, n)` | `0x050` | two operands and a number | `b - (a >> n)` |
| `a * b` | `0x200` | two operands | `(a * b) >> k`, where `k` is the shift written after it ([6.4](#64-sat-and-the-shifts)) |
| `a & b` | `0x0c0` | two operands | the bitwise and |
| `clamp(x, low, high)` | `0x07c` | one operand and two numbers | `x` limited between `low` and `high` |
| `mac(a, b)` | `0x240` | two operands | a running inner product |
| `acc(x)` | `0x250` | one operand | a running sum |

- `mul`, `mac` and `acc` cannot be the output operation of a pe that holds more than one operation ([5.3](pe.md#53-operations-in-a-pe)).
- `acc` reads a buffer or a `Staging` variable only. `clamp` also reads an operation.

## 6.2 Operators

The operators `+`, `-`, `*` and `&` take two operands, each one a buffer or a `Staging` variable. A number or another operation is refused: keep the first result in a `Staging` variable, or wrap it in a function such as `clamp`.

```c
.pe0 { .top0 + base0; }
.pe1 { .top1 - base1; }
.pe2 { .top2 * base2 >> 8; }
.pe3 { .top3 & base3; }
```

- `a + b` adds the two operands.
- `a - b` subtracts `b` from `a`.
- `a * b` multiplies them. A shift written after the product, `a * b >> 8`, is applied to the product ([6.4](#64-sat-and-the-shifts)).
- `a & b` is the bitwise and.

An operand can be the `Staging` variable of another operation:

```c
Staging s;

.pe0 { s = top0 + top1; .top2 - s; }
```

## 6.3 Functions

A function is written like an operator, with its operands between parentheses. The numbers it takes are known at compile time.

### 6.3.1 clamp

`clamp(x, low, high)` limits `x` between `low` and `high`. `x` is a buffer, a `Staging` variable or an operation.

```c
Staging s;

.pe0 { .clamp(top0, 0, 255); }
.pe1 { .clamp(top0 + base0, 0, 255); }
.pe2 { s = top0 + base0; .clamp(s, -5, 5); }
```

### 6.3.2 subacst

`subacst(a, b, c)` computes `(a - b) + c`. `a` and `b` are buffers or `Staging` variables, `c` is a number.

```c
.pe0 { .subacst(top0, base0, 16); }
```

### 6.3.3 subshr

`subshr(a, b, n)` computes `b - (a >> n)`. `a` and `b` are buffers or `Staging` variables, `n` is a number that cannot be negative.

```c
.pe0 { .subshr(top0, base0, 2); }
```

The sign of the result and the place of `n` are not yet verified on the hardware.
