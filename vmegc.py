import argparse
import os
import re
import sys

from vmeg.blocks import body_tokens, decorator_names, find_blocks, kernel_name
from vmeg.expr import fold, to_c
from vmeg.kernel import flatten, target_pe, unroll
from vmeg.parser import AGU_PARAMS, ICN_NAMES, Parser, kernel_statements, parse_body, upload_call, upload_text
from vmeg.scanner import tokens

SUFFIXES = ((".vmeg.cpp", ".cpp"), (".vmeg.c", ".c"))
INFO_SUFFIX = ".vmeg-info"


def globals_header(path):
  name = os.path.basename(path)
  for source, _ in SUFFIXES:
    if name.endswith(source):
      return name[:-len(source)] + ".gen.h"
  return os.path.splitext(name)[0] + ".gen.h"


def default_output(path):
  name = os.path.basename(path)
  for source, result in SUFFIXES:
    if name.endswith(source):
      return name[:-len(source)] + result
  raise SystemExit("vmegc: input must end with .vmeg.c or .vmeg.cpp (or pass -o)")


def generate_agu(target, params, env):
  pe = target_pe(target, env)
  agu = target[2]
  values = {}
  for key, value in params[1]:
    if key not in AGU_PARAMS[agu]:
      raise ValueError(f"pe{pe}.{agu}: unknown parameter '{key}' ({', '.join(AGU_PARAMS[agu])})")
    if key in values:
      raise ValueError(f"pe{pe}.{agu}: duplicate parameter '{key}'")
    values[key] = to_c(fold(value, env))
  if "count" not in values:
    raise ValueError(f"pe{pe}.{agu}: 'count' is required")
  mode = f"agu_mode({values['mode']})" if "mode" in values else "VME_DEF_MODE"
  if "offset" in values:
    mode += f", {values['offset']}"
  if "cyc" in values:
    mode += f", vme_cyc({values['cyc']})"
  step = f"agu_step({values['step']})" if "step" in values else "VME_DEF_STEP"
  return [
    f"vme_pe{pe}(agu_{agu}(MODE), {mode});",
    f"vme_pe{pe}(agu_{agu}(COUNT), {step}, {values['count']});",
  ]


KERNEL_OPTIONS = ("direct",)


def swen_mask(pes):
  return sum(1 << (3 - pe) for pe in pes)


def emit(statement, env, lines, state):
  try:
    emit_statement(statement, env, lines, state)
  except ValueError as e:
    if str(e).startswith("line "):
      raise
    raise ValueError(f"line {statement[-1]}: {e}") from None


def emit_statement(statement, env, lines, state):
  kind = statement[0]
  if kind == "const":
    if statement[1] in env:
      raise ValueError(f"'{statement[1]}' is defined twice")
    env[statement[1]] = fold(statement[2], env)
  elif kind == "icn":
    for icn, value in statement[1]:
      if icn == "swen":
        state["swen"] = True
      lines.append(f"vme_icn({ICN_NAMES[icn]}, {to_c(fold(value, env))});")
  elif kind == "agu":
    lines.extend(generate_agu(statement[1], statement[2], env))
  elif kind == "assign":
    pe = target_pe(statement[1], env)
    operations = flatten(fold(statement[2], env))
    _, front, back = operations[0]
    fu = f"vme_mux({front}, {back}), fu_code(OP_ADD)"
    after = 1
    if len(operations) > 1 and operations[1][0] == "sat":
      fu += f", fu_sat({operations[1][1]})"
      after = 2
    lines.append(f"vme_pe{pe}(vme_fu(PRIMARY), {fu});")
    if len(operations) > after and operations[after][0] == "clamp":
      _, low, high = operations[after]
      state["secondary"].add(pe)
      lines.append(f"vme_pe{pe}(vme_fu(SECONDARY), vme_mux(NONE, STAGING_{pe}), fu_code(OP_CLP));")
      lines.append(f"vme_pe{pe}(fu_reg(SECONDARY, A), {to_c(('num', high))});")
      lines.append(f"vme_pe{pe}(fu_reg(SECONDARY, B), {to_c(('num', low))});")
  elif kind == "for":
    loop = ("for", statement[1], fold(statement[2], env), fold(statement[3], env), statement[4], statement[5])
    for inner in unroll(loop):
      emit(inner, env, lines, state)


def generate(text, block):
  kind, start, open_pos, _ = block
  if kind == "decorator":
    return ""
  if kind == "vme":
    return "{ vmeLibEnable();"
  if kind == "vme-end":
    return "vmeLibDisable();"
  if kind == "buffers":
    line = text.count("\n", 0, start) + 1
    raise ValueError(f"line {line}: buffers must be inside a kernel (global buffers or local buffers)")
  header = text[start:open_pos]
  words = [(value, start + s) for _, value, s, _ in tokens(header)]
  name, options = words[1][0], []
  for word, pos in words[2:]:
    line = text.count("\n", 0, pos) + 1
    if word not in KERNEL_OPTIONS:
      raise ValueError(f"line {line}: unknown kernel option '{word}' ({', '.join(KERNEL_OPTIONS)})")
    if word in options:
      raise ValueError(f"line {line}: duplicate kernel option '{word}'")
    options.append(word)
  toks, limit = body_tokens(text, block)
  statements = parse_body(Parser(text, toks, limit))
  if "direct" not in options:
    return ""
  lines = ["vmeLibStart();"]
  env = {}
  state = {"swen": False, "secondary": set()}
  for statement in statements:
    emit(statement, env, lines, state)
  if state["secondary"] and not state["swen"]:
    lines.append(f"vme_icn(SWEN, fu_on(0b{swen_mask(state['secondary']):04b}));")
  lines.append("vmeLibFinish();")
  body = "".join(f"  {line}\n" for line in lines)
  return f"void {name}() {{\n{body}}}"


BUFFER_TYPE = "u32 __attribute__((aligned(64)))"


def passthrough(text, begin, end, edits):
  out = []
  pos = begin
  for at, length, replacement in edits:
    if begin <= at < end:
      out.append(text[pos:at])
      out.append(replacement)
      pos = at + length
  out.append(text[pos:end])
  return "".join(out)


DECLARATION_QUALIFIERS = ("static", "const", "volatile", "extern", "register", "restrict")


def declarator_names(toks, i):
  names = []
  expect = True
  nest = 0
  for kind, value, _, _ in toks[i + 1:]:
    if kind == "punct" and value in "([{":
      nest += 1
    elif kind == "punct" and value in ")]}":
      nest -= 1
      if nest < 0:
        break
    elif nest == 0:
      if kind == "punct" and value == ";":
        break
      if kind == "punct" and value == ",":
        expect = True
      elif kind == "ident" and expect:
        names.append(value)
        expect = False
  return names


def file_buffer_names(toks):
  names = set()
  depth = 0
  for i, (kind, value, _, _) in enumerate(toks):
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
    elif kind == "ident" and value == "Buffer" and depth == 0:
      names.update(declarator_names(toks, i))
  return names


def function_tokens(text, block):
  begin = block[3]
  parens = 0
  found = False
  depth = 0
  body = []
  for kind, value, start, end in tokens(text[begin:]):
    token = (kind, value, start + begin, end + begin)
    if not found:
      if kind == "punct" and value == "(":
        parens += 1
      elif kind == "punct" and value == ")":
        parens -= 1
      elif kind == "punct" and value == "{" and parens == 0:
        found = True
        depth = 1
        body.append(token)
      continue
    body.append(token)
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
      if depth == 0:
        break
  return body


def function_buffer_names(text, block):
  toks = function_tokens(text, block)
  names = set()
  depth = 0
  for i, (kind, value, _, _) in enumerate(toks):
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
    elif kind == "ident" and value == "Buffer" and depth == 1:
      names.update(declarator_names(toks, i))
  return names


def check_buffers(text, toks, blocks):
  depth = 0
  for i, (kind, value, start, _) in enumerate(toks):
    if any(b[1] <= start < b[3] for b in blocks):
      continue
    if kind == "punct" and value == "(":
      depth += 1
    elif kind == "punct" and value == ")":
      depth = max(0, depth - 1)
    if kind != "ident" or value != "Buffer":
      continue
    line = text.count("\n", 0, start) + 1
    if depth > 0:
      raise ValueError(f"line {line}: Buffer only declares a variable, it cannot be used in a parameter or a cast")
    if i + 1 >= len(toks) or toks[i + 1][0] != "ident":
      raise ValueError(f"line {line}: Buffer must be followed by a variable name (volatile Buffer name[...])")
    found = False
    j = i - 1
    while j >= 0 and toks[j][0] == "ident" and toks[j][1] in DECLARATION_QUALIFIERS:
      if toks[j][1] == "volatile":
        found = True
      j -= 1
    if not found:
      raise ValueError(f"line {line}: Buffer must be volatile (volatile Buffer name[...])")


def vme_calls(toks, blocks, names):
  events = [(b[3], 1) if b[0] == "vme" else (b[1], -1) for b in blocks if b[0] in ("vme", "vme-end")]
  called = set()
  if not events or not names:
    return called
  depth = 0
  e = 0
  size = len(toks)
  for i, (kind, value, start, _) in enumerate(toks):
    while e < len(events) and events[e][0] <= start:
      depth += events[e][1]
      e += 1
    if depth and kind == "ident" and value in names and i + 1 < size and toks[i + 1][1] == "(":
      called.add(value)
  return called


def check_decorators(text, toks, blocks):
  kernels = {kernel_name(text, b): b for b in blocks if b[0] == "kernel"}
  decorated = vme_calls(toks, blocks, kernels)
  for block in blocks:
    if block[0] != "decorator":
      continue
    line = text.count("\n", 0, block[1]) + 1
    for name in decorator_names(text, block):
      if name not in kernels:
        known = f"kernels: {', '.join(kernels)}" if kernels else "there is no kernel in this file"
        raise ValueError(f"line {line}: @kernel refers to an unknown kernel '{name}' ({known})")
      decorated.add(name)
  for name, block in kernels.items():
    if name not in decorated:
      line = text.count("\n", 0, block[1]) + 1
      raise ValueError(f"line {line}: kernel '{name}' is never called, add a function marked with @kernel {name} or call {name}() in a @vme block")


def function_body(text, block):
  begin = block[3]
  parens = 0
  open_at = None
  depth = 0
  declaration = None
  pending = False
  for kind, value, start, _ in tokens(text[begin:]):
    start += begin
    if open_at is None:
      if kind == "punct" and value == "(":
        parens += 1
      elif kind == "punct" and value == ")":
        parens -= 1
      elif kind == "punct" and value == "{" and parens == 0:
        open_at = start
        depth = 1
      continue
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
      if depth == 0:
        break
    elif kind == "ident" and value == "Buffer" and depth == 1:
      pending = True
    elif kind == "punct" and value == ";" and depth == 1 and pending:
      declaration = start + 1
      pending = False
  return (declaration if declaration is not None else open_at + 1), open_at + 1


def on_process_bodies(toks):
  bodies = []
  depth = 0
  i = 0
  size = len(toks)
  open_body = False
  while i < size:
    kind, value, start, end = toks[i]
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
      if depth == 0 and open_body:
        bodies[-1][1] = start
        open_body = False
    elif kind == "ident" and value == "meLibOnProcess" and depth == 0 and i + 1 < size and toks[i + 1][1] == "(":
      nest = 0
      j = i + 1
      while j < size:
        if toks[j][0] == "punct" and toks[j][1] == "(":
          nest += 1
        elif toks[j][0] == "punct" and toks[j][1] == ")":
          nest -= 1
          if nest == 0:
            break
        j += 1
      if j + 1 < size and toks[j + 1][0] == "punct" and toks[j + 1][1] == "{":
        bodies.append([toks[j + 1][3], toks[-1][3]])
        open_body = True
        depth += 1
        i = j + 1
    i += 1
  return bodies


def global_lines(text, blocks, cache):
  lines = []
  for block in blocks:
    if block[0] != "kernel":
      continue
    for statement in kernel_statements(text, block, cache):
      if statement[0] == "buffers" and statement[1] == "global":
        lines += statement[2]
  return lines


def local_uploads(text, block):
  body, limit = body_tokens(text, block)
  calls = []
  for statement in parse_body(Parser(text, body, limit)):
    if statement[0] == "buffers" and statement[1] == "local":
      calls += [upload_call(entry) for entry in statement[2]]
  return calls


def call_edits(text, blocks, quoted, on_process_starts):
  kernels = {kernel_name(text, b): b for b in blocks if b[0] == "kernel"}
  edits = []
  merged = set()
  for block in blocks:
    if block[0] != "decorator":
      continue
    line = text.count("\n", 0, block[1]) + 1
    lines = ["vmeLibEnable();"]
    for name in decorator_names(text, block):
      words = [value for _, value, _, _ in tokens(text[kernels[name][1]:kernels[name][2]])]
      if "direct" not in words[2:]:
        raise ValueError(f"line {line}: kernel '{name}' is not direct, calling it is not supported yet")
      lines += local_uploads(text, kernels[name])
      lines.append(f"{name}();")
    lines.append("vmeLibDisable();")
    at, start = function_body(text, block)
    if start in on_process_starts:
      lines[1:1] = ["vmeLibWipe();", "vmegUploadGlobals();"]
      merged.add(start)
    calls = "".join(f"\n  {code}" for code in lines)
    resume = text.count("\n", 0, at - 1) + 1
    edits.append((at, 0, f'{calls}\n#line {resume} "{quoted}"\n'))
  return edits, merged


def check_global_sources(text, blocks, toks):
  declared = file_buffer_names(toks)
  for block in blocks:
    if block[0] != "kernel":
      continue
    body, limit = body_tokens(text, block)
    for statement in parse_body(Parser(text, body, limit)):
      if statement[0] != "buffers" or statement[1] != "global":
        continue
      for _, _, _, source, line in statement[2]:
        if source not in declared:
          raise ValueError(f"line {line}: '{source}' is not declared with Buffer at the top level of the file (global buffers)")


def check_local_sources(text, blocks):
  functions = {}
  for block in blocks:
    if block[0] != "decorator":
      continue
    declared = function_buffer_names(text, block)
    where = text.count("\n", 0, block[1]) + 1
    for kernel in decorator_names(text, block):
      functions.setdefault(kernel, []).append((declared, where))
  for block in blocks:
    if block[0] != "kernel":
      continue
    kernel = kernel_name(text, block)
    body, limit = body_tokens(text, block)
    for statement in parse_body(Parser(text, body, limit)):
      if statement[0] != "buffers" or statement[1] != "local":
        continue
      for _, _, _, source, line in statement[2]:
        for declared, where in functions[kernel]:
          if source not in declared:
            raise ValueError(f"line {line}: '{source}' is not declared with Buffer in the function marked with @kernel {kernel} at line {where} (local buffers)")


GLOBALS_PROTOTYPE = "static void vmegUploadGlobals(void);\n"


def on_process_edit(text, toks, quoted):
  bodies = on_process_bodies(toks)
  if len(bodies) > 1:
    line = text.count("\n", 0, bodies[1][0]) + 1
    raise ValueError(f"line {line}: meLibOnProcess is defined twice in this file")
  if not bodies:
    return None
  at, end = bodies[0]
  resume = text.count("\n", 0, at - 1) + 1
  return (at, 0, f'\n  vmeLibEnable();\n  vmeLibWipe();\n  vmegUploadGlobals();\n  vmeLibDisable();\n#line {resume} "{quoted}"\n'), end


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
