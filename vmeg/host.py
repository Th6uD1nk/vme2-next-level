from vmeg.blocks import decorator_calls, decorator_names
from vmeg.scanner import tokens
from vmeg.vmecalls import ASYNC_END, ASYNC_START, DISABLE, ENABLE

DECLARATION_QUALIFIERS = ("static", "const", "volatile", "extern", "register", "restrict")

BUFFER_TYPE = "u32 __attribute__((aligned(64)))"


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


def check_decorators(text, blocks, registry):
  known = registry["kernels"]
  for block in blocks:
    if block[0] not in ("decorator", "kernel-block"):
      continue
    line = text.count("\n", 0, block[1]) + 1
    for name, actions in decorator_calls(text, block):
      if name not in known:
        names = f"kernels: {', '.join(known)}" if known else "there is no kernel in the project"
        raise ValueError(f"line {line}: @kernel refers to an unknown kernel '{name}' ({names})")
      if not known[name][0]["mode"]:
        raise ValueError(f"line {line}: kernel '{name}' needs the option direct or memory")
      if "build" in actions and known[name][0]["mode"] != "memory":
        raise ValueError(f"line {line}: build is for a memory kernel, kernel '{name}' is direct")
      if "config" in actions and known[name][0]["mode"] == "memory" and not any(name == call["name"] and "build" in call["actions"] for call in registry["calls"]):
        raise ValueError(f"line {line}: kernel '{name}' is configured but never built, add a build")
      if "async" in actions and "config" not in actions and known[name][0]["stores"]:
        raise ValueError(f"line {line}: async does not wait for the end of the run, the .store of kernel '{name}' would read unfinished data")


def check_local_sources(text, blocks, registry, path, per_block):
  functions = {}
  for block in blocks:
    if block[0] not in ("decorator", "kernel-block"):
      continue
    where = text.count("\n", 0, block[1]) + 1
    if block[0] == "decorator":
      declared = function_buffer_names(text, block)
    else:
      declared = declared_buffer_names(enclosing_function_tokens(text, block[1]))
      for record in per_block[block[1]]:
        if record["scope"] == "local" and record["memory"] not in declared:
          raise ValueError(f"line {record['line']}: '{record['memory']}' is not declared with Buffer in the function that contains the @kernel block at line {where} (local {record['kind']})")
    for kernel in decorator_names(text, block):
      where_text = f"the function marked with @kernel {kernel} at line {where}" if block[0] == "decorator" else f"the function that contains the @kernel {kernel} block at line {where}"
      functions.setdefault(kernel, []).append((declared, where_text))
  for kernel, callers in functions.items():
    definition = registry["kernels"][kernel][0]
    owner = "" if definition["path"] == path else f" (kernel of {definition['path']})"
    for source, line, kind in kernel_sources(definition, "local"):
      for declared, where in callers:
        if source not in declared:
          raise ValueError(f"line {line}{owner}: '{source}' is not declared with Buffer in {where} (local {kind})")


def passthrough(text, begin, end, edits):
  out = []
  pos = begin
  for at, length, replacement in edits:
    if begin <= at < end or at == begin == end:
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
  return (at, 0, f'\n  meCoreDcacheWritebackInvalidateAll();\n  meLibExceptionHandlerInit(0);\n  {ENABLE}\n  vmeLibWipe();\n  {DISABLE}\n#line {resume} "{quoted}"\n'), end


def kernel_sources(kernel, qualifier):
  return [(transfer["memory"], transfer["line"], transfer["kind"]) for transfer in kernel["loads"] + kernel["stores"] if transfer["scope"] == qualifier]


def kernel_actions(name, actions, mode="direct", built=False, args=""):
  if "build" in actions:
    made = [f"{name}Context = {name}({args or 0});"]
    rest = tuple(action for action in actions if action != "build")
    return made + kernel_actions(name, rest, mode, True, args) if rest else made
  if mode == "memory":
    load = [f"vmeLibLoadCustomContext({name}Context);"]
  else:
    load = [f"{name}({args});"]
  if "async" in actions:
    if "config" not in actions:
      return ["vmeLibTrigger();"]
    return [ASYNC_START] + load + ["vmeLibProcessAsync();", ASYNC_END]
  if len(set(actions)) == 2:
    return ["vmeLibStart();"] + load + ["vmeLibFinish();"]
  if actions[0] == "config":
    return load if mode == "memory" else ["vmeLibSetFlow(VME_DEFAULT);"] + load
  return ["vmeLibTrigger();", "meCoreDMACPrimWaitVMEFinish();"]


def kernel_mode(registry, name):
  return registry["kernels"][name][0]["mode"]


def kernel_arguments(registry, name, pairs):
  given = dict(pairs)
  return ", ".join(given[parameter] for parameter in registry["kernels"][name][0]["params"] if parameter in given)


def kernel_lines(registry, name, actions, pairs=()):
  args = kernel_arguments(registry, name, pairs)
  if actions == ("build",):
    return kernel_actions(name, actions, kernel_mode(registry, name), False, args)
  return kernel_uploads(registry, name) + kernel_actions(name, actions, kernel_mode(registry, name), False, args) + kernel_downloads(registry, name)


def kernel_uploads(registry, name):
  return [call for load in registry["kernels"][name][0]["loads"] for call in load["calls"]]


def kernel_downloads(registry, name):
  return [call for store in registry["kernels"][name][0]["stores"] for call in store["calls"]]


def line_indent(text, position):
  begin = text.rfind("\n", 0, position) + 1
  before = text[begin:position]
  return before if not before.strip() else ""


def function_start(text, position, floor):
  boundary = floor
  depth = 0
  begin = None
  for kind, value, start, end in tokens(text):
    if kind == "punct" and value == "{":
      if depth == 0:
        begin = boundary
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
      if depth == 0:
        if begin is not None and begin <= position < end:
          return begin
        boundary = max(boundary, end)
    elif depth == 0 and (kind == "pp" or (kind == "punct" and value == ";")):
      boundary = max(boundary, end)
  return None


def function_name(text, start):
  parens = 0
  previous = None
  for kind, value, begin, _ in tokens(text[start:]):
    if kind == "punct" and value == "(":
      if parens == 0 and previous is not None:
        return previous
      parens += 1
    elif kind == "punct" and value == ")":
      parens -= 1
    elif kind == "punct" and value == "{" and parens == 0:
      return None
    elif kind == "ident" and parens == 0:
      previous = value
  return None


def block_owners(text, blocks):
  owners = {}
  counts = {}
  decorator_ends = [block[3] for block in blocks if block[0] == "decorator"]
  for block in blocks:
    if block[0] != "kernel-block":
      continue
    floor = max([end for end in decorator_ends if end <= block[1]], default=0)
    start = function_start(text, block[1], floor)
    name = (function_name(text, start) if start is not None else None) or "block"
    counts[name] = counts.get(name, 0) + 1
    owners[block[1]] = name if counts[name] == 1 else f"{name}{counts[name]}"
  return owners


def definition_edits(text, blocks, quoted, registry, per_block):
  edits = []
  seen = set()
  decorator_ends = [block[3] for block in blocks if block[0] == "decorator"]
  for block in blocks:
    if block[0] not in ("decorator", "kernel-block"):
      continue
    if block[0] == "decorator":
      at = block[3]
    else:
      floor = max([end for end in decorator_ends if end <= block[1]], default=0)
      at = function_start(text, block[1], floor)
      if at is None:
        continue
    code = []
    for name, _ in decorator_calls(text, block):
      for record in registry["kernels"][name][0]["loads"] + registry["kernels"][name][0]["stores"]:
        if record["function"] not in seen:
          seen.add(record["function"])
          code.append(record["definition"])
    for record in per_block.get(block[1], []):
      if record["function"] not in seen:
        seen.add(record["function"])
        code.append(record["definition"])
    if code:
      resume = text.count("\n", 0, at) + 1
      edits.append((at, 0, "\n" + "\n\n".join(code) + f'\n#line {resume} "{quoted}"\n'))
  return edits


def build_only(text, block):
  return all(actions == ("build",) for _, actions in decorator_calls(text, block))


def params_by_kernel(text, blocks, call_params):
  found = {}
  for block in blocks:
    if block[0] != "kernel-block":
      continue
    calls = decorator_calls(text, block)
    given = call_params.get(block[1], [])
    if len(given) > len(calls):
      line = text.count("\n", 0, block[1]) + 1
      raise ValueError(f"line {line}: the block gives {len(given)} .params but names {len(calls)} kernel{'s' if len(calls) > 1 else ''}")
    found[block[1]] = [(name, given[i] if i < len(given) else []) for i, (name, _) in enumerate(calls)]
  return found


def check_params(text, blocks, assigned, registry):
  for block in blocks:
    if block[0] not in ("decorator", "kernel-block"):
      continue
    line = text.count("\n", 0, block[1]) + 1
    actions_of = decorator_calls(text, block)
    if block[0] == "decorator":
      calls = [(name, []) for name, _ in actions_of]
    else:
      calls = assigned[block[1]]
    for (name, pairs), (_, actions) in zip(calls, actions_of):
      definitions = registry["kernels"].get(name)
      if not definitions:
        continue
      declared = definitions[0]["params"]
      runs = "build" in actions if definitions[0]["mode"] == "memory" else "config" in actions
      for given, _ in pairs:
        if not declared:
          raise ValueError(f"line {line}: the kernel '{name}' declares no parameters, it takes no .params")
        if given not in declared:
          raise ValueError(f"line {line}: the kernel '{name}' has no parameter '{given}' ({', '.join(declared)})")
      missing = [parameter for parameter in declared if parameter not in [given for given, _ in pairs]]
      if missing and runs:
        way = "write the call as a block with a .params" if block[0] == "decorator" else "give it in the .params of the block"
        raise ValueError(f"line {line}: the kernel '{name}' needs the parameter{'s' if len(missing) > 1 else ''} {', '.join(missing)}, {way}")


def call_edits(text, blocks, quoted, on_process_starts, registry, assigned):
  edits = []
  started = set()
  for block in blocks:
    if block[0] == "kernel-block":
      brace = block[3] + next(tokens(text[block[3]:]))[2] + 1
      indent = line_indent(text, block[1])
      lines = ([] if build_only(text, block) else [ENABLE]) + [call for (name, actions), (_, pairs) in zip(decorator_calls(text, block), assigned[block[1]]) for call in kernel_lines(registry, name, actions, pairs)]
      edits.append((block[3], brace - block[3], indent + "{" + "".join(f"\n{indent}  {line}" for line in lines)))
      continue
    if block[0] != "decorator":
      continue
    line = text.count("\n", 0, block[1]) + 1
    wrap = not build_only(text, block)
    lines = [ENABLE] if wrap else []
    for name, actions in decorator_calls(text, block):
      lines += kernel_lines(registry, name, actions)
    if wrap:
      lines.append(DISABLE)
    at, start = function_body(text, block)
    if wrap and start in on_process_starts:
      lines[0:0] = ["meCoreDcacheWritebackInvalidateAll();", "meLibExceptionHandlerInit(0);"]
      lines[3:3] = ["vmeLibWipe();"]
      started.add(start)
    calls = "".join(f"\n  {code}" for code in lines)
    resume = text.count("\n", 0, at - 1) + 1
    edits.append((at, 0, f'{calls}\n#line {resume} "{quoted}"\n'))
  return edits, started
