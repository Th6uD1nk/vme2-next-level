from vmeg.expr import fold, substitute
from vmeg.parser import buffer_ref


def target_pe(target, env):
  index = fold(target[1], env)
  if index[0] != "num":
    raise ValueError("processing element index must be a number")
  pe = index[1]
  if not 0 <= pe <= 3:
    raise ValueError(f"pe{pe}: processing element out of range (pe0 to pe3)")
  return pe


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
