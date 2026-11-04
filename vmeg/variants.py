import itertools

from vmeg.scanner import walk
from vmeg.unroll import closing, flatten

STARTS = (";", "}", "{")


def line_of(text, position):
  return text.count("\n", 0, position) + 1


def member_end(text, items, at):
  line = line_of(text, items[at][2])
  name = items[at + 1][1]
  following = items[at + 2][1] if at + 2 < len(items) else None
  if following == ";":
    return [], at + 2
  if following == "{" and items[at + 3][1] == "}":
    return [], at + 3 + (items[at + 4][1] == ";" if at + 4 < len(items) else 0)
  if following == "=" and items[at + 3][1] == "{" and items[at + 4][1] == "}" and items[at + 5][1] == ";":
    return [], at + 5
  depth = items[at][4]
  k = at + 2
  while k < len(items) and not (items[k][1] == ";" and items[k][4] == depth):
    if items[k][1] == "}" and items[k][4] < depth:
      raise ValueError(f"line {line}: expected ';' after .{name}")
    k += 1
  if k >= len(items):
    raise ValueError(f"line {line}: expected ';' after .{name}")
  return items[at + 2:k], k


def read_with(text, items, at, tokens):
  line = line_of(text, items[at][2])
  example = "for example .with buffer in 0..3, slot in 0..3;"
  variables = []
  parts = [[]]
  for token in tokens:
    if token[1] == ",":
      parts.append([])
    else:
      parts[-1].append(token)
  for part in parts:
    shape = [token[1] for token in part]
    if len(part) != 6 or part[0][0] != "ident" or shape[1] != "in" or shape[3:5] != [".", "."]:
      raise ValueError(f"line {line}: expected '.with name in low..high;', {example}")
    try:
      low, high = int(shape[2], 0), int(shape[5], 0)
    except ValueError:
      raise ValueError(f"line {line}: the bounds of a .with are integers, '{shape[2]}..{shape[5]}' is not accepted") from None
    if low > high:
      raise ValueError(f"line {line}: the .with runs from {low} to {high}, the first bound must not be above the second")
    if any(shape[0] == name for name, _, _ in variables):
      raise ValueError(f"line {line}: the variable '{shape[0]}' is declared twice in the .with")
    variables.append((shape[0], low, high))
  return variables


def read_as(text, items, at, tokens):
  line = line_of(text, items[at][2])
  shape = [token[1] for token in tokens]
  if not tokens or tokens[0][0] != "ident" or len(tokens) % 3 != 1 or len(tokens) < 4:
    raise ValueError(f"line {line}: expected '.as alias[variable]...;', for example .as row[buffer][slot];")
  indexes = []
  for k in range(1, len(tokens), 3):
    if shape[k] != "[" or tokens[k + 1][0] != "ident" or shape[k + 2] != "]":
      raise ValueError(f"line {line}: expected '.as alias[variable]...;', for example .as row[buffer][slot];")
    indexes.append(shape[k + 1])
  return shape[0], indexes


def kernel_members(text, items, opening, close):
  depth = items[opening][4] + 1
  found = {}
  for k in range(opening + 1, close):
    token = items[k]
    if token[1] != "." or token[4] != depth or token[5] not in STARTS or items[k + 1][1] not in ("with", "as"):
      continue
    name = items[k + 1][1]
    if name in found:
      raise ValueError(f"line {line_of(text, token[2])}: a kernel has one .{name}")
    tokens, last = member_end(text, items, k)
    found[name] = (k, last, tokens)
  return found


def replaced(text, items, first, last, removed, names, rename=None):
  start = items[first][2]
  edits = [(items[a][2], items[b][3], "\n" * text.count("\n", items[a][2], items[b][3])) for a, b in removed]
  hidden = set(k for a, b in removed for k in range(a, b + 1))
  if rename is not None:
    edits.append((items[rename[0]][2], items[rename[0]][3], rename[1]))
  for k in range(first, last + 1):
    kind, token, begin, end, _, previous = items[k]
    if k in hidden or kind != "ident" or token not in names or previous == ".":
      continue
    if previous in ("{", ",") and k + 1 < len(items) and items[k + 1][1] == ":":
      continue
    edits.append((begin, end, names[token]))
  body = text[start:items[last][3]]
  for begin, end, new in sorted(edits, reverse=True):
    body = body[:begin - start] + new + body[end - start:]
  return body


def variant_number(variables, values):
  number = 0
  for (_, low, high), value in zip(variables, values):
    number = number * (high - low + 1) + value - low
  return number + 1


def read_call_as(text, items, at, tokens):
  line = line_of(text, items[at][2])
  if not tokens:
    return None
  message = f"line {line}: expected '.as alias[index]...;', for example .as row[1][2];"
  if tokens[0][0] != "ident" or len(tokens) < 4 or tokens[1][1] != "[":
    raise ValueError(message)
  indexes = []
  k = 1
  while k < len(tokens):
    if tokens[k][1] != "[":
      raise ValueError(message)
    depth = 0
    end = k
    while end < len(tokens):
      depth += (tokens[end][1] == "[") - (tokens[end][1] == "]")
      if depth == 0:
        break
      end += 1
    if end >= len(tokens) or end == k + 1:
      raise ValueError(message)
    indexes.append(text[tokens[k + 1][2]:tokens[end - 1][3]])
    k = end + 1
  return tokens[0][1], indexes


def kernel_names(items, first, last):
  names = [first]
  for k in range(first, last):
    if items[k][1] == "," and items[k + 1][0] == "ident":
      names.append(k + 1)
  return names


def expand_variants(text):
  items = list(walk(text))
  groups = []
  for i, item in enumerate(items):
    if item[1] != "." or item[4] != 0 or item[5] not in STARTS or i + 4 >= len(items) or items[i + 1][1] != "kernel" or items[i + 4][1] != "{":
      continue
    opening = i + 4
    close = closing(items, opening)
    members = kernel_members(text, items, opening, close)
    if not members:
      continue
    line = line_of(text, item[2])
    variables = read_with(text, items, members["with"][0], members["with"][2]) if "with" in members and members["with"][2] else []
    alias = read_as(text, items, members["as"][0], members["as"][2]) if "as" in members and members["as"][2] else None
    if variables and alias is None:
      raise ValueError(f"line {line}: a kernel with a .with needs a .as, for example .as row[buffer][slot];")
    if alias is not None and not variables:
      raise ValueError(f"line {line}: a .as needs a .with")
    if alias is not None:
      if sorted(alias[1]) != sorted(name for name, _, _ in variables):
        raise ValueError(f"line {line}: the .as must name each variable of the .with once")
    removed = [(members[name][0], members[name][1]) for name in members]
    name_at = i + 2
    if not variables:
      groups.append((item[2], items[close][3], replaced(text, items, i, close, removed, {})))
      continue
    copies = []
    ranges = [range(low, high + 1) for _, low, high in variables]
    for number, values in enumerate(itertools.product(*ranges), 1):
      names = {name: str(value) for (name, _, _), value in zip(variables, values)}
      copies.append(flatten(replaced(text, items, i, close, removed, names, (name_at, f"{items[name_at][1]}_kernel{number}"))).strip())
    statement = text[item[2]:items[close][3]]
    groups.append((item[2], items[close][3], " ".join(copies) + "\n" * statement.count("\n")))
  for begin, end, new in reversed(groups):
    text = text[:begin] + new + text[end:]
  return text
