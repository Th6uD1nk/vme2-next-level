import argparse
import os
import re
import sys

SUFFIX = ".vmeg.c"

IDENT = re.compile(r"[A-Za-z_]\w*")
NUMBER = re.compile(r"[0-9][\w.]*")
STRING = re.compile(r'"(?:[^"\\\n]|\\[\s\S])*"|\'(?:[^\'\\\n]|\\[\s\S])*\'')
DIRECTIVE = re.compile(r"#(?:\\\r?\n|\\.|[^\n\\])*")
BLANK = re.compile(r"(?:\s+|//[^\n]*|/\*.*?\*/)+", re.S)


def tokens(text):
  pos = 0
  size = len(text)
  while pos < size:
    m = BLANK.match(text, pos)
    if m:
      pos = m.end()
      continue
    if text.startswith("/*", pos):
      line = text.count("\n", 0, pos) + 1
      raise ValueError(f"line {line}: unterminated comment")
    m = STRING.match(text, pos)
    if m:
      yield ("str", m.group(), m.start(), m.end())
      pos = m.end()
      continue
    if text[pos] in "\"'":
      line = text.count("\n", 0, pos) + 1
      raise ValueError(f"line {line}: unterminated literal")
    if text[pos] == "#" and text[text.rfind("\n", 0, pos) + 1:pos].strip() == "":
      m = DIRECTIVE.match(text, pos)
      yield ("pp", m.group(), m.start(), m.end())
      pos = m.end()
      continue
    m = IDENT.match(text, pos)
    kind = "ident"
    if not m:
      m = NUMBER.match(text, pos)
      kind = "num"
    if not m:
      yield ("punct", text[pos], pos, pos + 1)
      pos += 1
      continue
    yield (kind, m.group(), m.start(), m.end())
    pos = m.end()


def default_output(path):
  name = os.path.basename(path)
  if not name.endswith(SUFFIX):
    raise SystemExit(f"vmegc: input must end with {SUFFIX} (or pass -o)")
  return name[:-len(SUFFIX)] + ".c"


def walk(text):
  depth = 0
  prev = ";"
  for kind, value, start, end in tokens(text):
    yield (kind, value, start, end, depth, prev)
    if kind == "pp":
      prev = ";"
      continue
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth = max(0, depth - 1)
    prev = value


def find_blocks(text):
  items = list(walk(text))
  blocks = []
  for i, (kind, value, start, end, depth, prev) in enumerate(items):
    if kind != "ident" or value not in ("buffers", "kernel"):
      continue
    if depth != 0 or prev not in (";", "}"):
      continue
    j = i + 1
    if value == "kernel":
      if j >= len(items) or items[j][0] != "ident":
        continue
      j += 1
      while j < len(items) and items[j][0] == "ident":
        j += 1
    if j < len(items) and items[j][0] == "punct" and items[j][1] == "{":
      blocks.append((value, start, items[j][2], block_end(text, items, j, start)))
  return blocks


def block_end(text, items, open_index, start):
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
  raise ValueError(f"line {line}: unterminated block")


def render(text, blocks, path):
  quoted = path.replace("\\", "\\\\").replace('"', '\\"')
  out = [f'#line 1 "{quoted}"\n']
  pos = 0
  for _, start, _, end in blocks:
    line = text.count("\n", 0, end) + 1
    out.append(text[pos:start])
    out.append(f'\n#line {line} "{quoted}"\n')
    pos = end
  out.append(text[pos:])
  return "".join(out)


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmegc")
  parser.add_argument("input")
  parser.add_argument("-o", "--output")
  parser.add_argument("--list", action="store_true")
  args = parser.parse_args(argv)

  with open(args.input, encoding="utf-8", newline="") as f:
    text = f.read()

  try:
    blocks = find_blocks(text)
  except ValueError as e:
    print(f"{args.input}: {e}", file=sys.stderr)
    return 1

  if args.list:
    for kind, start, open_pos, end in blocks:
      first = text.count("\n", 0, start) + 1
      last = text.count("\n", 0, end - 1) + 1
      header = " ".join(text[start:open_pos].split())
      print(f"{args.input}:{first}-{last}: {header}")
    return 0

  output = args.output or default_output(args.input)
  with open(output, "w", encoding="utf-8", newline="") as f:
    f.write(render(text, blocks, args.input))
  return 0


if __name__ == "__main__":
  sys.exit(main())
