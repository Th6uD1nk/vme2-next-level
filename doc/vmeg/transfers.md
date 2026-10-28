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
Transfer in = { memory: input, count: 15 };
Transfer(Words) spread = { memory: input, count: 15, step: 4 };
```

| Type | Copy | Fields |
|---|---|---|
| `Transfer` | one run of consecutive words | `memory`, `count` |
| `Transfer(Words)` | words, with the AGUs of the DMAC on ([9.2](#92-the-extended-mode)) | `memory`, `count`, `gap`, `step`, `group` |
| `Transfer(Halves)` | halves (16 bits), with the AGUs of the DMAC on | same as `Transfer(Words)` |
| `Transfer(Bytes)` | bytes (8 bits), with the AGUs of the DMAC on | same as `Transfer(Words)` |

**Explanation of the code above:**

- `Transfer in` copies a run of consecutive words.
- `Transfer(Words) spread` turns on the AGUs of the DMAC: it takes the fields `gap`, `step` and `group` too.
- `memory: input` is the array that is copied.
- `count: 15` is the number of words minus one: both `Transfer` copy 16 words.

**Rules:**

- `memory` and `count` are needed, whatever the type.
- Each type has its own fields: a field that is not in the type is refused ([9.6](#96-errors)).
- The numbers cannot be negative. They are numbers known at compile time, or a name that is not known yet ([9.5](#95-unknown-names-in-a-transfer)).
- The name of a `Transfer` is declared once, whatever the type of the variables ([2.2.2](language.md#222-names)).
- Currently not supported: the `.load` and the `.store` of a `Transfer(Halves)` and of a `Transfer(Bytes)`. The types are read, nothing is generated.

## 9.2 The extended mode

The extended mode is the type `Transfer(Words)` (and `Transfer(Halves)`, `Transfer(Bytes)`, [9.1](#91-the-transfer-variable)). It turns on the AGUs of the DMAC, and the fields `gap`, `step` and `group` set them.

### 9.2.1 The fields

```c
Transfer(Words) in = { memory: input, count: 15, gap: 0, step: 4, group: { size: 3, outer: 16, inner: 1 } };
```

| Field | Meaning | Unit |
|---|---|---|
| `count` | the number of words, minus one | words |
| `gap` | the words left between two words, in the scratchpad | words |
| `step` | the distance between two words, in the memory | bytes |
| `group.size` | the number of words of a group, minus one | words |
| `group.outer` | the distance between two groups, in the scratchpad | words |
| `group.inner` | the distance between two words of a group, in the scratchpad | words |

**Explanation of the code above:**

- `count: 15` is 16 words, as in the basic type.
- `gap: 0` leaves no word between two words.
- `step: 4` goes from one word of the memory to the next one: 4 bytes.
- `group: { size: 3, outer: 16, inner: 1 }` is groups of 4 words.

**Rules:**

- The values are the **real values of the registers**: nothing is added or removed, `count: 15` is 16 words.
- `memory` and `count` are needed. `gap`, `step` and `group` can be left out, and `vmegc` does not write what is left out.
- `group` takes `size`, and `outer` with `inner` together.
- The same `Transfer` is used by a `.load` and by a `.store` ([9.3](#93-load-and-store)).
