# fft-dif-16-point-radix-2

A port in vmeg of the `fft-dif-16-point-radix-2` sample of `me-vme-samples`: a 16-point FFT, radix 2, decimation in frequency, in four stages, computed on the VME.

## Files

| File | Content |
|---|---|
| `fft-dif-16-point-radix-2.vmeg.c` | the data, the two kernels `butterfly` and `lowerLeg`, and the emulation `fft-4-stages` |

The file has no `main` and no CMake project. `vmee` plays the emulation, and `vmeh` builds a program of it for the PSP ([VMEE](../../../doc/VMEE.md)).

## Data

The arrays are `Buffer(Q4.20)`: a word holds a value with 20 fractional bits, so 1.0 is `0x100000`.

| Array | Words | Content |
|---|---|---|
| `fftTwiddleReal`, `fftTwiddleImag` | 15 each | the twiddle factors of the four stages one after the other: 8 for the first stage, then 4, 2 and 1 |
| `fftReal0` to `fftReal7` | 32 each | an input signal: 16 values, then 16 zeros |
| `fftImag` | 32 | the imaginary part of the input, all zero |
| `fftStageReal`, `fftStageImag` | 32 each | the result of a stage, which the next stage reads |

The eight signals, 16 values each:

| Array | Values |
|---|---|
| `fftReal0` | 1.0 sixteen times |
| `fftReal1` | 1.0, then 15 zeros |
| `fftReal2` | 1.0 at the word 4, zero elsewhere |
| `fftReal3` | 1.0, 0.924, 0.707, 0.383, 0.0, -0.383, -0.707, -0.924, -1.0, -0.924, -0.707, -0.383, 0.0, 0.383, 0.707, 0.924 |
| `fftReal4` | 1.0, 0.707, 0.0, -0.707, -1.0, -0.707, 0.0, 0.707, then the same again |
| `fftReal5` | 1.0, -1.0, 1.0, -1.0, and so on |
| `fftReal6` | 0.0, 0.383, 0.707, 0.924, 1.0, 0.924, 0.707, 0.383, 0.0, -0.383, -0.707, -0.924, -1.0, -0.924, -0.707, -0.383 |
| `fftReal7` | 2.0, 1.307, 0.0, -0.541, 0.0, 0.541, 0.0, -1.307, then the same values with the opposite sign |
