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
- `memory` and `count` are needed. `gap` is 0 when it is left out. `step` and `group` can be left out too, and `vmegc` does not write them.
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

## 9.4 The offsets

`.offsets` says in which buffers of the VME a `.load` or a `.store` copies, and from which word of each buffer.

```c
.kernel k direct {
  Transfer in = { memory: input, count: 15 };
  Int stride = 4;
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; .top1 = 4; .base2 = 0x10; } }
  for i in 0..3 {
    .load { .transfer = in; .scope = global; .offsets { base[i] = i * stride; } }
  }
}
```

| Entry | Meaning |
|---|---|
| `.top0 = n;` to `.top3 = n;` | the buffer `top0` to `top3`, from the word `n` |
| `.base0 = n;` to `.base3 = n;` | the buffer `base0` to `base3`, from the word `n` |
| `top[i] = n;`, `base[i] = n;` | the same, with the number of the buffer in `i` |

**Explanation of the code above:**

- The first `.load` copies `input` three times: into `top0` from its first word, into `top1` from its word 4, and into `base2` from its word 16.
- `base[i] = i * stride;` is in a `for` ([2.7](language.md#27-loops)), so it is written once for each value of `i`: the second `.load` copies `input` into `base0` from the word 0, into `base1` from the word 4, into `base2` from the word 8 and into `base3` from the word 12.

**Rules:**

- An offset is a number of words, counted from the start of the buffer.
- `i` in `top[i]` and `base[i]` is a number or a loop variable, from 0 to 3.
- The value is a number, an `Int`, an expression ([2.5](language.md#25-expressions)) or a name that `vmegc` does not know ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- Currently not supported: a negative offset.
- `.offsets` is the same in a `.load` and in a `.store`: in a `.store` it says where the copy starts in the buffer.

## 9.5 Unknown names in a Transfer

The numbers of a `Transfer` (`count`, `gap`, `step` and the fields of `group`) can use a name that `vmegc` does not know: a macro of a header, a variable of the function that calls the kernel ([2.6](language.md#26-numbers-macros-and-unknown-names)).

```c
volatile Buffer input[64];

.kernel k direct {
  Transfer(Words) in = { memory: input, count: HEADER_COUNT - 1, gap: skipped, step: 4 };
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }
}

@kernel k config | exec
void run(int skipped) {
}
```

**Explanation of the code above:**

- `HEADER_COUNT` is a macro of a header and `skipped` is a variable of `run`: `vmegc` knows neither value.
- The copy is a function that `vmegc` writes. It takes one parameter for each unknown name, and computes `HEADER_COUNT - 1` itself.
- The call of that function in `run` gives the names as they are written, `HEADER_COUNT` and `skipped`.

**Rules:**

- A name is one parameter, however many times it is used in the fields. The parameters follow the order of the fields: `count`, `gap`, `step`, then `group`.
- A name has to be known where the kernel is called: a macro that the file includes, or a variable of the function.
- The part of an expression that `vmegc` knows is replaced by its value ([2.6](language.md#26-numbers-macros-and-unknown-names)).
- `memory` is not a number: it names an array ([8](arrays.md)).

## 9.6 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [9.1](#91-the-transfer-variable) | `the Transfer type Foo is not described (Words, Halves, Bytes)` | `Transfer(Foo)` with a type that does not exist |
| [9.1](#91-the-transfer-variable) | `the Transfer variable 'in' is declared twice` | two `Transfer` with the same name |
| [9.1](#91-the-transfer-variable) | `'in' is already declared as an Agu variable` | the name belongs to an `Agu` variable (or to a `Staging` variable) |
| [9.1](#91-the-transfer-variable) | `Transfer in: unknown field 'foo' (memory, count)` | a field that is not in the type, the message lists the ones that are |
| [9.1](#91-the-transfer-variable) | `Transfer in: duplicate field 'count'` | the same field written twice |
| [9.1](#91-the-transfer-variable) | `Transfer in: the field 'count' is needed` | a `Transfer` without `memory` or without `count` |
| [9.1](#91-the-transfer-variable) | `Transfer in: 'memory' takes a name` | `memory` with something else than the name of an array |
| [9.1](#91-the-transfer-variable) | `Transfer in: 'count' takes a value, not a list of fields` | braces given to a field that takes a value |
| [9.1](#91-the-transfer-variable) | `Transfer in: count cannot be negative` | a negative number in a field |
| [9.2.3](#923-the-group) | `Transfer in: 'group' takes a list of fields` | `group` with a value |
| [9.2.3](#923-the-group) | `Transfer in: unknown field 'foo' of group (size, outer, inner)` | a field of `group` other than `size`, `outer` and `inner` |
| [9.2.3](#923-the-group) | `Transfer in: duplicate field 'size' of group` | the same field of `group` written twice |
| [9.2.3](#923-the-group) | `Transfer in: group needs at least one field (size, outer, inner)` | `group: {}` |
| [9.2.3](#923-the-group) | `Transfer in: the field 'inner' of group is needed, outer and inner are one register` | `outer` without `inner`, or `inner` without `outer` |
| [9.2.3](#923-the-group) | `braces cannot be nested more than one level inside the parameters` | braces inside the braces of `group` |
| [9.3](#93-load-and-store) | `.load needs a .transfer = name;` | a `.load` or a `.store` without `.transfer` |
| [9.3](#93-load-and-store) | `unknown Transfer variable 'zzz'` | `.transfer = zzz;` with a name that is not a `Transfer` |
| [9.3](#93-load-and-store) | `unknown attribute '.foo' of .load (.transfer, .scope, .offsets)` | an attribute that does not exist |
| [9.3](#93-load-and-store) | `.transfer is already written in this .load` | the same attribute written twice |
| [9.3](#93-load-and-store) | `.scope must be local or global` | `.scope` with another value |
| [9.3](#93-load-and-store) | `this .load is not generated yet (only Transfer and Transfer(Words))` | a `.load` or a `.store` that uses a `Transfer(Halves)` or a `Transfer(Bytes)` |
| [9.4](#94-the-offsets) | `top0 is already set in this .load` | the same buffer twice in `.offsets` |
| [9.4](#94-the-offsets) | `the offset of top0 cannot be negative` | a negative offset |
| [9.4](#94-the-offsets) | `top[...]: buffer index must be a number from 0 to 3` | `top[i]` or `base[i]` with an index out of range |
| [9.4](#94-the-offsets) | `unknown offset '.top4' (.top0 to .top3, .base0 to .base3)` | a buffer that does not exist |
| [9.4](#94-the-offsets) | `expected .top0 to .top3, .base0 to .base3, top[...] or base[...]` | an entry of `.offsets` that is none of the forms |
