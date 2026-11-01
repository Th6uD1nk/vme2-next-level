# agu-2 (WIP)

Finds what the registers `COUNT` and `INNER_0` of a read AGU do in the mode 2, and compares the mode 2 with the mode 4. Every kernel sets a read AGU in a different way, reads the same table through it and writes what it reads.

## Kernels

The table has 32 words: the word `n` holds `n + 1`, so a value read says which word of the table the AGU visited.

| Id | AGU | `COUNT` | Ring (`inner0`) | `repeat` | Other |
|---|---|---|---|---|---|
| `agu2-c7-r4` | `Agu(2)` | 7 | 4 words, step 1 | yes | |
| `agu2-c5-r4` | `Agu(2)` | 5 | 4 words, step 1 | yes | |
| `agu2-c3-r8` | `Agu(2)` | 3 | 8 words, step 1 | yes | |
| `agu2-c0-r4` | `Agu(2)` | 0 | 4 words, step 1 | yes | |
| `agu2-c15-r4` | `Agu(2)` | 15 | 4 words, step 1 | yes | |
| `agu2-c7-r4-s2` | `Agu(2)` | 7 | 4 words, step 2 | yes | |
| `agu2-c7-r4-no-repeat` | `Agu(2)` | 7 | 4 words, step 1 | no | |
| `agu2-c7-no-inner` | `Agu(2)` | 7 | none | no | |
| `agu2-c7-r4-offset3` | `Agu(2)` | 7 | 4 words, step 1 | yes | `offset: 3` |
| `agu4-c7-r4` | `Agu` | 7 | 4 words, step 1 | yes | |
| `agu4-c5-r4` | `Agu` | 5 | 4 words, step 1 | yes | |
| `agu4-c0-r4` | `Agu` | 0 | 4 words, step 1 | yes | |
| `agu4-c7-no-inner` | `Agu` | 7 | none | no | |

`COUNT` is the `count` of the AGU. A ring of 4 words is `inner0: { count: 3, step: 1 }`.

## Results

`pe0` reads `TOP_0` through the AGU and writes it in `BASE_0`, words 0 to 23 (the write AGU has `count: 23`). The window of 32 words, the default, shows all of them.

## Running on the PSP

```
cd samples/vmeh && mkdir build && cd build
cmake -DVMEH_SOURCE=samples/debug/vmegc-agu-2/agu-2.vmeg.cpp -DVMEH_ID=agu2-c5-r4 ..
make
```

`-DVMEH_ID` keeps one kernel. Without it, the program has all of them: the first one runs at the start and Right goes to the next one. `log.txt` holds the dump of the current kernel and its first line says which one. Copy it before moving to the next kernel.

## Emulator

```
python3 vmeemu.py --run agu2-c5-r4 samples/debug/vmegc-agu-2/agu-2.vmeg.cpp
```
