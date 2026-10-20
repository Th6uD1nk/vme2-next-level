import re

from vmeg.scanner import tokens, walk

EMULATE_ID = re.compile(r'"[A-Za-z0-9_-]+"')


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


def read_kernel_block(text, items, index):
  start = items[index][2]
  line = text.count("\n", 0, start) + 1
  last = index + 1
  while True:
    if last + 1 >= len(items) or items[last + 1][0] != "ident":
      raise ValueError(f"line {line}: expected a kernel name after @kernel")
    last += 1
    if last + 1 < len(items) and items[last + 1][0] == "punct" and items[last + 1][1] == ",":
      last += 1
      continue
    break
  if last + 1 >= len(items) or items[last + 1][0] != "punct" or items[last + 1][1] != "{":
    raise ValueError(f"line {line}: @kernel inside a function must be followed by the kernel names and a block {{ ... }}")
  close = block_end(text, items, last + 1, start, "@kernel block") - 1
  return [("kernel-block", start, items[last][3], items[last][3]), ("kernel-block-end", close, close, close)]


def read_emulate(text, items, index):
  start = items[index][2]
  line = text.count("\n", 0, start) + 1
  if index + 2 >= len(items) or items[index + 2][0] != "str" or not EMULATE_ID.fullmatch(items[index + 2][1]):
    raise ValueError(f"line {line}: expected @emulate \"id\", the id is made of letters, digits, - and _ between double quotes")
  shift = 1 if index + 3 < len(items) and items[index + 3][1] == "." else 0
  if index + 4 + shift >= len(items) or items[index + 3 + shift][1] != "kernel" or items[index + 4 + shift][0] != "ident":
    raise ValueError(f"line {line}: @emulate \"id\" must be followed by 'kernel name'")
  end = items[index + 2][3]
  return ("emulate", start, end, end), items[index + 2][1][1:-1], line, items[index + 3][2]


def check_emulate(blocks, ids, kernels):
  for k, block in enumerate(blocks):
    if block[0] != "emulate":
      continue
    following = blocks[k + 1] if k + 1 < len(blocks) else None
    if following is None or following[0] != "kernel" or following[1] != kernels[block[1]][1]:
      raise ValueError(f"line {kernels[block[1]][0]}: @emulate must be followed by a kernel definition with its body")


def find_blocks(text):
  items = list(walk(text))
  blocks = []
  skip = 0
  nested = False
  ids = {}
  kernels = {}
  allowed = set()
  for i, (kind, value, start, end, depth, prev) in enumerate(items):
    if start < skip:
      continue
    if kind == "punct" and value == "@" and depth > 0:
      if i + 1 < len(items) and items[i + 1][1] == "vme":
        line = text.count("\n", 0, start) + 1
        raise ValueError(f"line {line}: @vme was removed, use @kernel name {{ ... }}")
      if prev in (";", "}", "{") and i + 1 < len(items) and items[i + 1][1] == "kernel":
        blocks.extend(read_kernel_block(text, items, i))
        nested = True
        continue
      line = text.count("\n", 0, start) + 1
      raise ValueError(f"line {line}: inside a function only '@kernel name {{ ... }}' is accepted")
    if kind == "punct" and value == "@" and depth == 0 and prev in (";", "}"):
      if i + 1 < len(items) and items[i + 1][1] == "vme":
        line = text.count("\n", 0, start) + 1
        raise ValueError(f"line {line}: @vme was removed, use @kernel name {{ ... }}")
      if i + 1 < len(items) and items[i + 1][1] == "emulate":
        block, name, line, kernel_start = read_emulate(text, items, i)
        if name in ids:
          raise ValueError(f"line {line}: the id \"{name}\" of @emulate is already used at line {ids[name]}")
        ids[name] = line
        kernels[start] = (line, kernel_start)
        allowed.add(i + 3)
        blocks.append(block)
        continue
      blocks.append(read_decorator(text, items, i))
      continue
    dotted = kind == "punct" and value == "." and i + 1 < len(items) and items[i + 1][1] == "kernel"
    if not dotted and (kind != "ident" or value not in ("buffers", "kernel", "context")):
      continue
    if depth != 0 or (prev not in (";", "}") and i not in allowed):
      continue
    if dotted:
      value = "kernel"
    j = i + 1 + dotted
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
  check_emulate(blocks, ids, kernels)
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
  return header_words(text, block)[1]


def header_words(text, block):
  words = [value for _, value, _, _ in tokens(text[block[1]:block[2]])]
  return words[1:] if words[0] == "." else words


def decorator_names(text, block):
  return [value for _, value, _, _ in tokens(text[block[1]:block[3]])][2::2]
