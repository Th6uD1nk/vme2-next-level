import re

from vmeg.blocks import body_tokens

ICN_NAMES = {
  "swen": "SWEN",
  "top": "AGU_TOP",
  "base": "AGU_BASE",
  "write": "AGU_WRITE",
  "xpcr": "XPCR",
  "skew": "SKEW",
}

AGU_COMMON = ("count", "offset", "mode", "step", "inner0", "reverse")

AGU_PARAMS = {
  "top": AGU_COMMON + ("repeat",),
  "base": AGU_COMMON + ("repeat",),
  "write": AGU_COMMON + ("cyc", "bubbles", "sync"),
}

TRANSFER_USE = ("transfer", "scope", "offsets")

TRANSFER_SCOPES = ("local", "global")

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


def parse_additive(p):
  left = parse_term(p)
  while True:
    if p.accept("+"):
      op = "+"
    elif p.accept("-"):
      op = "-"
    else:
      return left
    left = ("bin", op, left, parse_term(p))


def accept_shift(p):
  tok = p.peek()
  following = p.toks[p.i + 1] if p.i + 1 < len(p.toks) else None
  if tok is None or following is None or tok[0] != "punct" or following[0] != "punct":
    return None
  if tok[1] in ("<", ">") and following[1] == tok[1] and tok[3] == following[2]:
    p.i += 2
    return tok[1] * 2
  return None


def parse_shift(p):
  left = parse_additive(p)
  while True:
    op = accept_shift(p)
    if op is None:
      return left
    left = ("bin", op, left, parse_additive(p))


def accept_and(p):
  tok = p.peek()
  following = p.toks[p.i + 1] if p.i + 1 < len(p.toks) else None
  if tok is None or tok[0] != "punct" or tok[1] != "&":
    return False
  if following is not None and following[0] == "punct" and following[1] == "&" and tok[3] == following[2]:
    return False
  p.i += 1
  return True


def parse_expr(p):
  left = parse_shift(p)
  while accept_and(p):
    left = ("bin", "&", left, parse_shift(p))
  return left


def parse_pe_index(p):
  tok = p.peek()
  if tok is not None and tok[0] == "ident" and tok[1] == "pe":
    p.ident()
    p.expect("[")
    index = parse_expr(p)
    p.expect("]")
    return index
  m = PE_NAME.match(tok[1]) if tok is not None else None
  if m is None:
    p.error("expected a processing element (pe0 to pe3)")
  if int(m.group(1)) > 3:
    p.error("processing element out of range (pe0 to pe3)")
  p.ident()
  return ("num", int(m.group(1)))


def parse_target(p):
  index = parse_pe_index(p)
  p.expect(".")
  return ("target", index, p.ident())


def parse_params(p, nested=False):
  p.expect("{")
  items = []
  if not p.accept("}"):
    while True:
      name = p.ident()
      if p.accept(":"):
        tok = p.peek()
        if tok is not None and tok[1] == "{":
          if nested:
            p.error("a list of parameters cannot be nested more than one level", tok)
          value = parse_params(p, True)
        else:
          value = parse_expr(p)
      else:
        value = ("name", name)
      items.append((name, value))
      if not p.accept(","):
        break
    p.expect("}")
  return ("params", items)


def parse_pe_assignment(p, target):
  name_token = p.toks[p.i - 1]
  p.expect("=")
  tok = p.peek()
  if tok is not None and tok[0] == "punct" and tok[1] == "{":
    if target[2] not in AGU_PARAMS:
      p.error(f"unknown agu '{target[2]}' ({', '.join(AGU_PARAMS)})", name_token)
    kind = "agu"
    value = parse_params(p)
  elif target[2] in AGU_PARAMS:
    if tok is None or tok[0] != "ident":
      p.error("expected parameters { ... } or the name of an Agu variable")
    kind = "aguref"
    value = ("name", p.ident())
  elif target[2] == "out":
    p.error(".out was removed, write the operation in a pe block: pe0 { .expr; }", name_token)
  else:
    p.error(f"unknown element '{target[2]}' of a pe ({', '.join(AGU_PARAMS)})", name_token)
  p.expect(";")
  return (kind, target, value)


def parse_agu_declaration(p):
  p.expect("Agu")
  name = p.ident()
  p.expect("=")
  params = parse_params(p)
  p.expect(";")
  return ("agudecl", name, params)


def parse_transfer_declaration(p):
  p.expect("Transfer")
  name = p.ident()
  p.expect("=")
  params = parse_params(p)
  p.expect(";")
  return ("transferdecl", name, params)


def parse_offsets(p):
  entries = []
  while not p.accept("}"):
    if p.peek() is None:
      p.error("expected '}'")
    start = p.peek()
    if p.accept("."):
      name = p.ident()
      m = BUFFER_NAME.match(name)
      if m is None:
        p.error(f"unknown offset '.{name}' (.top0 to .top3, .base0 to .base3)", start)
      kind, index = m.group(1), ("num", int(m.group(2)))
    else:
      kind = p.ident()
      if kind not in ("top", "base"):
        p.error("expected .top0 to .top3, .base0 to .base3, top[...] or base[...]", start)
      p.expect("[")
      index = parse_expr(p)
      p.expect("]")
    p.expect("=")
    entries.append((kind, index, parse_expr(p)))
    p.expect(";")
  return ("offsets", entries)


def parse_transfer_use(p):
  direction = p.ident()
  p.expect("{")
  items = []
  while not p.accept("}"):
    if p.peek() is None:
      p.error("expected '}'")
    p.expect(".")
    start = p.peek()
    name = p.ident()
    if name not in TRANSFER_USE:
      p.error(f"unknown attribute '.{name}' of .{direction} ({', '.join('.' + n for n in TRANSFER_USE)})", start)
    if any(item[0] == name for item in items):
      p.error(f".{name} is already written in this .{direction}", start)
    if name == "offsets":
      p.expect("{")
      items.append((name, parse_offsets(p)))
      continue
    p.expect("=")
    value = p.peek()
    items.append((name, ("name", p.ident())))
    if name == "scope" and value[1] not in TRANSFER_SCOPES:
      p.error(f".scope must be {' or '.join(TRANSFER_SCOPES)}", value)
    p.expect(";")
  return (direction, items)


def parse_staging_declaration(p):
  p.expect("Staging")
  name = p.ident()
  p.expect(";")
  return ("stagingdecl", name)


def parse_pe_block(p, index):
  body = []
  while not p.accept("}"):
    if p.peek() is None:
      p.error("expected '}'")
    line = p.text.count("\n", 0, p.peek()[2]) + 1
    if p.peek()[1] == "Agu":
      body.append(parse_agu_declaration(p) + (line,))
      continue
    if p.peek()[1] == "Staging":
      body.append(parse_staging_declaration(p) + (line,))
      continue
    if p.peek()[0] == "ident":
      start = p.peek()
      name = p.ident()
      p.expect("=")
      if p.peek() is not None and p.peek()[1] == "{":
        p.error("expected '.'", start)
      expr = parse_expr(p)
      p.expect(";")
      body.append(("stageset", ("target", index, "stage"), name, expr, line))
      continue
    p.expect(".")
    following = p.toks[p.i + 1] if p.i + 1 < len(p.toks) else None
    if following is not None and following[0] == "punct" and following[1] == "=":
      body.append(parse_pe_assignment(p, ("target", index, p.ident())) + (line,))
    else:
      expr = parse_expr(p)
      p.expect(";")
      body.append(("operation", ("target", index, "operation"), expr, line))
  return ("peblock", body)


def parse_pe_statement(p):
  index = parse_pe_index(p)
  if p.accept("{"):
    return parse_pe_block(p, index)
  p.expect(".")
  return parse_pe_assignment(p, ("target", index, p.ident()))


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
    body.append(parse_statement(p))
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
    if tok[1] == "Agu":
      return parse_agu_declaration(p) + (line,)
    if tok[1] == "Staging":
      return parse_staging_declaration(p) + (line,)
    if tok[1] == "Transfer":
      return parse_transfer_declaration(p) + (line,)
    if tok[1] == "pe":
      return parse_pe_statement(p) + (line,)
    if PE_NAME.match(tok[1]):
      following = p.toks[p.i + 1] if p.i + 1 < len(p.toks) else None
      if following is not None and following[1] == "{":
        p.error(f"{tok[1]} {{ }} was removed, write .{tok[1]} {{ }}")
      p.error(f"{tok[1]}.name was removed, write .{tok[1]}.name")
  if tok[0] == "punct" and tok[1] == ".":
    following = p.toks[p.i + 1] if p.i + 1 < len(p.toks) else None
    if following is not None and following[0] == "ident" and PE_NAME.match(following[1]):
      p.i += 1
      return parse_pe_statement(p) + (line,)
    if following is not None and following[0] == "ident" and following[1] in ("load", "store"):
      p.i += 1
      return parse_transfer_use(p) + (line,)
    if following is not None and following[0] == "ident" and following[1] == "pe":
      p.error("pe[...] is an access by index, it takes no dot", following)
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
