import re

from vmeg.blocks import find_blocks, kernel_name
from vmeg.expr import to_c
from vmeg.parser import kernel_statements
from vmeg.scanner import tokens

DEFINE = re.compile(r"#\s*define\s+([A-Za-z_]\w*(?:\([^)]*\))?)(.*)", re.S)
COMMENTS = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)


def defines(text):
  found = []
  for kind, value, _, _ in tokens(text):
    if kind != "pp":
      continue
    m = DEFINE.match(value)
    if m:
      found.append((m.group(1), " ".join(COMMENTS.sub(" ", m.group(2).replace("\\\n", " ")).split())))
  return found


def buffer_entries(statements, qualifier):
  entries = []
  for statement in statements:
    if statement[0] == "buffers" and statement[1] == qualifier:
      entries += [(target, count, "" if offset is None else to_c(offset), source, line) for target, count, offset, source, line in statement[2]]
  return entries


def emulations(text):
  blocks = find_blocks(text)
  found = []
  for k, block in enumerate(blocks):
    if block[0] != "emulate":
      continue
    kernel = blocks[k + 1]
    statements = kernel_statements(text, kernel, {})
    found.append({
      "id": list(tokens(text[block[1]:block[2]]))[2][1][1:-1],
      "kernel": kernel_name(text, kernel),
      "first": text.count("\n", 0, kernel[1]) + 1,
      "last": text.count("\n", 0, kernel[3] - 1) + 1,
      "global": buffer_entries(statements, "global"),
      "local": buffer_entries(statements, "local"),
    })
  return found
