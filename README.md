## VME2 Next Level. (Transpiler, Emulator and Debugger)

A transpiler, emulator and debugger for the PSP Virtual Mobile Engine (VME2). Write kernels in vmeg, a graph-like language embedded in C/C++, compile them to plain C/C++ for vme-lib, play them in an emulator, and check them on a real PSP.

## vmeg

**vmeg** is a language to describe VME kernels inside C and C++ files. `vmegc.py` turns a `.vmeg.c` or `.vmeg.cpp` file into plain C or C++ built on vme-lib.

Compile a file:
```
python3 vmegc.py samples/c/saturate-clamp.vmeg.c -o saturate-clamp.c
```

Or add it to a CMake build, the samples folder shows how:
```
include(cmake/vmegc.cmake)
vmegc_sources(app SOURCES main.vmeg.cpp)
```

More details in the documentation: [vmeg](doc/VMEG.md)

## vmee

**vmee** is the emulator and debugger of the VME kernels written in vmeg. It plays a kernel on a model of the VME and shows the content of the buffers, without a PSP.

Mark a kernel with `@emulate "my-kernel"` right above its `.kernel`, then run:
```
python3 vmeemu.py --run my-kernel file.vmeg.cpp
```

It needs `g++` with 32 bit support (`-m32`) and the `me-custom-core` submodule (`git submodule update --init me-custom-core`).

`--run` is currently tested on Linux only.

More details in the documentation: [vmee](doc/VMEE.md) (work in progress)

## vmeh

**vmeh** (VME hardware) generates the code that runs a kernel marked with `@emulate` on the real PSP. This code writes the content of the buffers in a log file, in the same format as vmee, so that the two results can be compared. The program shows nothing on the screen.

Go to `samples/vmeh`, give the vmeg file (a path relative to the root of the project) and the id of its `@emulate`, then build:
```
cd samples/vmeh
mkdir build && cd build
cmake -DVMEH_SOURCE=samples/c/saturate-clamp.vmeg.c -DVMEH_ID=saturate-clamp ..
make
```

The EBOOT is in `build`. Run it on the PSP: it writes `log.txt` in the folder of the EBOOT and exits.

The window of the buffers that is written can be changed with `-DVMEH_BUFFERS_START=0` and `-DVMEH_BUFFERS_WORDS=32` (the defaults). `vmeemu.py --run` has the same options, `--buffers-start` and `--buffers-words`.

It needs the PSP toolchain, like the other samples.

## Related Project

[PSP Media Engine Custom Core](https://github.com/mcidclan/psp-media-engine-custom-core)  
[PSP Virtual Mobile Engine Ext](https://github.com/mcidclan/psp-virtual-mobile-engine-ext)  

## Contribution Guidelines

AI tools may be used as development aids. However, additionnaly to the AGENT.md rule, the following apply strictly:

* Contributors must fully review, understand, and validate all submitted code before opening a pull request.
* Contributors are expected to be able to explain and justify their changes during code review.
* The contributor is responsible for ensuring their code does not break existing functionality, including dependencies and the overall library behavior.

Pull requests that include AI attribution in commits, or that are not clearly understood and validated by the contributor, will be rejected.

## License compatibility

All code submitted to this repository must be compatible with the MIT License. Dependencies or code snippets under more restrictive licenses (e.g. GPL, LGPL, proprietary) are not accepted. Contributors are responsible for verifying that any third-party code they include is under a permissive license granting at least the same level of freedom as MIT.

## Disclaimer
This project and code are provided as-is without warranty. Users assume full responsibility for any implementation or consequences. Use at your own discretion and risk


*Hey, Hi! Leverage AI. Stay in charge, stay wise!*

*Th6uD1nk.*
