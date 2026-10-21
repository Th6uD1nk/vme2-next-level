import re

from vmeg.scanner import tokens, walk

EMULATE_ID = re.compile(r'"[A-Za-z0-9_-]+"')

ACTIONS = ("config", "exec", "async")


def read_kernel_list(items, last, line):
  while True:
    if last + 1 >= len(items) or items[last + 1][0] != "ident" or items[last + 1][1] in ACTIONS:
      raise ValueError(f"line {line}: expected a kernel name")
    last += 1
    if last + 1 >= len(items) or items[last + 1][0] != "ident" or items[last + 1][1] not in ACTIONS:
      raise ValueError(f"line {line}: expected config, exec or async after the kernel name")
    actions = []
    while last + 1 < len(items) and items[last + 1][0] == "ident" and items[last + 1][1] in ACTIONS:
      last += 1
      actions.append(items[last][1])
      if last + 2 < len(items) and items[last + 1][1] == "," and items[last + 2][1] in ACTIONS:
        last += 1
        continue
      break
    if "async" in actions and len(actions) > 1:
      raise ValueError(f"line {line}: async is a configuration and an execution, it cannot be combined with config or exec")
    if last + 2 < len(items) and items[last + 1][0] == "punct" and items[last + 1][1] == "," and items[last + 2][0] == "ident":
      last += 1
      continue
    if last + 1 < len(items) and items[last + 1][0] == "ident" and items[last + 1][1] in ACTIONS:
      raise ValueError(f"line {line}: the actions of a kernel are separated by a comma")
    return last


def read_decorator(text, items, index):
  start = items[index][2]
  line = text.count("\n", 0, start) + 1
  if index + 2 >= len(items) or items[index + 1][1] not in ("kernel", "context") or items[index + 2][0] != "ident":
    raise ValueError(f"line {line}: expected '@kernel name'")
  last = read_kernel_list(items, index + 1, line)
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


def read_block_statements(text, items, open_index, close):
  statements = []
  contexts = {items[open_index][4] + 1: True}
  j = open_index + 1
  while j < len(items) and items[j][2] < close:
    kind, value, start, end, depth, prev = items[j]
    if kind == "punct" and value == "{":
      contexts[depth + 1] = contexts.get(depth, False) if prev in (";", "}", "{") else False
      j += 1
      continue
    if prev not in (";", "}", "{"):
      j += 1
      continue
    stop = None
    if kind == "ident" and value in ("Transfer", "Int") and contexts.get(depth) and j + 2 < len(items) and items[j + 1][0] == "ident" and items[j + 2][1] == "=":
      k = j
      while items[k][1] != ";" or items[k][4] != depth:
        k += 1
      stop = k
    elif kind == "punct" and value == "." and j + 2 < len(items) and items[j + 1][1] in ("load", "store") and items[j + 2][1] == "{":
      k = j + 2
      while items[k][3] < block_end(text, items, j + 2, start, f".{items[j + 1][1]}"):
        k += 1
      stop = k
    elif kind == "ident" and value == "for" and contexts.get(depth) and j + 3 < len(items) and items[j + 1][0] == "ident" and items[j + 2][1] == "in":
      k = j + 3
      while items[k][1] != "{":
        k += 1
      end_pos = block_end(text, items, k, start, "for")
      while items[k][3] < end_pos:
        k += 1
      stop = k
    if stop is None:
      j += 1
      continue
    statements.append(("block-statement", start, start, items[stop][3]))
    j = stop + 1
  return statements


def read_kernel_block(text, items, index):
  start = items[index][2]
  line = text.count("\n", 0, start) + 1
  last = read_kernel_list(items, index + 1, line)
  if last + 1 >= len(items) or items[last + 1][0] != "punct" or items[last + 1][1] != "{":
    raise ValueError(f"line {line}: @kernel inside a function must be followed by the kernel names and a block {{ ... }}")
  close = block_end(text, items, last + 1, start, "@kernel block") - 1
  inner = read_block_statements(text, items, last + 1, close)
  return [("kernel-block", start, items[last][3], items[last][3])] + inner + [("kernel-block-end", close, close, close)]


def read_emulate(text, items, index):
  start = items[index][2]
  line = text.count("\n", 0, start) + 1
  if index + 2 >= len(items) or items[index + 2][0] != "str" or not EMULATE_ID.fullmatch(items[index + 2][1]):
    raise ValueError(f"line {line}: expected @emulate \"id\", the id is made of letters, digits, - and _ between double quotes")
  if index + 5 >= len(items) or items[index + 3][1] != "." or items[index + 4][1] != "kernel" or items[index + 5][0] != "ident":
    raise ValueError(f"line {line}: @emulate \"id\" must be followed by '.kernel name'")
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
      if prev in (";", "}", "{") and i + 1 < len(items) and items[i + 1][1] == "kernel":
        blocks.extend(read_kernel_block(text, items, i))
        nested = True
        continue
      line = text.count("\n", 0, start) + 1
      raise ValueError(f"line {line}: inside a function only '@kernel name {{ ... }}' is accepted")
    if kind == "punct" and value == "@" and depth == 0 and prev in (";", "}"):
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
    if not (kind == "punct" and value == "." and i + 1 < len(items) and items[i + 1][1] in ("kernel", "context")):
      continue
    if depth != 0 or (prev not in (";", "}") and i not in allowed):
      continue
    j = i + 2
    if j >= len(items) or items[j][0] != "ident":
      continue
    j += 1
    while j < len(items) and items[j][0] == "ident":
      j += 1
    if j < len(items) and items[j][0] == "punct" and items[j][1] == "{":
      blocks.append(("kernel", start, items[j][2], block_end(text, items, j, start)))
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


def decorator_calls(text, block):
  words = [value for _, value, _, _ in tokens(text[block[1]:block[3]])]
  calls = []
  i = 2
  while i < len(words):
    name = words[i]
    actions = []
    i += 1
    while i < len(words) and words[i] in ACTIONS:
      actions.append(words[i])
      i += 1
      if i + 1 < len(words) and words[i] == "," and words[i + 1] in ACTIONS:
        i += 1
        continue
      break
    calls.append((name, tuple(actions)))
    i += 1
  return calls


def decorator_names(text, block):
  return [name for name, _ in decorator_calls(text, block)]
