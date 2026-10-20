import re

from vmeg.expr import fold
from vmeg.parser import Parser, parse_expr
from vmeg.scanner import tokens

DIRECTIVE = re.compile(r"#\s*([A-Za-z_]\w*)\s*(.*)", re.S)
DEFINE = re.compile(r"([A-Za-z_]\w*)(\([^)]*\))?(.*)", re.S)
COMMENTS = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
OPENING = ("if", "ifdef", "ifndef")


def macro_events(text):
  events = []
  depth = 0
  for kind, value, start, _ in tokens(text):
    if kind != "pp":
      continue
    m = DIRECTIVE.match(value)
    if m is None:
      continue
    name, rest = m.group(1), m.group(2)
    if name in OPENING:
      depth += 1
    elif name == "endif":
      depth = max(depth - 1, 0)
    elif name == "define":
      parts = DEFINE.match(rest.strip())
      if parts is not None:
        body = " ".join(COMMENTS.sub(" ", parts.group(3).replace("\\\n", " ")).split())
        events.append({"kind": "define", "name": parts.group(1), "params": parts.group(2), "body": body, "start": start, "conditional": depth > 0})
    elif name == "undef":
      target = rest.split()
      if target:
        events.append({"kind": "undef", "name": target[0], "params": None, "body": "", "start": start, "conditional": depth > 0})
  return events


def trusted_macros(text, position):
  defined = {}
  undone = set()
  for event in macro_events(text):
    if event["kind"] == "define":
      defined.setdefault(event["name"], []).append(event)
    else:
      undone.add(event["name"])
  trusted = {}
  for name, found in defined.items():
    event = found[0]
    if len(found) == 1 and name not in undone and not event["conditional"] and event["params"] is None and event["start"] < position:
      trusted[name] = event["body"]
  return trusted


def evaluate(body, resolve):
  toks = list(tokens(body))
  if not toks:
    return None
  env = {}
  for kind, value, _, _ in toks:
    if kind == "ident":
      number = resolve(value)
      if number is None:
        return None
      env[value] = ("num", number)
  try:
    p = Parser(body, toks, len(body))
    expr = parse_expr(p)
    if p.peek() is not None:
      return None
  except ValueError:
    return None
  folded = fold(expr, env)
  return folded[1] if folded[0] == "num" else None


def known_macros(text, position):
  bodies = trusted_macros(text, position)
  values = {}
  visiting = set()

  def resolve(name):
    if name in values:
      return values[name]
    if name not in bodies or name in visiting:
      return None
    visiting.add(name)
    values[name] = evaluate(bodies[name], resolve)
    visiting.discard(name)
    return values[name]

  return {name: number for name in bodies for number in [resolve(name)] if number is not None}
