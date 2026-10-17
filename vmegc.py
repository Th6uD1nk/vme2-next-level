import argparse
import os
import re
import sys

from vmeg.blocks import find_blocks
from vmeg.expr import to_c
from vmeg.host import BUFFER_TYPE, GLOBALS_PROTOTYPE, call_edits, check_buffers, check_decorators, check_global_sources, check_local_sources, global_lines, on_process_bodies, on_process_edit, passthrough
from vmeg.kernel import generate
from vmeg.names import INFO_SUFFIX, SUFFIXES, globals_header
from vmeg.parser import upload_text
from vmeg.scanner import tokens


def default_output(path):
  name = os.path.basename(path)
  for source, result in SUFFIXES:
    if name.endswith(source):
      return name[:-len(source)] + result
  raise SystemExit("vmegc: input must end with .vmeg.c or .vmeg.cpp (or pass -o)")


def summary(path, text, toks, blocks, cache):
  rows = ["vmeg-info\t1", f"source\t{path}"]
  for target, count, offset, source, line in global_lines(text, blocks, cache):
    where = "" if offset is None else to_c(offset)
    rows.append(f"global\t{target}\t{count}\t{where}\t{source}\t{line}")
  for at, _ in on_process_bodies(toks):
    rows.append(f"on-process\t{text.count(chr(10), 0, at) + 1}")
  return "\n".join(rows) + "\n"


def read_summary(text, name):
  rows = text.split("\n")
  if rows and rows[-1] == "":
    rows.pop()
  if not rows or rows[0].split("\t") != ["vmeg-info", "1"]:
    raise ValueError(f"{name}:1: not a vmeg-info file of version 1")
  info = {"source": name, "globals": [], "on_process": []}
  for number, row in enumerate(rows[1:], 2):
    fields = row.split("\t")
    if fields[0] == "source" and len(fields) == 2:
      info["source"] = fields[1]
    elif fields[0] == "global" and len(fields) == 6 and fields[2].isdigit() and fields[5].isdigit():
      info["globals"].append((fields[1], int(fields[2]), fields[3], fields[4], int(fields[5])))
    elif fields[0] == "on-process" and len(fields) == 2 and fields[1].isdigit():
      info["on_process"].append(int(fields[1]))
    else:
      raise ValueError(f"{name}:{number}: unknown or malformed line")
  return info


def merge_globals(infos):
  seen = {}
  merged = []
  for info in infos:
    for target, count, offset, source, line in info["globals"]:
      key = (target, offset or "0")
      first = seen.get(key)
      if first is None:
        seen[key] = (count, source, info["source"], line)
        merged.append((target, count, offset, source))
      elif first[:2] != (count, source):
        name = target.replace("_", "").lower()
        raise ValueError(f"{info['source']}:{line}: {name} is already loaded at the same offset by {first[2]}:{first[3]} with a different source or size")
  return merged


def check_on_process(infos):
  defined = []
  first_global = None
  for info in infos:
    defined += [(info["source"], line) for line in info["on_process"]]
    if first_global is None and info["globals"]:
      first_global = (info["source"], info["globals"][0][4])
  if len(defined) > 1:
    places = " and ".join(f"{source}:{line}" for source, line in defined)
    raise ValueError(f"meLibOnProcess is defined more than once: {places}")
  if not defined and first_global is not None:
    raise ValueError(f"{first_global[0]}:{first_global[1]}: global buffers need a function meLibOnProcess in one of the files, none defines it")


def merged_file(merged):
  rows = [f"extern volatile u32 {source}[];" for source in dict.fromkeys(source for _, _, _, source in merged)]
  rows.append("static void vmegUploadGlobals(void) {")
  rows += [f"  {upload_text(*entry)}" for entry in merged]
  rows.append("}")
  return "\n".join(rows) + "\n"


def merge_command(paths):
  infos = []
  for path in paths:
    with open(path, encoding="utf-8", newline="") as f:
      infos.append(read_summary(f.read(), path))
  merged = merge_globals(infos)
  check_on_process(infos)
  for path, info in zip(paths, infos):
    if info["on_process"]:
      target = os.path.join(os.path.dirname(path), globals_header(info["source"]))
      with open(target, "w", encoding="utf-8", newline="") as f:
        f.write(merged_file(merged))


def render(text, blocks, path):
  return translate(text, blocks, path)[0]


def translate(text, blocks, path):
  quoted = path.replace("\\", "\\\\").replace('"', '\\"')
  toks = list(tokens(text))
  on_process, on_end = on_process_edit(text, toks, quoted) or (None, None)
  out = [(GLOBALS_PROTOTYPE if on_process else "") + f'#line 1 "{quoted}"\n']
  check_buffers(text, toks, blocks)
  codes = [generate(text, block) for block in blocks]
  check_decorators(text, toks, blocks)
  check_global_sources(text, blocks, toks)
  check_local_sources(text, blocks)
  calls, merged = call_edits(text, blocks, quoted, {on_process[0]} if on_process else set())
  edits = []
  if on_process and on_process[0] not in merged:
    first = next((k for k, block in enumerate(blocks) if block[0] == "vme" and on_process[0] <= block[1] < on_end), None)
    if first is None:
      edits.append(on_process)
    else:
      codes[first] += " vmeLibWipe(); vmegUploadGlobals();"
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

  if len(args.inputs) != 1:
    parser.error("give a single .vmeg.c file, or --merge with the .vmeg-info files")
  args.input = args.inputs[0]

  with open(args.input, encoding="utf-8", newline="") as f:
    text = f.read()

  try:
    blocks = find_blocks(text)
  except ValueError as e:
    print(f"{args.input}: {e}", file=sys.stderr)
    return 1

  if args.list:
    for kind, start, open_pos, end in blocks:
      if kind == "vme-end":
        continue
      first = text.count("\n", 0, start) + 1
      last = text.count("\n", 0, end - 1) + 1
      header = " ".join(text[start:open_pos].split())
      print(f"{args.input}:{first}-{last}: {header}")
    return 0

  try:
    result, info = translate(text, blocks, args.input)
  except ValueError as e:
    print(f"{args.input}: {e}", file=sys.stderr)
    return 1

  output = args.output or default_output(args.input)
  with open(output, "w", encoding="utf-8", newline="") as f:
    f.write(result)
  base = output[:-4] if output.endswith(".cpp") else output[:-2] if output.endswith(".c") else output
  with open(base + INFO_SUFFIX, "w", encoding="utf-8", newline="") as f:
    f.write(info)
  return 0


if __name__ == "__main__":
  sys.exit(main())
