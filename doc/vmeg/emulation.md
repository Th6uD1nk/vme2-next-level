[Index](../VMEG.md) · [meLibOnProcess](on-process.md) · [Errors](errors.md)

# Emulation

The emulator plays a kernel marked here, or the calls of kernels written in a block. How it plays them and how to run it are in [VMEE](../VMEE.md).

## Contents

- [13.1 The @emulate mark](#131-the-emulate-mark)
- [13.2 The rules of the mark](#132-the-rules-of-the-mark)
- [13.3 The block form](#133-the-block-form)
- [13.4 Errors](#134-errors)

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

## 13.3 The block form

`@emulate "id" { … }` is a second way to mark. It surrounds calls of kernels written in a function, and the emulator plays these calls, with their values.

```c
volatile Memory stage[2];

.kernel butterfly memory {
  .params { int stride; }
  Agu t = { count: 7, step: stride }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

.kernel total direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

void meLibOnProcess(void) {
  @emulate "two-steps" {
    @kernel butterfly build {
      .params = { stride: 2 };
      .memory = stage[1];
    }
    @kernel butterfly config | exec {
      .memory = stage[1];
    }
    @kernel total config | exec {
    }
  }
}
```

**Explanation of the code above:**

- `@emulate "two-steps" { … }` surrounds three calls of `meLibOnProcess`. They are real calls of the program: `vmegc` leaves out `@emulate "two-steps" {` and the brace that closes it, and writes the calls where they are, as if the mark was not there.
- The emulator plays the three calls in their order, with their `.params` and their `.memory` ([11.3.1](blocks.md#1131-the-params-of-a-call), [11.3.2](blocks.md#1132-the-memory-config-of-a-call)): `butterfly` is built in `stage[1]`, loaded from it and run, then `total` is run.
- The emulator is asked for this emulation by its id, `two-steps` ([VMEE](../VMEE.md)).

**Rules:**

- The block is written in a function, as a statement, and holds at least one `@kernel` call. The C code that it holds stays in the program: the emulator plays the calls only.
- The id has the same characters as in the first form, and it is unique in the file for the two forms together ([13.2](#132-the-rules-of-the-mark)).
- The two forms can be in the same file. Each one is an emulation: they are listed as different emulations ([VMEE](../VMEE.md)).
- The arrays that the calls name, `Buffer` and `Memory`, are the ones declared in the file or in the function that holds the block.
- Currently not supported: a value of `.params` or `.memory` that uses a variable of the function, like `stage[s]` or `8 >> s`. The emulator plays the calls, not the code of the function around them: write a number or a constant, like `stage[1]`.
- Currently not supported: a kernel called in the block that is defined in another file than the block.

## 13.4 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [13.1](#131-the-emulate-mark) | `expected @emulate "id", the id is made of letters, digits, - and _ between double quotes` | an id that is not between double quotes, or with another character |
| [13.2](#132-the-rules-of-the-mark) | `@emulate "id" must be followed by '.kernel name'` | a mark followed by something else than `.kernel` and a name, or by a second mark |
| [13.2](#132-the-rules-of-the-mark) | `the id "a" of @emulate is already used at line N` | a second mark, in either form, with the same id in the file |
| [13.2](#132-the-rules-of-the-mark) | `@emulate must be followed by a kernel definition with its body` | a mark on a `.kernel` that has no body `{ … }` (the line is the one of the mark) |
| [13.3](#133-the-block-form) | `inside a function @emulate "id" is followed by a block { ... }` | `@emulate "id"` written in a function with no block after it |
| [13.3](#133-the-block-form) | `the @emulate "x" block calls no kernel, write at least one @kernel call in it` | a block with no `@kernel` call |
| [13.3](#133-the-block-form) | `unterminated @emulate block` | a block that is never closed |
| [13.3](#133-the-block-form) | `the kernel q of the @emulate "far" is not defined in this file` | a kernel of the block defined in another file |
