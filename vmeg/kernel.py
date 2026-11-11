import re

from vmeg.blocks import body_tokens
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

KERNEL_OPTIONS = ("direct", "memory")

ROUTING_NAMES = {"top": "AGU_TOP", "base": "AGU_BASE", "write": "AGU_WRITE"}

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


def source_ref(expr, stagings):
  if expr[0] == "name":
    if expr[1] in stagings:
      if stagings[expr[1]] is None:
        raise ValueError(f"the Staging variable '{expr[1]}' is read before it is set")
      return stagings[expr[1]]
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
      if stagings[key] is None:
        raise ValueError(f"the Staging variable '{key}' is read before it is set")
      return stagings[key]
  return buffer_ref(expr)


def operand(expr, stagings):
  ref = source_ref(expr, stagings)
  if ref is None:
    raise ValueError("an operand must be a buffer (top0 to top3, base0 to base3) or a Staging variable")
  return ref


def split_source(expr, stagings, compat):
  ref = source_ref(expr, stagings)
  if ref is not None:
    return ref, []
  return None, flatten(expr, stagings, compat)


def operations_of(expr, stagings, compat):
  source, operations = split_source(expr, stagings, compat)
  if source is not None:
    return [{"kind": "pass", "source": source, "numbers": {}, "sat": None}]
  return operations


def check_arguments(name, args):
  names = [argument for argument, _ in OPERATIONS[FUNCTIONS[name]]["arguments"]]
  if len(args) != len(names):
    raise ValueError(f"{name} takes {len(names)} argument{'' if len(names) == 1 else 's'} ({', '.join(names)})")


def table_operands(label, specification, args, stagings, compat):
  given = [(kind, expr) for (_, kind), expr in zip(specification["arguments"], args) if kind != "number"]
  if not given:
    return {"source": None}, []
  if len(specification["operands"]) == 2:
    return {slot: operand(expr, stagings) for slot, (_, expr) in zip(specification["operands"], given)}, []
  source, operations = split_source(given[0][1], stagings, compat)
  if operations and given[0][0] == "operand":
    raise ValueError(f"{label} takes a buffer or a Staging variable")
  return {"source": source}, operations


def table_operation(kind, label, args, stagings, compat):
  specification = OPERATIONS[kind]
  numbers = {}
  for (argument, argument_kind), expr_argument in zip(specification["arguments"], args):
    if argument_kind == "number":
      numbers[argument] = constant(expr_argument, f"{label} {argument}")
  operands, operations = table_operands(label, specification, args, stagings, compat)
  operation = {"kind": kind, **operands, "numbers": numbers, "sat": None}
  if "shift" in specification:
    if not 0 <= numbers[specification["shift"]] <= 63:
      raise ValueError("the shift must be 0 to 63")
    operation["shift"] = numbers[specification["shift"]]
  return operations + [operation]


def flatten(expr, stagings, compat):
  kind = expr[0]
  if kind == "call":
    name, args = expr[1], expr[2]
    if name == "sat":
      if len(args) != 2:
        raise ValueError("sat takes 2 arguments (value, bits)")
      bits = constant(args[1], "sat bits")
      if not 0 <= bits <= 31:
        raise ValueError("sat bits out of range (0 to 31)")
      operations = operations_of(args[0], stagings, compat)
      if operations[-1]["sat"] is not None:
        raise ValueError("an operation takes only one sat")
      if operations[-1].get("shift") is not None:
        raise ValueError("the shift goes after the sat: sat(x, n) >> k")
      operations[-1]["sat"] = bits
      return operations
    if name == "round":
      if len(args) != 1:
        raise ValueError("round takes 1 argument (value)")
      operations = operations_of(args[0], stagings, compat)
      if operations[-1].get("round"):
        raise ValueError("an operation takes only one round")
      operations[-1]["round"] = True
      return operations
    if name in FUNCTIONS:
      check_arguments(name, args)
      return table_operation(FUNCTIONS[name], name, args, stagings, compat)
    raise ValueError(f"unknown operation '{name}' ({', '.join(['sat', 'round', *FUNCTIONS])})")
  if kind == "not":
    found = choose_opcode(expr, compat)
    if found is None:
      return table_operation("not", "not", [expr[1]], stagings, compat)
    kind, bound, _ = found
    return table_operation(kind, kind, [bound[name] for name, _ in OPERATIONS[kind]["arguments"]], stagings, compat)
  if kind == "bin":
    if expr[1] in (">>", "<<", ">>>", "<<<") and expr[2][0] not in OPERATION_NODES:
      found = choose_opcode(expr, compat)
      if found is not None:
        kind, bound, _ = found
        return table_operation(kind, kind, [bound[name] for name, _ in OPERATIONS[kind]["arguments"]], stagings, compat)
    if expr[1] in (">>", "<<"):
      if expr[2][0] == "num" and expr[3][0] != "num":
        raise ValueError("no opcode covers this expression: a number shifted by a buffer must be from -0x800000 to 0xffffff")
      operations = operations_of(expr[2], stagings, compat)
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
    return table_operation(kind, kind, [bound[name] for name, _ in OPERATIONS[kind]["arguments"]], stagings, compat)
  if kind == "cond":
    found = choose_opcode(expr, compat)
    if found is None:
      raise ValueError("no opcode covers this expression")
    kind, bound, _ = found
    return table_operation(kind, kind, [bound[name] for name, _ in OPERATIONS[kind]["arguments"]], stagings, compat)
  if kind == "num":
    return table_operation("cst", "cst", [expr], stagings, compat)
  if source_ref(expr, stagings) is not None:
    return operations_of(expr, stagings, compat)
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


def generate_agu(target, params, env, state, at, line, mode=4):
  pe = target_pe(target, env)
  agu = target[2]
  values = {}
  for key, value in params[1]:
    if key == "mode":
      raise ValueError(f"pe{pe}.{agu}: the mode of an Agu is its type, write Agu(4) or Agu(2)")
    if key not in AGU_PARAMS[mode][agu]:
      raise ValueError(f"pe{pe}.{agu}: unknown parameter '{key}' ({', '.join(AGU_PARAMS[mode][agu])})")
    if key in values:
      raise ValueError(f"pe{pe}.{agu}: duplicate parameter '{key}'")
    if key == "inner0":
      values[key] = check_inner(pe, agu, key, value, env)
      continue
    if value[0] == "params":
      raise ValueError(f"pe{pe}.{agu}: '{key}' takes a value, not parameters between braces")
    if has_auto(value):
      if key != "cyc":
        raise ValueError(f"pe{pe}.{agu}: auto is only for cyc")
      values[key] = AUTO
      state["autos"].append({"pe": pe, "expr": value, "env": env, "at": at, "line": line})
      continue
    folded = full_value(value, env)
    if key in ("reverse", "repeat", "sync"):
      if folded[0] != "num" or folded[1] not in (0, 1):
        raise ValueError(f"pe{pe}.{agu}: {key} takes true or false")
      values[key] = folded[1]
      continue
    if key == "bubbles" and folded[0] == "num" and not 0 <= folded[1] <= 4095:
      raise ValueError(f"pe{pe}.{agu}: the bubbles {folded[1]} are outside 0 to 4095")
    if key == "bubbles":
      values[key] = to_c(folded) if folded[0] == "num" else f"{to_c(folded) if folded[0] != 'name' else '(' + to_c(folded) + ')'} & 0xfff"
      continue
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
  two = mode == 2
  mode = "agu_mode(2)" if two else "VME_DEF_MODE"
  if "offset" in values:
    mode += f", {values['offset']}"
  if "cyc" in values:
    mode += f", vme_cyc({values['cyc']})"
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
  name = f"VME_{buffer.upper()}_BUFF{slot}_WOFF"
  if offset[0] == "num" and offset[1] < 0:
    return f"{name} - {to_c(('num', -offset[1]))}"
  return name + (f" + {offset_text(offset)}" if offset_text(offset) else "")


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


def claim(state, pe, name, line):
  key = (pe, name)
  if key in state["set"]:
    raise ValueError(f"pe{pe}.{name} is already set at line {state['set'][key]}")
  state["set"][key] = line


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


def staging_refs(state):
  return {name: f"STAGING_{variable['pe'] + 4 * variable['unit']}" if "pe" in variable else None for name, variable in state["stagings"].items()}


def staging_depths(state):
  return {f"STAGING_{variable['pe'] + 4 * variable['unit']}": variable["depth"] for variable in state["stagings"].values() if "pe" in variable}


def place(state, lines, pe, operations, line):
  used = state["fus"].get(pe, 0)
  depths = staging_depths(state)
  depth = 0
  if used + len(operations) > 2:
    raise ValueError(f"a pe holds two operations at most, this pe needs {used + len(operations)}")
  for operation in operations:
    number = state["fus"].get(pe, 0)
    state["fus"][pe] = number + 1
    unit = "PRIMARY" if number == 0 else "SECONDARY"
    specification = OPERATIONS[operation["kind"]]
    state["operations"].append(dict(operation, pe=pe, line=line))
    remap = state["remaps"].get(pe, {}).get(ROOT_OPERATORS[operation["kind"]], {})
    if specification["units"] == "primary" and number != 0 and unit.lower() not in remap:
      warn(state, line, f"{operation['kind']} is the second operation of pe{pe}, it is not known to run in the second unit")
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
      mux = f"vme_mux({operation['front']}, {operation['back']})"
      reads = (operation["front"], operation["back"])
    elif operands == ("front",):
      source = operation["source"] or f"STAGING_{pe}"
      mux = f"vme_mux({source}, NONE)"
      reads = (operation["source"],) if operation["source"] else ()
    else:
      source = operation["source"] or f"STAGING_{pe}"
      mux = f"vme_mux(NONE, {source})"
      reads = (operation["source"],) if operation["source"] else ()
    for ref in reads:
      if not ref.startswith("STAGING"):
        state["reads"].setdefault(ref, line)
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
    for name, value in statement[1]:
      if value[0] != "num":
        raise ValueError(f".{name} takes a number")
      limit = 0xf if name == "swen" else 0xffff
      if not 0 <= value[1] <= limit:
        raise ValueError(f".{name} takes a number from 0 to 0x{limit:x}")
      if name == "swen":
        state["secondary"] = {pe for pe in range(4) if value[1] >> (3 - pe) & 1}
        state["swen_raw"] = True
      else:
        state["routing"][name] = [value[1] >> 4 * pe & 0xf for pe in range(4)]
  elif kind == "icn":
    for icn, value in statement[1]:
      if icn in state["icn"]:
        raise ValueError(f"duplicate interconnect '{icn}'")
      state["icn"].add(icn)
      lines.append(f"vme_icn({ICN_NAMES[icn]}, {to_c(full_value(value, env))});")
  elif kind == "agu":
    pe = target_pe(statement[1], env)
    claim(state, pe, statement[1][2], statement[-1])
    state["routing"][statement[1][2]][pe] = pe
    lines.extend(generate_agu(statement[1], statement[2], env, state, len(lines), statement[-1]))
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
    for buffer, index, value in items.get("offsets", ("offsets", []))[1]:
      slot = fold(index, env)
      if slot[0] != "num" or not 0 <= slot[1] <= 3:
        raise ValueError(f"{buffer}[...]: buffer index must be a number from 0 to 3")
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
    pe = target_pe(statement[1], env)
    slot = statement[1][2]
    for bound in variable["owners"]:
      if bound != slot:
        raise ValueError(f"the Agu variable '{ref}' is already bound to .{bound}, it cannot be bound to .{slot}")
    claim(state, pe, slot, statement[-1])
    if slot not in variable["owners"]:
      variable["owners"][slot] = pe
      lines.extend(generate_agu(("target", ("num", pe), slot), variable["params"], env, state, len(lines), statement[-1], variable["mode"]))
    if any(key == "cyc" and has_auto(value) for key, value in variable["params"][1]):
      state["sharers"].setdefault(ref, []).append((pe, statement[-1]))
    state["routing"][slot][pe] = variable["owners"][slot]
  elif kind == "operation":
    pe = target_pe(statement[1], env)
    if (pe, "operation") in state["set"]:
      raise ValueError(f"pe{pe} has two outputs on the same write, the first one is at line {state['set'][(pe, 'operation')]}")
    claim(state, pe, "operation", statement[-1])
    last, depth = place(state, lines, pe, flatten(fold(statement[2], env), staging_refs(state), state["compat"]), statement[-1])
    state["outputs"].setdefault(pe, statement[-1])
    state["depths"][pe] = depth
    if last == 1:
      state["secondary"].add(pe)
    else:
      state["secondary"].discard(pe)
  elif kind == "paramsdef":
    if state["params"] is not None:
      raise ValueError("the parameters of the kernel are declared twice")
    state["params"] = statement[1]
  elif kind == "remap":
    pe = target_pe(statement[1], env)
    operator = statement[2]
    if not any(operator in operators for operators in PATTERN_OPERATORS.values()):
      raise ValueError(f"unknown operator '{operator}' in .remap")
    remaps = state["remaps"].setdefault(pe, {})
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
    pe = target_pe(statement[1], env)
    last, depth = place(state, lines, pe, flatten(fold(statement[3], env), staging_refs(state), state["compat"]), statement[-1])
    variable.update({"pe": pe, "unit": last, "line": statement[-1], "depth": depth})
  elif kind == "peblock":
    for inner in sorted(statement[1], key=lambda item: item[0] != "remap"):
      emit(inner, env, lines, state)
  elif kind == "for":
    loop = ("for", statement[1], fold(statement[2], env), fold(statement[3], env), statement[4], statement[5])
    for inner in unroll(loop):
      emit(inner, env, lines, state)


def new_state(macros=None, owner=None, compat=None):
  return {"owner": owner, "macros": set(macros or ()), "secondary": set(), "set": {}, "agus": {}, "stagings": {}, "transfers": {}, "arrays": {}, "loads": [], "stores": [], "sequence": [], "fus": {}, "routing": {slot: [4, 4, 4, 4] for slot in ("top", "base", "write")}, "warnings": [], "reads": {}, "outputs": {}, "depths": {}, "autos": [], "icn": set(), "swen_raw": False, "sharers": {}, "compat": compat, "operations": [], "remaps": {}, "params": None}


def new_env(macros=None):
  env = {"true": ("num", 1), "false": ("num", 0)}
  for name, number in (macros or {}).items():
    env.setdefault(name, ("num", number))
  return env


def check_shared_auto(state):
  for name, sharers in state["sharers"].items():
    owner = sharers[0][0]
    for pe, line in sharers[1:]:
      if pe in state["depths"] and state["depths"][pe] != state["depths"][owner]:
        warn(state, line, f"pe{pe} shares the write Agu '{name}' with pe{owner} but its operations need another delay, cyc: auto follows pe{owner}")


def resolve_auto(lines, state):
  for pending in state["autos"]:
    pe = pending["pe"]
    if pe not in state["depths"]:
      raise ValueError(f"line {pending['line']}: pe{pe}.write: cyc auto needs an operation in pe{pe}")
    env = dict(pending["env"])
    env["auto"] = ("num", 3 + 3 * state["depths"][pe])
    lines[pending["at"]] = lines[pending["at"]].replace(AUTO, to_c(full_value(pending["expr"], env)))
  check_shared_auto(state)


def run_statements(statements, macros=None, owner=None, compat=None):
  lines = []
  env = new_env(macros)
  state = new_state(macros, owner, compat)
  for statement in statements:
    emit(statement, env, lines, state)
  resolve_auto(lines, state)
  return lines, state


def block_statement_records(text, blocks):
  found = {}
  per_block = {}
  call_params = {}
  call_memories = {}
  state = None
  env = None
  owners = block_owners(text, blocks)
  for block in blocks:
    if block[0] == "kernel-block":
      macros = known_macros(text, block[1])
      state = new_state(macros, owners[block[1]])
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
      parser = Parser(text, toks, end)
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


def kernel_transfers(statements, macros=None, owner=None):
  state = run_statements(statements, macros, owner)[1]
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
  statements = declared_statements(text, start) + parse_body(Parser(text, toks, limit))
  if not options:
    raise ValueError(f"line {text.count(chr(10), 0, start) + 1}: kernel '{name}' needs the option direct or memory")
  lines, state = run_statements(statements, known_macros(text, start), name, compat)
  for ref, line in state["reads"].items():
    slot, number = ref.lower().split("_")
    if state["routing"][slot][int(number)] == 4:
      warn(state, line, f"{slot}{number} is read but no .{slot} is bound in pe{number} of this kernel")
  for pe, line in state["outputs"].items():
    if state["routing"]["write"][pe] == 4:
      warn(state, line, f"pe{pe} has an operation but no .write is bound in this kernel")
  for slot, nibbles in state["routing"].items():
    lines.append(f"vme_icn({ROUTING_NAMES[slot]}, 0x{sum(nibble << 4 * i for i, nibble in enumerate(nibbles)):04x});")
  if state["secondary"] or state["swen_raw"]:
    lines.append(f"vme_icn(SWEN, fu_on(0b{swen_mask(state['secondary']):04b}));")
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
