# opcodes

Kernels for the opcodes 0x000 to 0x0ff. A row of the table `spec000.py` gives a kernel: the four PEs write the same operation in four different ways, and `BASE_0` to `BASE_3` must hold the result of the equation of the row, for 256 words of input. The `@emulate` id is the id of the row. A row with several sets of values gives the ids `id`, `id_2`, `id_3`, and so on.

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

Opcodes used by a kernel:
```
python3 vmegc.py --list --kernel checkAddCst samples/debug/vmegc-opcodes/opcodes-0x000-0x0ff.vmeg.cpp
```

A new operation gets a row in `spec000.py`, then the file is generated again.
