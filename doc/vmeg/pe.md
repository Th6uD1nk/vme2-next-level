[Index](../VMEG.md) · [AGU variables](agu.md) · [Operations](operations.md)

# Processing elements

## Contents

- [5.1 The pe block](#51-the-pe-block)
- [5.2 What a block holds](#52-what-a-block-holds)
- [5.3 Operations in a pe](#53-operations-in-a-pe)
- [5.4 Remapping an opcode](#54-remapping-an-opcode)
- [5.5 Errors](#55-errors)

## 5.1 The pe block

A kernel has four processing elements, `pe0` to `pe3`. Each one is described in a block:

```c
.pe0 { .top = t; .write = w; .spad = top0 + top0; }
```

**Rules:**

- Inside the block, a dot refers to the pe of the block ([2.1](language.md#21-attributes)).
- The pe can be given by an index, `pe[p]`, where `p` is a number, an `Int` or a loop variable ([2.3](language.md#23-accesses-by-index)).
- A member can be written outside a block, with the pe in front: `.pe0.top = t;` is the same as `.pe0 { .top = t; }`.
- A pe can have several blocks, each one sets other members of the pe.

```c
.pe0 { .top = t; .spad = top0 + top0; }
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
  .spad = clamp(s, 0, 255);
}
```

**Explanation of the code above:**

- The bindings of the AGUs: `.top`, `.base` and `.write` ([4.3](agu.md#43-binding-an-agu-to-a-pe)).
- The operation of the pe, which is the member `.spad`: its result leaves on the write AGU (`.spad = clamp(s, 0, 255);`). A pe has one.
- An operation kept in a `Staging` variable, which starts with the name of the variable (`s = top1 + top2;`): the result stays in the pe and another operation can read it.
- The declaration of an `Agu` or of a `Staging` variable for this block.
- Currently not supported: `Int` and loops inside a pe block, write them around the block.

## 5.3 Operations in a pe

A pe holds at most two operations. An operation written inside another one counts for itself:

```c
Staging s;

.pe0 { .spad = top0 + top1; }
.pe1 { .spad = clamp(top0 + top1, 0, 255); }
.pe2 { s = top0 + top1; .spad = clamp(top2, 0, 255); }
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

.pe0 { .spad = clamp(mac(top0, top1), 0, 9); }
.pe1 { s = mac(top0, top1); .spad = clamp(s, 0, 9); }
.pe2 { t = top0 + top1; .spad = mac(top2, top3); }
```

`pe0` and `pe1` are accepted, `pe2` is refused.

The operations are described in [Operations](operations.md).

## 5.4 Remapping an opcode

The opcode of an operation is chosen from the way it is written ([6.2.3](operations.md#623-how-the-opcode-is-chosen)). `.remap` gives another opcode to the operations of a pe, by operator.

```c
Staging s;

.pe0 {
  .top = t;
  .write = w;
  .remap = { operator: "*", primary: 0x220 };
  .spad = top0 * top1;
}

.pe1 {
  .top = t;
  .write = w;
  .remap = { operator: "+", primary: 0x030, secondary: 0x010 };
  s = top0 + top1;
  .spad = s + top2;
}
```

**Explanation of the code above:**

- In `pe0`, the `*` that the first unit of the pe computes takes the opcode `0x220`. Without the `.remap`, it takes the opcode that the selector chooses for `*`.
- In `pe1`, a `+` takes `0x030` in the first unit (`primary`) and `0x010` in the second one (`secondary`). The first `+` of `pe1` (`s = top0 + top1;`) is in the first unit, the second one (`.spad = s + top2;`) in the second unit.
- `primary` and `secondary` are both optional, but at least one is needed. A unit that is not given keeps the opcode that the selector chooses.

**Rules:**

- `.remap` is written in a pe block. It applies to this pe only, wherever it stands in the block.
- A pe has one `.remap` per operator. Several `.remap` can be written, one for each operator.
- The operator is written between double quotes. The opcodes are numbers, or `Int` variables.
- The opcode must be in the table of `vmegc`, and it must have the operator of the `.remap`. `vmegc --ops` lists, under each opcode, the opcodes it can be remapped with ([1.5](running.md#15---ops)).
- The selector is not changed: it chooses the opcode from the way the operation is written, then the `.remap` replaces it. The registers (`A`, `B`) are those of the new opcode: a register that the new opcode has and the expression does not give is 0.
- A warning is given when the expression gives a value that the new opcode has no register for. It is not given in the other direction.
- A `.remap` lifts the rule of 5.3 that makes `mul`, `mac` and `acc` the first operation of the pe, for the unit it names.

## 5.5 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [5.1](#51-the-pe-block) | `processing element out of range (pe0 to pe3)` | a pe above 3, written `.pe4`. With an index that is computed, the message starts with the pe (`pe6: …`) |
| [5.1](#51-the-pe-block) | `pe[...] is an access by index, it takes no dot` | `.pe[1]` instead of `pe[1]` |
| [5.2](#52-what-a-block-holds) | `expected '='` | in a pe block, an operation that leaves written without `.spad =` (`top0 + top1;`), or an `Int` or a loop in the block (currently not supported) |
| [5.2](#52-what-a-block-holds) | `expected ';'` | an operation or an assignment of a pe without its `;` (`.spad = top0 + top1` or `s = top0 + 1`) |
| [5.2](#52-what-a-block-holds) | `pe0.top is already set at line N` | the same member (`.top`, `.base`, `.write`) set twice in a pe |
| [5.2](#52-what-a-block-holds) | `pe0 has two outputs on the same write, the first one is at line N` | two operations that leave in the same pe |
| [5.3](#53-operations-in-a-pe) | `a pe holds two operations at most, this pe needs 3` | more than two operations in a pe |
| [5.3](#53-operations-in-a-pe) | `mac must be the first operation of the pe` | `mul`, `mac` or `acc` (the message names the one used) after another operation of the same pe |
