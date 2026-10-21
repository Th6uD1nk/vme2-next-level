import argparse
import os
import re
import sys

from vmeg.blocks import find_blocks
from vmeg.host import BUFFER_TYPE, call_edits, check_buffers, check_decorators, check_local_sources, definition_edits, on_process_edit, passthrough
from vmeg.kernel import block_statement_records, generate
from vmeg.vmecalls import finish_calls
from vmeg.names import SUFFIXES
from vmeg.operations import format_operations
from vmeg.registry import check_calls, check_definitions, check_uses, needed_externs, needed_prototypes, project_registry
from vmeg.scanner import tokens


def default_output(path):
  name = os.path.basename(path)
  for source, result in SUFFIXES:
    if name.endswith(source):
      return name[:-len(source)] + result
  raise SystemExit("vmegc: input must end with .vmeg.c or .vmeg.cpp (or pass -o)")


def render(text, blocks, path):
  return translate(text, blocks, path)


def extern_edit(text, toks, blocks, quoted, declarations):
  first = min((block[1] for block in blocks), default=len(text))
  includes = [(start, end) for kind, value, start, end in toks if kind == "pp" and value.startswith("#include") and start < first]
  lines = "".join(f"\n{re.sub(r'\bBuffer\b', BUFFER_TYPE, declaration)}" for declaration in declarations)
  if not includes:
    return (0, 0, lines.lstrip("\n") + "\n" + f'#line 1 "{quoted}"\n')
  at = includes[-1][1]
  resume = text.count("\n", 0, at) + 2
  return (at, 0, f'{lines}\n#line {resume} "{quoted}"')


def translate(text, blocks, path, registry=None, warnings=None):
  quoted = path.replace("\\", "\\\\").replace('"', '\\"')
  toks = list(tokens(text))
  registry = registry or project_registry([(path, text)])
  on_process = (on_process_edit(text, toks, quoted) or (None, None))[0]
  out = [f'#line 1 "{quoted}"\n']
  check_buffers(text, toks, blocks)
  found = []
  codes = [generate(text, block, found) for block in blocks]
  records, per_block = block_statement_records(text, blocks)
  codes = ["\n".join(line for record in records[block[1]] for line in record["calls"]) if block[0] == "block-statement" else code for block, code in zip(blocks, codes)]
  check_decorators(text, blocks, registry)
  check_local_sources(text, blocks, registry, path, per_block)
  calls, started = call_edits(text, blocks, quoted, {on_process[0]} if on_process else set(), registry)
  edits = []
  declarations = needed_externs(registry, path) + needed_prototypes(registry, path)
  if declarations:
    edits.append(extern_edit(text, toks, blocks, quoted, declarations))
  if on_process and on_process[0] not in started:
    edits.append(on_process)
  edits += [(s, len("Buffer"), BUFFER_TYPE) for kind, value, s, _ in toks if kind == "ident" and value == "Buffer"]
  edits += calls
  edits += definition_edits(text, blocks, quoted, registry, per_block)
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
  result = finish_calls("".join(out))
  if warnings is not None:
    warnings.extend((path, line, message) for line, message in found)
  return result


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmegc")
  parser.add_argument("inputs", nargs="*")
  parser.add_argument("-o", "--output")
  parser.add_argument("--list", action="store_true")
  parser.add_argument("--ops", action="store_true")
  args = parser.parse_args(argv)

  if args.ops:
    if args.inputs or args.output or args.list:
      parser.error("--ops goes alone")
    sys.stdout.write(format_operations())
    return 0
  if not args.inputs:
    parser.error("the input files are required")

  if args.output and len(args.inputs) != 1:
    parser.error("-o goes with a single input file, every output is written next to its source")

  for path in args.inputs:
    if path.endswith(".vmeg.h"):
      parser.error(f"{path}: a .vmeg.h is not a source, the buffers are declared in .vmeg.c or .vmeg.cpp files")

  found = []
  for path in args.inputs:
    with open(path, encoding="utf-8", newline="") as f:
      text = f.read()
    try:
      found.append((path, text, find_blocks(text)))
    except ValueError as e:
      print(f"{path}: {e}", file=sys.stderr)
      return 1

  try:
    registry = project_registry([(path, text) for path, text, _ in found])
    check_definitions(registry)
    check_uses(registry)
    check_calls(registry)
  except ValueError as e:
    print(e, file=sys.stderr)
    return 1

  if args.list:
    for path, text, blocks in found:
      for kind, start, open_pos, end in blocks:
        if kind in ("kernel-block-end", "block-statement"):
          continue
        first = text.count("\n", 0, start) + 1
        last = text.count("\n", 0, end - 1) + 1
        header = " ".join(text[start:open_pos].split())
        print(f"{path}:{first}-{last}: {header}")
    return 0

  results = []
  warnings = []
  for path, text, blocks in found:
    try:
      result = translate(text, blocks, path, registry, warnings)
    except ValueError as e:
      print(f"{path}: {e}", file=sys.stderr)
      return 1
    results.append((args.output or default_output(path), result))

  for path, line, message in warnings:
    print(f"{path}: line {line}: warning: {message}", file=sys.stderr)

  for output, result in results:
    with open(output, "w", encoding="utf-8", newline="") as f:
      f.write(result)
  return 0


if __name__ == "__main__":
  sys.exit(main())
