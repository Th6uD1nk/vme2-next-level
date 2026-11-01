import re

from vmeg.scanner import STRING, walk

COMMENT = re.compile(STRING.pattern + r"|//[^\n]*|/\*.*?\*/", re.S)


def flatten(text):
  def comment(match):
    value = match.group()
    return "/*" + value[2:].replace("*/", "* /") + "*/" if value.startswith("//") else value
  return re.sub(r"[ \t]*[\r\n]+[ \t]*", " ", COMMENT.sub(comment, text))


def closing(items, opening):
  depth = items[opening][4] + 1
  return next(k for k in range(opening + 1, len(items)) if items[k][1] == "}" and items[k][4] == depth)


def block_loop(items):
  for i, item in enumerate(items):
    if not (item[1] == "@" and item[4] > 0 and i + 3 < len(items) and items[i + 1][1] == "emulate" and items[i + 3][1] == "{"):
      continue
    level = items[i + 3][4] + 1
    for j in range(i + 4, closing(items, i + 3)):
      if items[j][1] == "for" and items[j][4] == level and items[j][5] in (";", "}", "{") and items[j + 1][0] == "ident" and items[j + 2][1] == "in":
        return j
  return None


def substitute(text, items, first, last, name, value):
  number = str(value) if value >= 0 else f"({value})"
  start = items[first][2]
  edits = []
  for k in range(first, last):
    kind, token, begin, end, _, previous = items[k]
    if kind != "ident" or token != name or previous == ".":
      continue
    if previous in ("{", ",") and items[k + 1][1] == ":":
      continue
    edits.append((begin, end))
  body = text[start:items[last][2]]
  for begin, end in reversed(edits):
    body = body[:begin - start] + number + body[end - start:]
  return body


def loop_bounds(text, items, j):
  line = text.count("\n", 0, items[j][2]) + 1
  opening = next((k for k in range(j, len(items)) if items[k][1] in ("{", ";")), None)
  if opening is None or items[opening][1] != "{":
    raise ValueError(f"line {line}: expected 'for name in low..high {{', for example for s in 0..3 {{")
  header = [item[1] for item in items[j + 3:opening]]
  if len(header) != 4 or header[1:3] != [".", "."]:
    raise ValueError(f"line {line}: expected 'for name in low..high {{', for example for s in 0..3 {{")
  try:
    low, high = int(header[0], 0), int(header[3], 0)
  except ValueError:
    raise ValueError(f"line {line}: the bounds of a for are integers, '{header[0]}..{header[3]}' is not accepted") from None
  if low > high:
    raise ValueError(f"line {line}: the for runs from {low} to {high}, the first bound must not be above the second")
  close = closing(items, opening)
  if not any(items[k][1] == "@" and items[k + 1][1] == "kernel" for k in range(opening + 1, close)):
    raise ValueError(f"line {line}: the for calls no kernel, write at least one @kernel call in it")
  if any(items[k][0] == "pp" for k in range(opening + 1, close)):
    raise ValueError(f"line {line}: a preprocessor line cannot be inside a for of an emulate block")
  return opening, close, low, high


def unroll_loops(text):
  while True:
    items = list(walk(text))
    j = block_loop(items)
    if j is None:
      return text
    opening, close, low, high = loop_bounds(text, items, j)
    copies = [flatten(substitute(text, items, opening + 1, close, items[j + 1][1], value)).strip() for value in range(low, high + 1)]
    statement = text[items[j][2]:items[close][3]]
    text = text[:items[j][2]] + " ".join(copies) + "\n" * statement.count("\n") + text[items[close][3]:]
