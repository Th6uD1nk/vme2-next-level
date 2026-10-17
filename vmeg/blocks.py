from vmeg.scanner import tokens, walk


def read_decorator(text, items, index):
  start = items[index][2]
  line = text.count("\n", 0, start) + 1
  if index + 2 >= len(items) or items[index + 1][1] not in ("kernel", "context") or items[index + 2][0] != "ident":
    raise ValueError(f"line {line}: expected '@kernel name'")
  last = index + 2
  while last + 1 < len(items) and items[last + 1][0] == "punct" and items[last + 1][1] == ",":
    if last + 2 >= len(items) or items[last + 2][0] != "ident":
      raise ValueError(f"line {line}: expected a kernel name after ','")
    last += 2
  name_end = items[last][3]
  parens = 0
  seen = False
  words = 0
  for kind, value, _, _, _, _ in items[last + 1:]:
    if kind == "ident" and not seen:
      words += 1
    if kind == "punct" and value == "(":
      parens += 1
      if not seen and words < 2:
        raise ValueError(f"line {line}: @kernel needs a kernel name, then a function definition with its return type")
      seen = True
    elif kind == "punct" and value == ")":
      parens -= 1
    elif kind == "punct" and value in (";", "=") and parens == 0:
      break
    elif kind == "punct" and value == "{" and parens == 0:
      if seen:
        return ("decorator", start, name_end, name_end)
      break
  raise ValueError(f"line {line}: @kernel must be followed by a function definition")


def find_blocks(text):
  items = list(walk(text))
  blocks = []
  skip = 0
  nested = False
  for i, (kind, value, start, end, depth, prev) in enumerate(items):
    if start < skip:
      continue
    if kind == "punct" and value == "@" and depth > 0:
      if prev in (";", "}", "{") and i + 2 < len(items) and items[i + 1][1] == "vme" and items[i + 2][1] == "{":
        close = block_end(text, items, i + 2, start, "@vme block") - 1
        blocks.append(("vme", start, items[i + 1][3], items[i + 2][3]))
        blocks.append(("vme-end", close, close, close))
        nested = True
        continue
      line = text.count("\n", 0, start) + 1
      raise ValueError(f"line {line}: inside a function only '@vme {{ ... }}' is accepted")
    if kind == "punct" and value == "@" and depth == 0 and prev in (";", "}"):
      if i + 1 < len(items) and items[i + 1][1] == "vme":
        line = text.count("\n", 0, start) + 1
        raise ValueError(f"line {line}: @vme must be inside the body of a function")
      blocks.append(read_decorator(text, items, i))
      continue
    if kind != "ident" or value not in ("buffers", "kernel", "context"):
      continue
    if depth != 0 or prev not in (";", "}"):
      continue
    j = i + 1
    if value != "buffers":
      if j >= len(items) or items[j][0] != "ident":
        continue
      j += 1
      while j < len(items) and items[j][0] == "ident":
        j += 1
    if j < len(items) and items[j][0] == "punct" and items[j][1] == "{":
      blocks.append(("buffers" if value == "buffers" else "kernel", start, items[j][2], block_end(text, items, j, start)))
      skip = blocks[-1][3]
  if nested:
    blocks.sort(key=lambda block: block[1])
  return blocks


def block_end(text, items, open_index, start, name="block"):
  level = 0
  for kind, value, _, end, _, _ in items[open_index:]:
    if kind != "punct":
      continue
    if value == "{":
      level += 1
    elif value == "}":
      level -= 1
      if level == 0:
        return end
  line = text.count("\n", 0, start) + 1
  raise ValueError(f"line {line}: unterminated {name}")


def body_tokens(text, block):
  _, _, open_pos, end = block
  offset = open_pos + 1
  body = text[offset:end - 1]
  return [(k, v, s + offset, e + offset) for k, v, s, e in tokens(body)], end - 1


def kernel_name(text, block):
  return [value for _, value, _, _ in tokens(text[block[1]:block[2]])][1]


def decorator_names(text, block):
  return [value for _, value, _, _ in tokens(text[block[1]:block[3]])][2::2]
