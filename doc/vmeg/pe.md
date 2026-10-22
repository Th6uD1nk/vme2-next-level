[Index](../VMEG.md) · [AGU variables](agu.md) · [Operations](operations.md)

# Processing elements

## Contents

- [5.1 The pe block](#51-the-pe-block)
- [5.2 What a block holds](#52-what-a-block-holds)
- [5.3 The FUs of a pe](#53-the-fus-of-a-pe)
- [5.4 Errors](#54-errors)

## 5.1 The pe block

A kernel has four processing elements, `pe0` to `pe3`. Each one is described in a block:

```c
.pe0 { .top = t; .write = w; .top0 + top0; }
```

- Inside the block, a dot refers to the pe of the block ([2.1](language.md#21-attributes)).
- The pe can be given by an index, `pe[p]`, where `p` is a number, an `Int` or a loop variable ([2.3](language.md#23-accesses-by-index)).
- A member can be written outside a block, with the pe in front: `.pe0.top = t;` is the same as `.pe0 { .top = t; }`.
- A pe can have several blocks, each one sets other members of the pe.

```c
.pe0 { .top = t; .top0 + top0; }
.pe0 { .write = w; }
```
