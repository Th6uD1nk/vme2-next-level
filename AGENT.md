# AGENT.md

Rules for any AI agent working in this repository.

## Project
A source-to-source compiler for the PSP Virtual Mobile Engine (VME), hosted by the Media Engine.
Files named `*.vmeg.c` or `*.vmeg.cpp` are processed by the `vmegc` script and transcribed into plain C or C++ that uses the macros of the VME library (`vme-lib.h`, `vme-lib.c`, `vme-fu-opcodes.h`).

## Rules
- Indent with 2 spaces.
- Never commit. Committing is always left to a human.
- Never write comments in the code. Only the human comments the code. The agent removes an existing comment only with explicit authorization from the human.
- No AI agent, LLM or other automated tool may modify this file (`AGENT.md`) without explicit authorization from the human.
- All text and strings in the codebase must be written in English.

## Language
- The `vmeg` syntax is a custom graph-like language that comes to extend the C and C++ languages.
- Everything outside the VME blocks (`kernel`, `@kernel`) is plain C or C++ and is passed through untouched.
- A `.vmeg.*` file is transcribed into a `.c` or `.cpp` file that only uses the names of the VME library, so keywords of the `.vmeg.*` syntax cannot conflict with the generated code.
- Only opcodes validated by the human are exposed.

## Method
- Work progressively, waiting for code or a clear technical directive from the user, and then review the work under the user's supervision.
- Always cut the work into coherent, logical tasks or subtasks.
- `vmeg`, `vmee` (emu) and `vmeh` share their basic building blocks whenever possible. A piece of logic needed by more than one of them is written once, in a generic form, and the others use it.
- A piece that belongs to one tool only stays in its own folder.
- Ask the human when hardware behavior is unknown. Do not guess any hardware values or behavior.
