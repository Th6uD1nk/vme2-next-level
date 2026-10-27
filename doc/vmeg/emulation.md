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
- `vmegc` does not write the mark in the C or C++ file: the output is the same as without it.

**Rules:**

- The id is made of letters, digits, `-` and `_`.
- The id is unique in the project ([13.2](#132-the-rules-of-the-mark)).
- `@emulate` is for a kernel: the line after it starts the `.kernel` ([13.2](#132-the-rules-of-the-mark)).
