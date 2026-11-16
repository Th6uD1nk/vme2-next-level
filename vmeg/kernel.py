import re

from vmeg.blocks import body_tokens, decorator_names, kernel_mode, kernel_name
from vmeg.host import block_owners
from vmeg.macros import known_macros
from vmeg.expr import fold, substitute, to_c
from vmeg.expr import value as full_value
from vmeg.operations import FAT_FALLBACKS, FUNCTIONS, OPCODE_KINDS, OPERATIONS, OPERATORS, PATTERN_OPERATORS, ROOT_OPERATORS
from vmeg.selector import OPERATION_NODES, choose_opcode
from vmeg.parser import AGU_PARAMS, ICN_NAMES, Parser, buffer_ref, declare_statements, declared_statements, parse_body
from vmeg.scanner import tokens
from vmeg.transfers import TRANSFER_KINDS
from vmeg.vmecalls import DISABLE, wait_marker

AUTO = "@auto@"

KERNEL_OPTIONS = ("direct", "memory", "extended")

ROUTING_NAMES = {"top": "AGU_TOP", "base": "AGU_BASE", "write": "AGU_WRITE"}


def phys_ref(name):
  head, number = name.rsplit("_", 1)
  return f"{head}_{int(number) & 3}" if head in ("TOP", "BASE") else name


def add_offset(base, offset):
  if offset is None:
    return ("num", base)
  return ("num", base + offset[1]) if offset[0] == "num" else ("bin", "+", ("num", base), offset)


def target_pe(target, env, limit=3):
  index = fold(target[1], env)
  if index[0] != "num":
    raise ValueError("processing element index must be a number")
  pe = index[1]
  if not 0 <= pe <= limit:
    raise ValueError(f"pe{pe}: processing element out of range (pe0 to pe{limit})")
  return pe


def target_spad(dest, env):
  if dest is None:
    return None
  index = fold(dest, env)
  if index[0] != "num":
    raise ValueError("spad destination index must be a number")
  if not 0 <= index[1] <= 3:
    raise ValueError(f"spad[{index[1]}]: buffer out of range (spad[0] to spad[3])")
  return index[1]


def constant(expr, what):
  if expr[0] != "num":
    raise ValueError(f"{what} must be a number")
  return expr[1]


def resolve_staging_value(key, value):
  if value is None:
    raise ValueError(f"the Staging variable '{key}' is read before it is set")
  if isinstance(value, tuple):
    if value[0] == "cross_back":
      raise ValueError(f"the Staging variable '{key}' is set in pe{value[1]} and cannot be read in pe{value[2]} (different pass)")
    if value[0] == "cross_forward":
      value[1]["exported"] = True
      return f"BASE_{value[1]['pe'] & 3}"
  return value


def source_ref(expr, stagings, limit=3):
  if expr[0] == "name":
    if expr[1] in stagings:
      return resolve_staging_value(expr[1], stagings[expr[1]])
    if f"{expr[1]}[0]" in stagings:
      raise ValueError(f"'{expr[1]}' is an array, write {expr[1]}[...]")
  if expr[0] == "index" and expr[1] not in ("top", "base"):
    if expr[1] in stagings:
      raise ValueError(f"'{expr[1]}' is not an array")
    if f"{expr[1]}[0]" in stagings:
      if expr[2][0] != "num":
        raise ValueError(f"{expr[1]}[...]: index must be a number")
      key = f"{expr[1]}[{expr[2][1]}]"
      if key not in stagings:
        size = sum(1 for name in stagings if name.startswith(expr[1] + "["))
        raise ValueError(f"{key}: index out of range (0 to {size - 1})")
      return resolve_staging_value(key, stagings[key])
  return buffer_ref(expr, limit)


def operand(expr, stagings, limit=3):
  ref = source_ref(expr, stagings, limit)
  if ref is None:
    raise ValueError(f"an operand must be a buffer (top0 to top{limit}, base0 to base{limit}) or a Staging variable")
  return ref


def split_source(expr, stagings, compat, limit=3):
  ref = source_ref(expr, stagings, limit)
  if ref is not None:
    return ref, []
  return None, flatten(expr, stagings, compat, limit)


def operations_of(expr, stagings, compat, limit=3):
  source, operations = split_source(expr, stagings, compat, limit)
  if source is not None:
    return [{"kind": "pass", "source": source, "numbers": {}, "sat": None}]
  return operations


def check_arguments(name, args):
  names = [argument for argument, _ in OPERATIONS[FUNCTIONS[name]]["arguments"]]
  if len(args) != len(names):
    raise ValueError(f"{name} takes {len(names)} argument{'' if len(names) == 1 else 's'} ({', '.join(names)})")


def table_operands(label, specification, args, stagings, compat, limit=3):
  given = [(kind, expr) for (_, kind), expr in zip(specification["arguments"], args) if kind != "number"]
  if not given:
    return {"source": None}, []
  if len(specification["operands"]) == 2:
    return {slot: operand(expr, stagings, limit) for slot, (_, expr) in zip(specification["operands"], given)}, []
  source, operations = split_source(given[0][1], stagings, compat, limit)
  if operations and given[0][0] == "operand":
    raise ValueError(f"{label} takes a buffer or a Staging variable")
  return {"source": source}, operations


def table_operation(kind, label, args, stagings, compat, limit=3):
  specification = OPERATIONS[kind]
  numbers = {}
  for (argument, argument_kind), expr_argument in zip(specification["arguments"], args):
    if argument_kind == "number":
      numbers[argument] = constant(expr_argument, f"{label} {argument}")
  operands, operations = table_operands(label, specification, args, stagings, compat, limit)
  operation = {"kind": kind, **operands, "numbers": numbers, "sat": None}
  if "shift" in specification:
    if not 0 <= numbers[specification["shift"]] <= 63:
      raise ValueError("the shift must be 0 to 63")
    operation["shift"] = numbers[specification["shift"]]
  return operations + [operation]


def flatten(expr, stagings, compat, limit=3):
  kind = expr[0]
  if kind == "call":
    name, args = expr[1], expr[2]
    if name == "sat":
      if len(args) != 2:
        raise ValueError("sat takes 2 arguments (value, bits)")
      bits = constant(args[1], "sat bits")
      if not 0 <= bits <= 31:
        raise ValueError("sat bits out of range (0 to 31)")
      operations = operations_of(args[0], stagings, compat, limit)
      if operations[-1]["sat"] is not None:
        raise ValueError("an operation takes only one sat")
      if operations[-1].get("shift") is not None:
        raise ValueError("the shift goes after the sat: sat(x, n) >> k")
      operations[-1]["sat"] = bits
      return operations
    if name == "round":
      if len(args) != 1:
        raise ValueError("round takes 1 argument (value)")
      operations = operations_of(args[0], stagings, compat, limit)
      if operations[-1].get("round"):
        raise ValueError("an operation takes only one round")
      operations[-1]["round"] = True
      return operations
    if name in FUNCTIONS:
      check_arguments(name, args)
      return table_operation(FUNCTIONS[name], name, args, stagings, compat, limit)
    raise ValueError(f"unknown operation '{name}' ({', '.join(['sat', 'round', *FUNCTIONS])})")
  if kind == "not":
    found = choose_opcode(expr, compat)
    if found is None:
      return table_operation("not", "not", [expr[1]], stagings, compat, limit)
    kind, bound, _ = found
    return table_operation(kind, kind, [bound[name] for name, _ in OPERATIONS[kind]["arguments"]], stagings, compat, limit)
  if kind == "bin":
    if expr[1] in (">>", "<<", ">>>", "<<<") and expr[2][0] not in OPERATION_NODES:
      found = choose_opcode(expr, compat)
      if found is not None:
        kind, bound, _ = found
        return table_operation(kind, kind, [bound[name] for name, _ in OPERATIONS[kind]["arguments"]], stagings, compat, limit)
    if expr[1] in (">>", "<<"):
      if expr[2][0] == "num" and expr[3][0] != "num":
        raise ValueError("no opcode covers this expression: a number shifted by a buffer must be from -0x800000 to 0xffffff")
      operations = operations_of(expr[2], stagings, compat, limit)
      amount = constant(expr[3], "the shift")
      if not 0 <= amount <= 63:
        raise ValueError("the shift must be 0 to 63")
      if operations[-1].get("shift") is not None:
        raise ValueError("an operation takes only one shift")
      operations[-1]["shift"] = amount if expr[1] == ">>" else (64 - amount) % 64
      return operations
    if expr[1] not in OPERATORS:
      raise ValueError(f"unsupported operator '{expr[1]}' ({', '.join([*OPERATORS, '>>', '<<'])})")
    found = choose_opcode(expr, compat)
    if found is None:
      raise ValueError("no opcode covers this expression")
    kind, bound, _ = found
    return table_operation(kind, kind, [bound[name] for name, _ in OPERATIONS[kind]["arguments"]], stagings, compat, limit)
  if kind == "cond":
    found = choose_opcode(expr, compat)
    if found is None:
      raise ValueError("no opcode covers this expression")
    kind, bound, _ = found
    return table_operation(kind, kind, [bound[name] for name, _ in OPERATIONS[kind]["arguments"]], stagings, compat, limit)
  if kind == "num":
    return table_operation("cst", "cst", [expr], stagings, compat, limit)
  if source_ref(expr, stagings, limit) is not None:
    return operations_of(expr, stagings, compat, limit)
  raise ValueError("an operation is expected (an addition, sat or clamp)")


def unroll(loop):
  if len(loop) == 6:
    _, var, low, high, body, _ = loop
    step = ("num", 1)
  else:
    _, var, low, high, step, body, _ = loop
  if low[0] != "num" or high[0] != "num" or step[0] != "num":
    raise ValueError(f"for {var}: bounds and step must be numbers")
  if step[1] < 1:
    raise ValueError(f"for {var}: step must be a positive number of 1 or more")
  values = range(low[1], high[1] + 1, step[1]) if low[1] <= high[1] else range(low[1], high[1] - 1, -step[1])
  out = []
  for value in values:
    env = {var: ("num", value)}
    for statement in body:
      statement = substitute(statement, env)
      if statement[0] == "int":
        if isinstance(statement[1], tuple):
          if statement[2] is not None:
            for i, item in enumerate(statement[2][1]):
              env[f"{statement[1][0]}[{i}]"] = item
        else:
          env[statement[1]] = statement[2]
      elif statement[0] == "elemset":
        if statement[2][0] == "num":
          env[f"{statement[1]}[{statement[2][1]}]"] = statement[3]
        out.append(statement)
      elif statement[0] == "for":
        out.extend(unroll(statement))
      elif statement[0] == "peblock":
        out.extend(statement[1])
      else:
        out.append(statement)
  return out


def check_inner(pe, agu, key, value, env):
  if value[0] != "params":
    raise ValueError(f"pe{pe}.{agu}: '{key}' takes parameters between braces: {key}: {{ count: 15, step: 1 }}")
  inner = {}
  for name, inner_value in value[1]:
    if name not in ("count", "step"):
      raise ValueError(f"pe{pe}.{agu}.{key}: unknown parameter '{name}' (count, step)")
    if name in inner:
      raise ValueError(f"pe{pe}.{agu}.{key}: duplicate parameter '{name}'")
    if inner_value[0] == "params":
      raise ValueError(f"pe{pe}.{agu}.{key}: '{name}' takes a value, not parameters between braces")
    folded = full_value(inner_value, env)
    inner[name] = f"({to_c(folded)})" if folded[0] == "name" else to_c(folded)
  for name in ("count", "step"):
    if name not in inner:
      raise ValueError(f"pe{pe}.{agu}.{key}: '{name}' is required")
  return inner


def has_auto(expr):
  if expr[0] == "name":
    return expr[1] == "auto"
  return any(has_auto(part) for part in expr[1:] if isinstance(part, tuple))


def format_agu_offset(folded, pe, agu):
  if folded[0] == "num":
    if not -32768 <= folded[1] <= 32767:
      raise ValueError(f"pe{pe}.{agu}: the offset {folded[1]} is outside -32768 to 32767")
    return to_c(("num", folded[1] & 0xffff))
  text = to_c(folded)
  return f"{text if folded[0] != 'name' else '(' + text + ')'} & 0xffff"


def generate_agu(target, params, env, pass_state, at, line, mode=4):
  pe = target_pe(target, env)
  label = pass_state["pe_offset"] + pe
  agu = target[2]
  values = {}
  raw_offset = None
  for key, value in params[1]:
    if key == "mode":
      raise ValueError(f"pe{label}.{agu}: the mode of an Agu is its type, write Agu(4) or Agu(2)")
    if key not in AGU_PARAMS[mode][agu]:
      raise ValueError(f"pe{label}.{agu}: unknown parameter '{key}' ({', '.join(AGU_PARAMS[mode][agu])})")
    if key in values:
      raise ValueError(f"pe{label}.{agu}: duplicate parameter '{key}'")
    if key == "inner0":
      values[key] = check_inner(label, agu, key, value, env)
      continue
    if value[0] == "params":
      raise ValueError(f"pe{label}.{agu}: '{key}' takes a value, not parameters between braces")
    if has_auto(value):
      if key != "cyc":
        raise ValueError(f"pe{label}.{agu}: auto is only for cyc")
      values[key] = AUTO
      pass_state["autos"].append({"pe": pe, "expr": value, "env": env, "at": at, "line": line})
      continue
    folded = full_value(value, env)
    if key in ("reverse", "repeat", "sync"):
      if folded[0] != "num" or folded[1] not in (0, 1):
        raise ValueError(f"pe{label}.{agu}: {key} takes true or false")
      values[key] = folded[1]
      continue
    if key == "bubbles" and folded[0] == "num" and not 0 <= folded[1] <= 4095:
      raise ValueError(f"pe{label}.{agu}: the bubbles {folded[1]} are outside 0 to 4095")
    if key == "bubbles":
      values[key] = to_c(folded) if folded[0] == "num" else f"{to_c(folded) if folded[0] != 'name' else '(' + to_c(folded) + ')'} & 0xfff"
      continue
    if key == "offset":
      values[key] = format_agu_offset(folded, label, agu)
      raw_offset = folded
    else:
      values[key] = to_c(folded)
  if "count" not in values:
    raise ValueError(f"pe{label}.{agu}: 'count' is required")
  two = mode == 2
  mode_arg = "agu_mode(2)" if two else "VME_DEF_MODE"
  cyc_part = f", vme_cyc({values['cyc']})" if "cyc" in values else ""
  pass_state["agu_modes"][(pe, agu)] = {"at": at, "mode_arg": mode_arg, "offset": raw_offset, "cyc": cyc_part, "line": line}
  pass_state["agu_specs"][(pe, agu)] = (params, mode, dict(env))
  if agu == "write":
    pass_state["write_modes"][pe] = pass_state["agu_modes"][(pe, agu)]
  mode = mode_arg
  if "offset" in values:
    mode += f", {values['offset']}"
  mode += cyc_part
  step = f"agu_step({values['step']})" if "step" in values else "VME_DEF_STEP"
  lines = [
    f"vme_pe{pe}(agu_{agu}(MODE), {mode});",
    f"vme_pe{pe}(agu_{agu}(COUNT), {step}, {values['count']});",
  ]
  if "inner0" in values:
    inner = values["inner0"]
    lines.append(f"vme_pe{pe}(agu_{agu}(INNER_0), agu_step({inner['step']}), {inner['count']});" if two else f"vme_pe{pe}(agu_{agu}(INNER_0), {inner['count']} << 16, {inner['step']});")
  format0 = []
  if values.get("bubbles", "0") != "0":
    format0.append(values["bubbles"])
  if values.get("reverse"):
    format0.append("0x10000000")
  if values.get("repeat"):
    format0.append("VME_RING_TOKEN")
  if format0:
    lines.append(f"vme_pe{pe}(agu_{agu}(FORMAT_0), {', '.join(format0)});")
  if values.get("sync"):
    lines.append(f"vme_pe{pe}(agu_{agu}(FORMAT_1), VME_END_TOKEN);")
  return lines


def swen_mask(pes):
  return sum(1 << (3 - pe) for pe in pes)


def offset_text(offset):
  return "" if offset == ("num", 0) else to_c(offset)


def transfer_registers(transfer, memory=None, names=None):
  return transfer["kind"].registers(transfer, memory or transfer["memory"], lambda value: replace_names(value, names or {}))


def transfer_texts(transfer):
  return transfer["kind"].texts(transfer)


NAME_IN_TEXT = re.compile(r"(?<![\w.])(?<!->)[A-Za-z_]\w*")


def transfer_names(transfer):
  names = []
  for text in transfer_texts(transfer):
    for name in NAME_IN_TEXT.findall(text):
      if name not in names:
        names.append(name)
  return names


def parameter_names(names, taken=("memory", "spadOffset")):
  used = set(taken)
  found = {}
  for name in names:
    words = [word for word in name.lower().split("_") if word] if "_" in name or name.isupper() else [name]
    base = camel(*words) if words else name
    candidate = base
    number = 2
    while candidate in used:
      candidate = f"{base}{number}"
      number += 1
    used.add(candidate)
    found[name] = candidate
  return found


def replace_names(text, names):
  return NAME_IN_TEXT.sub(lambda found: names.get(found.group(), found.group()), text) if isinstance(text, str) else text


def transfer_control(transfer, direction):
  return transfer["kind"].control(direction)


def transfer_destination(buffer, slot, offset):
  name = f"VME_{buffer.upper()}_BUFF{slot & 3}_WOFF"
  effective = add_offset(0x400, offset) if slot > 3 else offset
  if effective[0] == "num" and effective[1] < 0:
    return f"{name} - {to_c(('num', -effective[1]))}"
  return name + (f" + {offset_text(effective)}" if offset_text(effective) else "")


def transfer_destinations(targets):
  return [
    "0" if buffer is None else transfer_destination(buffer, slot, offset)
    for buffer, slot, offset in targets or [(None, 0, ("num", 0))]
  ]


def transfer_lines(transfer, targets, direction):
  lines = transfer_registers(transfer)
  control = transfer_control(transfer, direction)
  for destination in transfer_destinations(targets):
    lines += [f"vme_dma(SPAD, OFFSET, {destination});", f"vme_dma(CTRL, VALUE, {control});", "meCoreDMACPrimWaitTransferFinish();"]
  return lines


def camel(*words):
  clean = [word.replace("[", "").replace("]", "") for word in words]
  return clean[0] + "".join(word[:1].upper() + word[1:] for word in clean[1:])


def transfer_function(name, transfer, direction):
  names = parameter_names(transfer_names(transfer))
  body = transfer_registers(transfer, "memory", names) + ["vme_dma(SPAD, OFFSET, spadOffset);", f"vme_dma(CTRL, VALUE, {transfer_control(transfer, direction)});"]
  parameters = "".join(f", u32 {parameter}" for parameter in names.values())
  return f"static inline void {name}(volatile u32* memory, u32 spadOffset{parameters}) {{\n" + "".join(f"  {line}\n" for line in body) + "}"


def spread_declaration(statement, transfers, env, state=None):
  name, spread, type_name = statement[1], statement[2], statement[3]
  base_key = resolve_var(spread[1], env, state) if state else spread[1]
  base = transfers.get(base_key)
  if base is None:
    base_ident = base_name(spread[1])
    if state and (base_ident in state["agus"] or state["arrays"].get(base_ident, {}).get("kind") == "Agu"):
      raise ValueError(f"'{base_ident}' is an Agu variable, only a Transfer variable can be written with ...")
    if state and (base_ident in state["stagings"] or state["arrays"].get(base_ident, {}).get("kind") == "Staging"):
      raise ValueError(f"'{base_ident}' is a Staging variable, only a Transfer variable can be written with ...")
    raise ValueError(f"unknown Transfer variable '{base_ident}'")
  if base.get("set") is False or "memory" not in base:
    raise ValueError(f"the Transfer variable '{base_key}' is read before it is set")
  if base["kind"] is not TRANSFER_KINDS[type_name]:
    raise ValueError(f"Transfer {name} is a {transfer_type_name(type_name)}, its base '{base_key}' is a {transfer_type_name(base['type'])}")
  spread_normalized = ("spread", base_key, spread[2])
  check_spread(spread_normalized, base, False)
  merged = dict(apply_spread(spread_normalized, base, env)[0], type=type_name)
  merged.pop("declared", None)
  return merged


def transfer_type_name(type_name):
  return "Transfer" if type_name == "basic" else f"Transfer({type_name})"


def check_spread(spread, transfer, declared_only=True):
  _, base, fields = spread
  if declared_only and not transfer.get("declared"):
    raise ValueError(f"'{base}' is a Transfer of a kernel, only a Transfer of a @declare can be written with ...")
  kind = transfer["kind"]
  for name, value in fields:
    if name not in kind.fields:
      raise ValueError(f"Transfer {base}: unknown field '{name}' ({', '.join(kind.fields)})")
    if name in kind.nested:
      if value[0] != "spreadparams":
        raise ValueError(f"Transfer {base}: '{name}' takes a list of fields")
      allowed = [field for register in kind.nested[name] for field in register]
      for field, _ in value[1]:
        if field not in allowed:
          raise ValueError(f"Transfer {base}: unknown field '{field}' of {name} ({', '.join(allowed)})")
      if not value[2]:
        for register in kind.nested[name]:
          given = [field for field in register if any(field == item for item, _ in value[1])]
          if 0 < len(given) < len(register):
            missing = next(field for field in register if field not in given)
            raise ValueError(f"Transfer {base}: the field '{missing}' of {name} is needed, {' and '.join(register)} are one register")
    elif value[0] == "spreadparams":
      raise ValueError(f"Transfer {base}: '{name}' takes a value, not a list of fields")


def shared_transfer_name(type_name, direction):
  return f"vmeTransfer{direction.capitalize()}{'Words' if type_name == 'Words' else ''}"


def shared_transfer_function(type_name, direction):
  fields = ["transfer->count", "transfer->gap"] if type_name == "Words" else ["transfer->count"]
  lines = ["vme_dma(MEMORY, ADDR, useg_mem((u32)transfer->memory));", f"vme_dma(ITERATION, DIMS, {', '.join(fields)});"]
  if type_name == "Words":
    lines += ["vme_dma(ITERATION, STEP, transfer->step);", "vme_dma(GROUP, SIZE, transfer->groupSize);", "vme_dma(GROUP, STEPS, transfer->groupOuter, transfer->groupInner);"]
  lines += ["vme_dma(SPAD, OFFSET, spadOffset);", f"vme_dma(CTRL, VALUE, {TRANSFER_KINDS[type_name].control(direction)});"]
  return f"static inline void {shared_transfer_name(type_name, direction)}(const {TRANSFER_TYPES[type_name]}* transfer, u32 spadOffset) {{\n" + "".join(f"  {line}\n" for line in lines) + "}"


def spread_value(item, env):
  folded = full_value(item, env)
  return folded[1] if folded[0] == "num" else to_c(folded)


def apply_spread(spread, transfer, env):
  _, base, fields = spread
  kind = transfer["kind"]
  merged = dict(transfer)
  assignments = []
  for name, value in fields:
    if name in kind.nested:
      names = [field for register in kind.nested[name] for field in register]
      given = {field: spread_value(item, env) for field, item in value[1]}
      group = dict(transfer.get(name, {})) if value[2] else {}
      group.update(given)
      for field in (given if value[2] else names):
        group.setdefault(field, 0)
        assignments.append(f"{name}{field.capitalize()} = {group[field]}")
      merged[name] = group
    else:
      merged[name] = spread_value(value, env)
      assignments.append(f"{name} = {merged[name]}")
  return merged, assignments


def shared_transfer_calls(name, variable, targets, type_name=None, assignments=None):
  if not assignments:
    return [line for destination in transfer_destinations(targets) for line in (f"{name}(&{variable}, {destination});", wait_marker(name))]
  copy = "vmeCopyVar"
  lines = ["{", f"  {TRANSFER_TYPES[type_name]} {copy} = {variable};"] + [f"  {copy}.{assignment};" for assignment in assignments]
  lines += [line for destination in transfer_destinations(targets) for line in (f"  {name}(&{copy}, {destination});", f"  {wait_marker(name)}")]
  return lines + ["}"]


def transfer_calls(name, transfer, targets):
  arguments = "".join(f", {original}" for original in transfer_names(transfer))
  return [line for destination in transfer_destinations(targets) for line in (f"{name}({transfer['memory']}, {destination}{arguments});", wait_marker(name))]


def transfer_links(transfer, targets):
  words = transfer["kind"].words(transfer)
  return [("SPAD" if buffer is None else f"{buffer.upper()}_{slot}", words, offset_text(offset), transfer["memory"], transfer["kind"].extended) for buffer, slot, offset in targets or [(None, 0, ("num", 0))]]


def emit(statement, env, lines, state):
  try:
    emit_statement(statement, env, lines, state)
  except ValueError as e:
    if str(e).startswith("line "):
      raise
    raise ValueError(f"line {statement[-1]}: {e}") from None


def warn(state, line, message):
  state["warnings"].append((line, message))


def claim(pass_state, pe, name, line):
  key = (pe, name)
  if key in pass_state["set"]:
    raise ValueError(f"pe{pass_state['pe_offset'] + pe}.{name} is already set at line {pass_state['set'][key]}")
  pass_state["set"][key] = line


def base_name(target):
  return target[0] if isinstance(target, tuple) else target


def check_name_free(name, kind, state, env):
  stores = {"Agu": (state["agus"], "an Agu"), "Staging": (state["stagings"], "a Staging"), "Transfer": (state["transfers"], "a Transfer")}
  array_kind = state["arrays"].get(name, {}).get("kind")
  if kind == "Int":
    if (name in env and name not in state["macros"]) or array_kind == "Int":
      raise ValueError(f"'{name}' is defined twice")
  elif name in stores[kind][0] or array_kind == kind:
    raise ValueError(f"the {kind} variable '{name}' is declared twice")
  elif (name in env and name not in state["macros"]) or array_kind == "Int":
    raise ValueError(f"'{name}' is already declared as an Int variable")
  for other, (table, label) in stores.items():
    if other != kind and (name in table or array_kind == other):
      raise ValueError(f"'{name}' is already declared as {label} variable")


def declare_keys(target, kind, env, state):
  name = base_name(target)
  check_name_free(name, kind, state, env)
  if not isinstance(target, tuple):
    return [name]
  size = fold(target[1], env)
  if size[0] != "num" or size[1] < 1:
    raise ValueError(f"{name}[...]: array size must be a number of 1 or more")
  state["arrays"][name] = {"kind": kind, "size": size[1]}
  return [f"{name}[{i}]" for i in range(size[1])]


def resolve_var(target, env, state):
  if isinstance(target, tuple):
    name, index = target[0], fold(target[1], env)
    if index[0] != "num":
      raise ValueError(f"{name}[...]: index must be a number")
    if name in state["arrays"]:
      size = state["arrays"][name]["size"]
      if not 0 <= index[1] < size:
        raise ValueError(f"{name}[{index[1]}]: index out of range (0 to {size - 1})")
    elif name in state["stagings"] or name in state["agus"] or name in state["transfers"] or (name in env and name not in state["macros"]):
      raise ValueError(f"'{name}' is not an array")
    return f"{name}[{index[1]}]"
  if target in state["arrays"]:
    raise ValueError(f"'{target}' is an array, write {target}[...]")
  return target


def staging_refs(state, pe=0):
  refs = {}
  for name, variable in state["stagings"].items():
    if "pe" not in variable:
      refs[name] = None
    elif (variable["pe"] >> 2) > (pe >> 2):
      refs[name] = ("cross_back", variable["pe"], pe)
    elif (variable["pe"] >> 2) < (pe >> 2):
      refs[name] = ("cross_forward", variable, pe)
    else:
      refs[name] = f"STAGING_{(variable['pe'] & 3) + 4 * variable['unit']}"
  return refs


def staging_depths(state, pass_id=0):
  return {
    f"STAGING_{(variable['pe'] & 3) + 4 * variable['unit']}": variable["depth"]
    for variable in state["stagings"].values()
    if "pe" in variable and (variable["pe"] >> 2) == pass_id
  }


def place(state, lines, pe, operations, line, pass_state=None):
  target = pass_state or state
  used = target["fus"].get(pe, 0)
  depths = staging_depths(state, target["pe_offset"] >> 2)
  logical = target["pe_offset"] + pe
  depth = 0
  if used + len(operations) > 2:
    raise ValueError(f"a pe holds two operations at most, this pe needs {used + len(operations)}")
  for operation in operations:
    number = target["fus"].get(pe, 0)
    target["fus"][pe] = number + 1
    unit = "PRIMARY" if number == 0 else "SECONDARY"
    specification = OPERATIONS[operation["kind"]]
    state["operations"].append(dict(operation, pe=logical, line=line))
    remap = target["remaps"].get(pe, {}).get(ROOT_OPERATORS[operation["kind"]], {})
    if specification["units"] == "primary" and number != 0 and unit.lower() not in remap:
      warn(state, line, f"{operation['kind']} is the second operation of pe{logical}, it is not known to run in the second unit")
    encoding = specification
    if state.get("compat") == "fat" and operation["kind"] in FAT_FALLBACKS:
      encoding = {**specification, **FAT_FALLBACKS[operation["kind"]]}
    if unit.lower() in remap:
      chosen = remap[unit.lower()]
      encoding = OPERATIONS[chosen] if isinstance(chosen, str) else {"opcode": chosen, "code": f"fu_code(0x{chosen:03x})", "registers": specification["registers"]}
    state["operations"][-1]["opcode"] = encoding["opcode"]
    code = encoding["code"]
    operands = encoding.get("operands", specification["operands"])
    if len(operands) == 2:
      mux = f"vme_mux({phys_ref(operation['front'])}, {phys_ref(operation['back'])})"
      reads = (operation["front"], operation["back"])
    elif operands == ("front",):
      source = operation["source"] or f"STAGING_{pe}"
      mux = f"vme_mux({phys_ref(source)})"
      reads = (operation["source"],) if operation["source"] else ()
    else:
      source = operation["source"] or f"STAGING_{pe}"
      mux = f"vme_mux(NONE, {phys_ref(source)})"
      reads = (operation["source"],) if operation["source"] else ()
    target.setdefault("unit_reads", {}).setdefault((pe, number), set()).update(reads)
    for ref in reads:
      if not ref.startswith("STAGING"):
        target["reads"].setdefault(ref, line)
    depth = max([depth] + [depths.get(ref, 0) for ref in reads]) + 1
    sat = "" if operation["sat"] is None else f", fu_sat({operation['sat']})"
    if operation.get("shift"):
      sat += f", {operation['shift']}"
    if operation.get("round"):
      sat += ", (1 << 6)"
    lines.append(f"vme_pe{pe}(vme_fu({unit}), {mux}, {code}{sat});")
    registers = dict(encoding["registers"])
    if encoding is not specification:
      for register, argument in specification["registers"].items():
        if argument in operation["numbers"] and argument not in encoding["registers"].values():
          if register in registers:
            warn(state, line, f"the value of '{argument}' is not written, the register {register} of the opcode 0x{encoding['opcode']:03x} of .remap {unit.lower()} is for another value")
          else:
            registers[register] = argument
            warn(state, line, f"the opcode 0x{encoding['opcode']:03x} of .remap {unit.lower()} has no register for '{argument}', its value is written as it is in the register {register}")
    for register, argument in registers.items():
      value = operation["numbers"].get(argument, 0)
      if not -0x800000 <= value <= 0xffffff:
        warn(state, line, f"the number {hex(value)} of '{argument}' does not fit in 24 bits, it is written as it is in the register {register}")
      lines.append(f"vme_pe{pe}(fu_reg({unit}, {register}), {to_c(('num', operation['numbers'].get(argument, 0)))});")
  return number, depth


def next_write_seq(state):
  seq = state["write_seq"]
  state["write_seq"] += 1
  return seq


def record_write(state, pe, driver, ref, line):
  state["writes"][pe] = {"driver": driver, "ref": ref, "line": line, "seq": next_write_seq(state)}


def pe_pass(target, env, state):
  pe = target_pe(target, env, 7 if state["extended"] else 3)
  state["active_pass"] = pe >> 2
  return pe, pe & 3, pass_for(state, pe)


def emit_statement(statement, env, lines, state):
  kind = statement[0]
  if kind == "int":
    if base_name(statement[1]) == "auto":
      raise ValueError("auto is reserved for the cyc of a write AGU")
    keys = declare_keys(statement[1], "Int", env, state)
    if isinstance(statement[1], tuple):
      if statement[2] is not None:
        name = statement[1][0]
        items = statement[2][1]
        if len(items) > len(keys):
          raise ValueError(f"{name}[...]: too many initializers ({len(items)} for size {len(keys)})")
        for key, item in zip(keys, items):
          env[key] = full_value(item, env)
    else:
      env[keys[0]] = full_value(statement[2], env)
  elif kind == "elemset":
    name = statement[1]
    key = resolve_var((name, statement[2]), env, state)
    if name not in state["arrays"]:
      raise ValueError(f"unknown array '{name}'")
    array_kind = state["arrays"][name]["kind"]
    if array_kind == "Int":
      env[key] = full_value(statement[3], env)
    elif array_kind == "Agu":
      if statement[3][0] != "params":
        raise ValueError(f"'{name}' is an Agu variable, it takes parameters between braces")
      state["agus"][key]["params"] = statement[3]
    elif array_kind == "Transfer":
      if statement[3][0] not in ("params", "spread"):
        raise ValueError(f"'{name}' is a Transfer variable, it takes parameters between braces")
      type_name = state["transfers"][key]["type"]
      if statement[3][0] == "spread":
        transfer = spread_declaration(("transferdecl", key, statement[3], type_name), state["transfers"], env, state)
      else:
        transfer = dict(TRANSFER_KINDS[type_name].check(key, statement[3], env), type=type_name)
      state["transfers"][key] = transfer
    else:
      raise ValueError(f"'{name}' is a {array_kind} variable, only an Int variable can receive an assignment")
  elif kind == "regs":
    target = pass_for(state, (state["active_pass"] or 0) * 4)
    for name, value in statement[1]:
      if value[0] != "num":
        raise ValueError(f".{name} takes a number")
      limit = 0xf if name == "swen" else 0xffffffff
      if not 0 <= value[1] <= limit:
        raise ValueError(f".{name} takes a number from 0 to 0x{limit:x}")
      if name == "swen":
        target["secondary"] = {pe for pe in range(4) if value[1] >> (3 - pe) & 1}
        target["swen_raw"] = True
      else:
        target["routing"][name] = [value[1] >> 4 * n & 0xf for n in range(8)]
        target["routing_regs"].add(name)
        if name == "write":
          target["write_reg_seq"] = next_write_seq(target)
  elif kind == "icn":
    target = pass_for(state, (state["active_pass"] or 0) * 4)
    for icn, value in statement[1]:
      if icn in target["icn"]:
        raise ValueError(f"duplicate interconnect '{icn}'")
      target["icn"].add(icn)
      target["lines"].append(f"vme_icn({ICN_NAMES[icn]}, {to_c(full_value(value, env))});")
  elif kind == "agu":
    _, phys, target = pe_pass(statement[1], env, state)
    slot = statement[1][2]
    claim(target, phys, slot, statement[-1])
    if slot == "write":
      record_write(target, phys, phys, None, statement[-1])
    else:
      target["routing"][slot][phys] = phys
      target["routing_bound"][slot].add(phys)
    target["lines"].extend(generate_agu(("target", ("num", phys), slot), statement[2], env, target, len(target["lines"]), statement[-1]))
  elif kind == "agudecl":
    keys = declare_keys(statement[1], "Agu", env, state)
    if isinstance(statement[1], tuple):
      items = statement[2][1] if statement[2] is not None else []
      if len(items) > len(keys):
        name = statement[1][0]
        raise ValueError(f"{name}[...]: too many initializers ({len(items)} for size {len(keys)})")
      for i, key in enumerate(keys):
        params = items[i] if i < len(items) else None
        state["agus"][key] = {"params": params, "owners": {}, "mode": statement[3]}
    else:
      state["agus"][keys[0]] = {"params": statement[2], "owners": {}, "mode": statement[3]}
  elif kind == "stagingdecl":
    for key in declare_keys(statement[1], "Staging", env, state):
      state["stagings"][key] = {}
  elif kind in ("load", "store"):
    items = dict(statement[1])
    if "transfer" not in items:
      raise ValueError(f".{kind} needs a .transfer = name;")
    seen = set()
    targets = []
    limit = 7 if state.get("extended") else 3
    for buffer, index, value in items.get("offsets", ("offsets", []))[1]:
      slot = fold(index, env)
      if slot[0] != "num" or not 0 <= slot[1] <= limit:
        raise ValueError(f"{buffer}[...]: buffer index must be a number from 0 to {limit}")
      if (buffer, slot[1]) in seen:
        raise ValueError(f"{buffer}{slot[1]} is already set in this .{kind}")
      seen.add((buffer, slot[1]))
      offset = full_value(value, env)
      targets.append((buffer, slot[1], offset))
    spread = items["transfer"] if items["transfer"][0] == "spread" else None
    ref = resolve_var(spread[1] if spread else items["transfer"][1], env, state)
    if ref not in state["transfers"]:
      base = base_name(spread[1] if spread else items["transfer"][1])
      if base in state["agus"] or state["arrays"].get(base, {}).get("kind") == "Agu":
        raise ValueError(f"'{base}' is an Agu variable, only a Transfer variable can be used in .{kind}")
      if base in state["stagings"] or state["arrays"].get(base, {}).get("kind") == "Staging":
        raise ValueError(f"'{base}' is a Staging variable, only a Transfer variable can be used in .{kind}")
      raise ValueError(f"unknown Transfer variable '{base}'")
    transfer = state["transfers"][ref]
    if transfer.get("set") is False or "memory" not in transfer:
      raise ValueError(f"the Transfer variable '{ref}' is read before it is set")
    assignments = None
    if spread is not None:
      spread = ("spread", ref, spread[2])
      check_spread(spread, transfer)
      transfer, assignments = apply_spread(spread, transfer, env)
    transfer["kind"].ensure_generated(kind)
    shared = transfer.get("declared")
    function = shared_transfer_name(transfer["type"], kind) if shared else camel(state["owner"], ref, kind.capitalize()) if state["owner"] else None
    definition = shared_transfer_function(transfer["type"], kind) if shared else transfer_function(function, transfer, kind) if function else None
    calls = shared_transfer_calls(function, shared, targets, transfer["type"], assignments) if shared else transfer_calls(function, transfer, targets) if function else None
    record = {"function": function, "definition": definition, "calls": calls, "kind": kind, "scope": items.get("scope", ("name", "local"))[1], "memory": transfer["memory"], "line": statement[-1], "lines": transfer_lines(transfer, targets, kind), "links": transfer_links(transfer, targets)}
    state[kind + "s"].append(record)
    state["sequence"].append(record)
  elif kind in ("transferdecl", "declaredtransfer"):
    keys = declare_keys(statement[1], "Transfer", env, state)
    type_name = statement[3]
    if isinstance(statement[1], tuple):
      items = statement[2][1] if statement[2] is not None else []
      if len(items) > len(keys):
        name = statement[1][0]
        raise ValueError(f"{name}[...]: too many initializers ({len(items)} for size {len(keys)})")
      for i, key in enumerate(keys):
        if i < len(items):
          item = items[i]
          if item[0] == "spread":
            transfer = spread_declaration(("transferdecl", key, item, type_name), state["transfers"], env, state)
          else:
            transfer = dict(TRANSFER_KINDS[type_name].check(key, item, env), type=type_name)
        else:
          transfer = {"type": type_name, "kind": TRANSFER_KINDS[type_name], "set": False}
        state["transfers"][key] = transfer
        if kind == "declaredtransfer":
          state["transfers"][key]["declared"] = transfer_variable(key)
    else:
      key = keys[0]
      if statement[2][0] == "spread":
        transfer = spread_declaration(statement, state["transfers"], env, state)
      else:
        transfer = dict(TRANSFER_KINDS[type_name].check(key, statement[2], env), type=type_name)
      state["transfers"][key] = transfer
      if kind == "declaredtransfer":
        state["transfers"][key]["declared"] = transfer_variable(key)
  elif kind == "aguref":
    ref = resolve_var(statement[2][1], env, state)
    variable = state["agus"].get(ref)
    if variable is None:
      raise ValueError(f"unknown Agu variable '{base_name(statement[2][1])}'")
    if variable["params"] is None:
      raise ValueError(f"the Agu variable '{ref}' is read before it is set")
    pe, phys, target = pe_pass(statement[1], env, state)
    slot = statement[1][2]
    for _, bound in variable["owners"]:
      if bound != slot:
        raise ValueError(f"the Agu variable '{ref}' is already bound to .{bound}, it cannot be bound to .{slot}")
    claim(target, phys, slot, statement[-1])
    owner = (pe >> 2, slot)
    if owner not in variable["owners"]:
      variable["owners"][owner] = phys
      target["lines"].extend(generate_agu(("target", ("num", phys), slot), variable["params"], env, target, len(target["lines"]), statement[-1], variable["mode"]))
    if any(key == "cyc" and has_auto(value) for key, value in variable["params"][1]):
      target["sharers"].setdefault(ref, []).append((phys, statement[-1]))
    if slot == "write":
      record_write(target, phys, variable["owners"][owner], ref, statement[-1])
    else:
      target["routing"][slot][phys] = variable["owners"][owner]
      target["routing_bound"][slot].add(phys)
  elif kind == "operation":
    pe, phys, target = pe_pass(statement[1], env, state)
    dest = target_spad(statement[1][3] if len(statement[1]) > 3 else None, env)
    if (phys, "operation") in target["set"]:
      raise ValueError(f"pe{pe} has two outputs on the same write, the first one is at line {target['set'][(phys, 'operation')]}")
    claim(target, phys, "operation", statement[-1])
    last, depth = place(state, target["lines"], phys, flatten(fold(statement[2], env), staging_refs(state, pe), state["compat"], 7 if state["extended"] else 3), statement[-1], target)
    target["outputs"].setdefault(phys, statement[-1])
    target["depths"][phys] = depth
    target["write_targets"][phys] = {"dest": dest, "line": statement[-1], "seq": next_write_seq(target)}
    if last == 1:
      target["secondary"].add(phys)
    else:
      target["secondary"].discard(phys)
  elif kind == "paramsdef":
    if state["params"] is not None:
      raise ValueError("the parameters of the kernel are declared twice")
    state["params"] = statement[1]
  elif kind == "remap":
    pe, phys, pass_state = pe_pass(statement[1], env, state)
    operator = statement[2]
    if not any(operator in operators for operators in PATTERN_OPERATORS.values()):
      raise ValueError(f"unknown operator '{operator}' in .remap")
    remaps = pass_state["remaps"].setdefault(phys, {})
    if operator in remaps:
      raise ValueError(f"the operator '{operator}' is remapped twice in pe{pe}")
    units = {}
    for unit, value in (("primary", statement[3]), ("secondary", statement[4])):
      if value is None:
        continue
      number = fold(value, env)
      if number[0] != "num":
        raise ValueError(f".remap {unit} takes a number")
      target = OPCODE_KINDS.get(number[1])
      if target is None:
        if not 0 <= number[1] <= 0xfff:
          raise ValueError(f".remap {unit} takes an opcode from 0x000 to 0xfff")
        warn(state, statement[-1], f"the opcode 0x{number[1]:03x} of .remap {unit} is not in the table (vmegc --ops), it is written as it is with the registers of the operation it replaces")
        units[unit] = number[1]
        continue
      if operator not in PATTERN_OPERATORS[target]:
        warn(state, statement[-1], f"the operator '{operator}' is not in the pattern of the opcode 0x{number[1]:03x} of .remap {unit}, it is written as it is")
      units[unit] = target
    remaps[operator] = units
  elif kind == "stageset":
    name = resolve_var(statement[2], env, state)
    variable = state["stagings"].get(name)
    if variable is None:
      base = base_name(statement[2])
      if name in state["agus"] or state["arrays"].get(base, {}).get("kind") == "Agu":
        raise ValueError(f"'{base}' is an Agu variable, only a Staging variable can receive an operation")
      if name in state["transfers"] or state["arrays"].get(base, {}).get("kind") == "Transfer":
        raise ValueError(f"'{base}' is a Transfer variable, only a Staging variable can receive an operation")
      raise ValueError(f"unknown Staging variable '{base}'")
    if "pe" in variable:
      raise ValueError(f"the Staging variable '{name}' is already set at line {variable['line']}")
    pe, phys, target = pe_pass(statement[1], env, state)
    last, depth = place(state, target["lines"], phys, flatten(fold(statement[3], env), staging_refs(state, pe), state["compat"], 7 if state["extended"] else 3), statement[-1], target)
    variable.update({"pe": pe, "unit": last, "line": statement[-1], "depth": depth})
  elif kind == "peblock":
    for inner in sorted(statement[1], key=lambda item: item[0] != "remap"):
      emit(inner, env, lines, state)
  elif kind == "for":
    if len(statement) == 6:
      loop = ("for", statement[1], fold(statement[2], env), fold(statement[3], env), ("num", 1), statement[4], statement[5])
    else:
      loop = ("for", statement[1], fold(statement[2], env), fold(statement[3], env), fold(statement[4], env), statement[5], statement[6])
    for inner in unroll(loop):
      emit(inner, env, lines, state)


def new_pass_state(pe_offset=0, halves=(0, 1)):
  return {
    "pe_offset": pe_offset,
    "halves": halves,
    "lines": [],
    "secondary": set(),
    "set": {},
    "fus": {},
    "routing": {slot: [4] * 8 for slot in ("top", "base", "write")},
    "routing_bound": {slot: set() for slot in ("top", "base", "write")},
    "routing_regs": set(),
    "reads": {},
    "outputs": {},
    "depths": {},
    "autos": [],
    "icn": set(),
    "swen_raw": False,
    "sharers": {},
    "remaps": {},
    "writes": {},
    "write_targets": {},
    "write_modes": {},
    "agu_modes": {},
    "agu_specs": {},
    "write_seq": 0,
    "write_reg_seq": -1,
    "bank_halves": None,
  }


def pass_for(state, pe=0):
  return state["passes"][pe >> 2]


def new_state(macros=None, owner=None, compat=None, extended=False):
  passes = [new_pass_state(0, (0,)), new_pass_state(4, (1,))] if extended else [new_pass_state(0)]
  state = {"owner": owner, "extended": extended, "macros": set(macros or ()), "agus": {}, "stagings": {}, "transfers": {}, "arrays": {}, "loads": [], "stores": [], "sequence": [], "warnings": [], "compat": compat, "operations": [], "params": None, "passes": passes, "active_pass": None}
  state.update(passes[0])
  return state


def new_env(macros=None):
  env = {"true": ("num", 1), "false": ("num", 0)}
  for name, number in (macros or {}).items():
    env.setdefault(name, ("num", number))
  return env


def check_shared_auto(pass_state, root=None):
  offset = pass_state["pe_offset"]
  for name, sharers in pass_state["sharers"].items():
    owner = sharers[0][0]
    for pe, line in sharers[1:]:
      if pe in pass_state["depths"] and pass_state["depths"][pe] != pass_state["depths"][owner]:
        warn(root or pass_state, line, f"pe{offset + pe} shares the write Agu '{name}' with pe{offset + owner} but its operations need another delay, cyc: auto follows pe{offset + owner}")


def resolve_write_routing(state):
  ref_pes = {}
  for pe, write in state["writes"].items():
    if write["ref"] is not None:
      ref_pes.setdefault(write["ref"], []).append(pe)
  for ref, pes in ref_pes.items():
    if len(pes) > 1:
      for pe in pes:
        target = state["write_targets"].get(pe)
        if target is not None and target["dest"] is not None:
          raise ValueError(f"line {target['line']}: pe{pe} cannot share the write Agu '{ref}' with .spad[{target['dest']}]")
  owners = {}
  claimed = sorted(
    set(state["writes"]) | set(state["write_targets"]),
    key=lambda pe: (state["write_targets"][pe]["seq"] if pe in state["write_targets"] else state["writes"][pe]["seq"], pe),
  )
  for pe in claimed:
    write = state["writes"].get(pe)
    target = state["write_targets"].get(pe)
    dest = target["dest"] if target is not None else None
    buf = pe if dest is None else dest
    line = target["line"] if target is not None else write["line"]
    if buf in owners:
      raise ValueError(f"line {line}: base{buf} is written by both pe{owners[buf]} and pe{pe}")
    owners[buf] = pe
  for pe, write in state["writes"].items():
    target = state["write_targets"].get(pe)
    last_seq = max(write["seq"], target["seq"] if target is not None else -1)
    if last_seq < state["write_reg_seq"]:
      continue
    dest = target["dest"] if target is not None else None
    buf = pe if dest is None else dest
    state["routing"]["write"][buf] = write["driver"] if dest is None else (8 | write["driver"])
    state["routing_bound"]["write"].add(buf)


def resolve_idle_routing(state, bank_halves=None):
  halves = state.get("halves", (0, 1))
  per_bank = state.get("bank_halves") if bank_halves is None else bank_halves
  for slot, nibbles in state["routing"].items():
    bound = state["routing_bound"][slot]
    if slot in state["routing_regs"] or not bound:
      continue
    extended = any(nibbles[buf] & 8 for buf in bound)
    if len(bound) < 4:
      drivers = {nibbles[buf] & 3 for buf in bound}
      idle = (12 if extended else 4) | min(set(range(4)) - drivers)
      for buf in range(4):
        if buf not in bound:
          nibbles[buf] = idle
    nibbles[4] = (nibbles[0] & 3) if extended else nibbles[0]
    nibbles[5:8] = nibbles[1:4]
    if halves != (0, 1) or per_bank:
      for buf in range(4):
        base = nibbles[buf]
        if buf not in bound:
          nibbles[4 + buf] = base
          continue
        active = (per_bank or {}).get((slot, buf), halves)
        nibbles[buf] = (base & 0xb) if 0 in active else (base | 4)
        nibbles[4 + buf] = (base & 0xb) if 1 in active else (base | 4)


def rewrite_agu_offset(lines, pe, label, slot, info, base):
  try:
    offset_text = format_agu_offset(add_offset(base, info["offset"]), label, slot)
  except ValueError as e:
    raise ValueError(f"line {info['line']}: {e}") from None
  lines[info["at"]] = f"vme_pe{pe}(agu_{slot}(MODE), {info['mode_arg']}, {offset_text}{info['cyc']});"


def resolve_write_offsets(lines, state):
  for pe, info in state["write_modes"].items():
    target = state["write_targets"].get(pe)
    if target is not None and target["dest"]:
      rewrite_agu_offset(lines, pe, pe, "write", info, target["dest"] * 2048)


def resolve_extended_offsets(pass_state):
  if not pass_state["pe_offset"]:
    return
  lines = pass_state["lines"]
  reads = pass_state["reads"]
  for (pe, slot), info in pass_state["agu_modes"].items():
    label = pass_state["pe_offset"] + pe
    if slot == "write":
      rewrite_agu_offset(lines, pe, label, slot, info, 0x400)
      continue
    nibbles = pass_state["routing"][slot]
    driven = [buf for buf in pass_state["routing_bound"][slot] if (nibbles[buf] & 3) == pe] or [pe]
    low = [buf for buf in driven if f"{slot.upper()}_{buf}" in reads]
    high = [buf for buf in driven if f"{slot.upper()}_{buf + 4}" in reads]
    if low and high:
      raise ValueError(f"line {info['line']}: pe{label}.{slot} cannot read both {slot}{low[0]} and {slot}{high[0] + 4}")
    if low:
      if pass_state["bank_halves"] is None:
        pass_state["bank_halves"] = {}
      for buf in driven:
        pass_state["bank_halves"][(slot, buf)] = (0,)
    else:
      rewrite_agu_offset(lines, pe, label, slot, info, 0x400)


def input_agu_count(pass_state, pe, unit, name, line):
  counts = []
  seen = set()
  stack = [(pe, unit)]
  unit_reads = pass_state.get("unit_reads", {})
  while stack:
    cur_pe, cur_unit = stack.pop()
    if (cur_pe, cur_unit) in seen:
      continue
    seen.add((cur_pe, cur_unit))
    reads = unit_reads.get((cur_pe, cur_unit), set())
    if not reads and cur_unit == 1:
      stack.append((cur_pe, 0))
    for ref in reads:
      if ref.startswith("STAGING_"):
        idx = int(ref.split("_")[1])
        stack.append((idx & 3, idx >> 2))
        continue
      slot, num = ref.lower().split("_")
      buf = int(num)
      if buf not in pass_state["routing_bound"][slot]:
        continue
      driver = pass_state["routing"][slot][buf] & 3
      spec = pass_state["agu_specs"].get((driver, slot))
      if spec is not None:
        params, _, agu_env = spec
        count = next(value for key, value in params[1] if key == "count")
        counts.append(full_value(count, agu_env))
  if not counts:
    raise ValueError(f"line {line}: Staging '{name}' has no input AGU to infer write count from")
  if all(item[0] == "num" for item in counts):
    return ("num", max(item[1] for item in counts))
  unique = {repr(item): item for item in counts}
  if len(unique) == 1:
    return counts[0]
  raise ValueError(f"line {line}: Staging '{name}' combines non-constant counts, set pe{pe}.write explicitly")


def resolve_cross_stagings(state):
  if not state["extended"]:
    return
  pass1, pass2 = state["passes"]
  exported = {}
  for name, variable in state["stagings"].items():
    if not variable.get("exported"):
      continue
    pe = variable["pe"] & 3
    if pe in exported:
      raise ValueError(f"line {variable['line']}: pe{pe} can only export one Staging across passes ('{exported[pe][0]}' is already exported)")
    exported[pe] = (name, variable)
  for pe, (name, variable) in exported.items():
    line = variable["line"]
    need_write = pe not in pass1["writes"]
    need_base = pe not in pass2["routing_bound"]["base"]
    count = input_agu_count(pass1, pe, variable["unit"], name, line) if (need_write or need_base) else None
    if pe not in pass1["outputs"] and not pass1["swen_raw"]:
      if variable["unit"] == 1:
        pass1["secondary"].add(pe)
      else:
        pass1["secondary"].discard(pe)
    if need_write:
      claim(pass1, pe, "write", line)
      record_write(pass1, pe, pe, None, line)
      params = ("params", [("count", count), ("cyc", ("num", 3 + 3 * variable["depth"]))])
      pass1["lines"].extend(generate_agu(("target", ("num", pe), "write"), params, {}, pass1, len(pass1["lines"]), line))
    else:
      pass1["depths"].setdefault(pe, variable["depth"])
    if need_base:
      claim(pass2, pe, "base", line)
      pass2["routing"]["base"][pe] = pe
      pass2["routing_bound"]["base"].add(pe)
      pass2["lines"].extend(generate_agu(("target", ("num", pe), "base"), ("params", [("count", count)]), {}, pass2, len(pass2["lines"]), line))
      if pass2["bank_halves"] is None:
        pass2["bank_halves"] = {}
      pass2["bank_halves"][("base", pe)] = (0,)


def resolve_auto(lines, pass_state, root=None):
  for pending in pass_state["autos"]:
    pe = pending["pe"]
    label = pass_state["pe_offset"] + pe
    if pe not in pass_state["depths"]:
      raise ValueError(f"line {pending['line']}: pe{label}.write: cyc auto needs an operation in pe{label}")
    env = dict(pending["env"])
    env["auto"] = ("num", 3 + 3 * pass_state["depths"][pe])
    lines[pending["at"]] = lines[pending["at"]].replace(AUTO, to_c(full_value(pending["expr"], env)))
  check_shared_auto(pass_state, root)


def target_pass(statement, env, limit):
  kind = statement[0]
  try:
    if kind in ("agu", "aguref", "operation", "remap", "stageset"):
      return target_pe(statement[1], env, limit) >> 2
    if kind in ("peblock", "for"):
      inner_env = dict(env, **{statement[1]: fold(statement[2], env)}) if kind == "for" else env
      body = statement[1] if kind == "peblock" else statement[-2]
      return next((p for inner in body if (p := target_pass(inner, inner_env, limit)) is not None), None)
  except ValueError:
    return None
  return None


def pass_active(pass_state):
  return any(pass_state[k] for k in ("lines", "writes", "outputs", "reads", "secondary", "swen_raw", "routing_regs"))


def finalize_pass(state, pass_state):
  lines = pass_state["lines"]
  resolve_extended_offsets(pass_state)
  resolve_write_routing(pass_state)
  resolve_write_offsets(lines, pass_state)
  resolve_auto(lines, pass_state, state)
  for ref, line in pass_state["reads"].items():
    slot, number = ref.lower().split("_")
    if pass_state["routing"][slot][int(number) & 3] == 4:
      warn(state, line, f"{slot}{number} is read but no .{slot} is bound in pe{number} of this kernel")
  for pe, line in pass_state["outputs"].items():
    target = pass_state["write_targets"].get(pe)
    buf = target["dest"] if target is not None and target["dest"] is not None else pe
    if (pe not in pass_state["writes"] and pass_state["write_reg_seq"] < 0) or pass_state["routing"]["write"][buf] == 4:
      warn(state, line, f"pe{pass_state['pe_offset'] + pe} has an operation but no .write is bound in this kernel")
  resolve_idle_routing(pass_state)
  for slot, nibbles in pass_state["routing"].items():
    lines.append(f"vme_icn({ROUTING_NAMES[slot]}, 0x{sum(nibble << 4 * i for i, nibble in enumerate(nibbles)):08x});")
  if pass_state["secondary"] or pass_state["swen_raw"]:
    lines.append(f"vme_icn(SWEN, fu_on(0b{swen_mask(pass_state['secondary']):04b}));")
  return lines


def reg_key(line):
  depth = 0
  for i, ch in enumerate(line):
    if ch == "(":
      depth += 1
    elif ch == ")":
      depth -= 1
    elif ch == "," and depth == 1:
      return line[:i]
  return line


def register_delta(pass1, pass2):
  prev = {reg_key(line): line for line in pass1["lines"]}
  next_keys = {reg_key(line) for line in pass2["lines"]}
  out = [f"{key}, 0);" for key in prev if key.startswith("vme_pe") and key not in next_keys]
  out.extend(line for line in pass2["lines"] if prev.get(reg_key(line)) != line)
  if "vme_icn(SWEN" in prev and "vme_icn(SWEN" not in next_keys and swen_mask(pass1["secondary"]) != swen_mask(pass2["secondary"]):
    out.append(f"vme_icn(SWEN, fu_on(0b{swen_mask(pass2['secondary']):04b}));")
  return out


def run_statements(statements, macros=None, owner=None, compat=None, extended=False):
  env = new_env(macros)
  state = new_state(macros, owner, compat, extended)
  lines = state["passes"][0]["lines"]
  limit = 7 if extended else 3
  for i, statement in enumerate(statements):
    if state["active_pass"] is None and statement[0] in ("regs", "icn"):
      state["active_pass"] = next((p for s in statements[i + 1:] if (p := target_pass(s, env, limit)) is not None), 0)
    emit(statement, env, lines, state)
  resolve_write_routing(state["passes"][0])
  return lines, state


def block_statement_records(text, blocks):
  found = {}
  per_block = {}
  call_params = {}
  call_memories = {}
  state = None
  env = None
  owners = block_owners(text, blocks)
  extended_owners = {kernel_name(text, block) for block in blocks if block[0] == "kernel" and kernel_mode(text, block) == "extended"}
  for block in blocks:
    if block[0] == "kernel-block":
      macros = known_macros(text, block[1])
      state = new_state(macros, owners[block[1]], extended=decorator_names(text, block)[0] in extended_owners)
      env = new_env(macros)
      for statement in declared_statements(text, block[1]):
        emit(statement, env, [], state)
      per_block[block[1]] = state["sequence"]
      call_params[block[1]] = []
      call_memories[block[1]] = []
      owner_start = block[1]
    elif block[0] == "block-statement":
      _, start, _, end = block
      toks = [(kind, value, s + start, e + start) for kind, value, s, e in tokens(text[start:end])]
      before = len(state["sequence"])
      parser = Parser(text, toks, end, state["extended"])
      parser.in_call = True
      for statement in parse_body(parser):
        if statement[0] == "paramsuse":
          call_params[owner_start].append(statement[1])
        elif statement[0] == "memoryuse":
          call_memories[owner_start].append(statement[1])
        else:
          emit(statement, env, [], state)
      found[start] = state["sequence"][before:]
  return found, per_block, call_params, call_memories


def kernel_transfers(statements, macros=None, owner=None, extended=False):
  state = run_statements(statements, macros, owner, None, extended)[1]
  return state["loads"], state["stores"]


def build_kernel(text, block, compat):
  _, start, open_pos, _ = block
  header = text[start:open_pos]
  words = [(value, start + s) for _, value, s, _ in tokens(header)]
  if words[0][0] == ".":
    words = words[1:]
  name, options = words[1][0], []
  for word, pos in words[2:]:
    line = text.count("\n", 0, pos) + 1
    if word not in KERNEL_OPTIONS:
      raise ValueError(f"line {line}: unknown kernel option '{word}' ({', '.join(KERNEL_OPTIONS)})")
    if word in options:
      raise ValueError(f"line {line}: duplicate kernel option '{word}'")
    if options:
      raise ValueError(f"line {line}: a kernel is either direct or memory, not both")
    options.append(word)
  toks, limit = body_tokens(text, block)
  statements = declared_statements(text, start) + parse_body(Parser(text, toks, limit, options == ["extended"]))
  if not options:
    raise ValueError(f"line {text.count(chr(10), 0, start) + 1}: kernel '{name}' needs the option direct or memory")
  _, state = run_statements(statements, known_macros(text, start), name, compat, options == ["extended"])
  resolve_cross_stagings(state)
  active = [pass_state for pass_state in state["passes"] if pass_active(pass_state)] or [state["passes"][0]]
  finalized = [finalize_pass(state, pass_state) for pass_state in active]
  lines = finalized[0] + ["_vmeLibFinish();", "_vmeLibStart();"] + register_delta(active[0], active[1]) if len(active) == 2 else finalized[0]
  return name, options, lines, state


TRANSFER_TYPES = {"basic": "VmegTransfer", "Words": "VmegTransferWords"}

TRANSFER_STRUCTS = {
  "basic": "typedef struct { volatile u32* memory; u32 count; } VmegTransfer;",
  "Words": "typedef struct { volatile u32* memory; u32 count; u32 gap; u32 step; u32 groupSize; u32 groupOuter; u32 groupInner; } VmegTransferWords;",
}


def transfer_variable(name):
  clean = name.replace("[", "").replace("]", "")
  return "vmeVar" + clean[:1].upper() + clean[1:]


def transfer_initializer(kind, transfer):
  group = transfer.get("group", {})
  fields = [transfer["memory"], transfer["count"]]
  if kind == "Words":
    fields += [transfer.get("gap", 0), transfer.get("step", 0), group.get("size", 0), group.get("outer", 0), group.get("inner", 0)]
  return ", ".join(str(field) for field in fields)


def declare_transfers(text, block):
  names = {base_name(statement[1]): statement[-1] for statement in declared_statements(text, block[1])}
  own = declare_statements(text, block)
  for statement in own:
    key = base_name(statement[1])
    if key in names:
      raise ValueError(f"line {statement[-1]}: '{key}' is already declared in a @declare, at line {names[key]}")
    names[key] = statement[-1]
  macros = known_macros(text, block[1])
  state = new_state(macros)
  env = new_env(macros)
  for statement in declared_statements(text, block[1]) + own:
    emit(statement, env, [], state)
  found = []
  for statement in own:
    if statement[0] != "transferdecl":
      continue
    if statement[3] not in TRANSFER_TYPES:
      raise ValueError(f"line {statement[-1]}: Transfer({statement[3]}) is not generated yet (only Transfer and Transfer(Words))")
    keys = [f"{statement[1][0]}[{i}]" for i in range(state["arrays"][statement[1][0]]["size"])] if isinstance(statement[1], tuple) else [statement[1]]
    for key in keys:
      transfer = state["transfers"][key]
      if transfer.get("set") is False or "memory" not in transfer:
        raise ValueError(f"line {statement[-1]}: the Transfer variable '{key}' is read before it is set")
      found.append((transfer_variable(key), statement[3], transfer))
  return found


def declare_code(text, block):
  return "\n".join(f"{TRANSFER_TYPES[type_name]} {variable} = {{ {transfer_initializer(type_name, transfer)} }};" for variable, type_name, transfer in declare_transfers(text, block))


def declare_struct_types(text, blocks):
  kinds = {statement[3] for block in blocks if block[0] == "declare" for statement in declare_statements(text, block) if statement[0] == "transferdecl" and statement[3] in TRANSFER_STRUCTS}
  return [TRANSFER_STRUCTS[kind] for kind in TRANSFER_STRUCTS if kind in kinds]


def generate(text, block, warnings=None, compat=None):
  kind = block[0]
  if kind == "declare":
    return declare_code(text, block)
  if kind in ("decorator", "emulate", "emulate-block", "emulate-block-end", "kernel-block", "block-statement"):
    return ""
  if kind == "kernel-block-end":
    return DISABLE
  name, options, lines, state = build_kernel(text, block, compat)
  if warnings is not None:
    warnings.extend(state["warnings"])
  signature = ", ".join(f"{kind} {parameter}" for kind, parameter in state["params"] or [])
  if "memory" in options:
    names = ", ".join(parameter for _, parameter in state["params"] or [])
    head = ["meCoreMemset(vmegMemory, 0, VME_CONTEXT_WORD_COUNT*4);", "volatile u32 VME_BASE_ADDR = (u32)vmegMemory;"]
    tail = ["meCoreDcacheWritebackRange(vmegMemory, VME_CONTEXT_WORD_COUNT*4);"]
    build = f"void {name}Build(void* vmegMemory{', ' + signature if signature else ''}) {{\n" + "".join(f"  {line}\n" for line in head + lines + tail) + "}\n"
    keep = f"void* {name}({signature or 'void* param'}) {{\n  static u32 vmegContext[VME_CONTEXT_WORD_COUNT] __attribute__((aligned(64)));\n  {name}Build(vmegContext{', ' + names if names else ''});\n  return vmegContext;\n}}\n"
    return build + keep + f"void* {name}Context;"
  body = "".join(f"  {line}\n" for line in ["volatile u32 VME_BASE_ADDR = VME_DATAPATH_BASE;"] + lines)
  return f"void {name}({signature}) {{\n{body}}}"
