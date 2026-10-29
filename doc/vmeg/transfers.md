[Index](../VMEG.md) · [Arrays](arrays.md) · [Calling a kernel](calling.md)

# Transfers

## Contents

- [9.1 The Transfer variable](#91-the-transfer-variable)
- [9.2 The extended mode](#92-the-extended-mode)
  - [9.2.1 The fields](#921-the-fields)
  - [9.2.2 Where each field applies](#922-where-each-field-applies)
  - [9.2.3 The group](#923-the-group)
  - [9.2.4 step: 0](#924-step-0)
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

### 9.2.2 Where each field applies

The memory is the array of the `Transfer`, the scratchpad is the buffers of the VME. `step` is on the memory side, in bytes. `gap` and `group` are on the scratchpad side, in words.

```c
Transfer(Words) spread = { memory: source, count: 15, step: 4, group: { size: 3, outer: 16, inner: 1 } };
Transfer(Words) picked = { memory: result, count: 15, gap: 3, step: 4 };
```

| Field | Side | Unit |
|---|---|---|
| `step` | memory | bytes |
| `gap` | scratchpad | words |
| `group` | scratchpad | words |

**Explanation of the code above:**

- `spread` is a load of 16 words. The memory is read one word after the other (`step: 4`). The scratchpad receives them in groups of 4 words, one after the other, and a group starts 16 words after the previous one.
- `picked` is a store of 16 words. The scratchpad is read one word out of 4 (`gap: 3` leaves 3 words between two), and the memory is written one word after the other (`step: 4`).

**Rules:**

- `step` is the same on a load and on a store: it moves in the memory, whatever the direction.
- The `mat4x4-mul-batch` sample loads a batch of vectors with a group and stores its results with a gap.

### 9.2.3 The group

```c
Transfer(Words) split = { memory: source, count: 15, step: 4, group: { size: 3, outer: 0x800, inner: 1 } };
```

| Field | Meaning |
|---|---|
| `size` | the number of words of a group, minus one |
| `outer` | the distance between the start of a group and the start of the next one, in the scratchpad |
| `inner` | the distance between two words of a group, in the scratchpad |

**Explanation of the code above:**

- `split` is a load of 16 words (`count: 15`), read from the memory one word after the other.
- The words fill the groups one after the other: a group takes 4 words (`size: 3`), laid next to each other (`inner: 1`).
- A group starts 0x800 words after the previous one (`outer: 0x800`), that is in the next buffer of the VME: the 4 groups are in 4 different buffers.

**Rules:**

- The groups are on the scratchpad side, in words.
- The groups can overlap, when `outer` is smaller than the size of a group: the last word written in a place is the one that stays.
- The `mat4x4-mul-host-batching` sample loads a matrix in several buffers this way, and the `fft-dif-16-point-radix-2` sample uses overlapping groups.

### 9.2.4 step: 0

```c
Transfer(Words) repeated = { memory: source, count: 1, gap: 7, step: 0, group: { size: 3, outer: 2, inner: 1 } };
```

With `step: 0`, `count` and `gap` do not have their meaning of [9.2.1](#921-the-fields):

| Field | Meaning with `step: 0` |
|---|---|
| `count` | the number of repetitions of the transfer, minus one |
| `gap` | the number of words of one repetition, minus one |

**Explanation of the code above:**

- `count: 1` repeats the transfer once: it runs twice, one after the other.
- `gap: 7` makes a repetition read 8 words of the array, from the first word.
- The memory starts again at the first word of the array for each repetition.
- The 16 words of the two repetitions form one stream. It fills the groups one after the other: `group` is windows of 4 words (`size: 3`) laid every 2 words (`outer: 2`) in the scratchpad. Where two windows overlap, the last word written is the one that stays.

**Rules:**

- A repetition reads `gap + 1` words of the array, so the array has to be at least that long.

## 9.3 .load and .store

A `.load` copies an array to the buffers of the VME. A `.store` copies a buffer back to an array. Both are written in a kernel, after the `Transfer` that they use.

```c
volatile Buffer input[16];
volatile Buffer result[16];

.kernel k direct {
  Transfer in = { memory: input, count: 15 };
  Transfer out = { memory: result, count: 15 };
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; .top1 = 0; } }
  .store { .transfer = out; .scope = global; .offsets { .base0 = 0; } }
}
```

| Attribute | Value |
|---|---|
| `.transfer` | the `Transfer` that describes the copy |
| `.scope` | `global` or `local`, the scope of the array ([8](arrays.md)). `local` when it is left out |
| `.offsets` | the buffers and the place in each of them ([9.4](#94-the-offsets)) |

**Explanation of the code above:**

- `.load` copies `input` with the `Transfer` `in`, once into the buffer `top0` and once into the buffer `top1`.
- `.store` copies the buffer `base0` into `result` with the `Transfer` `out`.
- `.scope = global` says that `input` and `result` are global arrays ([8.2](arrays.md#82-global-arrays)).

**Rules:**

- `.transfer` is needed. The `Transfer` is declared before, in the kernel.
- Each attribute is written once in a `.load` or a `.store`.
- A buffer is written once in `.offsets`. The copy is done once for each buffer that `.offsets` lists.
- Without `.offsets` the copy uses the scratchpad from its offset 0.
- Several `.load` and `.store` can use the same `Transfer`.
- The copies are done when the kernel is called: the `.load` first and the `.store` last ([10.5](calling.md#105-uploads-and-downloads-around-the-run)).
