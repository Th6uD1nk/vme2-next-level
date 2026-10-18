from vmeg.blocks import body_tokens, decorator_names, kernel_name
from vmeg.parser import Parser, kernel_statements, parse_body, upload_call
from vmeg.scanner import tokens

DECLARATION_QUALIFIERS = ("static", "const", "volatile", "extern", "register", "restrict")

BUFFER_TYPE = "u32 __attribute__((aligned(64)))"

GLOBALS_PROTOTYPE = "static void vmegUploadGlobals(void);\n"


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
  return declared_buffer_names(function_tokens(text, block))


def enclosing_function_tokens(text, position):
  body = []
  depth = 0
  for kind, value, start, end in tokens(text):
    if kind == "punct" and value == "{":
      depth += 1
    if depth:
      body.append((kind, value, start, end))
    if kind == "punct" and value == "}":
      depth -= 1
      if depth == 0:
        if body[0][2] <= position < end:
          return body
        body = []
  return []


def declared_buffer_names(toks):
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
    if block[0] not in ("decorator", "kernel-block"):
      continue
    line = text.count("\n", 0, block[1]) + 1
    for name in decorator_names(text, block):
      if name not in kernels:
        known = f"kernels: {', '.join(kernels)}" if kernels else "there is no kernel in this file"
        raise ValueError(f"line {line}: @kernel refers to an unknown kernel '{name}' ({known})")
      if block[0] == "kernel-block" and "direct" not in [value for _, value, _, _ in tokens(text[kernels[name][1]:kernels[name][2]])][2:]:
        raise ValueError(f"line {line}: kernel '{name}' is not direct, calling it is not supported yet")
      decorated.add(name)
  for name, block in kernels.items():
    if name not in decorated:
      line = text.count("\n", 0, block[1]) + 1
      raise ValueError(f"line {line}: kernel '{name}' is never called, add a function marked with @kernel {name} or call {name}() in a @vme block")


def check_local_sources(text, blocks):
  functions = {}
  for block in blocks:
    if block[0] not in ("decorator", "kernel-block"):
      continue
    where = text.count("\n", 0, block[1]) + 1
    if block[0] == "decorator":
      declared = function_buffer_names(text, block)
    else:
      declared = declared_buffer_names(enclosing_function_tokens(text, block[1]))
    for kernel in decorator_names(text, block):
      where_text = f"the function marked with @kernel {kernel} at line {where}" if block[0] == "decorator" else f"the function that contains the @kernel {kernel} block at line {where}"
      functions.setdefault(kernel, []).append((declared, where_text))
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
            raise ValueError(f"line {line}: '{source}' is not declared with Buffer in {where} (local buffers)")


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


def on_process_edit(text, toks, quoted):
  bodies = on_process_bodies(toks)
  if len(bodies) > 1:
    line = text.count("\n", 0, bodies[1][0]) + 1
    raise ValueError(f"line {line}: meLibOnProcess is defined twice in this file")
  if not bodies:
    return None
  at, end = bodies[0]
  resume = text.count("\n", 0, at - 1) + 1
  return (at, 0, f'\n  meCoreDcacheWritebackInvalidateAll();\n  meLibExceptionHandlerInit(0);\n  vmeLibEnable();\n  vmeLibWipe();\n  vmegUploadGlobals();\n  vmeLibDisable();\n#line {resume} "{quoted}"\n'), end


def block_only_kernels(text, blocks):
  kernels = {kernel_name(text, b) for b in blocks if b[0] == "kernel"}
  in_blocks = {name for b in blocks if b[0] == "kernel-block" for name in decorator_names(text, b)}
  elsewhere = {name for b in blocks if b[0] == "decorator" for name in decorator_names(text, b)}
  elsewhere |= vme_calls(list(tokens(text)), blocks, kernels)
  return in_blocks - elsewhere


def global_lines(text, blocks, cache):
  lines = []
  skipped = block_only_kernels(text, blocks)
  for block in blocks:
    if block[0] != "kernel" or kernel_name(text, block) in skipped:
      continue
    for statement in kernel_statements(text, block, cache):
      if statement[0] == "buffers" and statement[1] == "global":
        lines += statement[2]
  return lines


def buffer_uploads(text, block, qualifier):
  body, limit = body_tokens(text, block)
  calls = []
  for statement in parse_body(Parser(text, body, limit)):
    if statement[0] == "buffers" and statement[1] == qualifier:
      calls += [upload_call(entry) for entry in statement[2]]
  return calls


def local_uploads(text, block):
  return buffer_uploads(text, block, "local")


def call_edits(text, blocks, quoted, on_process_starts):
  kernels = {kernel_name(text, b): b for b in blocks if b[0] == "kernel"}
  edits = []
  merged = set()
  for block in blocks:
    if block[0] == "kernel-block":
      brace = block[3] + next(tokens(text[block[3]:]))[2] + 1
      calls = "".join("".join(f" {call}" for call in buffer_uploads(text, kernels[name], "global") + local_uploads(text, kernels[name])) + f" {name}();" for name in decorator_names(text, block))
      edits.append((brace, 0, f" vmeLibEnable();{calls}"))
      continue
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
      lines[0:0] = ["meCoreDcacheWritebackInvalidateAll();", "meLibExceptionHandlerInit(0);"]
      lines[3:3] = ["vmeLibWipe();", "vmegUploadGlobals();"]
      merged.add(start)
    calls = "".join(f"\n  {code}" for code in lines)
    resume = text.count("\n", 0, at - 1) + 1
    edits.append((at, 0, f'{calls}\n#line {resume} "{quoted}"\n'))
  return edits, merged
