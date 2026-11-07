[Index](../VMEE.md) · [Running on the PSP with vmeh](vmeh.md)

# Running on the PSP with vmegt

Runs the `@emulate` kernels of a vmeg file on a PSP through psplink, one after the other, and writes the dump of the base buffers of every kernel in one log.

For each kernel `vmegt` builds a program with [vmeh](vmeh.md) that holds this kernel only (`-DVMEH_ID=<id>`), loads it on the PSP, waits for the `log.txt` that the program writes, keeps it, and resets the PSP before the next kernel.

## Requirements

- Python 3, `cmake` and `make`.
- The PSP toolchain (`PSPDEV`), with `pspsh` in its `bin` folder.
- A PSP with psplink running, connected so that `pspsh` reaches it (port 10000 by default).
- The folder that psplink serves as `host0:` (`--host`). `vmegt` copies the programs into it and reads `log.txt` from it.

## Usage

```
vmegt [options] FILE.vmeg.cpp [ID ...]
```

`vmegt` is the command of `./install.sh`, `python3 vmegt.py` is the same command. Without ids, every `@emulate` of the file runs. With ids, only these ones run, in the order given.

List the ids of a file and stop:
```
vmegt --list FILE.vmeg.cpp
```

Run two kernels with a window of 256 words per buffer:
```
vmegt --buffers-words 256 samples/debug/vmegc-opcodes/opcodes-0x000-0x0ff.vmeg.cpp add_cst sel_neg_3
```

Run all the kernels of a file, with the toolchain and the host folder given on the command line:
```
vmegt --pspdev /path/to/pspdev --host /path/to/host0 FILE.vmeg.cpp
```

## Options

| Option | Default | Role |
|---|---|---|
| `--list` | off | prints the ids of the file and stops |
| `--pspdev` | the `PSPDEV` variable | folder of the PSP toolchain, required to build |
| `--pspsh` | `bin/pspsh` of the toolchain, then the `PATH` | path of `pspsh` |
| `--host` | the `PSP_HOST` variable, then `samples/vmeh/build` of the toolkit | folder that psplink serves as `host0:` |
| `--work` | `./psp-kernels` | folder of the builds, one sub-folder per kernel |
| `--log` | `results.log` in the work folder | final log |
| `--port` | the `PSP_PORT` variable, then 10000 | port of `pspsh` |
| `--reset-wait` | 14 | seconds to wait after a reset of psplink |
| `--timeout` | 60 | seconds to wait for the `log.txt` of a kernel |
| `--retries` | 1 | new tries of a kernel that gives no log |
| `--jobs` | the number of cores | builds in parallel (the runs on the PSP are one after the other) |
| `--buffers-start` | 0 | first word of the window of the buffers |
| `--buffers-words` | 32 | number of words of the window of the buffers |
| `--use` | none | `pointer=array` pair given to vmeh, can be repeated |

`--buffers-start`, `--buffers-words` and `--use` are the options of vmeh ([window of the buffers](running.md#14-the-window-of-the-buffers)).

## What it does

1. Lists the ids with `vmeemu.py --list`.
2. Builds the program of every kernel, in parallel, in `<work>/<id>`. The folders are kept, and `cmake` and `make` run again in them each time.
3. Resets the PSP and waits `--reset-wait` seconds.
4. For each kernel, one after the other: copies `vme.prx` to `gk_<id>.prx` in the host folder, deletes the old `log.txt`, loads the program with `pspsh`, waits for `log.txt` to be written, reads it, resets the PSP and waits `--reset-wait` seconds. A kernel that gives no log is tried again `--retries` times.
5. Writes the final log and prints its path.

The progress is printed on the standard error, one line per kernel:
```
[3/44] add_cst: done
```

## The final log

One section for each kernel, in the order of the run, then a summary:
```
=== kernel add_cst ===
Buffer: BASE 0
0x...
...

=== summary ===
add_cst: done
sel_neg_3: no log
```

The text of a kernel is the `log.txt` of the program as it is, the dump of the base buffers in the format of `vmee --run` ([vmeh](vmeh.md)). The program of a kernel holds one `@emulate`, so the log has no `Kernel:` line. A kernel that did not build has `build failed` and the output of `cmake` and `make` in its section.

The statuses of the summary are `done`, `no log` and `build failed`.

## Exit code

| Code | Meaning |
|---|---|
| 0 | every kernel gave its log |
| 1 | at least one kernel is `no log` or `build failed` |
| 2 | wrong use: file not found, unknown id, no `@emulate`, no `PSPDEV`, `pspsh` not found |

## From CMake

`vmegt` can be called from a custom target. It returns its exit code and prints the path of the log on the standard output.

```cmake
add_custom_target(psp-run
  COMMAND vmegt
    --pspdev $ENV{PSPDEV} --host ${PSP_HOST}
    --work ${CMAKE_BINARY_DIR}/psp-kernels
    ${CMAKE_SOURCE_DIR}/main.vmeg.cpp
  USES_TERMINAL)
```

## Notes

- Only one run at a time can use a PSP and its host folder: `log.txt` is shared by all the kernels.
- `vmegt` compares nothing. The logs can be compared with the emulator: `vmee --run <id> FILE`.
