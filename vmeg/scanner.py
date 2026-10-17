import re

IDENT = re.compile(r"[A-Za-z_]\w*")
NUMBER = re.compile(r"[0-9]\w*(?:\.(?!\.)\w*)?")
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
