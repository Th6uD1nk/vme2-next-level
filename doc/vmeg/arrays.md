[Index](../VMEG.md) · [Staging, routing and warnings](staging-routing.md) · [Transfers](transfers.md)

# Arrays

## Contents

- [8.1 The Buffer keyword](#81-the-buffer-keyword)
- [8.2 Global arrays](#82-global-arrays)
- [8.3 Local arrays](#83-local-arrays)
- [8.4 Arrays in several files](#84-arrays-in-several-files)
- [8.5 Errors](#85-errors)

## 8.1 The Buffer keyword

`Buffer` declares an array that the VME reads from or writes to, through a `Transfer` ([9](transfers.md)). It is written where the type of the elements would be.

```c
volatile Buffer input[16];
volatile Buffer a[4], b[2];
volatile Buffer table[4] = { 1, 2, 3, 4 };
```

**Explanation of the code above:**

- `volatile Buffer input[16];` declares an array of 16 words.
- Several arrays can be declared at once, as in C.
- An array can have an initializer, as in C.

**Rules:**

- The elements of a `Buffer` array are 32-bit words, and the array is aligned on 64 bytes, the way the VME reads it.
- `Buffer` is always written with `volatile`, because the VME can change the content of the array.
- `static` and `extern` can be written in front of it ([8.4](#84-arrays-in-several-files)).
- `Buffer` declares a variable: it cannot be used in a parameter or in a cast.
- An array is global ([8.2](#82-global-arrays)) or local ([8.3](#83-local-arrays)).

## 8.2 Global arrays

A global array is declared outside any function. A kernel uses it in a `.load` or a `.store` with `.scope = global`.

```c
volatile Buffer input[16];

.kernel k direct {
  Transfer t = { type: words, mode: basic, memory: input, count: 15 };
  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }
}

@kernel k config | exec
void run(void) {
}
```

**Explanation of the code above:**

- `volatile Buffer input[16];` is outside any function: it is a global array.
- `memory: input` names the array in the `Transfer` ([9](transfers.md)).
- `.scope = global` says that `input` is a global array. The function that calls the kernel with `config` loads it into `top0` before the run.

**Rules:**

- The same global array serves every kernel and every function that names it. Nothing is declared in the function.
- The array can be declared in another file of the project ([8.4](#84-arrays-in-several-files)).
- An array that is named by a global `.load` or `.store` and declared with `Buffer` in no file is an error ([8.5](#85-errors)).
