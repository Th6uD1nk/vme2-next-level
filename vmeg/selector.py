from functools import lru_cache
from itertools import combinations

from vmeg.operations import OPERATIONS, slots
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


def bind_entry(tree, specification):
  roles = dict(specification["arguments"])
  constants = tuple(name for name, role in roles.items() if role == "number")
  texts = (specification["pattern"], *specification.get("aliases", ()))
  for zeroed in zeroings(constants):
    for text in texts:
      pattern = reduced(text, zeroed)
      if pattern[0] in ("name", "num"):
        continue
      bound = match(pattern, tree, set(constants) - set(zeroed))
      if bound is not None and operands_ok(bound, roles):
        return {**bound, **{name: ZERO for name in zeroed}}
  return None


def candidates(tree, operations=OPERATIONS):
  found = []
  for kind, specification in operations.items():
    bound = bind_entry(tree, specification)
    if bound is not None:
      found.append((kind, bound))
  return found


def cost(kind, bound, operations):
  specification = operations[kind]
  total = slots(specification)
  for name, role in specification["arguments"]:
    if role == "source" and bound[name][0] in OPERATION_NODES:
      inner = select(bound[name], operations)
      if inner is None:
        return None
      total += inner[2]
  return total


def select(tree, operations=OPERATIONS):
  best = None
  for kind, bound in candidates(tree, operations):
    total = cost(kind, bound, operations)
    if total is not None and (best is None or total < best[2]):
      best = (kind, bound, total)
  return best


def usable(operations, compat):
  if compat != "fat":
    return operations
  return {kind: specification for kind, specification in operations.items() if not specification.get("not_portable")}


def choose_opcode(tree, compat, operations=OPERATIONS):
  found = select(tree, usable(operations, compat))
  if found is None:
    anywhere = select(tree, operations)
    if anywhere is not None:
      raise ValueError(f"{anywhere[0]} does not work on the fat and nothing replaces it")
  return found
