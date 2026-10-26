# vmee

**vmee** is the first emulator designed for the execution and the debugging of VME kernels, through the vmeg language. It plays a kernel written in a `.vmeg.c` or `.vmeg.cpp` file on a model of the VME, and shows the content of the buffers, without a PSP.

`--run` accepts `--compat fat` to play the kernel with the opcodes that `vmegc --compat fat` chooses ([1.6](vmeg/running.md#16---compat)). `--compat` goes with `--run`.

*Work in progress.*
