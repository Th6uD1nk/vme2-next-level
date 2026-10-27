[Index](../VMEG.md) · [meLibOnProcess](on-process.md) · [Errors](errors.md)

# Emulation

The emulator plays a kernel marked here. How it plays it and how to run it are in [VMEE](../VMEE.md).

## Contents

- [13.1 The @emulate mark](#131-the-emulate-mark)
- [13.2 The rules of the mark](#132-the-rules-of-the-mark)
- [13.3 Errors](#133-errors)

## 13.1 The @emulate mark

`@emulate` marks a kernel to be played by the emulator. It is written right above the `.kernel` of the kernel, with an id between double quotes.

```c
@emulate "add-test"
.kernel add direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

@kernel add config | exec
void run(void) {
}
```

**Explanation of the code above:**

- `@emulate "add-test"` marks the kernel `add`. The emulator is asked for the kernel by this id ([VMEE](../VMEE.md)).
- `vmegc` does not write the mark in the C or C++ file.

**Rules:**

- The id is made of letters, digits, `-` and `_`.
- The id is unique in the file ([13.2](#132-the-rules-of-the-mark)).
- `@emulate` is followed by the `.kernel` it marks ([13.2](#132-the-rules-of-the-mark)).

## 13.2 The rules of the mark

```c
@emulate "sum"
.kernel add direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

// no mark: this kernel is not played
.kernel sub direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 - top0; }
}
```

**Explanation of the code above:**

- Only `add` is marked. A kernel with no mark is a kernel as any other: it is compiled and called, but the emulator is not asked for it.

**Rules:**

- The mark is followed by `.kernel name` and the body of the kernel. Empty lines and comments can be written between the mark and `.kernel`.
- A kernel has one mark. Each mark has its own id.
- An id is used once in a file. The same id in two files of the same command is not an error of `vmegc`.
- The mark has no effect on the output of `vmegc`, only on what the emulator can play ([VMEE](../VMEE.md)).

## 13.3 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [13.1](#131-the-emulate-mark) | `expected @emulate "id", the id is made of letters, digits, - and _ between double quotes` | an id that is not between double quotes, or with another character |
| [13.2](#132-the-rules-of-the-mark) | `@emulate "id" must be followed by '.kernel name'` | a mark followed by something else than `.kernel` and a name, or by a second mark |
| [13.2](#132-the-rules-of-the-mark) | `the id "a" of @emulate is already used at line N` | a second mark with the same id in the file |
| [13.2](#132-the-rules-of-the-mark) | `@emulate must be followed by a kernel definition with its body` | a mark on a `.kernel` that has no body `{ … }` (the line is the one of the mark) |
