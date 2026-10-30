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

## 1.2 Running a kernel

```c
volatile Buffer input[8] = { 1, 2, 3, 4, 5, 6, 7, 8 };

@emulate "twice"
.kernel twice direct {
  Agu t = { count: 7 }, w = { count: 7, cyc: auto };
  Transfer in = { memory: input, count: 7 };
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

@kernel twice config | exec
void run(void) {
}
```

```
vmee --run twice main.vmeg.cpp --buffers-words 8
```

shows:

```
Buffer: BASE 0
0x00000002, 0x00000004, 0x00000006, 0x00000008,
0x0000000a, 0x0000000c, 0x0000000e, 0x00000010,
```

followed by the same lines for `BASE 1` to `BASE 3`.

**Explanation of the code above:**

- `--run twice` plays the kernel marked `twice`. `vmee` is the command of `./install.sh`, `python3 vmeemu.py` is the same command.
- The result is written like `vmeDebugDumpBuffers` does on the PSP: `Buffer: BASE n`, then the words of the buffer, four per line, each one as `0x%08x`.
- The `.load` copies `input` to `TOP_0` before the kernel runs. The kernel adds each word to itself and writes the result in `BASE_0`.

**Rules:**

- The kernel is `direct` or `memory`. A memory kernel gives the same result as a direct one. The emulator plays the definition of the kernel as `config | exec`: the actions of a `@kernel` call, `build` and `async` among them, are not played.
- The `.load` of the kernel are played before the run, the `.store` after it, the way `vmegc` generates them for a call. The arrays they use must be declared in the files ([1.3](#13-several-files)).
- Only the `.load` and the `.store` written in the `.kernel` are played. Currently not supported: the ones written in the block of a `@kernel` call.
- Only the four base buffers are shown. A `.store` does not show its array: read the result in the buffer it comes from.
- The kernel is built into a small host program with `g++ -m32` and the library of the submodule `me-core-mapper`. `--run` needs `g++` with 32 bit support, and the submodule must not be empty (`git submodule update --init me-core-mapper`).
- The host program is run, and the events it writes are played by the emulator. The run is stopped after 60 seconds.
