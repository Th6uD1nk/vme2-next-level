import re

from vmeg.blocks import body_tokens

ICN_NAMES = {
  "xpcr": "XPCR",
  "skew": "SKEW",
}

AGU_KINDS = ("top", "base", "write")

AGU_PARAMS = {
  4: {
    "top": ("count", "offset", "step", "inner0", "reverse", "repeat"),
    "base": ("count", "offset", "step", "inner0", "reverse", "repeat"),
    "write": ("count", "offset", "step", "inner0", "reverse", "cyc", "bubbles", "sync"),
  },
  2: {
    "top": ("count", "offset", "step", "reverse", "repeat"),
    "base": ("count", "offset", "step", "reverse", "repeat"),
    "write": ("count", "offset", "step", "reverse", "cyc", "bubbles", "sync"),
  },
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
    self.in_call = False

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
  if p.accept("~"):
    return ("not", parse_primary(p))
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


def accept_single(p, symbol):
  tok = p.peek()
  following = p.toks[p.i + 1] if p.i + 1 < len(p.toks) else None
  if tok is None or tok[0] != "punct" or tok[1] != symbol:
    return False
  if following is not None and following[0] == "punct" and following[1] == symbol and tok[3] == following[2]:
    return False
  p.i += 1
  return True


def parse_and(p):
  left = parse_shift(p)
  while accept_single(p, "&"):
    left = ("bin", "&", left, parse_shift(p))
  return left


def parse_xor(p):
  left = parse_and(p)
  while accept_single(p, "^"):
    left = ("bin", "^", left, parse_and(p))
  return left


def parse_expr(p):
  left = parse_xor(p)
  while accept_single(p, "|"):
    left = ("bin", "|", left, parse_xor(p))
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
            p.error("braces cannot be nested more than one level inside the parameters", tok)
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
    if target[2] not in AGU_KINDS:
      p.error(f"unknown agu '{target[2]}' ({', '.join(AGU_KINDS)})", name_token)
    kind = "agu"
    value = parse_params(p)
  elif target[2] in AGU_KINDS:
    if tok is None or tok[0] != "ident":
      p.error("expected parameters { ... } or the name of an Agu variable")
    kind = "aguref"
    value = ("name", p.ident())
  else:
    p.error(f"unknown element '{target[2]}' of a pe ({', '.join(AGU_KINDS)})", name_token)
  p.expect(";")
  return (kind, target, value)


def add_statement(statements, statement):
  if statement[0] == "declarations":
    statements.extend(member + (statement[-1],) for member in statement[1])
  else:
    statements.append(statement)


def parse_declarators(p, keyword, kind, initialized):
  p.expect(keyword)
  members = []
  while True:
    name = p.ident()
    if initialized:
      p.expect("=")
      members.append((kind, name, parse_params(p)))
    else:
      members.append((kind, name))
    if not p.accept(","):
      break
  p.expect(";")
  return ("declarations", members)


def parse_int_declaration(p):
  p.expect("Int")
  members = []
  while True:
    name = p.ident()
    p.expect("=")
    members.append(("int", name, parse_expr(p)))
    if not p.accept(","):
      break
  p.expect(";")
  return ("declarations", members)


AGU_MODES = (2, 4)


def parse_agu_declaration(p):
  p.expect("Agu")
  mode = 4
  if p.accept("("):
    token = p.peek()
    mode = p.number()
    p.expect(")")
    if mode not in AGU_MODES:
      p.error(f"the Agu mode {mode} is not described ({', '.join(str(known) for known in AGU_MODES)})", token)
  members = []
  while True:
    name = p.ident()
    p.expect("=")
    members.append(("agudecl", name, parse_params(p), mode))
    if not p.accept(","):
      break
  p.expect(";")
  return ("declarations", members)


def parse_transfer_declaration(p):
  return parse_declarators(p, "Transfer", "transferdecl", True)


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
  return parse_declarators(p, "Staging", "stagingdecl", False)


def parse_output(p, index):
  p.expect("=")
  expr = parse_expr(p)
  p.expect(";")
  return ("operation", ("target", index, "operation"), expr)


def parse_remap(p, index):
  p.expect("=")
  p.expect("{")
  found = {}
  while True:
    start = p.peek()
    name = p.ident()
    if name not in ("operator", "primary", "secondary"):
      p.error(f"unknown field '{name}' of .remap (operator, primary, secondary)", start)
    if name in found:
      p.error(f"duplicate field '{name}' in .remap", start)
    p.expect(":")
    if name == "operator":
      tok = p.peek()
      if tok is None or tok[0] != "str":
        p.error("operator takes an operator between double quotes, for example \"*\"")
      p.i += 1
      found[name] = tok[1][1:-1]
    else:
      found[name] = parse_expr(p)
    if not p.accept(","):
      break
  p.expect("}")
  p.expect(";")
  if "operator" not in found:
    p.error("the field 'operator' is needed in .remap")
  if "primary" not in found and "secondary" not in found:
    p.error("a .remap needs primary, secondary or both")
  return ("remap", ("target", index, "remap"), found["operator"], found.get("primary"), found.get("secondary"))


def parse_pe_block(p, index):
  body = []
  while not p.accept("}"):
    if p.peek() is None:
      p.error("expected '}'")
    line = p.text.count("\n", 0, p.peek()[2]) + 1
    if p.peek()[1] == "Agu":
      add_statement(body, parse_agu_declaration(p) + (line,))
      continue
    if p.peek()[1] == "Staging":
      add_statement(body, parse_staging_declaration(p) + (line,))
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
    if p.peek()[1] == "spad":
      p.ident()
      body.append(parse_output(p, index) + (line,))
    elif p.peek()[1] == "remap":
      p.ident()
      body.append(parse_remap(p, index) + (line,))
    else:
      body.append(parse_pe_assignment(p, ("target", index, p.ident())) + (line,))
  return ("peblock", body)


def parse_pe_statement(p):
  index = parse_pe_index(p)
  if p.accept("{"):
    return parse_pe_block(p, index)
  p.expect(".")
  if p.peek() is not None and p.peek()[1] == "spad":
    p.ident()
    return parse_output(p, index)
  return parse_pe_assignment(p, ("target", index, p.ident()))


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


def parse_for(p):
  _, var, low, high = parse_for_header(p)
  body = []
  while not p.accept("}"):
    if p.peek() is None:
      p.error("expected '}'")
    add_statement(body, parse_statement(p))
  return ("for", var, low, high, body)


def parse_params_definition(p):
  p.expect("{")
  items = []
  while not p.accept("}"):
    if p.peek() is None:
      p.error("expected '}'")
    parts = []
    while True:
      tok = p.peek()
      if tok is None or (tok[0] != "str" and tok[1] == "}"):
        p.error("expected ';'")
      p.i += 1
      if tok[0] != "str" and tok[1] == ";":
        break
      parts.append(tok)
    if len(parts) < 2 or parts[-1][0] != "ident":
      p.error("a parameter is a C type and a name, for example 'int stage;'", parts[0] if parts else tok)
    name = parts[-1][1]
    if any(name == existing for _, existing in items):
      p.error(f"the parameter '{name}' is declared twice", parts[-1])
    items.append((p.text[parts[0][2]:parts[-1][2]].strip(), name))
  return ("paramsdef", items)


def read_value(p, stops):
  depth = 0
  first = last = None
  while True:
    tok = p.peek()
    if tok is None:
      p.error("expected '}'")
    if tok[0] != "str":
      if depth == 0 and tok[1] in stops:
        break
      if tok[1] in ("(", "[", "{"):
        depth += 1
      elif tok[1] in (")", "]", "}"):
        depth -= 1
        if depth < 0:
          p.error(f"expected {' or '.join(repr(stop) for stop in stops)}")
    if first is None:
      first = tok
    last = tok
    p.i += 1
  if first is None:
    p.error("expected a value")
  return p.text[first[2]:last[3]]


def parse_params_use(p):
  pairs = []

  def add(name, value, token):
    if any(name == existing for existing, _ in pairs):
      p.error(f"the parameter '{name}' is given twice", token)
    pairs.append((name, value))

  if p.accept("="):
    p.expect("{")
    if not p.accept("}"):
      while True:
        token = p.peek()
        name = p.ident()
        p.expect(":")
        add(name, read_value(p, (",", "}")), token)
        if not p.accept(","):
          break
      p.expect("}")
    p.expect(";")
  else:
    p.expect("{")
    while not p.accept("}"):
      p.expect(".")
      token = p.peek()
      name = p.ident()
      p.expect("=")
      add(name, read_value(p, (";",)), token)
      p.expect(";")
  return ("paramsuse", pairs)


def parse_memory_use(p):
  p.expect("=")
  value = read_value(p, (";",))
  p.expect(";")
  return ("memoryuse", value)


def parse_statement(p):
  tok = p.peek()
  line = p.text.count("\n", 0, tok[2]) + 1
  if tok[0] == "ident":
    if tok[1] == "for":
      return parse_for(p) + (line,)
    if tok[1] == "icn":
      return parse_icn(p) + (line,)
    if tok[1] == "Agu":
      return parse_agu_declaration(p) + (line,)
    if tok[1] == "Staging":
      return parse_staging_declaration(p) + (line,)
    if tok[1] == "Transfer":
      return parse_transfer_declaration(p) + (line,)
    if tok[1] == "Int":
      return parse_int_declaration(p) + (line,)
    if tok[1] == "pe":
      return parse_pe_statement(p) + (line,)
  if tok[0] == "punct" and tok[1] == ".":
    following = p.toks[p.i + 1] if p.i + 1 < len(p.toks) else None
    if following is not None and following[0] == "ident" and PE_NAME.match(following[1]):
      p.i += 1
      return parse_pe_statement(p) + (line,)
    if following is not None and following[0] == "ident" and following[1] in ("load", "store"):
      p.i += 1
      return parse_transfer_use(p) + (line,)
    if following is not None and following[0] == "ident" and following[1] == "memory" and p.in_call:
      p.i += 2
      return parse_memory_use(p) + (line,)
    if following is not None and following[0] == "ident" and following[1] == "params":
      p.i += 2
      return (parse_params_use(p) if p.in_call else parse_params_definition(p)) + (line,)
    if following is not None and following[0] == "ident" and following[1] == "pe":
      p.error("pe[...] is an access by index, it takes no dot", following)
  p.error(f"unknown statement '{tok[1]}'")


def parse_body(p):
  statements = []
  while p.peek() is not None:
    add_statement(statements, parse_statement(p))
  return statements


def kernel_statements(text, block, cache):
  statements = cache.get(block[1])
  if statements is None:
    body, limit = body_tokens(text, block)
    statements = cache[block[1]] = parse_body(Parser(text, body, limit))
  return statements
