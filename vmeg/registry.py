from vmeg.blocks import decorator_calls, find_blocks, header_words, kernel_name
from vmeg.host import declarator_names, kernel_sources
from vmeg.kernel import block_statement_records, kernel_transfers
from vmeg.macros import known_macros
from vmeg.parser import kernel_statements
from vmeg.scanner import tokens

BOUNDARIES = (";", "}", "{")


def statement_span(toks, i):
  first = i
  while first > 0 and not (toks[first - 1][0] == "pp" or toks[first - 1][0] == "punct" and toks[first - 1][1] in BOUNDARIES):
    first -= 1
  nest = 0
  for last in range(i, len(toks)):
    kind, value, _, _ = toks[last]
    if kind == "punct" and value in "([{":
      nest += 1
    elif kind == "punct" and value in ")]}":
      nest -= 1
    elif kind == "punct" and value == ";" and nest == 0:
      return first, last
  return first, len(toks) - 1


def declarations(text, toks, depth_wanted):
  found = []
  depth = 0
  for i, (kind, value, _, _) in enumerate(toks):
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
    elif kind == "ident" and value == "Buffer" and depth == depth_wanted:
      first, last = statement_span(toks, i)
      statement = toks[first:last + 1]
      found.append({
        "names": declarator_names(toks, i),
        "text": text[statement[0][2]:statement[-1][3]],
        "line": text.count("\n", 0, statement[0][2]) + 1,
        "extern": any(kind == "ident" and value == "extern" for kind, value, _, _ in statement),
        "static": any(kind == "ident" and value == "static" for kind, value, _, _ in statement),
      })
  return found


def array_definitions(path, text):
  return [
    {"name": name, "path": path, "line": declaration["line"], "static": declaration["static"], "extern": declaration["extern"], "text": declaration["text"]}
    for declaration in declarations(text, list(tokens(text)), 0)
    for name in declaration["names"]
  ]


def kernel_definitions(path, text):
  found = []
  for block in find_blocks(text):
    if block[0] != "kernel":
      continue
    statements = kernel_statements(text, block, {})
    words = header_words(text, block)
    direct = "direct" in words[2:]
    mode = next((word for word in words[2:] if word in ("direct", "memory")), None)
    loads, stores = kernel_transfers(statements, known_macros(text, block[1]), kernel_name(text, block)) if mode else ([], [])
    found.append({
      "name": kernel_name(text, block),
      "path": path,
      "line": text.count("\n", 0, block[1]) + 1,
      "mode": mode,
      "direct": direct,
      "loads": loads,
      "stores": stores,
      "params": [name for statement in statements if statement[0] == "paramsdef" for _, name in statement[1]],
    })
  return found


def block_definitions(path, text):
  blocks = find_blocks(text)
  per_block = block_statement_records(text, blocks)[1]
  return [
    {"path": path, "global": [(record["memory"], record["line"], record["kind"]) for record in records if record["scope"] == "global"]}
    for records in per_block.values()
  ]


def call_definitions(path, text):
  return [
    {"name": name, "path": path, "line": text.count("\n", 0, block[1]) + 1, "block": block[0] == "kernel-block", "actions": actions}
    for block in find_blocks(text) if block[0] in ("decorator", "kernel-block")
    for name, actions in decorator_calls(text, block)
  ]


def project_registry(sources):
  arrays = {}
  kernels = {}
  calls = []
  block_transfers = []
  for path, text in sources:
    try:
      array_list = array_definitions(path, text)
      kernel_list = kernel_definitions(path, text)
      calls += call_definitions(path, text)
      block_transfers += block_definitions(path, text)
    except ValueError as e:
      raise ValueError(f"{path}: {e}") from None
    for definition in array_list:
      arrays.setdefault(definition["name"], []).append(definition)
    for definition in kernel_list:
      kernels.setdefault(definition["name"], []).append(definition)
  return {"arrays": arrays, "kernels": kernels, "calls": calls, "block_transfers": block_transfers}


def check_definitions(registry):
  for name, definitions in registry["arrays"].items():
    defined = [definition for definition in definitions if not definition["extern"]]
    if len(defined) > 1:
      first, second = defined[0], defined[1]
      raise ValueError(f"{second['path']}: line {second['line']}: the array '{name}' is already defined at {first['path']} line {first['line']}")
  for name, definitions in registry["kernels"].items():
    if len(definitions) > 1:
      first, second = definitions[0], definitions[1]
      raise ValueError(f"{second['path']}: line {second['line']}: the kernel '{name}' is already defined at {first['path']} line {first['line']}")


def check_array(registry, source, path, line, kind):
  where = f"{path}: line {line}"
  declared = registry["arrays"].get(source, [])
  if not declared:
    raise ValueError(f"{where}: the array '{source}' of a global {kind} is not declared with Buffer in any file")
  defined = [definition for definition in declared if not definition["extern"]]
  if not defined:
    raise ValueError(f"{where}: the array '{source}' of a global {kind} is declared extern but defined in no file")
  if defined[0]["static"] and defined[0]["path"] != path:
    raise ValueError(f"{where}: the array '{source}' of a global {kind} is static in {defined[0]['path']} line {defined[0]['line']}, it cannot be used from another file")


def check_uses(registry):
  for definitions in registry["kernels"].values():
    for kernel in definitions:
      for source, line, kind in kernel_sources(kernel, "global"):
        check_array(registry, source, kernel["path"], line, kind)
  for block in registry["block_transfers"]:
    for source, line, kind in block["global"]:
      check_array(registry, source, block["path"], line, kind)


def split_declarators(text):
  toks = list(tokens(text))
  at = next(i for i, (kind, value, _, _) in enumerate(toks) if kind == "ident" and value == "Buffer")
  qualifiers = [value for kind, value, _, _ in toks[:at] if kind == "ident" and value not in ("static", "extern")]
  declarators = [[]]
  nest = 0
  for token in toks[at + 1:]:
    kind, value = token[0], token[1]
    if kind == "punct" and value in "([{":
      nest += 1
    elif kind == "punct" and value in ")]}":
      nest -= 1
    if nest == 0 and kind == "punct" and value in ",;":
      declarators.append([])
    else:
      declarators[-1].append(token)
  return qualifiers, declarators


def drop_initializer(declarator):
  nest = 0
  for i, (kind, value, _, _) in enumerate(declarator):
    if kind == "punct" and value in "([{":
      nest += 1
    elif kind == "punct" and value in ")]}":
      nest -= 1
    elif nest == 0 and kind == "punct" and value == "=":
      return declarator[:i]
  return declarator


def extern_declaration(definition):
  qualifiers, declarators = split_declarators(definition["text"])
  for declarator in declarators:
    if declarator and declarator[0][1] == definition["name"]:
      kept = drop_initializer(declarator)
      return " ".join(["extern"] + qualifiers + ["Buffer"]) + " " + definition["text"][kept[0][2]:kept[-1][3]] + ";"
  raise ValueError(f"the array '{definition['name']}' is not in its own declaration")


def needed_externs(registry, path):
  sources = {}
  for definitions in registry["kernels"].values():
    for kernel in definitions:
      if kernel["path"] == path:
        for source, _, _ in kernel_sources(kernel, "global"):
          sources[source] = True
  for call in registry["calls"]:
    if call["path"] == path and call["block"]:
      for kernel in registry["kernels"].get(call["name"], []):
        for source, _, _ in kernel_sources(kernel, "global"):
          sources[source] = True
  for block in registry["block_transfers"]:
    if block["path"] == path:
      for source, _, _ in block["global"]:
        sources[source] = True
  declarations = []
  for source in sources:
    definitions = registry["arrays"].get(source, [])
    if any(definition["path"] == path for definition in definitions):
      continue
    defined = [definition for definition in definitions if not definition["extern"]]
    if defined:
      declarations.append(extern_declaration(defined[0]))
  return declarations


def check_calls(registry):
  called = {call["name"] for call in registry["calls"]}
  for name, definitions in registry["kernels"].items():
    if name not in called:
      definition = definitions[0]
      raise ValueError(f"{definition['path']}: line {definition['line']}: kernel '{name}' is never called, add a function marked with @kernel {name} config | exec or a block @kernel {name} config | exec {{ ... }}")


def needed_prototypes(registry, path):
  names = {}
  for call in registry["calls"]:
    definitions = registry["kernels"].get(call["name"], [])
    if call["path"] == path and definitions and definitions[0]["path"] != path:
      names[call["name"]] = True
  found = []
  for name in names:
    if registry["kernels"][name][0]["mode"] == "memory":
      found += [f"void* {name}(void*);", f"extern void* {name}Context;"]
    else:
      found.append(f"void {name}();")
  return found
