from vmeg.parser import Parser, parse_expr
from vmeg.scanner import tokens


def parse_pattern(text):
  toks = list(tokens(text))
  p = Parser(text, toks, len(text))
  tree = parse_expr(p)
  if p.peek() is not None:
    p.error("unexpected text after the pattern")
  return tree
