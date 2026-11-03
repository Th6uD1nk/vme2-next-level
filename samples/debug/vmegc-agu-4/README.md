# agu-4 (WIP)

Finds what the registers `COUNT`, `INNER_0` and `FORMAT_0` of a read AGU do in the mode 4, with and without `repeat`, and what the AGU reads after its `COUNT`. Every kernel sets the read AGUs in a different way and reads two tables through them.

## Tables

Two tables of 32 words, loaded in `top0` and `top1`:

| Table | Buffer | Word `n` holds |
|---|---|---|
| `aguTableA` | `top0` | `n + 1` |
| `aguTableB` | `top1` | `100 * (n + 1)` |

A value read says which word of the table the AGU visited. The kernels read their inputs from `top0` and `top1` only: a pe writes its result in the `BASE` buffer of its number, so a table loaded in a `base` buffer would be overwritten by the results.

## Operation kernels

`pe0` reads `top0` and `top1` and writes `BASE_0`. `pe1` only binds the AGU of `top1` (`acc` has no `pe1`). The read AGUs have `count: 7` (8 words) and the write AGU `count: 23` (24 words), so the write goes 16 words past the read.

The id is `agu4-c7-<case>-<operation>`, and the case is left out for the first one.

| Case | Read AGU |
|---|---|
| (none) | no `inner0`, no `repeat` |
| `r4` | `inner0: { count: 3, step: 1 }` |
| `rep` | `repeat: true` |
| `i7` | `inner0: { count: 7, step: 1 }` |
| `i7-rep` | `inner0: { count: 7, step: 1 }` and `repeat: true` |
| `r4-rep` | `inner0: { count: 3, step: 1 }` and `repeat: true` |

| Operation | `.spad` of `pe0` |
|---|---|
| `add` | `top0 + top1` |
| `sub` | `top0 - top1` |
| `mul` | `top0 * top1` |
| `mac` | `mac(top0, top1)` |
| `acc` | `acc(top0)`, one input only |

## Copy kernels

`pe0` copies `top0` into `BASE_0` and `pe1` copies `top1` into `BASE_1`. Both read AGUs have the same parameters, the write AGUs have `count: 23`. A word of `BASE_0` is the index read in `aguTableA` plus 1, a word of `BASE_1` the index read in `aguTableB` plus 1, times 100.

The id is `agu4-copy-<kernel>`.

| Kernel | Read AGU |
|---|---|
| `none` | `count: 7` |
| `rep` | `count: 7`, `repeat: true` |
| `i1s1-rep` | `count: 7`, `inner0: { count: 1, step: 1 }`, `repeat: true` |
| `i3s1-rep` | `count: 7`, `inner0: { count: 3, step: 1 }`, `repeat: true` |
| `i5s1-rep` | `count: 7`, `inner0: { count: 5, step: 1 }`, `repeat: true` |
| `i7s1-rep` | `count: 7`, `inner0: { count: 7, step: 1 }`, `repeat: true` |
| `i9s3-rep` | `count: 7`, `inner0: { count: 9, step: 3 }`, `repeat: true` |
| `c6s2` | `count: 6`, `step: 2` |
| `c6s2-i3s1-rep` | `count: 6`, `step: 2`, `inner0: { count: 3, step: 1 }`, `repeat: true` |
| `c12s4` | `count: 12`, `step: 4` |
| `c12s4-i3s1-rep` | `count: 12`, `step: 4`, `inner0: { count: 3, step: 1 }`, `repeat: true` |
| `i1s2-rep` | `count: 7`, `inner0: { count: 1, step: 2 }`, `repeat: true` |
| `i3s2-rep` | `count: 7`, `inner0: { count: 3, step: 2 }`, `repeat: true` |

Two more kernels are written between `/*` and `*/` in the source: `agu4-copy-i2s1-rep` (`inner0: { count: 2, step: 1 }`) and `agu4-copy-i4s1-rep` (`inner0: { count: 4, step: 1 }`), both with `repeat: true`. They did not finish on the PSP.

## Results on the PSP

Measured on the PSP, each kernel played alone or in a program that holds all of them, with the same words every time.

| Kernels | After the `COUNT` |
|---|---|
| no `inner0`, no `repeat`; `repeat` alone; `inner0` alone | the AGU holds the last word it read |
| `add`, `sub`, `mul` | the result of the last operands is written again |
| `mac`, `acc` | the last total is written again |
| `inner0` of `count` 3, 5, 7, 9 (`step: 3`), 1 (`step: 2`) or 3 (`step: 2`), with `repeat` | the AGU reads again from the first word of the `COUNT` range, every `count / step + 1` words |
| `inner0` of `count` 1 and `step` 1, with `repeat` | the AGU holds the last word it read |
| `mac`, `acc` with `inner0` and `repeat` | the total goes on at each period |
| `inner0` of `count` 2 or 4 and `step` 1, with `repeat` | the kernel does not finish |

`COUNT` is the `count` of the read AGU, with its `step`.

## Running on the PSP

```
cd samples/vmeh && mkdir build && cd build
cmake -DVMEH_SOURCE=samples/debug/vmegc-agu-4/agu-4.vmeg.cpp -DVMEH_ID=agu4-c7-add ..
make
```

`-DVMEH_ID` keeps one kernel. Without it, the program has all of them: the first one runs at the start and Right goes to the next one. `log.txt` holds the dump of the current kernel and its first line says which one. `BASE 0` holds the words of `pe0`, `BASE 1` the words of `pe1` (the copy kernels). Copy `log.txt` before moving to the next kernel.

## Emulator

```
python3 vmeemu.py --run agu4-c7-add samples/debug/vmegc-agu-4/agu-4.vmeg.cpp
```

With the current version of `vmee`, the words are not the same as on the PSP for the kernels that read after the `COUNT` with `mac`, `acc` or a `step`, and for the kernels with `inner0` and `repeat`, except the ones with `inner0: { count: 7, step: 1 }`.
