# fu-bit6 (WIP)

Finds what the bit 6 of the register of a FU does. Two kernels have the same inputs and the same operations. The kernel `fu-bit6-on` sets the bit 6 on its four PEs (`zsm(…)`), the kernel `fu-bit6-off` does not. The outputs of the two are compared.

Each PE has its own pair of inputs, `TOP_p` and `BASE_p`, and writes its result in `BASE_p`, words 0 to 15:

| PE | Operation | Inputs |
|---|---|---|
| `pe0` | `top0 + base0 >> 1` | small values around 0 |
| `pe1` | `top1 - base1 >> 1` | odd and even values, positive and negative |
| `pe2` | `top2 + base2 >> 2` | values of 24 bits and small values |
| `pe3` | `top3 * base3 >> 4` | small values, positive and negative |

The `TOP_p` inputs are loaded at the word 0 of their buffer. The `BASE_p` inputs are loaded at the word 16, so they are not overwritten by the outputs: in `log.txt`, the words 0 to 15 of each `BASE` are the outputs and the words 16 to 31 are the inputs.

`zsm` is the name of `fu_zsm` in the library: it is provisional, it sets the bit 6 of the operation it wraps, and it is not in the documentation until the behavior is known.

PSP, with vmeh:
```
cd samples/vmeh && mkdir build && cd build
cmake -DVMEH_SOURCE=samples/debug/vmegc-fu-bit6/fu-bit6.vmeg.cpp ..
make
```

The program has the two kernels: `001 - fu-bit6-on` runs at the start, Right goes to `002 - fu-bit6-off`. `log.txt` holds the dump of the current kernel, and its first line says which one. Copy it before moving to the other one.

Emulator (the kernel with the bit is refused, the emulator does not model the bit with a shift):
```
python3 vmeemu.py --run fu-bit6-off samples/debug/vmegc-fu-bit6/fu-bit6.vmeg.cpp
```
