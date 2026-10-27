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

## 8.3 Local arrays

A local array is declared inside the function that calls the kernel. A kernel uses it in a `.load` or a `.store` with `.scope = local`, or with no `.scope`.

```c
.kernel k direct {
  Transfer t = { type: words, mode: basic, memory: x, count: 15 };
  .load { .transfer = t; .scope = local; .offsets { .top0 = 0; } }
}

@kernel k config | exec
void run(void) {
  volatile Buffer x[16];
}
```

**Explanation of the code above:**

- `volatile Buffer x[16];` is inside `run`, the function that calls the kernel: it is a local array.
- `memory: x` names the array in the `Transfer`.
- `.scope = local` says that `x` is declared in the function. It is the scope of a `.load` or a `.store` that has no `.scope`.

**Rules:**

- The array is declared in the body of the function, not in a block `{ }` inside it.
- Each function that calls the kernel declares its own array. Two functions that call the same kernel declare an array each.
- With `@kernel` above the function, the call of the kernel is written right after the declarations of the arrays, before the other statements of the function. To run statements first, for example to fill the array, write the call as a block, `@kernel k config | exec { … }`, at the place you want ([11](blocks.md)).
- An array that is named by a local `.load` or `.store` and not declared in the function is an error ([8.5](#85-errors)).

## 8.4 Arrays in several files

The files given to `vmegc` in the same command are one project ([1.2](running.md#12-several-files)). A global array is defined in one file and named by the kernels of the others.

`data.vmeg.c` defines the array:

```c
volatile Buffer input[16] = { 1, 2, 3 };
```

`main.vmeg.c` has the kernel that loads it:

```c
.kernel k direct {
  Transfer t = { type: words, mode: basic, memory: input, count: 15 };
  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }
}

@kernel k config | exec
void run(void) {
}
```

```
python3 vmegc.py data.vmeg.c main.vmeg.c
```

**Explanation of the code above:**

- `input` is defined in `data.vmeg.c`, and the kernel of `main.vmeg.c` names it with `.scope = global`.
- `vmegc` writes the declaration of `input` in the output of `main.vmeg.c` by itself. Nothing is written for it.

**Rules:**

- A global array is defined in one file only. A second definition is an error ([8.5](#85-errors)).
- A file can declare an array that another file defines, with `extern`: `extern volatile Buffer input[16];`. The array must then be defined in a file of the project.
- A `static` array can only be named by the kernels of its own file.
- A local array stays in the function that calls the kernel: it is never shared between files.
