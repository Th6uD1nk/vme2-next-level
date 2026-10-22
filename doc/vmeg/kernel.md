[Index](../VMEG.md) · [The language](language.md) · [AGU variables](agu.md)

# The kernel

## Contents

- [3.1 Header](#31-header)
- [3.2 Modes](#32-modes)
  - [3.2.1 direct](#321-direct)
  - [3.2.2 memory](#322-memory)
- [3.3 Body](#33-body)
  - [3.3.1 Statements](#331-statements)
  - [3.3.2 Scope of the variables](#332-scope-of-the-variables)
  - [3.3.3 Order of the writes](#333-order-of-the-writes)
- [3.4 Interconnect registers](#34-interconnect-registers)
- [3.5 Errors](#35-errors)

## 3.1 Header

```c
.kernel name mode {
  …
}
```

- `name` is the name of the kernel. It is unique in the project: two kernels with the same name, in the same file or in two files, are an error.
- `mode` is `direct` or `memory` ([3.2](#32-modes)). It is compulsory and there is only one.
- A kernel is written at the top level of a file, not inside a function. `.context` is a synonym of `.kernel` ([2.8](language.md#28-synonyms)).
- A kernel that no `@kernel` calls, in any file of the project, is an error: see [Calling a kernel](calling.md).

## 3.2 Modes

The body of a kernel is the same in both modes. The mode says where the registers of the kernel are written.

| | `direct` | `memory` |
|---|---|---|
| The registers are written | in the VME | in a context in RAM, which is then sent to the VME |
| The VME gets them | when the kernel is called with `config` | when the context is sent, by `config` after `build` |
| A register that the kernel does not write | keeps its value | is 0: a loaded context replaces all the registers |

```c
.kernel add direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: 6 };
  .pe0 { .top = t; .write = w; .top0 + top0; }
}
```

Replace `direct` with `memory` and the same kernel is a memory kernel. The names of the operations (`OP_ADD`, …) come from `<me-core-mapper/vme-fu-opcodes.h>`: the file includes it.

### 3.2.1 direct

A direct kernel writes its registers in the VME. The registers that it does not write keep the value they have.

### 3.2.2 memory

A memory kernel is written in a context in RAM (`build`), then the context is sent to the VME (`config`), see [Calling a kernel](calling.md).

- Loading a context replaces all the registers: the ones that the kernel does not write are 0.
- The writes of a direct kernel that come after the load are applied on top of the loaded context.
