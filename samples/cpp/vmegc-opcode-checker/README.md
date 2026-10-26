# opcode-checker

One kernel per opcode of the table (`python3 vmegc.py --ops`). In each kernel the four PEs read the same data and write the same operation in four different ways: `BASE_0` to `BASE_3` must be equal (the first 16 words). The `@emulate` id is the name of the opcode.

Emulator:
```
python3 vmeemu.py --run add samples/cpp/vmegc-opcode-checker/opcode-checker.vmeg.cpp
```

PSP, with vmeh:
```
cd samples/vmeh && mkdir build && cd build
cmake -DVMEH_SOURCE=samples/cpp/vmegc-opcode-checker/opcode-checker.vmeg.cpp -DVMEH_ID=add ..
make
```

Opcodes used by a kernel:
```
python3 vmegc.py --list --kernel checkAdd samples/cpp/vmegc-opcode-checker/opcode-checker.vmeg.cpp
```

A new opcode in the table gets its kernel here.
