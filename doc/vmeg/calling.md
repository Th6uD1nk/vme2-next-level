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
- A kernel that declares parameters ([3.3.4](kernel.md#334-parameters)) is called in a block, which gives the values ([11.3.1](blocks.md#1131-the-params-of-a-call)).
- Every kernel of the project is called at least once, by a function or by a block. A kernel that nothing calls is an error ([10.6](#106-errors)).
- The kernel can be defined in another file of the project ([1.2](running.md#12-several-files)).
- `@context` is a synonym of `@kernel` ([2.8](language.md#28-synonyms)).

## 10.2 The actions

After the name of the kernel, the call gives what to do with it. An action is one of these words:

| Action | What it does |
|---|---|
| `build` | builds the context of a `memory` kernel in RAM. It does not touch the VME. |
| `config` | writes the kernel to the VME: a `direct` kernel writes its registers, a `memory` kernel loads its context (built first if no `build` was done). It does not run it. |
| `exec` | starts the run of the kernel that is configured and waits for its end. |
| `async` | starts the run and does not wait for its end. |

```c
@kernel add config
void setup(void) {
}

@kernel add exec
void go(void) {
}
```

**Explanation of the code above:**

- `setup` configures the kernel `add` and `go` runs it. Two functions can each call the same kernel with their own actions.

**Rules:**

- `build` is for a `memory` kernel. For a `direct` kernel it is an error ([10.6](#106-errors)).
- `exec` and `async` run what the VME holds: the kernel must have been configured before, by a `config` of this call or of an earlier one.
- With `async` the results are not ready when the call returns. A kernel that has a `.store` cannot be called with `async` alone ([10.6](#106-errors)).
- The actions can be given together, as `config | exec` ([10.3](#103-several-actions-in-one-call)).

## 10.3 Several actions in one call

The actions are written together with `|`.

```c
@kernel add config | exec
void run(void) {
}
```

| Call | What it does |
|---|---|
| `config \| exec` | configures the kernel, runs it and waits for its end |
| `config \| async` | configures the kernel and starts the run without waiting for its end. Calls of this kind that follow each other are one series: the end is awaited once, after the last one |
| `build \| config` | builds the context of a `memory` kernel, then loads it |
| `build \| config \| exec` | builds the context, loads it, runs the kernel and waits for its end |
| `build \| config \| async` | builds the context, loads it and starts the run without waiting |

**Rules:**

- The order of the actions does not matter: `exec | config` is the same as `config | exec`.
- `exec` and `async` cannot be given together: they are two different executions ([10.6](#106-errors)).
- `build` is for a `memory` kernel, in a call with other actions as well.
- In a series of `config | async`, each kernel is configured while the previous one runs, and the end of the last run is awaited once.

## 10.4 Several kernels in one call

A call can name several kernels, separated by commas. Each kernel has its own actions.

```c
@kernel a config | exec, b config | exec
void run(void) {
}
```

**Explanation of the code above:**

- `run` configures and runs `a`, then configures and runs `b`, in the order written.
- The VME is enabled once for the whole call, not once for each kernel.

**Rules:**

- Every name of the list is a kernel of the project. An unknown name is an error ([10.6](#106-errors)).
- A kernel can appear several times in a call, or in several calls, with different actions: `@kernel a build, b build` builds two contexts, and a later call configures and runs them.
- `exec` and `async` do not choose a kernel: they run the one that the VME holds, which is the last one configured. After `a config, b config`, an `exec` runs `b`.

## 10.5 Uploads and downloads around the run

A kernel can copy arrays to the VME before it runs, with `.load`, and copy buffers back after, with `.store` ([9.3](transfers.md#93-load-and-store)). The call does these copies around the actions.

```c
volatile Buffer input[16];
volatile Buffer result[16];

.kernel k direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  Transfer in = { type: words, mode: basic, memory: input, count: 15 };
  Transfer out = { type: words, mode: basic, memory: result, count: 15 };
  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
  .store { .transfer = out; .scope = global; .offsets { .base0 = 0; } }
}

@kernel k config | exec
void run(void) {
}
```

**Explanation of the code above:**

- `run` copies `input` into the buffer `top0` first, and waits for the copy to finish.
- `config | exec` configures the kernel, runs it and waits for its end.
- `run` then copies the buffer `base0` into `result`, and waits for the copy to finish.

**Rules:**

- Every call does the `.load` of the kernel first and its `.store` last, whatever the actions are.
- A call with `config` alone does the `.store` too: it copies what the buffers hold, the kernel has not run.
- A call made of `build` alone does neither: it does not touch the VME.
- A kernel that has a `.store` cannot be called with `async` alone ([10.2](#102-the-actions)).

## 10.6 Errors

The messages start with `line N:`, left out here.

| Section | Message | Cause |
|---|---|---|
| [10.1](#101-the-call-of-a-kernel) | `kernel 'k' is never called, add a function marked with @kernel k config \| exec or a block @kernel k config \| exec { ... }` | a kernel that no function and no block calls |
| [10.1](#101-the-call-of-a-kernel) | `@kernel refers to an unknown kernel 'zz' (kernels: k)` | a name in the call that is not a kernel of the project. The message lists the kernels, or says that there is none |
| [10.2](#102-the-actions) | `expected build, config, exec or async after the kernel name` | a kernel name with no action after it |
| [10.2](#102-the-actions) | `expected an action after \|` | a word after `\|` that is not an action |
| [10.2](#102-the-actions) | `build is for a memory kernel, kernel 'k' is direct` | `build` on a `direct` kernel |
| [10.2](#102-the-actions) | `async does not wait for the end of the run, the .store of kernel 'k' would read unfinished data` | `async` alone on a kernel that has a `.store` |
| [10.3](#103-several-actions-in-one-call) | `exec and async are two different executions, they cannot be combined` | `exec` and `async` in the same call of a kernel |
| [10.1](#101-the-call-of-a-kernel) | `the kernel 'k' needs the parameter n, write the call as a block with a .params` | a kernel that declares parameters, called above a function (the message lists all the ones that are missing) |
