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


ZERO = ("num", 0)


def rebuild(tree, change):
  kind = tree[0]
  if kind == "bin":
    return ("bin", tree[1], change(tree[2]), change(tree[3]))
  if kind in ("not", "neg"):
    return (kind, change(tree[1]))
  if kind == "call":
    return ("call", tree[1], [change(argument) for argument in tree[2]])
  return tree


def substitute(tree, names):
  if tree[0] == "name" and tree[1] in names:
    return ZERO
  return rebuild(tree, lambda child: substitute(child, names))


def simplify(tree):
  tree = rebuild(tree, simplify)
  if tree[0] != "bin":
    return tree
  _, operator, left, right = tree
  if operator in ("+", "|", "^"):
    if left == ZERO:
      return right
    if right == ZERO:
      return left
  if operator in ("-", "<<", ">>") and right == ZERO:
    return left
  if operator in ("*", "&") and ZERO in (left, right):
    return ZERO
  return tree


def without(pattern, names):
  return simplify(substitute(pattern, names))


def children(tree):
  kind = tree[0]
  if kind == "bin":
    return [tree[2], tree[3]]
  if kind in ("not", "neg"):
    return [tree[1]]
  if kind == "call":
    return tree[2]
  return []


def names_of(tree):
  if tree[0] == "name":
    return [tree[1]]
  return [name for child in children(tree) for name in names_of(child)]


def canonical(tree):
  if tree[0] == "name":
    return tree
  tree = rebuild(tree, canonical)
  if tree[0] == "bin" and tree[1] in COMMUTATIVE:
    return ("bin", tree[1], *sorted(tree[2:], key=repr))
  return tree


def check_patterns(operations):
  seen = {}
  for kind, specification in operations.items():
    names = [name for name, _ in specification["arguments"]]
    for text in (specification["pattern"], *specification.get("aliases", ())):
      try:
        tree = parse_pattern(text)
      except ValueError as error:
        raise ValueError(f"the pattern of '{kind}' is not valid: {error}")
      if sorted(set(names_of(tree))) != sorted(names):
        raise ValueError(f"the pattern of '{kind}' must use its arguments ({', '.join(names)})")
      if specification.get("auxiliary"):
        continue
      key = repr(canonical(tree))
      if key in seen:
        raise ValueError(f"'{kind}' and '{seen[key]}' have the same pattern")
      seen[key] = kind
