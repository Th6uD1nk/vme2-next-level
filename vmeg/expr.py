OPERATORS = {
  "+": lambda a, b: a + b,
  "-": lambda a, b: a - b,
  "*": lambda a, b: a * b,
  ">>": lambda a, b: a >> b,
  "<<": lambda a, b: a << b,
  "&": lambda a, b: a & b,
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


def fold_params(items, env):
  return [(key, ("params", fold_params(value[1], env)) if value[0] == "params" else fold(value, env)) for key, value in items]


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
    return ("agu", substitute_target(statement[1], env), ("params", fold_params(statement[2][1], env)), line)
  if kind == "stageset":
    return ("stageset", substitute_target(statement[1], env), statement[2], fold(statement[3], env), line)
  if kind in ("stagingdecl", "transferdecl", "load", "store"):
    return statement
  if kind == "agudecl":
    return ("agudecl", statement[1], ("params", fold_params(statement[2][1], env)), line)
  if kind == "aguref":
    return ("aguref", substitute_target(statement[1], env), statement[2], line)
  if kind == "peblock":
    return ("peblock", [substitute(inner, env) for inner in statement[1]], line)
  if kind == "operation":
    return ("operation", substitute_target(statement[1], env), fold(statement[2], env), line)
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
