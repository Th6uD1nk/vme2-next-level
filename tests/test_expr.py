import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.expr import value
from vmeg.parser import Parser, parse_expr
from vmeg.scanner import tokens


def evaluate(text, env):
  toks = list(tokens(text))
  return value(parse_expr(Parser(text, toks, len(text))), env)


def chain(rows):
  env = {}
  for name, text in rows:
    env[name] = evaluate(text, env)
  return env


class KnownValueTest(unittest.TestCase):
  def test_a_calculation_of_numbers_gives_a_number(self):
    results = [evaluate(text, {}) for text in ["2", "3 + 2 * 4", "(1 << 4) & 0xff", "0 - 3"]]
    self.assertEqual(results, [("num", 2), ("num", 11), ("num", 16), ("num", -3)])

  def test_a_chain_of_assignments_is_evaluated_from_the_previous_ones(self):
    env = chain([("a", "2"), ("b", "a * 3"), ("c", "b + a"), ("d", "(c - a) * b")])
    self.assertEqual(env, {"a": ("num", 2), "b": ("num", 6), "c": ("num", 8), "d": ("num", 36)})


if __name__ == "__main__":
  unittest.main()
