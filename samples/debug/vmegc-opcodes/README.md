# opcodes

Kernels for the opcodes 0x000 to 0x0ff. A row of the table `spec000.py` gives a kernel: the four PEs write the same operation in four different ways, and `BASE_0` to `BASE_3` must hold the result of the equation of the row, for 256 words of input. The `@emulate` id is the id of the row.

A row can give several kernels, with the ids `id`, `id_2`, `id_3`, and so on:
- With `values`, one kernel for each set of numbers written in the operation.
- With `sets`, one kernel for each set of inputs (`SETS` in the table, `b0` to `b7`: the combinations of the two low bytes, the bits 16 to 23, random words). The other rows read the inputs `IN0` and `IN1`.

Some rows differ from the general case:
- A pe can write its registers A and B with `.remap`, for the opcodes that do not read them.
- A pe can write a shift after the operation, and the equation is then given for each pe.
- A row with a `Staging` has no equation: `check.py` runs it on the emulator, checks the opcode of each pe, and says `no equation, compare with the PSP`.

`opcodes-0x000-0x0ff.vmeg.cpp` is generated from the table, it is not edited by hand:
```
python3 samples/debug/vmegc-opcodes/generate.py
```

Emulator, one kernel:
```
python3 vmeemu.py --run add_cst samples/debug/vmegc-opcodes/opcodes-0x000-0x0ff.vmeg.cpp --buffers-words 256
```

Check every kernel in the emulator against the equation of its row, and that each PE uses the opcode of the row (`check.py`):
```
python3 samples/debug/vmegc-opcodes/check.py
```

Some kernels only:
```
python3 samples/debug/vmegc-opcodes/check.py add_cst sel_neg_3
```

Run kernels on the PSP and compare their buffers against the emulator (`vmegt --check`):
```
python3 vmegt.py --check --buffers-words 256 samples/debug/vmegc-opcodes/opcodes-0x000-0x0ff.vmeg.cpp add_cst sel_neg_3
```

Compare an existing PSP log (`results.log` or `log.txt`) against the emulator without touching the PSP:
```
python3 vmegt.py --check --reuse-log --log psp-kernels/results.log --buffers-words 256 samples/debug/vmegc-opcodes/opcodes-0x000-0x0ff.vmeg.cpp add_cst sel_neg_3
```

Opcodes used by a kernel:
```
python3 vmegc.py --list --kernel checkAddCst samples/debug/vmegc-opcodes/opcodes-0x000-0x0ff.vmeg.cpp
```

A new operation gets a row in `spec000.py`, then the file is generated again.
