# logic-add

A 4-bit ripple-carry logic adder implemented as a `pipeline` kernel (`logicAdd`) using only bitwise `^`, `&`, and `<< 1` across four carry stages, producing a 5-bit result (4-bit sum + carry out).

## Files

| File | Content |
|---|---|
| `logic-add.vmeg.c` | the 1-word buffers `inA` (`3`), `inB` (`10`), `outSum`, and the `@emulate "logic-add"` `pipeline` kernel `logicAdd` |
| `emulate.sh` | runs `logic-add` on the `vmee` emulator alone and prints the 4 `BASE` buffers (`0x0000000d` = `13`) |
| `check.sh` | builds `logic-add` with `vmeh`, runs it on a connected PSP via `vmegt`, prints the PSP log to the console, and compares it against `vmee` |

## Emulation (`vmee` only)

```bash
./samples/c/logic-add/emulate.sh
```

## PSP Check (`vmegt` + `vmee`)

Connect the PSP with `usbhostfs_pc` running in `samples/vmeh/build` and `pspsh` listening on port `10000`, then run:

```bash
./samples/c/logic-add/check.sh
```
