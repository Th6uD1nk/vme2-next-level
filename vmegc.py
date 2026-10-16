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


def read_decorator(text, items, index):
  start = items[index][2]
  line = text.count("\n", 0, start) + 1
  if index + 2 >= len(items) or items[index + 1][1] != "kernel" or items[index + 2][0] != "ident":
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
  for i, (kind, value, start, end, depth, prev) in enumerate(items):
    if kind == "punct" and value == "@" and depth == 0 and prev in (";", "}"):
      blocks.append(read_decorator(text, items, i))
      continue
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


def parse_buffers_block(p):
  qualifier = p.ident()
  p.expect("buffers")
  p.expect("{")
  return ("buffers", qualifier, parse_buffers(p, True))


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


def substitute_target(target, env):
  return ("target", fold(target[1], env), target[2])


def substitute(statement, env):
  kind = statement[0]
  line = statement[-1]
  if kind == "icn":
    return ("icn", [(name, fold(value, env)) for name, value in statement[1]], line)
  if kind == "const":
    return ("const", statement[1], fold(statement[2], env), line)
  if kind == "agu":
    params = [(key, fold(value, env)) for key, value in statement[2][1]]
    return ("agu", substitute_target(statement[1], env), ("params", params), line)
  if kind == "assign":
    return ("assign", substitute_target(statement[1], env), fold(statement[2], env), line)
  var, low, high, body = statement[1], statement[2], statement[3], statement[4]
  inner = {name: value for name, value in env.items() if name != var}
  return ("for", var, fold(low, env), fold(high, env), [substitute(s, inner) for s in body], line)


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


READ_PARAMS = ("count", "offset", "mode", "step")
AGU_PARAMS = {
  "top": READ_PARAMS,
  "base": READ_PARAMS,
  "write": READ_PARAMS + ("cyc",),
}


def target_pe(target, env):
  index = fold(target[1], env)
  if index[0] != "num":
    raise ValueError("processing element index must be a number")
  pe = index[1]
  if not 0 <= pe <= 3:
    raise ValueError(f"pe{pe}: processing element out of range (pe0 to pe3)")
  return pe


def generate_agu(target, params, env):
  pe = target_pe(target, env)
  agu = target[2]
  values = {}
  for key, value in params[1]:
    if key not in AGU_PARAMS[agu]:
      raise ValueError(f"pe{pe}.{agu}: unknown parameter '{key}' ({', '.join(AGU_PARAMS[agu])})")
    if key in values:
      raise ValueError(f"pe{pe}.{agu}: duplicate parameter '{key}'")
    values[key] = to_c(fold(value, env))
  if "count" not in values:
    raise ValueError(f"pe{pe}.{agu}: 'count' is required")
  mode = f"agu_mode({values['mode']})" if "mode" in values else "VME_DEF_MODE"
  if "offset" in values:
    mode += f", {values['offset']}"
  if "cyc" in values:
    mode += f", vme_cyc({values['cyc']})"
  step = f"agu_step({values['step']})" if "step" in values else "VME_DEF_STEP"
  return [
    f"vme_pe{pe}(agu_{agu}(MODE), {mode});",
    f"vme_pe{pe}(agu_{agu}(COUNT), {step}, {values['count']});",
  ]


BUFFER_NAME = re.compile(r"(top|base)([0-3])$")


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


def constant(expr, what):
  if expr[0] != "num":
    raise ValueError(f"{what} must be a number")
  return expr[1]


def operand(expr):
  ref = buffer_ref(expr)
  if ref is None:
    raise ValueError("an operand must be a buffer (top0 to top3, base0 to base3)")
  return ref


def flatten(expr):
  kind = expr[0]
  if kind == "call":
    name, args = expr[1], expr[2]
    if name == "sat":
      if len(args) != 2:
        raise ValueError("sat takes 2 arguments (value, bits)")
      bits = constant(args[1], "sat bits")
      if not 0 <= bits <= 31:
        raise ValueError("sat bits out of range (0 to 31)")
      return flatten(args[0]) + [("sat", bits)]
    if name == "clamp":
      if len(args) != 3:
        raise ValueError("clamp takes 3 arguments (value, low, high)")
      low = constant(args[1], "clamp low")
      high = constant(args[2], "clamp high")
      return flatten(args[0]) + [("clamp", low, high)]
    raise ValueError(f"unknown operation '{name}' (sat, clamp)")
  if kind == "bin":
    if expr[1] != "+":
      raise ValueError(f"unsupported operator '{expr[1]}' (+)")
    return [("add", operand(expr[2]), operand(expr[3]))]
  raise ValueError("an operation is expected (an addition, sat or clamp)")


KERNEL_OPTIONS = ("direct",)


def unroll(loop):
  _, var, low, high, body, _ = loop
  if low[0] != "num" or high[0] != "num":
    raise ValueError(f"for {var}: bounds must be numbers")
  out = []
  for value in range(low[1], high[1] + 1):
    env = {var: ("num", value)}
    for statement in body:
      statement = substitute(statement, env)
      if statement[0] == "const":
        env[statement[1]] = statement[2]
      elif statement[0] == "for":
        out.extend(unroll(statement))
      else:
        out.append(statement)
  return out


def swen_mask(pes):
  return sum(1 << (3 - pe) for pe in pes)


def emit(statement, env, lines, state):
  try:
    emit_statement(statement, env, lines, state)
  except ValueError as e:
    if str(e).startswith("line "):
      raise
    raise ValueError(f"line {statement[-1]}: {e}") from None


def emit_statement(statement, env, lines, state):
  kind = statement[0]
  if kind == "const":
    if statement[1] in env:
      raise ValueError(f"'{statement[1]}' is defined twice")
    env[statement[1]] = fold(statement[2], env)
  elif kind == "icn":
    for icn, value in statement[1]:
      if icn == "swen":
        state["swen"] = True
      lines.append(f"vme_icn({ICN_NAMES[icn]}, {to_c(fold(value, env))});")
  elif kind == "agu":
    lines.extend(generate_agu(statement[1], statement[2], env))
  elif kind == "assign":
    pe = target_pe(statement[1], env)
    operations = flatten(fold(statement[2], env))
    _, front, back = operations[0]
    fu = f"vme_mux({front}, {back}), fu_code(OP_ADD)"
    after = 1
    if len(operations) > 1 and operations[1][0] == "sat":
      fu += f", fu_sat({operations[1][1]})"
      after = 2
    lines.append(f"vme_pe{pe}(vme_fu(PRIMARY), {fu});")
    if len(operations) > after and operations[after][0] == "clamp":
      _, low, high = operations[after]
      state["secondary"].add(pe)
      lines.append(f"vme_pe{pe}(vme_fu(SECONDARY), vme_mux(NONE, STAGING_{pe}), fu_code(OP_CLP));")
      lines.append(f"vme_pe{pe}(fu_reg(SECONDARY, A), {to_c(('num', high))});")
      lines.append(f"vme_pe{pe}(fu_reg(SECONDARY, B), {to_c(('num', low))});")
  elif kind == "for":
    loop = ("for", statement[1], fold(statement[2], env), fold(statement[3], env), statement[4], statement[5])
    for inner in unroll(loop):
      emit(inner, env, lines, state)


def generate(text, block):
  kind, start, open_pos, _ = block
  if kind == "decorator":
    return ""
  if kind == "buffers":
    line = text.count("\n", 0, start) + 1
    raise ValueError(f"line {line}: buffers must be inside a kernel (global buffers or local buffers)")
  header = text[start:open_pos]
  words = [(value, start + s) for _, value, s, _ in tokens(header)]
  name, options = words[1][0], []
  for word, pos in words[2:]:
    line = text.count("\n", 0, pos) + 1
    if word not in KERNEL_OPTIONS:
      raise ValueError(f"line {line}: unknown kernel option '{word}' ({', '.join(KERNEL_OPTIONS)})")
    if word in options:
      raise ValueError(f"line {line}: duplicate kernel option '{word}'")
    options.append(word)
  toks, limit = body_tokens(text, block)
  statements = parse_body(Parser(text, toks, limit))
  if "direct" not in options:
    return ""
  lines = ["vmeLibStart();"]
  env = {}
  state = {"swen": False, "secondary": set()}
  for statement in statements:
    emit(statement, env, lines, state)
  if state["secondary"] and not state["swen"]:
    lines.append(f"vme_icn(SWEN, fu_on(0b{swen_mask(state['secondary']):04b}));")
  lines.append("vmeLibFinish();")
  body = "".join(f"  {line}\n" for line in lines)
  return f"void {name}() {{\n{body}}}"


BUFFER_TYPE = "u32 __attribute__((aligned(64)))"


def passthrough(text, begin, end, edits):
  out = []
  pos = begin
  for at, length, replacement in edits:
    if begin <= at < end:
      out.append(text[pos:at])
      out.append(replacement)
      pos = at + length
  out.append(text[pos:end])
  return "".join(out)


DECLARATION_QUALIFIERS = ("static", "const", "volatile", "extern", "register", "restrict")


def declarator_names(toks, i):
  names = []
  expect = True
  nest = 0
  for kind, value, _, _ in toks[i + 1:]:
    if kind == "punct" and value in "([{":
      nest += 1
    elif kind == "punct" and value in ")]}":
      nest -= 1
      if nest < 0:
        break
    elif nest == 0:
      if kind == "punct" and value == ";":
        break
      if kind == "punct" and value == ",":
        expect = True
      elif kind == "ident" and expect:
        names.append(value)
        expect = False
  return names


def file_buffer_names(toks):
  names = set()
  depth = 0
  for i, (kind, value, _, _) in enumerate(toks):
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
    elif kind == "ident" and value == "Buffer" and depth == 0:
      names.update(declarator_names(toks, i))
  return names


def function_tokens(text, block):
  begin = block[3]
  parens = 0
  found = False
  depth = 0
  body = []
  for kind, value, start, end in tokens(text[begin:]):
    token = (kind, value, start + begin, end + begin)
    if not found:
      if kind == "punct" and value == "(":
        parens += 1
      elif kind == "punct" and value == ")":
        parens -= 1
      elif kind == "punct" and value == "{" and parens == 0:
        found = True
        depth = 1
        body.append(token)
      continue
    body.append(token)
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
      if depth == 0:
        break
  return body


def function_buffer_names(text, block):
  toks = function_tokens(text, block)
  names = set()
  depth = 0
  for i, (kind, value, _, _) in enumerate(toks):
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
    elif kind == "ident" and value == "Buffer" and depth == 1:
      names.update(declarator_names(toks, i))
  return names


def check_buffers(text, toks, blocks):
  depth = 0
  for i, (kind, value, start, _) in enumerate(toks):
    if any(b[1] <= start < b[3] for b in blocks):
      continue
    if kind == "punct" and value == "(":
      depth += 1
    elif kind == "punct" and value == ")":
      depth = max(0, depth - 1)
    if kind != "ident" or value != "Buffer":
      continue
    line = text.count("\n", 0, start) + 1
    if depth > 0:
      raise ValueError(f"line {line}: Buffer only declares a variable, it cannot be used in a parameter or a cast")
    if i + 1 >= len(toks) or toks[i + 1][0] != "ident":
      raise ValueError(f"line {line}: Buffer must be followed by a variable name (volatile Buffer name[...])")
    found = False
    j = i - 1
    while j >= 0 and toks[j][0] == "ident" and toks[j][1] in DECLARATION_QUALIFIERS:
      if toks[j][1] == "volatile":
        found = True
      j -= 1
    if not found:
      raise ValueError(f"line {line}: Buffer must be volatile (volatile Buffer name[...])")


def kernel_name(text, block):
  return [value for _, value, _, _ in tokens(text[block[1]:block[2]])][1]


def decorator_names(text, block):
  return [value for _, value, _, _ in tokens(text[block[1]:block[3]])][2::2]


def check_decorators(text, blocks):
  kernels = {kernel_name(text, b): b for b in blocks if b[0] == "kernel"}
  decorated = set()
  for block in blocks:
    if block[0] != "decorator":
      continue
    line = text.count("\n", 0, block[1]) + 1
    for name in decorator_names(text, block):
      if name not in kernels:
        known = f"kernels: {', '.join(kernels)}" if kernels else "there is no kernel in this file"
        raise ValueError(f"line {line}: @kernel refers to an unknown kernel '{name}' ({known})")
      decorated.add(name)
  for name, block in kernels.items():
    if name not in decorated:
      line = text.count("\n", 0, block[1]) + 1
      raise ValueError(f"line {line}: kernel '{name}' is never called, add a function marked with @kernel {name}")


def function_body(text, block):
  begin = block[3]
  parens = 0
  open_at = None
  depth = 0
  declaration = None
  pending = False
  for kind, value, start, _ in tokens(text[begin:]):
    start += begin
    if open_at is None:
      if kind == "punct" and value == "(":
        parens += 1
      elif kind == "punct" and value == ")":
        parens -= 1
      elif kind == "punct" and value == "{" and parens == 0:
        open_at = start
        depth = 1
      continue
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
      if depth == 0:
        break
    elif kind == "ident" and value == "Buffer" and depth == 1:
      pending = True
    elif kind == "punct" and value == ";" and depth == 1 and pending:
      declaration = start + 1
      pending = False
  return declaration if declaration is not None else open_at + 1


def call_edits(text, blocks, quoted):
  kernels = {kernel_name(text, b): b for b in blocks if b[0] == "kernel"}
  edits = []
  for block in blocks:
    if block[0] != "decorator":
      continue
    line = text.count("\n", 0, block[1]) + 1
    calls = ""
    for name in decorator_names(text, block):
      words = [value for _, value, _, _ in tokens(text[kernels[name][1]:kernels[name][2]])]
      if "direct" not in words[2:]:
        raise ValueError(f"line {line}: kernel '{name}' is not direct, calling it is not supported yet")
      calls += f"\n  {name}();"
    at = function_body(text, block)
    resume = text.count("\n", 0, at - 1) + 1
    edits.append((at, 0, f'{calls}\n#line {resume} "{quoted}"\n'))
  return edits


def check_global_sources(text, blocks, toks):
  declared = file_buffer_names(toks)
  for block in blocks:
    if block[0] != "kernel":
      continue
    body, limit = body_tokens(text, block)
    for statement in parse_body(Parser(text, body, limit)):
      if statement[0] != "buffers" or statement[1] != "global":
        continue
      for _, _, _, source, line in statement[2]:
        if source not in declared:
          raise ValueError(f"line {line}: '{source}' is not declared with Buffer at the top level of the file (global buffers)")


def check_local_sources(text, blocks):
  functions = {}
  for block in blocks:
    if block[0] != "decorator":
      continue
    declared = function_buffer_names(text, block)
    where = text.count("\n", 0, block[1]) + 1
    for kernel in decorator_names(text, block):
      functions.setdefault(kernel, []).append((declared, where))
  for block in blocks:
    if block[0] != "kernel":
      continue
    kernel = kernel_name(text, block)
    body, limit = body_tokens(text, block)
    for statement in parse_body(Parser(text, body, limit)):
      if statement[0] != "buffers" or statement[1] != "local":
        continue
      for _, _, _, source, line in statement[2]:
        for declared, where in functions[kernel]:
          if source not in declared:
            raise ValueError(f"line {line}: '{source}' is not declared with Buffer in the function marked with @kernel {kernel} at line {where} (local buffers)")


def render(text, blocks, path):
  quoted = path.replace("\\", "\\\\").replace('"', '\\"')
  out = [f'#line 1 "{quoted}"\n']
  toks = list(tokens(text))
  check_buffers(text, toks, blocks)
  codes = [generate(text, block) for block in blocks]
  check_decorators(text, blocks)
  check_global_sources(text, blocks, toks)
  check_local_sources(text, blocks)
  edits = [(s, len("Buffer"), BUFFER_TYPE) for kind, value, s, _ in toks if kind == "ident" and value == "Buffer"]
  edits += call_edits(text, blocks, quoted)
  edits.sort(key=lambda edit: edit[0])
  pos = 0
  for block, code in zip(blocks, codes):
    _, start, _, end = block
    out.append(passthrough(text, pos, start, edits))
    if code:
      first = text.count("\n", 0, start) + 1
      out.append(f'\n#line {first} "{quoted}"\n{code}')
    line = text.count("\n", 0, end) + 1
    out.append(f'\n#line {line} "{quoted}"\n')
    pos = end
  out.append(passthrough(text, pos, len(text), edits))
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
