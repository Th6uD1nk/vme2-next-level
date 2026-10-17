from vmeg.blocks import body_tokens, decorator_names, kernel_name
from vmeg.parser import Parser, parse_body
from vmeg.scanner import tokens

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
