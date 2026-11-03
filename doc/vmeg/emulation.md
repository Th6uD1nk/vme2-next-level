[Index](../VMEG.md) · [meLibOnProcess](on-process.md) · [Errors](errors.md)

# Emulation

The emulator plays a kernel marked here, or the calls of kernels written in a block. How it plays them and how to run it are in [VMEE](../VMEE.md).

## Contents

- [13.1 The @emulate mark](#131-the-emulate-mark)
- [13.2 The rules of the mark](#132-the-rules-of-the-mark)
- [13.3 The block form](#133-the-block-form)
- [13.4 Loops](#134-loops)
- [13.5 C loops marked @unroll](#135-c-loops-marked-unroll)
- [13.6 Errors](#136-errors)

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
- Currently not supported: a value of `.params` or `.memory` that uses a variable of the function, like the `s` of a C `for (int s = 0; …)` in `configs[s]` or `8 >> s`. The emulator plays the calls, not the code of the function around them: write a number or a constant, like `configs[1]`, or the name of a loop of the block, which is replaced by its number ([13.4](#134-loops)), or mark the C loop with `@unroll` ([13.5](#135-c-loops-marked-unroll)).
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

- The loop is written in the block `@emulate "id" { … }` ([13.3](#133-the-block-form)), around calls, at any depth of the block, for example inside a C `while` or `if`. A `for` anywhere else is left as it is: a C `for (…)`, the `for` of the vmeg statements in the body of a call ([2.7](language.md#27-loops)), or a loop outside a block.
- The form is `for name in low..high {`. Both bounds are integers, and both are included. A first bound above the second is an error, unlike the loop of [2.7](language.md#27-loops), which then writes nothing.
- The body holds at least one `@kernel` call. It holds no preprocessor line.
- A loop can hold other loops, with other names.
- The name of the loop is replaced wherever it is used as a name in the body. It is not replaced after a dot, and a key of `.params` with the same name keeps its name: in `.params = { stride: 8 >> stride }` only the second `stride` is replaced.
- The lines of the file do not change: the copies are written on the line of the `for`, and the lines that follow stay where they were. An error found in a copy gives the line of the `for`.

## 13.5 C loops marked @unroll

`@unroll` written before a C `for` stands for the copies of the calls in its body, for the emulator and for `vmeh` only. `vmegc` keeps the loop.

```c
volatile Memory configs[3];

.kernel reader memory {
  .params { int skip; }
  Agu t = { count: 7, step: skip }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

void meLibOnProcess(void) {
  @emulate "c-steps" {
    @unroll
    for (int s = 0; s < 3; s++) {
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

`vmee --list main.vmeg.cpp` shows the same six calls as the loop of [13.4](#134-loops).

**Explanation of the code above:**

- `@unroll` marks the loop. `vmegc` removes the mark and writes `for (int s = 0; s < 3; s++)` with `configs[s]` and `1 << s` as they are: the program has one copy of the calls, run three times by the C loop.
- The emulator and `vmeh` play six calls: for each value of `s`, from 0 to 2, `s` is replaced by its number in the body, as in [13.4](#134-loops).

**Rules:**

- `@unroll` is written alone, at the start of a statement, right before `for (`, in an `@emulate "id" { … }` block ([13.3](#133-the-block-form)) at any depth, outside the body of a `@kernel` call. A `for` without the mark is left as it is, by the emulator and by `vmegc`.
- The header is `for (type name = low; name < high; name++)`. The comparison can be `<` or `<=`, and the step `name++` or `name += n`. The type is the identifiers before the name, like `int` or `unsigned int`.
- `low`, `high` and `n` are numbers, macros of the file that are defined once before the loop, or expressions made of them. `n` is above 0.
- The loop runs at most 256 turns.
- The body holds at least one `@kernel` call. The C statements of the body, like an `if (s == 3)`, stay in the program and are not played by the emulator.
- The name of the loop is replaced as in [13.4](#134-loops): not after a dot, and a key of `.params` with the same name keeps its name.
- A loop can hold other marked loops, and loops of [13.4](#134-loops). The loops of [13.4](#134-loops) are unrolled first.
- The lines of the file do not change, and an error gives the line of the mark.

## 13.6 Errors

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
| [13.4](#134-loops) | `expected 'for name in low..high {', for example for s in 0..3 {` | a loop of a block whose header is not a name, `in`, two bounds with `..` between them and `{` (the line is the one of the `for`, as for the next four) |
| [13.4](#134-loops) | `the bounds of a for are integers, '0..N' is not accepted` | a bound that is a name, a macro or a number with a point |
| [13.4](#134-loops) | `the for runs from 3 to 1, the first bound must not be above the second` | a first bound above the second |
| [13.4](#134-loops) | `the for calls no kernel, write at least one @kernel call in it` | a loop of a block whose body has no `@kernel` call |
| [13.4](#134-loops) | `a preprocessor line cannot be inside a for of an emulate block` | a line starting with `#` in the body of the loop |
| [13.5](#135-c-loops-marked-unroll) | `@unroll is written before a for loop of an @emulate block, outside the calls` | a mark that is not right before `for (`, not at the start of a statement, outside an `@emulate` block or in the body of a call |
| [13.5](#135-c-loops-marked-unroll) | `the @unroll loop is not unrolled, the form is for (int name = low; name < high; name++) with bounds and step made of numbers and macros of the file` | a header of another form, or a bound or a step that is not known |
| [13.5](#135-c-loops-marked-unroll) | `the @unroll loop runs N turns, at most 256 are unrolled` | a loop of more than 256 turns |
| [13.5](#135-c-loops-marked-unroll) | `the @unroll loop calls no kernel, write at least one @kernel call in it` | a marked loop whose body has no `@kernel` call |
