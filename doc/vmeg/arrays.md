[Index](../VMEG.md) · [Staging, routing and warnings](staging-routing.md) · [Transfers](transfers.md)

# Arrays

## Contents

- [8.1 The Buffer keyword](#81-the-buffer-keyword)
  - [8.1.1 The Q format](#811-the-q-format)
- [8.2 Global arrays](#82-global-arrays)
- [8.3 Local arrays](#83-local-arrays)
- [8.4 Arrays in several files](#84-arrays-in-several-files)
- [8.5 Memory configs](#85-memory-configs)
- [8.6 Errors](#86-errors)

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

### 8.1.1 The Q format

```c
volatile Buffer(Q8.8) matrix[4] = { 0.5, -1.25, 3, 0x10 };
volatile Buffer(Q4.20) angle[2] = { 0.7071068f, -2.0 };
```

**Explanation of the code above:**

- `Buffer(Q8.8)` is an array of values with 8 bits of integer part (the sign counts) and 8 bits of fraction: from -128 to 127.99609375, in steps of 1/256.
- The numbers are the real values. `vmegc` writes them as words: `0.5` is `0x00000080`, `-1.25` is `0xfffffec0` and `3` is `0x00000300`.
- `0x10` is a hexadecimal number: it stays the word that is written.
- `Buffer(Q4.20)` has 4 bits of integer part and 20 of fraction, from -8 to 7.999999046325684: `-2.0` is `0xffe00000`.

**Rules:**

- The format is `Qm.n`: `m` is the number of bits of the integer part, sign included, and `n` the number of bits of the fraction. `m` is 1 at least, and `m + n` is 24 at most, the 24 bits of a word of the VME.
- A decimal number is the real value, with or without a point, an exponent, or the suffix `f`. It is cut toward zero and written on 32 bits, the bit 23 repeated in the 8 high bits.
- A value outside the range of the format is an error ([8.6](#86-errors)).
- A hexadecimal number, a macro or an expression stays as it is written, and the C compiler computes it.
- The array is a `Buffer` like the others, with the same size and the same alignment ([8.1](#81-the-buffer-keyword)). Without a format, the numbers of the initializer stay as they are written.

## 8.2 Global arrays

A global array is declared outside any function. A kernel uses it in a `.load` or a `.store` with `.scope = global`.

```c
volatile Buffer input[16];

.kernel k direct {
  Transfer t = { memory: input, count: 15 };
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
- An array that is named by a global `.load` or `.store` and declared with `Buffer` in no file is an error ([8.6](#86-errors)).

## 8.3 Local arrays

A local array is declared inside the function that calls the kernel. A kernel uses it in a `.load` or a `.store` with `.scope = local`, or with no `.scope`.

```c
.kernel k direct {
  Transfer t = { memory: x, count: 15 };
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
- An array that is named by a local `.load` or `.store` and not declared in the function is an error ([8.6](#86-errors)).

## 8.4 Arrays in several files

The files given to `vmegc` in the same command are one project ([1.2](running.md#12-several-files)). A global array is defined in one file and named by the kernels of the others.

`data.vmeg.c` defines the array:

```c
volatile Buffer input[16] = { 1, 2, 3 };
```

`main.vmeg.c` has the kernel that loads it:

```c
.kernel k direct {
  Transfer t = { memory: input, count: 15 };
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

- A global array is defined in one file only. A second definition is an error ([8.6](#86-errors)).
- A file can declare an array that another file defines, with `extern`: `extern volatile Buffer input[16];`. The array must then be defined in a file of the project.
- A `static` array can only be named by the kernels of its own file.
- A local array stays in the function that calls the kernel: it is never shared between files.

## 8.5 Memory configs

A `memory` kernel is built in RAM before it is sent to the VME ([3.2.2](kernel.md#322-memory)). `Memory` declares the places in RAM where it is built, when a kernel has to keep several of them at the same time.

```c
volatile Memory configs[4];

void run(void) {
  volatile Memory local[2];
  volatile Memory one;
}
```

**Explanation of the code above:**

- `volatile Memory configs[4];` declares 4 memory configs. Each one has the size and the alignment that the VME needs to load it: 112 words, aligned on 64 bytes. `configs[2]` is the third one.
- `volatile Memory one;` declares a single memory config.
- A `Memory` is declared where you need it, outside any function or inside one, as any variable of your program. A call of a kernel names it with `.memory` in the code that sees it, see [11.3.2](blocks.md#1132-the-memory-config-of-a-call).

**Rules:**

- `Memory` is always written with `volatile`, followed by a name. It declares a variable: it cannot be used in a parameter or in a cast.
- A `Memory` has no initializer: a `build` fills it.
- `static` and `extern` can be written in front of it, as in C. `vmegc` does not declare it in the other files: a file that uses a `Memory` defined in another file declares it with `extern`.
- Without `Memory`, a kernel has one memory config of its own, which a `build` fills and a `config` loads ([10.2](calling.md#102-the-actions)).

## 8.6 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [8.1](#81-the-buffer-keyword) | `Buffer must be volatile (volatile Buffer name[...])` | `Buffer` written without `volatile` |
| [8.1](#81-the-buffer-keyword) | `Buffer must be followed by a variable name (volatile Buffer name[...])` | `Buffer` with no name after it |
| [8.1](#81-the-buffer-keyword) | `Buffer only declares a variable, it cannot be used in a parameter or a cast` | `Buffer` in a parameter or in a cast |
| [8.2](#82-global-arrays) | `the array 'input' of a global load is not declared with Buffer in any file` | a global `.load` or `.store` (the message says `load` or `store`) that names an array declared with `Buffer` in no file |
| [8.3](#83-local-arrays) | `'x' is not declared with Buffer in the function marked with @kernel k at line N (local load)` | a local `.load` or `.store` whose array is not declared in the function marked with `@kernel` (the message says `load` or `store`) |
| [8.3](#83-local-arrays) | `'x' is not declared with Buffer in the function that contains the @kernel k block at line N (local load)` | the same, for a function that holds a block `@kernel k config \| exec { … }` |
| [8.4](#84-arrays-in-several-files) | `the array 'input' is already defined at data.vmeg.c line N` | an array defined in two files (the message starts with the second file) |
| [8.4](#84-arrays-in-several-files) | `the array 'input' of a global load is declared extern but defined in no file` | an `extern` array that no file of the project defines |
| [8.4](#84-arrays-in-several-files) | `the array 'input' of a global load is static in stat.vmeg.c line N, it cannot be used from another file` | a `static` array named by a kernel of another file |
| [8.5](#85-memory-configs) | `Memory must be volatile (volatile Memory name[...])` | `Memory` written without `volatile` |
| [8.5](#85-memory-configs) | `Memory must be followed by a variable name (volatile Memory name[...])` | `Memory` with no name after it |
| [8.5](#85-memory-configs) | `Memory only declares a variable, it cannot be used in a parameter or a cast` | `Memory` in a parameter or in a cast |
| [8.5](#85-memory-configs) | `a Memory cannot have an initializer` | a `Memory` declared with `= …` |
