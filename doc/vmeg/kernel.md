[Index](../VMEG.md) · [The language](language.md) · [AGU variables](agu.md)

# The kernel

## Contents

- [3.1 Header](#31-header)
- [3.2 Modes](#32-modes)
  - [3.2.1 direct](#321-direct)
  - [3.2.2 memory](#322-memory)
  - [3.2.3 extended](#323-extended)
  - [3.2.4 pipeline](#324-pipeline)
- [3.3 Body](#33-body)
  - [3.3.1 Statements](#331-statements)
  - [3.3.2 Scope of the variables](#332-scope-of-the-variables)
  - [3.3.3 Order of the writes](#333-order-of-the-writes)
  - [3.3.4 Parameters](#334-parameters)
- [3.4 Interconnect registers](#34-interconnect-registers)
- [3.5 Errors](#35-errors)

## 3.1 Header

```c
.kernel name mode {
  …
}
```

**Explanation of the code above:**

- `name` is the name of the kernel. It is unique in the project: two kernels with the same name, in the same file or in two files, are an error.
- `mode` is `direct`, `memory`, `extended` or `pipeline` ([3.2](#32-modes)). It is compulsory and there is only one.
- A kernel is written at the top level of a file, not inside a function. `.context` is a synonym of `.kernel` ([2.8](language.md#28-synonyms)).
- A kernel that no `@kernel` calls, in any file of the project, is an error: see [Calling a kernel](calling.md).

## 3.2 Modes

The body of a kernel is the same across `direct`, `memory` and `extended` (except `.pe4`..`.pe7` and `top4`..`base7` in `extended`), while `pipeline` replaces PE blocks with a `.flow { … }` block ([3.2.4](#324-pipeline)). The mode says where the registers of the kernel are written.

| | `direct` | `memory` | `extended` | `pipeline` |
|---|---|---|---|---|
| The registers are written | in the VME | in a context in RAM, which is then sent to the VME | in the VME across up to two passes | in the VME across as many passes as needed |
| The VME gets them | when the kernel is called with `config` | when the context is sent, by `config` after `build` | when called with `config`, chaining Pass 1 and Pass 2 automatically | when called with `config \| exec`, running all passes automatically |
| A register that the kernel does not write | keeps its value | is 0: a loaded context replaces all the registers | keeps its value, while Pass 1 registers unused in Pass 2 are reset to 0 between passes | is set by `vmegc` for each pass |

```c
.kernel add direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}
```

Replace `direct` with `memory` and the same kernel is a memory kernel. Your file must include `<me-core-mapper/vme-fu-opcodes.h>`: `vmegc` does not add it.

### 3.2.1 direct

A direct kernel writes its registers in the VME. The registers that it does not write keep the value they have.

### 3.2.2 memory

A memory kernel is written in a context in RAM (`build`), then the context is sent to the VME (`config`), see [Calling a kernel](calling.md).

- Loading a context replaces all the registers: the ones that the kernel does not write are 0.

### 3.2.3 extended

An extended kernel compiles as a `direct` kernel across up to two chained passes: `.pe0` to `.pe3` run in Pass 1 (scratchpad words `0` to `1023`), and `.pe4` to `.pe7` run in Pass 2 (words `1024` to `2047`, automatic `+ 0x400` offset).

- When both passes are active, `vmegc` emits `vmeLibProcessAsync();` and `_vmeLibStart();` between Pass 1 and the Pass 2 register delta. Calling `@kernel name config | exec` emits `vmeLibStart();` before the kernel call and closes with `vmeLibProcessAsync();` and `vmeLibFinishAsync();`.
- `Staging` variables written in Pass 1 can be read in Pass 2 (`vmegc` bridges them through the low half of `base0`..`base3` automatically); reading Pass 2 staging values from Pass 1 and redirecting outputs with `.spad[n]` are rejected.

### 3.2.4 pipeline

A pipeline kernel schedules a dataflow graph inside a single `.flow { … }` block across as many hardware passes as needed:

```c
.kernel pipe pipeline {
  Transfer ta = { memory: in0, count: 15 }, dst = { memory: out0, count: 15 };
  .load { .transfer = ta; .scope = global; .offsets { .top0 = 0; } }
  .flow {
    .count = 15;
    Slot tap = (top0 & 0xff) >> 1;
    .slot = top0 + tap;
    for i in 0..7 { .slot = slot + 1; }
  }
  .store { .transfer = dst; .scope = global; }
}
```
- `.flow` requires `.count = N` (`0` to `1023`, up to 1024 words) and at least one `.slot = expr;` statement (`slot` reads the previous `.slot`; `Slot` variables and `Slot` arrays hold named intermediates).
- `vmegc` places the operations, sets the AGUs and routes the results across passes by itself.
- `Agu`, `Staging`, `.pe0`..`.pe7`, `pe[i]`, `.regs`, `.params` and `icn` are not used in a `pipeline` kernel, and `.store` takes no `.offsets` (`vmegc` stores the final `.slot` result automatically).

## 3.3 Body

The body of a kernel (.kernel) describes what the VME computes and moves. It holds vmeg statements only, no C.

### 3.3.1 Statements

| Statement | What it does | Page |
|---|---|---|
| `Int name = expression;` | names a number | [2.4](language.md#24-int) |
| `Agu name = { … };`, `Agu(2) name = { … };` | declares an address generator, in the mode 4 or in the mode 2 | [AGU variables](agu.md) |
| `Staging name;` | declares a result kept in a pe | [Staging, routing and warnings](staging-routing.md) |
| `Transfer name = { … };`, `Transfer(Words) name = { … };` | declares a DMAC transfer, basic or with the AGUs of the DMAC on | [Transfers](transfers.md) |
| `.pe0 { … }` to `.pe3 { … }` (`.pe7` in `extended`), `pe[i] { … }` | describes a processing element | [Processing elements](pe.md) |
| `.flow { .count = …; .slot = …; }` | describes the dataflow of a `pipeline` kernel | [3.2.4](#324-pipeline) |
| `Slot name;`, `Slot name = …;` | declares a named intermediate in a `pipeline` kernel | [2.2](language.md#22-variables) |
| `.load { … }`, `.store { … }` | moves data between the RAM and the scratchpad | [Transfers](transfers.md) |
| `icn xpcr = …, skew = …;` | writes the interconnect registers | [3.4](#34-interconnect-registers) |
| `.params { … }` | declares the parameters of the kernel | [3.3.4](#334-parameters) |
| `for p in a..b { … }` | repeats statements | [2.7](language.md#27-loops) |

### 3.3.2 Scope of the variables

A variable declared in a kernel can only be used inside that kernel. Two kernels can each declare a variable with the same name: they are two different variables.

```c
.kernel add direct {
  Agu t = { count: 15 };
  .pe0 { .top = t; .spad = top0 + top0; }
}

.kernel sub direct {
  Agu t = { count: 7 };
  .pe0 { .top = t; .spad = top0 + top0; }
}
```

### 3.3.3 Order of the writes

The registers are written in the order of the statements. The routing of the buffers and the enabling of the outputs of the pes that hold two operations, which `vmegc` works out from the kernel, are written last.


### 3.3.4 Parameters

A kernel can take parameters: values that the call gives to it, instead of values written in the kernel.

```c
.kernel shifted memory {
  .params { int start; int* table; }
  Agu t = { count: 15, offset: start }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}
```

**Explanation of the code above:**

- `.params { int start; int* table; }` declares two parameters. Each one is written like a C declaration: a C type, then a name, then `;`.
- `start` is used as a value of the kernel, here the offset of the AGU `t`. The call gives the value, so the same kernel can be called with several values.
- The kernel is called in a block that gives the values, see [11.3.1](blocks.md#1131-the-params-of-a-call).

**Rules:**

- A kernel has one `.params`. It can be written anywhere in the body.
- The type is any C type, for example `int`, `int*` or a type of your program. An array is not a parameter: use a pointer.
- A name is declared once in a `.params`.
- A parameter can stand wherever a name that `vmegc` does not know can stand ([2.6](language.md#26-numbers-macros-and-unknown-names)): the numbers of an `Agu` (`count`, `offset`, `step`, `inner0`, `cyc`, `bubbles`) and of a `Transfer`. It is written as it is and not checked. The parameters that are `true` or `false` of an `Agu` (`reverse`, `repeat`, `sync`) cannot be a parameter of the kernel.


## 3.4 Interconnect registers

`icn` defines the values of the `xpcr` and `skew` registers of the interconnect.

```c
icn xpcr = 5, skew = 0x10;
```

| Register | Role |
|---|---|
| `xpcr` | cross pack control register: unpack on read, pack on write |
| `skew` | stream router with skew |

- The two can be written in one statement or in two. Each one at most once in a kernel.
- The value is a number, an expression ([2.5](language.md#25-expressions)) or a name that `vmegc` does not know ([2.6](language.md#26-numbers-macros-and-unknown-names)). It is written as it is and not checked.
- The other interconnect registers, the routing of the buffers and the outputs of the pes that hold two operations, are not written with `icn`: they are set from the kernel, see [Staging, routing and warnings](staging-routing.md).

## 3.5 Errors

| Section | Message | Cause |
|---|---|---|
| [3.1](#31-header) | `the kernel 'k' is already defined at file line N` | two kernels with the same name in the project |
| [3.1](#31-header) | `kernel 'k' is never called, add a function marked with @kernel k config \| exec …` | no `@kernel` calls the kernel |
| [3.2](#32-modes) | `unknown kernel option 'wrong' (direct, memory, extended, pipeline)` | a mode other than `direct`, `memory`, `extended` or `pipeline` |
| [3.2](#32-modes) | `duplicate kernel option 'direct'` | the same mode written twice |
| [3.2](#32-modes) | `a kernel is either direct or memory, not both` | both modes |
| [3.2](#32-modes) | `kernel 'k' needs the option direct or memory` | no mode |
| [3.3](#33-body) | `unknown statement 'int'` | a statement that is not a vmeg statement, such as C code |
| [3.3.2](#332-scope-of-the-variables) | `unknown Agu variable 't'` | a variable of another kernel (the message names the type) |
| [3.4](#34-interconnect-registers) | `duplicate interconnect 'xpcr'` | the same register written twice |
| [3.4](#34-interconnect-registers) | `unknown interconnect 'foo' (xpcr, skew)` | a register other than `xpcr` and `skew` |
| [3.1](#31-header) | `a kernel is written at the top level of a file, not inside a function` | a `.kernel` or a `.context` written inside a function |
| [3.1](#31-header) | `unterminated block` | a `{` of a kernel that is never closed |
| [3.3.4](#334-parameters) | `the parameters of the kernel are declared twice` | two `.params` in the same kernel |
| [3.3.4](#334-parameters) | `the parameter 'start' is declared twice` | the same name twice in a `.params` |
| [3.3.4](#334-parameters) | `a parameter is a C type and a name, for example 'int stage;'` | an entry with no type, or an array |
| [3.3.4](#334-parameters) | `expected ';'` | an entry of a `.params` without its `;` |
