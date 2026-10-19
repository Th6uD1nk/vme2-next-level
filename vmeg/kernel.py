from vmeg.blocks import body_tokens
from vmeg.expr import fold, substitute, to_c
from vmeg.parser import AGU_PARAMS, ICN_NAMES, Parser, buffer_ref, parse_body
from vmeg.scanner import tokens

KERNEL_OPTIONS = ("direct",)


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
      elif statement[0] == "peblock":
        out.extend(statement[1])
      else:
        out.append(statement)
  return out


def generate_agu(target, params, env):
  pe = target_pe(target, env)
  agu = target[2]
  values = {}
  for key, value in params[1]:
    if key not in AGU_PARAMS[agu]:
      raise ValueError(f"pe{pe}.{agu}: unknown parameter '{key}' ({', '.join(AGU_PARAMS[agu])})")
    if key in values:
      raise ValueError(f"pe{pe}.{agu}: duplicate parameter '{key}'")
    folded = fold(value, env)
    if key == "offset" and folded[0] == "num" and not -32768 <= folded[1] <= 32767:
      raise ValueError(f"pe{pe}.{agu}: the offset {folded[1]} is outside -32768 to 32767")
    if key == "offset":
      if folded[0] == "num":
        values[key] = to_c(("num", folded[1] & 0xffff))
      else:
        text = to_c(folded)
        values[key] = f"{text if folded[0] != 'name' else '(' + text + ')'} & 0xffff"
    else:
      values[key] = to_c(folded)
  if "count" not in values:
    raise ValueError(f"pe{pe}.{agu}: 'count' is required")
  mode = f"agu_mode({values['mode']})" if "mode" in values else "VME_DEF_MODE"
  if "offset" in values:
    mode += f", {values['offset']}"
  if "cyc" in values:
    mode += f", vme_cyc({values['cyc']})"
  step = f"agu_step({values['step']})" if "step" in values else "VME_DEF_STEP"
  return [
    f"vme_pe{pe}(agu_{agu}(MODE), {mode});",
    f"vme_pe{pe}(agu_{agu}(COUNT), {step}, {values['count']});",
  ]


def swen_mask(pes):
  return sum(1 << (3 - pe) for pe in pes)


def emit(statement, env, lines, state):
  try:
    emit_statement(statement, env, lines, state)
  except ValueError as e:
    if str(e).startswith("line "):
      raise
    raise ValueError(f"line {statement[-1]}: {e}") from None


def warn(state, line, message):
  state["warnings"].append((line, message))


def claim(state, pe, name, line):
  key = (pe, name)
  if key in state["set"]:
    raise ValueError(f"pe{pe}.{name} is already set at line {state['set'][key]}")
  state["set"][key] = line


def emit_statement(statement, env, lines, state):
  kind = statement[0]
  if kind == "const":
    if statement[1] in env:
      raise ValueError(f"'{statement[1]}' is defined twice")
    env[statement[1]] = fold(statement[2], env)
  elif kind == "icn":
    for icn, value in statement[1]:
      if icn == "swen":
        state["swen"] = True
      if icn in state["routing"]:
        raise ValueError(f"icn {icn} was removed, the routing is derived from the .{icn} bindings")
      lines.append(f"vme_icn({ICN_NAMES[icn]}, {to_c(fold(value, env))});")
  elif kind == "agu":
    pe = target_pe(statement[1], env)
    claim(state, pe, statement[1][2], statement[-1])
    state["routing"][statement[1][2]][pe] = pe
    lines.extend(generate_agu(statement[1], statement[2], env))
  elif kind == "agudecl":
    if statement[1] in state["agus"]:
      raise ValueError(f"the Agu variable '{statement[1]}' is declared twice")
    state["agus"][statement[1]] = {"params": statement[2], "owners": {}}
  elif kind == "aguref":
    variable = state["agus"].get(statement[2][1])
    if variable is None:
      raise ValueError(f"unknown Agu variable '{statement[2][1]}'")
    pe = target_pe(statement[1], env)
    slot = statement[1][2]
    for bound in variable["owners"]:
      if bound != slot:
        raise ValueError(f"the Agu variable '{statement[2][1]}' is already bound to .{bound}, it cannot be bound to .{slot}")
    claim(state, pe, slot, statement[-1])
    if slot not in variable["owners"]:
      variable["owners"][slot] = pe
      lines.extend(generate_agu(("target", ("num", pe), slot), variable["params"], env))
    state["routing"][slot][pe] = variable["owners"][slot]
  elif kind == "assign":
    pe = target_pe(statement[1], env)
    claim(state, pe, "out", statement[-1])
    operations = flatten(fold(statement[2], env))
    _, front, back = operations[0]
    fu = f"vme_mux({front}, {back}), fu_code(OP_ADD)"
    after = 1
    if len(operations) > 1 and operations[1][0] == "sat":
      fu += f", fu_sat({operations[1][1]})"
      after = 2
    lines.append(f"vme_pe{pe}(vme_fu(PRIMARY), {fu});")
    if len(operations) > after and operations[after][0] == "clamp":
      _, low, high = operations[after]
      state["secondary"].add(pe)
      lines.append(f"vme_pe{pe}(vme_fu(SECONDARY), vme_mux(NONE, STAGING_{pe}), fu_code(OP_CLP));")
      lines.append(f"vme_pe{pe}(fu_reg(SECONDARY, A), {to_c(('num', high))});")
      lines.append(f"vme_pe{pe}(fu_reg(SECONDARY, B), {to_c(('num', low))});")
  elif kind == "peblock":
    for inner in statement[1]:
      emit(inner, env, lines, state)
  elif kind == "for":
    loop = ("for", statement[1], fold(statement[2], env), fold(statement[3], env), statement[4], statement[5])
    for inner in unroll(loop):
      emit(inner, env, lines, state)


def generate(text, block, warnings=None):
  kind, start, open_pos, _ = block
  if kind in ("decorator", "emulate", "kernel-block"):
    return ""
  if kind == "kernel-block-end":
    return "vmeLibDisable();"
  if kind == "buffers":
    line = text.count("\n", 0, start) + 1
    raise ValueError(f"line {line}: buffers must be inside a kernel (global buffers or local buffers)")
  header = text[start:open_pos]
  words = [(value, start + s) for _, value, s, _ in tokens(header)]
  name, options = words[1][0], []
  for word, pos in words[2:]:
    line = text.count("\n", 0, pos) + 1
    if word not in KERNEL_OPTIONS:
      raise ValueError(f"line {line}: unknown kernel option '{word}' ({', '.join(KERNEL_OPTIONS)})")
    if word in options:
      raise ValueError(f"line {line}: duplicate kernel option '{word}'")
    options.append(word)
  toks, limit = body_tokens(text, block)
  statements = parse_body(Parser(text, toks, limit))
  if "direct" not in options:
    return ""
  lines = ["vmeLibStart();"]
  env = {}
  state = {"swen": False, "secondary": set(), "set": {}, "agus": {}, "routing": {slot: [4, 4, 4, 4] for slot in ("top", "base", "write")}, "warnings": []}
  for statement in statements:
    emit(statement, env, lines, state)
  for slot, nibbles in state["routing"].items():
    lines.append(f"vme_icn({ICN_NAMES[slot]}, 0x{sum(nibble << 4 * i for i, nibble in enumerate(nibbles)):04x});")
  if state["secondary"] and not state["swen"]:
    lines.append(f"vme_icn(SWEN, fu_on(0b{swen_mask(state['secondary']):04b}));")
  lines.append("vmeLibFinish();")
  if warnings is not None:
    warnings.extend(state["warnings"])
  body = "".join(f"  {line}\n" for line in lines)
  return f"void {name}() {{\n{body}}}"
