# AGENT.md

Rules for any AI agent working in this repository.

## Project

A source-to-source compiler for the PSP Virtual Mobile Engine (VME), hosted by the Media Engine.
Files named `*.vmeg.c` are processed by a script and transcribed into plain C that uses the macros of the VME library (`vme-lib.h`, `vme-lib.c`, `vme-fu-opcodes.h`).

## Rules

- Indent with 2 spaces.
- Never commit. Committing is always left to a human.
- Never write comments in the code. Only the human comments the code. The agent removes an existing comment only with explicit authorization from the human.
- No AI agent, LLM or other automated tool may modify this file (`AGENT.md`) without explicit authorization from the human.

## Language

- The `.vmeg.c` syntax stays close to the C language, so that editors apply C syntax highlighting.
- Everything outside the VME blocks (`kernel`, `buffers`) is plain C and is passed through untouched.
- A `.vmeg.c` file is transcribed into a `.c` file that only uses the names of the VME library, so keywords of the `.vmeg.c` syntax cannot conflict with the generated code.
- Prefer dedicated operators (`+`, `>>`, `clamp(...)`) over naming opcodes. The script maps each form to its opcode from `vme-fu-opcodes.h`.
- Only opcodes validated by the human are exposed. Opcodes marked `UN_*` are not.

## Method

- Work progressively: basic kernel written by hand first, then the script, then more operators.
- Ask the human when hardware behavior is unknown. Do not guess values derived from hardware testing.
