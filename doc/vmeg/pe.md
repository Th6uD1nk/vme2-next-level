[Index](../VMEG.md) · [AGU variables](agu.md) · [Operations](operations.md)

# Processing elements

## Contents

- [5.1 The pe block](#51-the-pe-block)
- [5.2 What a block holds](#52-what-a-block-holds)
- [5.3 Operations in a pe](#53-operations-in-a-pe)
- [5.4 Errors](#54-errors)

## 5.1 The pe block

A kernel has four processing elements, `pe0` to `pe3`. Each one is described in a block:

```c
.pe0 { .top = t; .write = w; .top0 + top0; }
```

**Rules:**

- Inside the block, a dot refers to the pe of the block ([2.1](language.md#21-attributes)).
- The pe can be given by an index, `pe[p]`, where `p` is a number, an `Int` or a loop variable ([2.3](language.md#23-accesses-by-index)).
- A member can be written outside a block, with the pe in front: `.pe0.top = t;` is the same as `.pe0 { .top = t; }`.
- A pe can have several blocks, each one sets other members of the pe.

```c
.pe0 { .top = t; .top0 + top0; }
.pe0 { .write = w; }
```

## 5.2 What a block holds

```c
Staging s;

.pe0 {
  Agu t = { count: 15 };
  .top = t;
  .write = { count: 15 };
  s = top1 + top2;
  .clamp(s, 0, 255);
}
```

**Explanation of the code above:**

- The bindings of the AGUs: `.top`, `.base` and `.write` ([4.3](agu.md#43-binding-an-agu-to-a-pe)).
- The operation of the pe, which starts with a dot: its result leaves on the write AGU (`.clamp(s, 0, 255);`). A pe has one.
- An operation kept in a `Staging` variable, which starts with the name of the variable (`s = top1 + top2;`): the result stays in the pe and another operation can read it.
- The declaration of an `Agu` or of a `Staging` variable for this block.
- Currently not supported: `Int` and loops inside a pe block, write them around the block.

## 5.3 Operations in a pe

A pe holds at most two operations. An operation written inside another one counts for itself:

```c
Staging s;

.pe0 { .top0 + top1; }
.pe1 { .clamp(top0 + top1, 0, 255); }
.pe2 { s = top0 + top1; .clamp(top2, 0, 255); }
```

**Explanation of the code above:**

- `pe0` holds one operation.
- `pe1` holds two: the addition, inside the `clamp`.
- `pe2` holds two: the one kept in `s`, and the one that leaves.

**Rules:**

- A third operation in the same pe is an error.
- `sat` and the shifts `>>` and `<<` are not operations: they set the saturation and the shift of the operation they wrap, and are not counted. Currently not supported: the signed zero option.
- `~` is one operation when it combines with what it complements, as in `~(a & b)`, and two operations otherwise, as in `~(a + b)` ([6.2.1](operations.md#621-the-complement)).
- `mul`, `mac` and `acc` must be the first operation of the pe: the innermost one, or the first one written. Written after another operation of the pe, they are refused.

```c
Staging s, t;

.pe0 { .clamp(mac(top0, top1), 0, 9); }
.pe1 { s = mac(top0, top1); .clamp(s, 0, 9); }
.pe2 { t = top0 + top1; .mac(top2, top3); }
```

`pe0` and `pe1` are accepted, `pe2` is refused.

The operations are described in [Operations](operations.md).

## 5.4 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [5.1](#51-the-pe-block) | `processing element out of range (pe0 to pe3)` | a pe above 3, written `.pe4`. With an index that is computed, the message starts with the pe (`pe6: …`) |
| [5.1](#51-the-pe-block) | `pe[...] is an access by index, it takes no dot` | `.pe[1]` instead of `pe[1]` |
| [5.2](#52-what-a-block-holds) | `expected '='` | in a pe block, an operation that leaves written without its dot (`top0 + top1;`), or an `Int` or a loop in the block (currently not supported) |
| [5.2](#52-what-a-block-holds) | `pe0.top is already set at line N` | the same member (`.top`, `.base`, `.write`) set twice in a pe |
| [5.2](#52-what-a-block-holds) | `pe0 has two outputs on the same write, the first one is at line N` | two operations that leave in the same pe |
| [5.3](#53-operations-in-a-pe) | `a pe holds two operations at most, this pe needs 3` | more than two operations in a pe |
| [5.3](#53-operations-in-a-pe) | `mac must be the first operation of the pe` | `mul`, `mac` or `acc` (the message names the one used) after another operation of the same pe |
