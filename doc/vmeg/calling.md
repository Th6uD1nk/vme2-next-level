[Index](../VMEG.md) · [Transfers](transfers.md) · [Blocks](blocks.md)

# Calling a kernel

## Contents

- [10.1 The call of a kernel](#101-the-call-of-a-kernel)
- [10.2 The actions](#102-the-actions)
- [10.3 Several actions in one call](#103-several-actions-in-one-call)
- [10.4 Several kernels in one call](#104-several-kernels-in-one-call)
- [10.5 Uploads and downloads around the run](#105-uploads-and-downloads-around-the-run)
- [10.6 Errors](#106-errors)

## 10.1 The call of a kernel

A kernel does nothing until a function calls it. The call is written with `@kernel`, right above the function.

```c
.kernel add direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

@kernel add config | exec
void run(void) {
}
```

**Explanation of the code above:**

- `@kernel add config | exec` calls the kernel `add`: `config` writes it to the VME and `exec` runs it ([10.2](#102-the-actions)).
- It is written above the function `run`. `vmegc` writes the call at the start of `run`, after the declarations of its local arrays ([8.3](arrays.md#83-local-arrays)).

**Rules:**

- `@kernel` is written above a function, not inside it. Inside a function the call is a block, `@kernel add config | exec { … }` ([11](blocks.md)).
- Every kernel of the project is called at least once, by a function or by a block. A kernel that nothing calls is an error ([10.6](#106-errors)).
- The kernel can be defined in another file of the project ([1.2](running.md#12-several-files)).
- `@context` is a synonym of `@kernel` ([2.8](language.md#28-synonyms)).
