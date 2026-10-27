[Index](../VMEG.md) · [Blocks](blocks.md) · [Emulation](emulation.md)

# meLibOnProcess

## Contents

- [12.1 The function of the Media Engine](#121-the-function-of-the-media-engine)
- [12.2 What vmegc writes at its start](#122-what-vmegc-writes-at-its-start)
- [12.3 A call on meLibOnProcess](#123-a-call-on-melibonprocess)
- [12.4 Errors](#124-errors)

## 12.1 The function of the Media Engine

`meLibOnProcess` is the function defined by the me-core library to access the Media Engine. The library calls it on the Media Engine, and you write its body.

```c
.kernel k direct {
}

void meLibOnProcess(void) {
  @kernel k config | exec {
    done();
  }
}
```

**Explanation of the code above:**

- `meLibOnProcess` is the function of the me-core library. The kernel is called from it, with a block ([11](blocks.md)).
- `vmegc` adds a few statements at the start of the function ([12.2](#122-what-vmegc-writes-at-its-start)). The rest is written as you wrote it.

**Rules:**

- The function is written once per file, outside any other function ([12.4](#124-errors)).
- A function with another name is a plain function: `vmegc` adds nothing to it.

## 12.2 What vmegc writes at its start

`vmegc` prepares the VME at the start of the body of `meLibOnProcess`, before your code. The function starts with the VME in a known state.

```c
void meLibOnProcess(void) {
  work();
}
```

**Explanation of the code above:**

- `vmegc` writes the preparation before `work();`.
- `work();` runs once the preparation is done, with the VME disabled, as it was written.

**Rules:**

- The preparation is written once per file, at the start of the function, whatever the function holds.
- It is done before any kernel is called.
- When a kernel is called on the function, the VME stays enabled after the preparation ([12.3](#123-a-call-on-melibonprocess)).
- Nothing is added to the other functions.

## 12.3 A call on meLibOnProcess

A kernel can be called on `meLibOnProcess` like on any function ([10.1](calling.md#101-the-call-of-a-kernel)), above it or with a block inside it ([11](blocks.md)).

```c
.kernel k direct {
}

@kernel k config | exec
void meLibOnProcess(void) {
  work();
}
```

**Explanation of the code above:**

- The kernel `k` is configured and run right after the preparation of the VME ([12.2](#122-what-vmegc-writes-at-its-start)), before `work();`.
- The VME is enabled once for the preparation and the call together, and disabled after the call.

**Rules:**

- With a block, the preparation comes first, then the actions, then the C code of the block, and the VME is disabled after it ([11.2](blocks.md#112-the-c-code-of-a-block)).
- A call written above another function does not share the preparation: that function enables and disables the VME on its own ([10.4](calling.md#104-several-kernels-in-one-call)).
