# vmee

**vmee** is the first emulator designed for the execution and the debugging of VME kernels, through the vmeg language. It plays a kernel written in a `.vmeg.c` or `.vmeg.cpp` file on a model of the VME, and shows the content of the buffers, without a PSP.

**vmeh** writes the program that runs the same kernels on the PSP. It writes the content of the buffers in the same format as vmee, so that the two results can be compared.

A quick example, a kernel marked for the emulator, and the command that plays it:

```c
// main.vmeg.cpp
@emulate "add-test"
.kernel add direct {
  Agu t = { count: 15 }, w = { count: 15, cyc: auto };
  .pe0 { .top = t; .write = w; .spad = top0 + top0; }
}

@kernel add config | exec
void run(void) {
}
```

```
vmee --run add-test main.vmeg.cpp
```

## Contents

| | Page | What it covers |
|---|---|---|
| 1 | [Running vmee](#1-running-vmee) | `--run`, several files, the window of the buffers, `--trace`, `--compat` |
| 2 | [Traces](#2-traces) | the trace file, the lines `W` and `M` |
| 3 | [Running on the PSP with vmeh](#3-running-on-the-psp-with-vmeh) | the build, the kernels, `config.txt`, `log.txt`, the comparison with vmee |
| 4 | [Memories](#4-memories) | the scratchpad, the stagings, the RAM |
| 5 | [The DMAC](#5-the-dmac) | the registers, the context, the transfers |
| 6 | [Datapath registers](#6-datapath-registers) | the 106 registers and the trigger |
| 7 | [The AGUs](#7-the-agus) | the modes, the registers, the read and write AGUs |
| 8 | [Routing](#8-routing) | the interconnect registers |
| 9 | [The FUs](#9-the-fus) | the register of a FU, the opcodes, the saturation |
| 10 | [The pipeline](#10-the-pipeline) | the cycles from the buffers to the scratchpad |
| 11 | [A run seen from the program](#11-a-run-seen-from-the-program) | the steps of a program, from the enable to the disable |
| 12 | [Errors](#12-errors) | where the messages of vmee are listed, by page |

## 1. Running vmee

Details: [Running vmee](vmee/running.md)

## 2. Traces

Details: [Traces](vmee/traces.md)

## 3. Running on the PSP with vmeh

Details: [Running on the PSP with vmeh](vmee/vmeh.md)

## 4. Memories

Details: [Memories](vmee/memories.md)

## 5. The DMAC

Details: [The DMAC](vmee/dmac.md)

## 6. Datapath registers

Details: [Datapath registers](vmee/registers.md)

## 7. The AGUs

Details: [The AGUs](vmee/agu.md)

## 8. Routing

Details: [Routing](vmee/routing.md)

## 9. The FUs

Details: [The FUs](vmee/fu.md)

## 10. The pipeline

Details: [The pipeline](vmee/pipeline.md)

## 11. A run seen from the program

Details: [A run seen from the program](vmee/run.md)

## 12. Errors

Details: [Errors](vmee/errors.md)
