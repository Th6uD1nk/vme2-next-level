import argparse
import os
import re
import sys

SUFFIX = ".vmeg.c"

IDENT = re.compile(r"[A-Za-z_]\w*")
NUMBER = re.compile(r"[0-9]\w*(?:\.(?!\.)\w*)?")
STRING = re.compile(r'"(?:[^"\\\n]|\\[\s\S])*"|\'(?:[^\'\\\n]|\\[\s\S])*\'')
DIRECTIVE = re.compile(r"#(?:\\\r?\n|\\.|[^\n\\])*")
BLANK = re.compile(r"(?:\s+|//[^\n]*|/\*.*?\*/)+", re.S)

ICN_NAMES = {
  "swen": "SWEN",
  "top": "AGU_TOP",
  "base": "AGU_BASE",
  "write": "AGU_WRITE",
  "xpcr": "XPCR",
  "skew": "SKEW",
}


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


def body_tokens(text, block):
  _, _, open_pos, end = block
  offset = open_pos + 1
  body = text[offset:end - 1]
  return [(k, v, s + offset, e + offset) for k, v, s, e in tokens(body)], end - 1


class Parser:
  def __init__(self, text, toks, limit):
    self.text = text
    self.toks = toks
    self.limit = limit
    self.i = 0

  def error(self, message):
    pos = self.toks[self.i][2] if self.i < len(self.toks) else self.limit
    line = self.text.count("\n", 0, pos) + 1
    raise ValueError(f"line {line}: {message}")

  def peek(self):
    return self.toks[self.i] if self.i < len(self.toks) else None

  def accept(self, value):
    tok = self.peek()
    if tok is not None and tok[0] != "str" and tok[1] == value:
      self.i += 1
      return True
    return False

  def expect(self, value):
    if not self.accept(value):
      self.error(f"expected '{value}'")

  def ident(self):
    tok = self.peek()
    if tok is None or tok[0] != "ident":
      self.error("expected a name")
    self.i += 1
    return tok[1]

  def number(self):
    tok = self.peek()
    if tok is None or tok[0] != "num":
      self.error("expected a number")
    try:
      value = int(tok[1], 0)
    except ValueError:
      self.error(f"invalid number '{tok[1]}'")
    self.i += 1
    return value


def parse_icn(p):
  p.expect("icn")
  items = []
  while True:
    tok = p.peek()
    if tok is not None and tok[0] == "ident":
      if tok[1] not in ICN_NAMES:
        p.error(f"unknown interconnect '{tok[1]}' ({', '.join(ICN_NAMES)})")
      if any(tok[1] == done for done, _ in items):
        p.error(f"duplicate interconnect '{tok[1]}'")
    name = p.ident()
    p.expect("=")
    items.append((name, parse_expr(p)))
    if not p.accept(","):
      break
  p.expect(";")
  return ("icn", items)


def parse_primary(p):
  if p.accept("("):
    expr = parse_expr(p)
    p.expect(")")
    return expr
  if p.accept("-"):
    return ("neg", parse_primary(p))
  tok = p.peek()
  if tok is not None and tok[0] == "ident":
    name = p.ident()
    if p.accept("["):
      index = parse_expr(p)
      p.expect("]")
      return ("index", name, index)
    if p.accept("("):
      args = []
      if not p.accept(")"):
        while True:
          args.append(parse_expr(p))
          if not p.accept(","):
            break
        p.expect(")")
      return ("call", name, args)
    return ("name", name)
  return ("num", p.number())


def parse_term(p):
  left = parse_primary(p)
  while p.accept("*"):
    left = ("bin", "*", left, parse_primary(p))
  return left


def parse_expr(p):
  left = parse_term(p)
  while True:
    if p.accept("+"):
      op = "+"
    elif p.accept("-"):
      op = "-"
    else:
      return left
    left = ("bin", op, left, parse_term(p))


PE_NAME = re.compile(r"pe([0-9]+)$")


def parse_target(p):
  tok = p.peek()
  if tok is not None and tok[0] == "ident" and tok[1] == "pe":
    p.ident()
    p.expect("[")
    index = parse_expr(p)
    p.expect("]")
  else:
    m = PE_NAME.match(tok[1]) if tok is not None else None
    if m is None:
      p.error("expected a processing element (pe0 to pe3)")
    if int(m.group(1)) > 3:
      p.error("processing element out of range (pe0 to pe3)")
    p.ident()
    index = ("num", int(m.group(1)))
  p.expect(".")
  return ("target", index, p.ident())


def parse_params(p):
  p.expect("{")
  items = []
  if not p.accept("}"):
    while True:
      name = p.ident()
      if p.accept(":"):
        value = parse_expr(p)
      else:
        value = ("name", name)
      items.append((name, value))
      if not p.accept(","):
        break
    p.expect("}")
  return ("params", items)


def parse_pe_statement(p):
  target = parse_target(p)
  p.expect("=")
  tok = p.peek()
  if tok is not None and tok[0] == "punct" and tok[1] == "{":
    kind = "agu"
    value = parse_params(p)
  else:
    kind = "assign"
    value = parse_expr(p)
  p.expect(";")
  return (kind, target, value)


def parse_const(p):
  p.expect("const")
  name = p.ident()
  p.expect("=")
  value = parse_expr(p)
  p.expect(";")
  return ("const", name, value)


def parse_for_header(p):
  p.expect("for")
  var = p.ident()
  p.expect("in")
  low = parse_expr(p)
  p.expect(".")
  p.expect(".")
  high = parse_expr(p)
  p.expect("{")
  return ("for", var, low, high)


def parse_for(p):
  _, var, low, high = parse_for_header(p)
  body = []
  while not p.accept("}"):
    if p.peek() is None:
      p.error("expected '}'")
    body.append(parse_statement(p))
  return ("for", var, low, high, body)


def parse_statement(p):
  tok = p.peek()
  if tok[0] == "ident":
    if tok[1] == "for":
      return parse_for(p)
    if tok[1] == "icn":
      return parse_icn(p)
    if tok[1] == "const":
      return parse_const(p)
    if tok[1] == "pe" or PE_NAME.match(tok[1]):
      return parse_pe_statement(p)
  p.error(f"unknown statement '{tok[1]}'")


def parse_body(p):
  statements = []
  while p.peek() is not None:
    statements.append(parse_statement(p))
  return statements


OPERATORS = {
  "+": lambda a, b: a + b,
  "-": lambda a, b: a - b,
  "*": lambda a, b: a * b,
}


def fold(expr, env):
  kind = expr[0]
  if kind == "name":
    return env.get(expr[1], expr)
  if kind == "neg":
    inner = fold(expr[1], env)
    return ("num", -inner[1]) if inner[0] == "num" else ("neg", inner)
  if kind == "bin":
    left = fold(expr[2], env)
    right = fold(expr[3], env)
    if left[0] == "num" and right[0] == "num":
      return ("num", OPERATORS[expr[1]](left[1], right[1]))
    return ("bin", expr[1], left, right)
  if kind == "index":
    return ("index", expr[1], fold(expr[2], env))
  if kind == "call":
    return ("call", expr[1], [fold(arg, env) for arg in expr[2]])
  return expr


def to_c(expr):
  kind = expr[0]
  if kind == "num":
    return hex(expr[1]) if expr[1] >= 10 else str(expr[1])
  if kind == "name":
    return expr[1]
  if kind == "neg":
    return f"(-{to_c(expr[1])})"
  if kind == "bin":
    return f"({to_c(expr[2])} {expr[1]} {to_c(expr[3])})"
  raise ValueError(f"'{kind}' expression not supported here")


def generate(text, block):
  kind, start, open_pos, _ = block
  if kind != "kernel":
    return ""
  words = text[start:open_pos].split()
  name, options = words[1], words[2:]
  if "direct" not in options:
    return ""
  toks, limit = body_tokens(text, block)
  statements = parse_body(Parser(text, toks, limit))
  lines = ["vmeLibStart();"]
  env = {}
  for statement in statements:
    if statement[0] == "const":
      if statement[1] in env:
        raise ValueError(f"'{statement[1]}' is defined twice")
      env[statement[1]] = fold(statement[2], env)
    elif statement[0] == "icn":
      for icn, value in statement[1]:
        lines.append(f"vme_icn({ICN_NAMES[icn]}, {to_c(fold(value, env))});")
  lines.append("vmeLibFinish();")
  body = "".join(f"  {line}\n" for line in lines)
  return f"void {name}() {{\n{body}}}"


def render(text, blocks, path):
  quoted = path.replace("\\", "\\\\").replace('"', '\\"')
  out = [f'#line 1 "{quoted}"\n']
  pos = 0
  for block in blocks:
    _, start, _, end = block
    code = generate(text, block)
    out.append(text[pos:start])
    if code:
      first = text.count("\n", 0, start) + 1
      out.append(f'\n#line {first} "{quoted}"\n{code}')
    line = text.count("\n", 0, end) + 1
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

  try:
    result = render(text, blocks, args.input)
  except ValueError as e:
    print(f"{args.input}: {e}", file=sys.stderr)
    return 1

  output = args.output or default_output(args.input)
  with open(output, "w", encoding="utf-8", newline="") as f:
    f.write(result)
  return 0


if __name__ == "__main__":
  sys.exit(main())
