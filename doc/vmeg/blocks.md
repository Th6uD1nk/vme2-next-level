[Index](../VMEG.md) · [Calling a kernel](calling.md) · [meLibOnProcess](on-process.md)

# Blocks

## Contents

- [11.1 The block form](#111-the-block-form)
- [11.2 The C code of a block](#112-the-c-code-of-a-block)
- [11.3 The vmeg statements of a block](#113-the-vmeg-statements-of-a-block)
- [11.4 Blocks in a row](#114-blocks-in-a-row)
- [11.5 Errors](#115-errors)

## 11.1 The block form

A call written above a function ([10.1](calling.md#101-the-call-of-a-kernel)) is put at the start of the function. When the call has to be in the middle of a function, it is written as a block.

```c
.kernel k direct {
  Transfer t = { type: words, mode: basic, memory: x, count: 15 };
  .load { .transfer = t; .scope = local; .offsets { .top0 = 0; } }
}

void run(void) {
  volatile Buffer x[16];
  fill(x);
  @kernel k config | exec {
    after();
  }
}
```

**Explanation of the code above:**

- `fill(x);` is C code. It runs before the call, because the call is where the block is written.
- `@kernel k config | exec { … }` calls the kernel `k` at this place.
- `after();` is in the block: it runs once the kernel has run ([11.2](#112-the-c-code-of-a-block)).

**Rules:**

- The block is written inside a function, as a statement. Above a function, the call is written without a block ([10.1](calling.md#101-the-call-of-a-kernel)).
- The actions are the same as for a call above a function, with the same `|`, and a block can name several kernels ([10.2](calling.md#102-the-actions), [10.3](calling.md#103-several-actions-in-one-call), [10.4](calling.md#104-several-kernels-in-one-call)).
- A local array of the kernel is declared in the function that holds the block ([8.3](arrays.md#83-local-arrays)).

## 11.2 The C code of a block

What a block holds, besides the vmeg statements of [11.3](#113-the-vmeg-statements-of-a-block), is C code. It stays as you wrote it.

```c
void run(int n) {
  @kernel k config | exec {
    for (int i = 0; i < n; i++) {
      check(i);
    }
  }
}
```

**Explanation of the code above:**

- The `for` is a C loop: it is not a vmeg loop ([2.7](language.md#27-loops)). It can use the variables and the parameters of the function.
- It runs after the actions of the call, while the VME is still enabled.

**Rules:**

- The C code runs after the actions of the call, and `vmegc` disables the VME after it.
- When the C code starts, depending on the actions:

| Actions of the block | When the C code runs |
|---|---|
| `config \| exec`, `exec`, `config \| async` | after the end of the run |
| `async` | while the VME runs: nothing waits for its end |
| `config` | after the kernel is configured: it has not run |
