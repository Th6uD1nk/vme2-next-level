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
