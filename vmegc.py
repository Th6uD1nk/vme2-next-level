import argparse
import os
import re
import sys

from vmeg.blocks import find_blocks, kernel_name
from vmeg.host import BUFFER_TYPE, build_only, call_edits, check_buffers, check_decorators, check_local_sources, definition_edits, line_indent, on_process_edit, passthrough
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


def statement_code(text, block, records):
  indent = line_indent(text, block[1])
  return "\n".join(f"{indent}{call}" for record in records for call in record["calls"])


def closing_codes(text, blocks, codes):
  opened = []
  found = []
  for block, code in zip(blocks, codes):
    if block[0] == "kernel-block":
      opened.append(build_only(text, block))
    elif block[0] == "kernel-block-end" and opened.pop():
      code = ""
    found.append(code)
  return found


def directive_break(out):
  written = next((piece for piece in reversed(out) if piece), "")
  return "" if written.endswith("\n") else "\n"


def translate(text, blocks, path, registry=None, warnings=None, compat=None):
  quoted = path.replace("\\", "\\\\").replace('"', '\\"')
  toks = list(tokens(text))
  registry = registry or project_registry([(path, text)])
  on_process = (on_process_edit(text, toks, quoted) or (None, None))[0]
  out = [f'#line 1 "{quoted}"\n']
  check_buffers(text, toks, blocks)
  found = []
  codes = [generate(text, block, found, compat) for block in blocks]
  records, per_block = block_statement_records(text, blocks)
  codes = [statement_code(text, block, records[block[1]]) if block[0] == "block-statement" else f"{line_indent(text, block[1])}  {code}" if block[0] == "kernel-block-end" and code else code for block, code in zip(blocks, closing_codes(text, blocks, codes))]
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
    before = passthrough(text, pos, start, edits)
    indent = line_indent(text, start)
    out.append(before[:-len(indent)] if indent and before.endswith(indent) else before)
    if code:
      first = text.count("\n", 0, start) + 1
      out.append(f'{directive_break(out)}#line {first} "{quoted}"\n{code}')
    line = text.count("\n", 0, end) + 1
    closing = line_indent(text, end) if block[0] == "kernel-block-end" else ""
    out.append(f'{directive_break(out)}#line {line} "{quoted}"\n{closing}')
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
  parser.add_argument("--kernel")
  parser.add_argument("--ops", action="store_true")
  parser.add_argument("--compat", choices=["fat"])
  args = parser.parse_args(argv)

  if args.ops:
    if args.inputs or args.output or args.list or args.compat or args.kernel is not None:
      parser.error("--ops goes alone")
    sys.stdout.write(format_operations())
    return 0
  if args.kernel is not None and not args.list:
    parser.error("--kernel goes with --list")
  if not args.inputs:
    parser.error("the input files are required")

  if args.output and len(args.inputs) != 1:
    parser.error("-o goes with a single input file, every output is written in the current directory")

  for path in args.inputs:
    if path.endswith(".vmeg.h"):
      parser.error(f"{path}: a .vmeg.h is not a source, the buffers are declared in .vmeg.c or .vmeg.cpp files")

  found = []
  for path in args.inputs:
    try:
      with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    except OSError as e:
      print(f"{path}: {e.strerror.lower()}", file=sys.stderr)
      return 1
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
    if args.kernel is not None:
      known = [kernel_name(text, block) for _, text, blocks in found for block in blocks if block[0] == "kernel"]
      if args.kernel not in known:
        parser.error(f"no kernel '{args.kernel}' ({', '.join(known) if known else 'there is no kernel in these files'})")
    for path, text, blocks in found:
      for kind, start, open_pos, end in blocks:
        if kind in ("kernel-block-end", "block-statement"):
          continue
        if args.kernel is not None and not (kind == "kernel" and kernel_name(text, (kind, start, open_pos, end)) == args.kernel):
          continue
        first = text.count("\n", 0, start) + 1
        last = text.count("\n", 0, end - 1) + 1
        header = " ".join(text[start:open_pos].split())
        print(f"{path}:{first}-{last}: {header}")
    return 0

  results = []
  warnings = []
  named = {}
  for path, text, blocks in found:
    try:
      result = translate(text, blocks, path, registry, warnings, args.compat)
    except ValueError as e:
      print(f"{path}: {e}", file=sys.stderr)
      return 1
    output = args.output or default_output(path)
    if output in named:
      print(f"{path}: the output '{output}' is already the output of {named[output]}", file=sys.stderr)
      return 1
    named[output] = path
    results.append((output, result))

  for path, line, message in warnings:
    print(f"{path}: line {line}: warning: {message}", file=sys.stderr)

  for output, result in results:
    if os.path.dirname(output):
      os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as f:
      f.write(result)
  return 0


if __name__ == "__main__":
  sys.exit(main())
