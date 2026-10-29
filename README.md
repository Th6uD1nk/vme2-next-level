## VME2 Next Level. (Transpiler, Emulator and Debugger)

VME2 Next Level is a toolkit for the PSP Virtual Mobile Engine (VME2), including a transpiler, an emulator and a debugger. Write kernels in vmeg, a graph-like language embedded in C/C++, compile them to plain C/C++ for vme-lib, play them in an emulator, and check them on a real PSP.

## Install

Clone with `--recursive`, then run `./install.sh` in the folder of the project. It builds the me-core libraries for the vmeg environment and adds `bin` to your `PATH` and `VMEGC_HOME` to your `~/.bashrc` (`./install.sh --uninstall` removes them). In a new terminal, `vmegc`, `vmee` and `vmeh` are available from any folder.

## vmeg

**vmeg** is a language to describe VME kernels inside C and C++ files. `vmegc.py` turns a `.vmeg.c` or `.vmeg.cpp` file into plain C or C++ built on vme-lib.

Compile a file:
```
python3 vmegc.py samples/c/saturate-clamp.vmeg.c -o saturate-clamp.c
```

Or add it to a CMake build:
```
include($ENV{VMEGC_HOME}/cmake/vmegc.cmake)
vmegc_sources(app SOURCES main.vmeg.cpp)
target_link_libraries(app nl-me-core nl-me-core-lib nl-vme-lib)
```
`nl-me-core`, `nl-me-core-lib`, `nl-me-core-mapper` and `nl-vme-lib` are the libraries, with their headers, of the me-core-mapper submodule. The samples include `cmake/vmegc.cmake` by a relative path and do not need the install.

More details in the documentation: [vmeg](doc/VMEG.md)

## vmee

**vmee** is the emulator and debugger of the VME kernels written in vmeg. It plays a kernel on a model of the VME and shows the content of the buffers, without a PSP.

Mark a kernel with `@emulate "my-kernel"` right above its `.kernel`, then run:
```
python3 vmeemu.py --run my-kernel file.vmeg.cpp
```

It needs `g++` with 32 bit support (`-m32`) and the `me-core-mapper` submodule (`git submodule update --init me-core-mapper`).

`--run` is currently tested on Linux only.

More details in the documentation: [vmee](doc/VMEE.md) (work in progress)

## vmeh

**vmeh** (VME hardware) generates the code that runs the kernels marked with `@emulate` on the real PSP. This code writes the content of the buffers in a log file, in the same format as vmee, so that the two results can be compared.

Go to `samples/vmeh`, give the vmeg file (a path relative to the root of the project), then build:
```
cd samples/vmeh
mkdir build && cd build
cmake -DVMEH_SOURCE=samples/c/saturate-clamp.vmeg.c ..
make
```

The EBOOT is in `build`. With one `@emulate`, the program runs it, writes `log.txt` in the folder of the EBOOT and exits, and it shows nothing on the screen.

With several `@emulate` in the file, the program has all of them. The screen shows the number and the id of the current one, like `001 - add`. The first one runs at the start. Left and Right go to the previous and to the next one (they stop at the first and at the last), and each one runs when you reach it. `log.txt` holds the dump of the current one only, and each new run replaces it. Its first line is `Kernel: 001 - add`.

`-DVMEH_ID=id` keeps only the `@emulate` with that id.

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
