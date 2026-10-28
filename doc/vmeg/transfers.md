[Index](../VMEG.md) · [Arrays](arrays.md) · [Calling a kernel](calling.md)

# Transfers

## Contents

- [9.1 The Transfer variable](#91-the-transfer-variable)
- [9.2 The extended mode](#92-the-extended-mode)
  - [9.2.1 The fields](#921-the-fields)
- [9.3 .load and .store](#93-load-and-store)
- [9.4 The offsets](#94-the-offsets)
- [9.5 Unknown names in a Transfer](#95-unknown-names-in-a-transfer)
- [9.6 Errors](#96-errors)

## 9.1 The Transfer variable

A `Transfer` variable describes a copy between an array ([8](arrays.md)) and the buffers of the VME. It is declared in the kernel, before the `.load` or the `.store` that uses it ([9.3](#93-load-and-store)).

```c
Transfer in = { type: words, mode: basic, memory: input, count: 15 };
```

**Explanation of the code above:**

- `type: words` says that the elements are words. The other values are `halves` and `bytes`.
- `mode: basic` is one run of consecutive words. The other mode is `extended` ([9.2](#92-the-extended-mode)).
- `memory: input` is the array that is copied.
- `count: 15` is the number of words minus one: this `Transfer` copies 16 words.

**Rules:**

- `type`, `mode` and `memory` are needed. In the basic mode `count` is needed too.
- The numbers cannot be negative. They are numbers known at compile time, or a name that is not known yet ([9.5](#95-unknown-names-in-a-transfer)).
- The name of a `Transfer` is declared once, whatever the type of the variables ([2.2.2](language.md#222-names)).
- Currently not supported: the `.load` and the `.store` of a `Transfer` of `halves` or of `bytes`. Only `words` are generated.

## 9.2 The extended mode

The extended mode turns on the AGUs of the DMAC. The fields `dims`, `step` and `group` set them, and replace the `count` of the basic mode, which is one run of consecutive words.

### 9.2.1 The fields

```c
Transfer in = { type: words, mode: extended, memory: input, dims: { count: 15, gap: 0 }, step: 4, group: { size: 3, outer: 16, inner: 1 } };
```

| Field | Meaning | Unit |
|---|---|---|
| `dims.count` | the number of words, minus one | words |
| `dims.gap` | the words left between two words, in the scratchpad | words |
| `step` | the distance between two words, in the memory | bytes |
| `group.size` | the number of words of a group, minus one | words |
| `group.outer` | the distance between two groups, in the scratchpad | words |
| `group.inner` | the distance between two words of a group, in the scratchpad | words |

**Explanation of the code above:**

- `mode: extended` replaces the `count` of the basic mode by the fields of the table.
- `dims: { count: 15, gap: 0 }` is 16 words, with no word left between two.
- `step: 4` goes from one word of the memory to the next one: 4 bytes.
- `group: { size: 3, outer: 16, inner: 1 }` is groups of 4 words.

**Rules:**

- The values are the **real values of the registers**: nothing is added or removed, `count: 15` is 16 words.
- `count` is not a field of the extended mode: the number of words is `dims.count`.
- `dims` takes `count` and `gap` together. `group` takes `size`, and `outer` with `inner` together.
- A field that is left out is not written by `vmegc`.
- The same `Transfer` is used by a `.load` and by a `.store` ([9.3](#93-load-and-store)).
