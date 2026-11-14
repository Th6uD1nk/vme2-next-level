# vmegc-spad-redirect

A sample demonstrating crossbar `.spad[n]` output redirection in `vmegc`. Processing elements redirect their ALU outputs to arbitrary base scratchpad buffers (`BASE_0`..`BASE_3`) through the interconnect while keeping untouched buffers intact, supporting `for` loop bank rotation as well as positive and negative write AGU offsets.

## Files

| File | Content |
|---|---|
| `spad-redirect.vmeg.cpp` | the input buffers, the `.spad[n]` kernels (`runSpadRedirect`, `runRotateSpad`, `runOffsetPos`, `runOffsetNeg`), and the PSP display program |
| `CMakeLists.txt` | the CMake build configuration |

## Building

```
cd samples/debug/vmegc-spad-redirect
mkdir build && cd build
cmake ..
make
```

`PSPDEV` is set, like for the other samples. The EBOOT is in `build`.

## Emulation

To test the kernels on the emulator:

```
python3 vmeemu.py --run spad-redirect --buffers-words 16 samples/debug/vmegc-spad-redirect/spad-redirect.vmeg.cpp
python3 vmeemu.py --run rotate --buffers-words 16 samples/debug/vmegc-spad-redirect/spad-redirect.vmeg.cpp
python3 vmeemu.py --run offset-pos --buffers-words 16 samples/debug/vmegc-spad-redirect/spad-redirect.vmeg.cpp
python3 vmeemu.py --run offset-neg --buffers-words 16 samples/debug/vmegc-spad-redirect/spad-redirect.vmeg.cpp
```
