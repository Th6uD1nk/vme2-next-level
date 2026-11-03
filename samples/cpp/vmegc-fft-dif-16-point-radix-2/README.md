# fft-dif-16-point-radix-2

A port in vmeg of the `fft-dif-16-point-radix-2` sample of `me-vme-samples`: a 16-point FFT, radix 2, decimation in frequency, in four stages, computed on the VME. It builds an EBOOT.

## Files

| File | Content |
|---|---|
| `fft-dif-16-point-radix-2.vmeg.cpp` | the data, the kernels `butterfly` and `lowerLeg`, the loop of the Media Engine and the program of the CPU |
| `CMakeLists.txt` | the project, translated by `vmegc` ([VMEG](../../../doc/VMEG.md)) |

## Building

```
cd samples/cpp/vmegc-fft-dif-16-point-radix-2
mkdir build && cd build
cmake ..
make
```

`PSPDEV` is set, like for the other samples. The EBOOT is in `build`.

## Running

The screen shows the counter of the Media Engine, the 16 real parts and the 16 imaginary parts of the result, and the index of the input signal. Triangle goes to the next signal and Cross to the previous one, from 0 to 7. HOME exits.

## Program

- `butterfly` and `lowerLeg` are two memory kernels. Each is built four times, once for each stage, in the arrays `butterflyConfigs` and `lowerLegConfigs`.
- The block `@emulate "fft-4-stages"` is the loop of the Media Engine. It builds the eight configs, loads the twiddles once, then for each FFT runs the stage 0 and the stages 1 to 3.
- The stages 1 to 3 are a C loop marked `@unroll`: the program has one copy of it, and the emulator plays three ([13.5](../../../doc/vmeg/emulation.md#135-c-loops-marked-unroll)).
- The output of a stage is stored in the eDRAM, at `0x40000000` for the real parts and `0x40000080` for the imaginary parts, and the next stage loads it from there.
- Each stage enables the VME in its first call and disables it in its last one, so four times for each FFT. The original sample does it once for each FFT.

## Data

The arrays are `Buffer(Q4.20)`: a word holds a value with 20 fractional bits, so 1.0 is `0x100000`.

| Array | Words | Content |
|---|---|---|
| `fftTwiddleReal`, `fftTwiddleImag` | 15 each | the twiddle factors of the four stages one after the other: 8 for the first stage, then 4, 2 and 1 |
| `fftReal0` to `fftReal7` | 32 each | an input signal: 16 values, then 16 zeros |
| `fftImag` | 32 | the imaginary part of the input, all zero |

The eight signals are the ones of [`samples/c/fft-dif-16-point-radix-2`](../../c/fft-dif-16-point-radix-2/README.md).

## Emulation

```
python3 vmeemu.py --run fft-4-stages samples/cpp/vmegc-fft-dif-16-point-radix-2/fft-dif-16-point-radix-2.vmeg.cpp --use signal=fftReal3
```

`--use` gives the pointer `signal` the array of the input ([1.7.1](../../../doc/vmee/running.md#171-pointers)).

## Result

For the eight signals, the 32 words of the result (16 real, 16 imaginary) are the same on the PSP as the ones of the original sample, and the same in `vmee`.
