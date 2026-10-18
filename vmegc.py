import argparse
import os
import sys

from vmeg.blocks import find_blocks
from vmeg.host import BUFFER_TYPE, GLOBALS_PROTOTYPE, call_edits, check_buffers, check_decorators, check_global_sources, check_local_sources, on_process_edit, passthrough
from vmeg.kernel import generate
from vmeg.merge import merge_command, summary
from vmeg.names import INFO_SUFFIX, SUFFIXES, globals_header
from vmeg.scanner import tokens


def default_output(path):
  name = os.path.basename(path)
  for source, result in SUFFIXES:
    if name.endswith(source):
      return name[:-len(source)] + result
  raise SystemExit("vmegc: input must end with .vmeg.c or .vmeg.cpp (or pass -o)")


def render(text, blocks, path):
  return translate(text, blocks, path)[0]


def translate(text, blocks, path):
  quoted = path.replace("\\", "\\\\").replace('"', '\\"')
  toks = list(tokens(text))
  on_process = (on_process_edit(text, toks, quoted) or (None, None))[0]
  out = [(GLOBALS_PROTOTYPE if on_process else "") + f'#line 1 "{quoted}"\n']
  check_buffers(text, toks, blocks)
  codes = [generate(text, block) for block in blocks]
  check_decorators(text, toks, blocks)
  check_global_sources(text, blocks, toks)
  check_local_sources(text, blocks)
  calls, merged = call_edits(text, blocks, quoted, {on_process[0]} if on_process else set())
  edits = []
  if on_process and on_process[0] not in merged:
    edits.append(on_process)
  edits += [(s, len("Buffer"), BUFFER_TYPE) for kind, value, s, _ in toks if kind == "ident" and value == "Buffer"]
  edits += calls
  edits.sort(key=lambda edit: edit[0])
  pos = 0
  for block, code in zip(blocks, codes):
    _, start, _, end = block
    out.append(passthrough(text, pos, start, edits))
    if code:
      first = text.count("\n", 0, start) + 1
      out.append(f'\n#line {first} "{quoted}"\n{code}')
    line = text.count("\n", 0, end) + 1
    out.append(f'\n#line {line} "{quoted}"\n')
    pos = end
  out.append(passthrough(text, pos, len(text), edits))
  if on_process:
    out.append(f'\n#include "{globals_header(path)}"\n')
  return "".join(out), summary(path, text, toks, blocks, {})


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmegc")
  parser.add_argument("inputs", nargs="+")
  parser.add_argument("-o", "--output")
  parser.add_argument("--list", action="store_true")
  parser.add_argument("--merge", action="store_true")
  args = parser.parse_args(argv)

  if args.merge:
    if args.output:
      parser.error("--merge does not take -o, the header is written next to the .vmeg-info of the file with meLibOnProcess")
    try:
      merge_command(args.inputs)
    except (ValueError, OSError) as e:
      print(e, file=sys.stderr)
      return 1
    return 0

  if args.output and len(args.inputs) != 1:
    parser.error("-o goes with a single input file, every output is written next to its source")
  if args.list and len(args.inputs) != 1:
    parser.error("--list takes a single file")

  found = []
  for path in args.inputs:
    with open(path, encoding="utf-8", newline="") as f:
      text = f.read()
    try:
      found.append((path, text, find_blocks(text)))
    except ValueError as e:
      print(f"{path}: {e}", file=sys.stderr)
      return 1
  args.input, text, blocks = found[0]

  if args.list:
    for kind, start, open_pos, end in blocks:
      if kind == "vme-end":
        continue
      first = text.count("\n", 0, start) + 1
      last = text.count("\n", 0, end - 1) + 1
      header = " ".join(text[start:open_pos].split())
      print(f"{args.input}:{first}-{last}: {header}")
    return 0

  results = []
  for path, text, blocks in found:
    try:
      result, info = translate(text, blocks, path)
    except ValueError as e:
      print(f"{path}: {e}", file=sys.stderr)
      return 1
    results.append((args.output or default_output(path), result, info))

  for output, result, info in results:
    with open(output, "w", encoding="utf-8", newline="") as f:
      f.write(result)
    base = output[:-4] if output.endswith(".cpp") else output[:-2] if output.endswith(".c") else output
    with open(base + INFO_SUFFIX, "w", encoding="utf-8", newline="") as f:
      f.write(info)
  return 0


if __name__ == "__main__":
  sys.exit(main())
