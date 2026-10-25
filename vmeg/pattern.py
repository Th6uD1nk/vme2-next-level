from vmeg.parser import Parser, parse_expr
from vmeg.scanner import tokens


def parse_pattern(text):
  toks = list(tokens(text))
  p = Parser(text, toks, len(text))
  tree = parse_expr(p)
  if p.peek() is not None:
    p.error("unexpected text after the pattern")
  return tree


COMMUTATIVE = ("+", "*", "&", "|", "^")


def match(pattern, expr, constants):
  return bind(pattern, expr, constants, {})


def bind(pattern, expr, constants, found):
  kind = pattern[0]
  if kind == "name":
    return bind_name(pattern[1], expr, constants, found)
  if kind == "num":
    return found if expr == pattern else None
  if expr[0] != kind:
    return None
  if kind == "bin":
    if expr[1] != pattern[1]:
      return None
    straight = bind_all(pattern[2:], expr[2:], constants, found)
    if straight is not None or pattern[1] not in COMMUTATIVE:
      return straight
    return bind_all(pattern[2:], expr[:1:-1], constants, found)
  if kind == "call":
    if expr[1] != pattern[1] or len(expr[2]) != len(pattern[2]):
      return None
    return bind_all(pattern[2], expr[2], constants, found)
  return bind(pattern[1], expr[1], constants, found)


def bind_all(patterns, exprs, constants, found):
  for pattern, expr in zip(patterns, exprs):
    found = bind(pattern, expr, constants, found)
    if found is None:
      return None
  return found


def bind_name(name, expr, constants, found):
  if (expr[0] == "num") != (name in constants):
    return None
  if name in found:
    return found if found[name] == expr else None
  return {**found, name: expr}
