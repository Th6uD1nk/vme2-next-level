[Index](../VMEG.md) · [meLibOnProcess](on-process.md) · [Errors](errors.md)

# Emulation

The emulator plays a kernel marked here, or the calls of kernels written in a block. How it plays them and how to run it are in [VMEE](../VMEE.md).

## Contents

- [13.1 The @emulate mark](#131-the-emulate-mark)
- [13.2 The rules of the mark](#132-the-rules-of-the-mark)
- [13.3 The block form](#133-the-block-form)
- [13.4 Loops](#134-loops)
- [13.5 Errors](#135-errors)

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
volatile Memory configs[2];

.kernel reader memory {
  .params { int skip; }
  Agu t = { count: 7, step: skip }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

.kernel total direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

void meLibOnProcess(void) {
  @emulate "two-steps" {
    @kernel reader build {
      .params = { skip: 2 };
      .memory = configs[1];
    }
    @kernel reader config | exec {
      .memory = configs[1];
    }
    @kernel total config | exec {
    }
  }
}
```

**Explanation of the code above:**

- `@emulate "two-steps" { … }` surrounds three calls of `meLibOnProcess`. They are real calls of the program: `vmegc` leaves out `@emulate "two-steps" {` and the brace that closes it, and writes the calls where they are, as if the mark was not there.
- The emulator plays the three calls in their order, with their `.params` and their `.memory` ([11.3.1](blocks.md#1131-the-params-of-a-call), [11.3.2](blocks.md#1132-the-memory-config-of-a-call)): `reader` is built in `configs[1]`, loaded from it and run, then `total` is run.
- The emulator is asked for this emulation by its id, `two-steps` ([VMEE](../VMEE.md)).

**Rules:**

- The block is written in a function, as a statement, and holds at least one `@kernel` call. The C code that it holds stays in the program: the emulator plays the calls only.
- The id has the same characters as in the first form, and it is unique in the file for the two forms together ([13.2](#132-the-rules-of-the-mark)).
- The two forms can be in the same file. Each one is an emulation: they are listed as different emulations ([VMEE](../VMEE.md)).
- The arrays that the calls name, `Buffer` and `Memory`, are the ones declared in the file or in the function that holds the block.
- Currently not supported: a value of `.params` or `.memory` that uses a variable of the function, like the `s` of a C `for (int s = 0; …)` in `configs[s]` or `8 >> s`. The emulator plays the calls, not the code of the function around them: write a number or a constant, like `configs[1]`, or the name of a loop of the block, which is replaced by its number ([13.4](#134-loops)).
- Currently not supported: a kernel called in the block that is defined in another file than the block.

## 13.4 Loops

A loop written around the calls of a block stands for the copies of those calls.

```c
volatile Memory configs[3];

.kernel reader memory {
  .params { int skip; }
  Agu t = { count: 7, step: skip }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

void meLibOnProcess(void) {
  @emulate "three-steps" {
    for s in 0..2 {
      @kernel reader build {
        .params = { skip: 1 << s };
        .memory = configs[s];
      }
      @kernel reader config | exec {
        .memory = configs[s];
      }
    }
  }
}
```

`vmee --list main.vmeg.cpp` shows the six calls that the loop stands for:

```
emulate "three-steps": kernels reader (lines 10-20)
  calls:
    reader  build
    reader  config | exec
    reader  build
    reader  config | exec
    reader  build
    reader  config | exec
```

**Explanation of the code above:**

- `for s in 0..2 { … }` stands for three copies of the two calls inside it: one with `s` equal to 0, one with 1 and one with 2. The two values 0 and 2 are both included.
- In each copy, `s` is replaced by its number: `skip: 1 << s` becomes `1 << 0`, `1 << 1` and `1 << 2`, and `configs[s]` becomes `configs[0]`, `configs[1]` and `configs[2]`.
- `vmegc` writes the program with the six calls, as if they were written one by one. The emulator and `vmeh` play the same six calls ([VMEE](../VMEE.md)).

**Rules:**

- The loop is written in the block `@emulate "id" { … }` ([13.3](#133-the-block-form)), around calls. A `for` anywhere else is left as it is: a C `for (…)`, the `for` of the vmeg statements in the body of a call ([2.7](language.md#27-loops)), or a loop outside a block.
- The form is `for name in low..high {`. Both bounds are integers, and both are included. A first bound above the second is an error, unlike the loop of [2.7](language.md#27-loops), which then writes nothing.
- The body holds at least one `@kernel` call. It holds no preprocessor line.
- A loop can hold other loops, with other names.
- The name of the loop is replaced wherever it is used as a name in the body. It is not replaced after a dot, and a key of `.params` with the same name keeps its name: in `.params = { stride: 8 >> stride }` only the second `stride` is replaced.
- The lines of the file do not change: the copies are written on the line of the `for`, and the lines that follow stay where they were. An error found in a copy gives the line of the `for`.

## 13.5 Errors

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
