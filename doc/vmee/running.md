[Index](../VMEE.md) · [Traces](traces.md)

# Running vmee

## Contents

- [1.1 Marking a kernel](#11-marking-a-kernel)
- [1.2 Running a kernel](#12-running-a-kernel)
- [1.3 Several files](#13-several-files)
- [1.4 The window of the buffers](#14-the-window-of-the-buffers)
- [1.5 --trace](#15---trace)
- [1.6 --compat](#16---compat)
- [1.7 --list](#17---list)
- [1.8 Errors](#18-errors)

## 1.1 Marking a kernel

```c
@emulate "twice"
.kernel twice direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}
```

**Explanation of the code above:**

- `@emulate "twice"` marks the kernel `twice`. The emulator is asked for the kernel by this id.
- `vmegc` does not write the mark in the C or C++ file.

**Rules:**

- The mark is written right above the `.kernel`. The id is made of letters, digits, `-` and `_`, between double quotes, and is unique in the file.
- The mark has a second form, `@emulate "id" { … }`, which surrounds calls of kernels written in a function. The rules of both forms are in [Emulation](../vmeg/emulation.md).
