# opcode-checker (WIP)

One kernel per opcode of the table (`python3 vmegc.py --ops`). In each kernel the four PEs read the same data and write the same operation in four different ways: `BASE_0` to `BASE_3` must be equal (the first 16 words). The `@emulate` id is the name of the opcode.

Emulator:
```
python3 vmeemu.py --run add samples/debug/vmegc-opcode-checker/opcode-checker.vmeg.cpp
```

PSP, with vmeh:
```
cd samples/vmeh && mkdir build && cd build
cmake -DVMEH_SOURCE=samples/debug/vmegc-opcode-checker/opcode-checker.vmeg.cpp ..
make
```

The program has all the kernels: Left and Right move from one to the other, and `log.txt` holds the dump of the current one. `-DVMEH_ID=add` keeps one kernel only.

Check every kernel in the emulator against its expected values (`check.py`, the table is in the script):
```
python3 samples/debug/vmegc-opcode-checker/check.py
```

Compare the `log.txt` written by vmeh for a kernel with the emulator (its id is on the first line of the log):
```
python3 samples/debug/vmegc-opcode-checker/check.py --log log.txt add
```

Opcodes used by a kernel:
```
python3 vmegc.py --list --kernel checkAdd samples/debug/vmegc-opcode-checker/opcode-checker.vmeg.cpp
```

A new opcode in the table gets its kernel here and a line in the table of `check.py`.
