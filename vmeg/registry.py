from vmeg.blocks import find_blocks, kernel_name
from vmeg.expr import to_c
from vmeg.host import declarator_names
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


def buffer_links(statements, qualifier):
  return [
    (target, count, "" if offset is None else to_c(offset), source, line)
    for statement in statements if statement[0] == "buffers" and statement[1] == qualifier
    for target, count, offset, source, line in statement[2]
  ]


def kernel_definitions(path, text):
  found = []
  for block in find_blocks(text):
    if block[0] != "kernel":
      continue
    statements = kernel_statements(text, block, {})
    words = [value for _, value, _, _ in tokens(text[block[1]:block[2]])]
    found.append({
      "name": kernel_name(text, block),
      "path": path,
      "line": text.count("\n", 0, block[1]) + 1,
      "direct": "direct" in words[2:],
      "global": buffer_links(statements, "global"),
      "local": buffer_links(statements, "local"),
    })
  return found


def project_registry(sources):
  arrays = {}
  kernels = {}
  for path, text in sources:
    try:
      array_list = array_definitions(path, text)
      kernel_list = kernel_definitions(path, text)
    except ValueError as e:
      raise ValueError(f"{path}: {e}") from None
    for definition in array_list:
      arrays.setdefault(definition["name"], []).append(definition)
    for definition in kernel_list:
      kernels.setdefault(definition["name"], []).append(definition)
  return {"arrays": arrays, "kernels": kernels}


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


def check_uses(registry):
  for definitions in registry["kernels"].values():
    for kernel in definitions:
      for _, _, _, source, line in kernel["global"]:
        where = f"{kernel['path']}: line {line}"
        declared = registry["arrays"].get(source, [])
        if not declared:
          raise ValueError(f"{where}: the array '{source}' is not declared with Buffer in any file")
        defined = [definition for definition in declared if not definition["extern"]]
        if not defined:
          raise ValueError(f"{where}: the array '{source}' is declared extern but defined in no file")
        if defined[0]["static"] and defined[0]["path"] != kernel["path"]:
          raise ValueError(f"{where}: the array '{source}' is static in {defined[0]['path']} line {defined[0]['line']}, it cannot be used from another file")
