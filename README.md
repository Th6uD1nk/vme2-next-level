## VME2 Next Level. (Transpiler, Emulator and Debugger)

A transpiler and debugger for the PSP Virtual Mobile Engine (VME2): turns C-like kernels into plain C/C++ built on vme-lib from the 'me-core' project

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
