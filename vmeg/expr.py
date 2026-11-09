def divide(a, b):
  if b == 0:
    raise ValueError("division by zero in an expression")
  quotient = abs(a) // abs(b)
  return -quotient if (a < 0) != (b < 0) else quotient


def modulo(a, b):
  return a - b * divide(a, b)


def logical_shift(a, amount):
  value = a & 0xffffff
  return (value << amount) & 0xffffff if amount >= 0 else value >> -amount


OPERATORS = {
  "+": lambda a, b: a + b,
  "-": lambda a, b: a - b,
  "*": lambda a, b: a * b,
  "/": divide,
  "%": modulo,
  ">>": lambda a, b: a >> b,
  "==": lambda a, b: int(a == b),
  "!=": lambda a, b: int(a != b),
  ">>>": lambda a, b: logical_shift(a, -b),
  "<<<": lambda a, b: logical_shift(a, b),
  "<<": lambda a, b: a << b,
  "&": lambda a, b: a & b,
  "^": lambda a, b: a ^ b,
  "|": lambda a, b: a | b,
}


def element(expr, env):
  index = fold(expr[2], env)
  key = f"{expr[1]}[{index[1]}]" if index[0] == "num" else None
  return index, env.get(key)


def fold(expr, env):
  kind = expr[0]
  if kind == "name":
    return env.get(expr[1], expr)
  if kind == "neg":
    inner = fold(expr[1], env)
    return ("num", -inner[1]) if inner[0] == "num" else ("neg", inner)
  if kind == "not":
    inner = fold(expr[1], env)
    return ("num", ~inner[1]) if inner[0] == "num" else ("not", inner)
  if kind == "bin":
    left = fold(expr[2], env)
    right = fold(expr[3], env)
    if left[0] == "num" and right[0] == "num":
      return ("num", OPERATORS[expr[1]](left[1], right[1]))
    return ("bin", expr[1], left, right)
  if kind == "cond":
    condition = fold(expr[1], env)
    if condition[0] == "num":
      return fold(expr[2] if condition[1] else expr[3], env)
    return ("cond", condition, fold(expr[2], env), fold(expr[3], env))
  if kind == "index":
    index, known = element(expr, env)
    return known if known is not None else ("index", expr[1], index)
  if kind == "call":
    return ("call", expr[1], [fold(arg, env) for arg in expr[2]])
  return expr


def fold_params(items, env):
  return [(key, ("params", fold_params(value[1], env)) if value[0] == "params" else fold(value, env)) for key, value in items]


def substitute_target(target, env):
  return ("target", fold(target[1], env), target[2])


def substitute_decl_name(target, env):
  return (target[0], fold(target[1], env)) if isinstance(target, tuple) else target


def substitute(statement, env):
  kind = statement[0]
  line = statement[-1]
  if kind == "icn":
    return ("icn", [(name, fold(value, env)) for name, value in statement[1]], line)
  if kind == "regs":
    return ("regs", [(name, fold(value, env)) for name, value in statement[1]], line)
  if kind == "int":
    return ("int", statement[1], fold(statement[2], env), line)
  if kind == "agu":
    return ("agu", substitute_target(statement[1], env), ("params", fold_params(statement[2][1], env)), line)
  if kind == "stageset":
    return ("stageset", substitute_target(statement[1], env), substitute_decl_name(statement[2], env), fold(statement[3], env), line)
  if kind == "stagingdecl":
    return ("stagingdecl", substitute_decl_name(statement[1], env), line)
  if kind in ("transferdecl", "paramsdef"):
    return statement
  if kind in ("load", "store"):
    return (kind, [(name, ("offsets", [(buffer, fold(index, env), fold(value, env)) for buffer, index, value in item[1]]) if name == "offsets" else item) for name, item in statement[1]], line)
  if kind == "agudecl":
    return ("agudecl", statement[1], ("params", fold_params(statement[2][1], env)), statement[3], line)
  if kind == "aguref":
    return ("aguref", substitute_target(statement[1], env), statement[2], line)
  if kind == "peblock":
    return ("peblock", [substitute(inner, env) for inner in statement[1]], line)
  if kind == "operation":
    return ("operation", substitute_target(statement[1], env), fold(statement[2], env), line)
  if kind == "remap":
    return ("remap", substitute_target(statement[1], env), statement[2], *(None if unit is None else fold(unit, env) for unit in statement[3:5]), line)
  var, low, high, body = statement[1], statement[2], statement[3], statement[4]
  inner = {name: value for name, value in env.items() if name != var}
  return ("for", var, fold(low, env), fold(high, env), [substitute(s, inner) for s in body], line)


def copy_text(expr, env):
  kind = expr[0]
  if kind == "num":
    return str(expr[1])
  if kind == "name":
    known = env.get(expr[1])
    if known is None:
      return expr[1]
    return str(known[1]) if known[0] == "num" else known[1]
  if kind == "neg":
    return f"(-{copy_text(expr[1], env)})"
  if kind == "not":
    return f"(~{copy_text(expr[1], env)})"
  if kind == "bin":
    return f"({copy_text(expr[2], env)} {expr[1]} {copy_text(expr[3], env)})"
  if kind == "cond":
    return f"({copy_text(expr[1], env)} ? {copy_text(expr[2], env)} : {copy_text(expr[3], env)})"
  if kind == "index":
    known = element(expr, env)[1]
    if known is not None:
      return str(known[1]) if known[0] == "num" else known[1]
  raise ValueError(f"'{kind}' expression not supported here")


def value(expr, env):
  folded = fold(expr, env)
  if folded[0] == "num":
    return folded
  return ("name", copy_text(expr, env))


def to_c(expr):
  kind = expr[0]
  if kind == "num":
    return hex(expr[1]) if expr[1] >= 10 else str(expr[1])
  if kind == "name":
    return expr[1]
  if kind == "neg":
    return f"(-{to_c(expr[1])})"
  if kind == "not":
    return f"(~{to_c(expr[1])})"
  if kind == "bin":
    return f"({to_c(expr[2])} {expr[1]} {to_c(expr[3])})"
  if kind == "cond":
    return f"({to_c(expr[1])} ? {to_c(expr[2])} : {to_c(expr[3])})"
  raise ValueError(f"'{kind}' expression not supported here")
