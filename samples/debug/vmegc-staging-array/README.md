# vmegc-staging-array

A sample illustrating `Staging` arrays (`Staging s[N]`) and indexed element access in `vmegc`. The kernel unrolls a loop across the four processing elements, storing an intermediate result into each element of `s[p]` on the primary functional unit, then reading it on the secondary functional unit.

## Files

| File | Content |
|---|---|
| `staging-array.vmeg.cpp` | the input buffers, the `runStagingArray` kernel with `Staging s[4]`, and the PSP display program |
| `CMakeLists.txt` | the CMake build configuration |

## Building

```
cd samples/debug/vmegc-staging-array
mkdir build && cd build
cmake ..
make
```

`PSPDEV` is set, like for the other samples. The EBOOT is in `build`.

## Emulation

To test the kernel on the emulator:

```
python3 vmeemu.py --run staging-array samples/debug/vmegc-staging-array/staging-array.vmeg.cpp
```
