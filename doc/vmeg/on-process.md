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
