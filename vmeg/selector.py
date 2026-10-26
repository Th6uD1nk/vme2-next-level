from functools import lru_cache
from itertools import combinations

from vmeg.operations import OPERATIONS
from vmeg.pattern import ZERO, match, parse_pattern, without

OPERATION_NODES = ("bin", "not", "neg", "call")


@lru_cache(maxsize=None)
def reduced(text, zeroed):
  return without(parse_pattern(text), zeroed)


def zeroings(constants):
  for size in range(len(constants) + 1):
    yield from combinations(constants, size)


def operands_ok(bound, roles):
  for name, role in roles.items():
    if role != "number" and (name not in bound or (role == "operand" and bound[name][0] in OPERATION_NODES)):
      return False
  return True


def candidates(tree, operations=OPERATIONS):
  found = []
  for kind, specification in operations.items():
    roles = dict(specification["arguments"])
    constants = tuple(name for name, role in roles.items() if role == "number")
    for zeroed in zeroings(constants):
      pattern = reduced(specification["pattern"], zeroed)
      if pattern[0] in ("name", "num"):
        continue
      bound = match(pattern, tree, set(constants) - set(zeroed))
      if bound is not None and operands_ok(bound, roles):
        found.append((kind, {**bound, **{name: ZERO for name in zeroed}}))
        break
  return found
