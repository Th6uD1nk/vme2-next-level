# fu-bit6 (WIP)

Finds what the bit 6 of the register of a FU does. Every kernel computes the same operation with the bit and without it, on the same inputs, and the two results are compared.

`round(…)` sets the bit 6 of the operation it wraps.

## Kernels

| Id | What it checks |
|---|---|
| `fu-bit6-on` | `+`, `-` and `*` with a shift of 1, 1, 2 and 4, the bit set on the four PEs |
| `fu-bit6-off` | the same operations, the bit not set |
| `fu-bit6-fft-mul` | `*` with the opcode `0x220` and a shift of 20, as the FFT multiplies by the twiddles |
| `fu-bit6-fft-legs` | `+` and `-` with a shift of 1, as the legs of the FFT butterfly |
| `fu-bit6-fft-noshift` | `+` and `-` with no shift: the bit alone |
| `fu-bit6-fft-chain` | a multiplication on two PEs, then a subtraction on the secondary FU, the bit on the three |
| `fu-bit6-fft-chain-split` | the same chain, the bit on the multiplications only, then on the subtraction only |
| `fu-bit6-shift-2`, `-3`, `-8` | `+` with a shift of 2, 3 and 8, on positive and negative values around the middle of each step |
| `fu-bit6-limits` | `+` with a shift of 1 and `*` with a shift of 20, on values at the limits of the 24 bits |
| `fu-bit6-limits-sat` | `+` with `sat` and a shift of 1 and 2, on values at the border of the saturation |
| `fu-bit6-sub-ofb-k0`, `-k1` | `a - b + c` (`0x048`) with `c` = 7 and -7, with no shift and with a shift of 1 |
| `fu-bit6-sub-inv-k0`, `-k1` | the same with the opcode `0x034` (`.remap` of the `+`), `c` in the register A |
| `fu-bit6-sub-shr-a` | `b - (a >> 2)` (`0x050`), with no shift and with a shift of 1 after it |
| `fu-bit6-sub-shr-b` | `b - (a >> n)` with `n` = 1 and 3, no shift after it |

## Results

Each PE writes its result in `BASE_p`, words 0 to 15. The inputs are in the words 16 to 31 of the same buffer.

In every kernel except `fu-bit6-on` and `fu-bit6-off`, the PEs work by pairs on the same inputs:

| PE | Bit 6 | Result in |
|---|---|---|
| `pe0` | set | `BASE_0` |
| `pe1` | not set | `BASE_1` |
| `pe2` | set | `BASE_2` |
| `pe3` | not set | `BASE_3` |

In `fu-bit6-fft-chain` and `fu-bit6-fft-chain-split`, a chain uses two PEs: the result of the first chain is in `BASE_1`, the one of the second chain is in `BASE_3`.

## Running on the PSP

```
cd samples/vmeh && mkdir build && cd build
cmake -DVMEH_SOURCE=samples/debug/vmegc-fu-bit6/fu-bit6.vmeg.cpp -DVMEH_ID=fu-bit6-shift-2 ..
make
```

`-DVMEH_ID` keeps one kernel. Without it, the program has all of them: the first one runs at the start and Right goes to the next one. `log.txt` holds the dump of the current kernel and its first line says which one. Copy it before moving to the next kernel.

## Emulator

```
python3 vmeemu.py --run fu-bit6-off samples/debug/vmegc-fu-bit6/fu-bit6.vmeg.cpp
```

The emulator plays the 18 kernels. `round` rounds the shift of an addition, of `a - b` and of a product to the nearest, a half goes up. On `subacst`, `subshr` and `(a >> n) - b` it changes nothing. On any other opcode the emulator refuses it.
