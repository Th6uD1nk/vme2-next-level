import re

from vmeg.blocks import body_tokens
from vmeg.expr import fold, to_c

ICN_NAMES = {
  "swen": "SWEN",
  "top": "AGU_TOP",
  "base": "AGU_BASE",
  "write": "AGU_WRITE",
  "xpcr": "XPCR",
  "skew": "SKEW",
}

READ_PARAMS = ("count", "offset", "mode", "step")

AGU_PARAMS = {
  "top": READ_PARAMS,
  "base": READ_PARAMS,
  "write": READ_PARAMS + ("cyc",),
}

PE_NAME = re.compile(r"pe([0-9]+)$")

BUFFER_NAME = re.compile(r"(top|base)([0-3])$")


class Parser:
  def __init__(self, text, toks, limit):
    self.text = text
    self.toks = toks
    self.limit = limit
    self.i = 0

  def error(self, message, token=None):
    if token is not None:
      pos = token[2]
    else:
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
  name_token = p.toks[p.i - 1]
  p.expect("=")
  tok = p.peek()
  if tok is not None and tok[0] == "punct" and tok[1] == "{":
    if target[2] not in AGU_PARAMS:
      p.error(f"unknown agu '{target[2]}' ({', '.join(AGU_PARAMS)})", name_token)
    kind = "agu"
    value = parse_params(p)
  else:
    if target[2] != "out":
      p.error(f"cannot assign an expression to '{target[2]}', only to 'out'", name_token)
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


def buffer_ref(expr):
  if expr[0] == "name":
    m = BUFFER_NAME.match(expr[1])
    if m:
      return f"{m.group(1).upper()}_{m.group(2)}"
    return None
  if expr[0] == "index" and expr[1] in ("top", "base"):
    if expr[2][0] != "num":
      raise ValueError(f"{expr[1]}[...]: buffer index must be a number")
    if not 0 <= expr[2][1] <= 3:
      raise ValueError(f"{expr[1]}[{expr[2][1]}]: buffer index out of range (0 to 3)")
    return f"{expr[1].upper()}_{expr[2][1]}"
  return None


def parse_buffer_target(p):
  start = p.peek()
  if start is None:
    p.error("expected a buffer (top0 to top3, base0 to base3)")
  try:
    ref = buffer_ref(fold(parse_expr(p), {}))
  except ValueError as e:
    p.error(str(e), start)
  if ref is None:
    p.error("expected a buffer (top0 to top3, base0 to base3)", start)
  return ref


def parse_buffer_count(p):
  p.expect(",")
  start = p.peek()
  count = fold(parse_expr(p), {})
  if count[0] != "num":
    p.error("the number of words must be a number", start)
  if count[1] < 1:
    p.error("the number of words must be at least 1", start)
  p.expect("words")
  return count[1]


def parse_buffer_offset(p):
  tok = p.peek()
  after = p.toks[p.i + 1] if p.i + 1 < len(p.toks) else None
  if tok is None or tok[1] != "," or after is None or after[1] != "at":
    return None
  p.expect(",")
  p.expect("at")
  start = p.peek()
  offset = fold(parse_expr(p), {})
  if offset[0] == "num" and offset[1] < 0:
    p.error("the offset must not be negative", start)
  return offset


def parse_buffer_source(p):
  p.expect(",")
  p.expect("from")
  return p.ident()


def parse_buffers(p, closed=False):
  entries = []
  while True:
    if closed:
      if p.accept("}"):
        break
      if p.peek() is None:
        p.error("expected '}'")
    elif p.peek() is None:
      break
    line = p.text.count("\n", 0, p.peek()[2]) + 1
    target = parse_buffer_target(p)
    count = parse_buffer_count(p)
    offset = parse_buffer_offset(p)
    source = parse_buffer_source(p)
    p.expect(";")
    entries.append((target, count, offset, source, line))
  return entries


def parse_buffers_block(p):
  qualifier = p.ident()
  p.expect("buffers")
  p.expect("{")
  return ("buffers", qualifier, parse_buffers(p, True))


def upload_text(target, count, offset, source):
  kind, index = target.split("_")
  destination = f"VME_{kind}_BUFF{index}_WOFF"
  if offset:
    destination += f" + {offset}"
  return f"vmeLibMemoryToRingBuffer((void*){source}, {destination}, {count});"



def parse_for(p):
  _, var, low, high = parse_for_header(p)
  body = []
  while not p.accept("}"):
    if p.peek() is None:
      p.error("expected '}'")
    start = p.peek()
    statement = parse_statement(p)
    if statement[0] == "buffers":
      p.error("buffers cannot be inside a for", start)
    body.append(statement)
  return ("for", var, low, high, body)


def parse_statement(p):
  tok = p.peek()
  line = p.text.count("\n", 0, tok[2]) + 1
  if tok[0] == "ident":
    if tok[1] == "for":
      return parse_for(p) + (line,)
    if tok[1] == "icn":
      return parse_icn(p) + (line,)
    if tok[1] == "const":
      return parse_const(p) + (line,)
    if tok[1] == "pe" or PE_NAME.match(tok[1]):
      return parse_pe_statement(p) + (line,)
    if tok[1] in ("global", "local"):
      return parse_buffers_block(p) + (line,)
    if tok[1] == "buffers":
      p.error("buffers needs a qualifier: global buffers or local buffers")
  p.error(f"unknown statement '{tok[1]}'")


def parse_body(p):
  statements = []
  while p.peek() is not None:
    statements.append(parse_statement(p))
  return statements


def kernel_statements(text, block, cache):
  statements = cache.get(block[1])
  if statements is None:
    body, limit = body_tokens(text, block)
    statements = cache[block[1]] = parse_body(Parser(text, body, limit))
  return statements
