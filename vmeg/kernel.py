import re

from vmeg.blocks import body_tokens
from vmeg.host import block_owners
from vmeg.macros import known_macros
from vmeg.expr import fold, substitute, to_c
from vmeg.expr import value as full_value
from vmeg.operations import FUNCTIONS, OPERATIONS, OPERATORS
from vmeg.parser import AGU_PARAMS, ICN_NAMES, Parser, buffer_ref, parse_body
from vmeg.scanner import tokens
from vmeg.vmecalls import DISABLE, wait_marker

AUTO = "@auto@"

KERNEL_OPTIONS = ("direct", "memory")

ROUTING_NAMES = {"top": "AGU_TOP", "base": "AGU_BASE", "write": "AGU_WRITE"}

TRANSFER_FIELDS = ("type", "mode", "memory", "count", "dims", "step", "group")

TRANSFER_NESTED = {"dims": (("count", "gap"),), "group": (("size",), ("outer", "inner"))}

TRANSFER_EXTENDED = ("dims", "step", "group")

TRANSFER_WORDS = {"type": ("words", "halves", "bytes"), "mode": ("basic", "extended")}


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


def transfer_number(name, what, value, env):
  folded = full_value(value, env)
  if folded[0] == "num" and folded[1] < 0:
    raise ValueError(f"Transfer {name}: {what} cannot be negative")
  return folded[1]


def plus_one(number):
  return number + 1 if isinstance(number, int) else f"({number} + 1)"


def check_transfer_nested(name, key, value, env):
  if value[0] != "params":
    raise ValueError(f"Transfer {name}: '{key}' takes a list of fields")
  names = [field for register in TRANSFER_NESTED[key] for field in register]
  inner = {}
  for field, item in value[1]:
    if field not in names:
      raise ValueError(f"Transfer {name}: unknown field '{field}' of {key} ({', '.join(names)})")
    if field in inner:
      raise ValueError(f"Transfer {name}: duplicate field '{field}' of {key}")
    if item[0] == "params":
      raise ValueError(f"Transfer {name}: '{field}' of {key} takes a value, not a list of fields")
    inner[field] = transfer_number(name, f"{key}.{field}", item, env)
  if not inner:
    raise ValueError(f"Transfer {name}: {key} needs at least one field ({', '.join(names)})")
  for register in TRANSFER_NESTED[key]:
    missing = [field for field in register if field not in inner]
    if 0 < len(missing) < len(register):
      raise ValueError(f"Transfer {name}: the field '{missing[0]}' of {key} is needed, {' and '.join(register)} are one register")
  return inner


def check_transfer(name, params, env):
  values = {}
  for key, value in params[1]:
    if key not in TRANSFER_FIELDS:
      raise ValueError(f"Transfer {name}: unknown field '{key}' ({', '.join(TRANSFER_FIELDS)})")
    if key in values:
      raise ValueError(f"Transfer {name}: duplicate field '{key}'")
    if key in TRANSFER_NESTED:
      values[key] = check_transfer_nested(name, key, value, env)
      continue
    if value[0] == "params":
      raise ValueError(f"Transfer {name}: '{key}' takes a value, not a list of fields")
    if key in ("count", "step"):
      values[key] = transfer_number(name, key, value, env)
      continue
    if value[0] != "name":
      raise ValueError(f"Transfer {name}: '{key}' takes a name")
    if key in TRANSFER_WORDS and value[1] not in TRANSFER_WORDS[key]:
      raise ValueError(f"Transfer {name}: {key} must be {', '.join(TRANSFER_WORDS[key][:-1])} or {TRANSFER_WORDS[key][-1]}")
    values[key] = value[1]
  for key in ("type", "mode", "memory"):
    if key not in values:
      raise ValueError(f"Transfer {name}: the field '{key}' is needed")
  if values["mode"] == "basic":
    if "count" not in values:
      raise ValueError(f"Transfer {name}: the field 'count' is needed")
    for key in TRANSFER_EXTENDED:
      if key in values:
        raise ValueError(f"Transfer {name}: '{key}' is for the extended mode, this Transfer is basic")
  elif "count" in values:
    raise ValueError(f"Transfer {name}: in the extended mode the count is written dims: {{ count, gap }}")
  return values


def source_ref(expr, stagings):
  if expr[0] == "name" and expr[1] in stagings:
    if stagings[expr[1]] is None:
      raise ValueError(f"the Staging variable '{expr[1]}' is read before it is set")
    return stagings[expr[1]]
  return buffer_ref(expr)


def operand(expr, stagings):
  ref = source_ref(expr, stagings)
  if ref is None:
    raise ValueError("an operand must be a buffer (top0 to top3, base0 to base3) or a Staging variable")
  return ref


def split_source(expr, stagings):
  ref = source_ref(expr, stagings)
  if ref is not None:
    return ref, []
  return None, flatten(expr, stagings)


def check_arguments(name, args):
  names = [argument for argument, _ in OPERATIONS[FUNCTIONS[name]]["arguments"]]
  if len(args) != len(names):
    raise ValueError(f"{name} takes {len(names)} argument{'' if len(names) == 1 else 's'} ({', '.join(names)})")


def flatten(expr, stagings):
  kind = expr[0]
  if kind == "call":
    name, args = expr[1], expr[2]
    if name == "sat":
      if len(args) != 2:
        raise ValueError("sat takes 2 arguments (value, bits)")
      bits = constant(args[1], "sat bits")
      if not 0 <= bits <= 31:
        raise ValueError("sat bits out of range (0 to 31)")
      _, operations = split_source(args[0], stagings)
      if not operations:
        raise ValueError("sat must wrap an operation")
      if operations[-1]["sat"] is not None:
        raise ValueError("an operation takes only one sat")
      if operations[-1].get("shift") is not None:
        raise ValueError("the shift goes after the sat: sat(x, n) >> k")
      operations[-1]["sat"] = bits
      return operations
    if name in FUNCTIONS:
      check_arguments(name, args)
    if name == "clamp":
      low = constant(args[1], "clamp low")
      high = constant(args[2], "clamp high")
      source, operations = split_source(args[0], stagings)
      return operations + [{"kind": "clamp", "source": source, "low": low, "high": high, "sat": None}]
    if name == "acc":
      source, operations = split_source(args[0], stagings)
      if operations:
        raise ValueError("acc takes a buffer or a Staging variable")
      return [{"kind": "acc", "source": source, "sat": None}]
    if name == "subacst":
      constant_b = constant(args[2], "the constant of subacst")
      return [{"kind": "subacst", "front": operand(args[0], stagings), "back": operand(args[1], stagings), "b": constant_b, "sat": None}]
    if name == "subshr":
      amount = constant(args[2], "the shift of subshr")
      if amount < 0:
        raise ValueError("the shift of subshr cannot be negative")
      return [{"kind": "subshr", "front": operand(args[0], stagings), "back": operand(args[1], stagings), "b": amount, "sat": None}]
    if name == "mac":
      return [{"kind": "mac", "front": operand(args[0], stagings), "back": operand(args[1], stagings), "sat": None}]
    raise ValueError(f"unknown operation '{name}' ({', '.join(['sat', *FUNCTIONS])})")
  if kind == "bin":
    if expr[1] in (">>", "<<"):
      _, operations = split_source(expr[2], stagings)
      if not operations:
        raise ValueError("a shift must wrap an operation")
      amount = constant(expr[3], "the shift")
      if not 0 <= amount <= 63:
        raise ValueError("the shift must be 0 to 63")
      if operations[-1].get("shift") is not None:
        raise ValueError("an operation takes only one shift")
      operations[-1]["shift"] = amount if expr[1] == ">>" else (64 - amount) % 64
      return operations
    if expr[1] not in OPERATORS:
      raise ValueError(f"unsupported operator '{expr[1]}' ({', '.join([*OPERATORS, '>>', '<<'])})")
    return [{"kind": OPERATORS[expr[1]], "front": operand(expr[2], stagings), "back": operand(expr[3], stagings), "sat": None}]
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
        env[statement[1]] = statement[2]
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


def generate_agu(target, params, env, state, at, line):
  pe = target_pe(target, env)
  agu = target[2]
  values = {}
  for key, value in params[1]:
    if key not in AGU_PARAMS[agu]:
      raise ValueError(f"pe{pe}.{agu}: unknown parameter '{key}' ({', '.join(AGU_PARAMS[agu])})")
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
  if values.get("repeat"):
    if "inner0" not in values:
      raise ValueError(f"pe{pe}.{agu}: repeat needs inner0, the range to repeat")
    if "mode" in values and values["mode"] != "4":
      raise ValueError(f"pe{pe}.{agu}: repeat works in the AGU mode 4")
  mode = f"agu_mode({values['mode']})" if "mode" in values else "VME_DEF_MODE"
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
    lines.append(f"vme_pe{pe}(agu_{agu}(INNER_0), {values['inner0']['count']} << 16, {values['inner0']['step']});")
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
  def text(value):
    return replace_names(value, names or {})
  lines = [f"vme_dma(MEMORY, ADDR, useg_mem((u32){memory or transfer['memory']}));"]
  if transfer["mode"] == "basic":
    return lines + [f"vme_dma(ITERATION, DIMS, {text(transfer['count'])});"]
  if "dims" in transfer:
    lines.append(f"vme_dma(ITERATION, DIMS, {text(transfer['dims']['count'])}, {text(transfer['dims']['gap'])});")
  if "step" in transfer:
    lines.append(f"vme_dma(ITERATION, STEP, {text(transfer['step'])});")
  group = transfer.get("group", {})
  if "size" in group:
    lines.append(f"vme_dma(GROUP, SIZE, {text(group['size'])});")
  if "outer" in group:
    lines.append(f"vme_dma(GROUP, STEPS, {text(group['outer'])}, {text(group['inner'])});")
  return lines


def transfer_texts(transfer):
  texts = [transfer.get("count"), transfer.get("step")]
  for key in ("dims", "group"):
    texts += list(transfer.get(key, {}).values())
  return [text for text in texts if isinstance(text, str)]


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
  return hex((0x40 if transfer["mode"] == "basic" else 0x50) + (0x08 if direction == "store" else 0))


def transfer_destinations(targets):
  return [
    "0" if buffer is None else f"VME_{buffer.upper()}_BUFF{slot}_WOFF" + (f" + {offset_text(offset)}" if offset_text(offset) else "")
    for buffer, slot, offset in targets or [(None, 0, ("num", 0))]
  ]


def transfer_lines(transfer, targets, direction):
  lines = transfer_registers(transfer)
  control = transfer_control(transfer, direction)
  for destination in transfer_destinations(targets):
    lines += [f"vme_dma(SPAD, OFFSET, {destination});", f"vme_dma(CTRL, VALUE, {control});", "meCoreDMACPrimWaitTransferFinish();"]
  return lines


def camel(*words):
  return words[0] + "".join(word[:1].upper() + word[1:] for word in words[1:])


def transfer_function(name, transfer, direction):
  names = parameter_names(transfer_names(transfer))
  body = transfer_registers(transfer, "memory", names) + ["vme_dma(SPAD, OFFSET, spadOffset);", f"vme_dma(CTRL, VALUE, {transfer_control(transfer, direction)});"]
  parameters = "".join(f", u32 {parameter}" for parameter in names.values())
  return f"static inline void {name}(volatile u32* memory, u32 spadOffset{parameters}) {{\n" + "".join(f"  {line}\n" for line in body) + "}"


def transfer_calls(name, transfer, targets):
  arguments = "".join(f", {original}" for original in transfer_names(transfer))
  return [line for destination in transfer_destinations(targets) for line in (f"{name}({transfer['memory']}, {destination}{arguments});", wait_marker(name))]


def transfer_links(transfer, targets):
  words = plus_one(transfer["count"] if transfer["mode"] == "basic" else transfer.get("dims", {"count": 0})["count"])
  return [("SPAD" if buffer is None else f"{buffer.upper()}_{slot}", words, offset_text(offset), transfer["memory"], transfer["mode"] == "extended") for buffer, slot, offset in targets or [(None, 0, ("num", 0))]]


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
    if specification["units"] == "primary" and number != 0:
      raise ValueError(f"{operation['kind']} must be the first operation of the pe")
    code = specification["code"]
    if specification["operands"] == ("front", "back"):
      mux = f"vme_mux({operation['front']}, {operation['back']})"
      reads = (operation["front"], operation["back"])
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
    lines.append(f"vme_pe{pe}(vme_fu({unit}), {mux}, {code}{sat});")
    if "b" in operation:
      lines.append(f"vme_pe{pe}(fu_reg({unit}, B), {to_c(('num', operation['b']))});")
    if operation["kind"] == "clamp":
      lines.append(f"vme_pe{pe}(fu_reg({unit}, A), {to_c(('num', operation['high']))});")
      lines.append(f"vme_pe{pe}(fu_reg({unit}, B), {to_c(('num', operation['low']))});")
  return number, depth


def emit_statement(statement, env, lines, state):
  kind = statement[0]
  if kind == "int":
    if statement[1] == "auto":
      raise ValueError("auto is reserved for the cyc of a write AGU")
    if statement[1] in env and statement[1] not in state["macros"]:
      raise ValueError(f"'{statement[1]}' is defined twice")
    env[statement[1]] = full_value(statement[2], env)
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
    if statement[1] in state["agus"]:
      raise ValueError(f"the Agu variable '{statement[1]}' is declared twice")
    if statement[1] in state["stagings"]:
      raise ValueError(f"'{statement[1]}' is already declared as a Staging variable")
    if statement[1] in state["transfers"]:
      raise ValueError(f"'{statement[1]}' is already declared as a Transfer variable")
    state["agus"][statement[1]] = {"params": statement[2], "owners": {}}
  elif kind == "stagingdecl":
    if statement[1] in state["stagings"]:
      raise ValueError(f"the Staging variable '{statement[1]}' is declared twice")
    if statement[1] in state["agus"]:
      raise ValueError(f"'{statement[1]}' is already declared as an Agu variable")
    if statement[1] in state["transfers"]:
      raise ValueError(f"'{statement[1]}' is already declared as a Transfer variable")
    state["stagings"][statement[1]] = {}
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
      if offset[0] == "num" and offset[1] < 0:
        raise ValueError(f"the offset of {buffer}{slot[1]} cannot be negative")
      targets.append((buffer, slot[1], offset))
    if items["transfer"][1] not in state["transfers"]:
      raise ValueError(f"unknown Transfer variable '{items['transfer'][1]}'")
    transfer = state["transfers"][items["transfer"][1]]
    if transfer["type"] != "words":
      raise ValueError(f"this .{kind} is not generated yet (only the Transfer of words)")
    function = camel(state["owner"], items["transfer"][1], kind.capitalize()) if state["owner"] else None
    record = {"function": function, "definition": transfer_function(function, transfer, kind) if function else None, "calls": transfer_calls(function, transfer, targets) if function else None, "kind": kind, "scope": items.get("scope", ("name", "local"))[1], "memory": transfer["memory"], "line": statement[-1], "lines": transfer_lines(transfer, targets, kind), "links": transfer_links(transfer, targets)}
    state[kind + "s"].append(record)
    state["sequence"].append(record)
  elif kind == "transferdecl":
    if statement[1] in state["transfers"]:
      raise ValueError(f"the Transfer variable '{statement[1]}' is declared twice")
    if statement[1] in state["agus"]:
      raise ValueError(f"'{statement[1]}' is already declared as an Agu variable")
    if statement[1] in state["stagings"]:
      raise ValueError(f"'{statement[1]}' is already declared as a Staging variable")
    state["transfers"][statement[1]] = check_transfer(statement[1], statement[2], env)
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
      lines.extend(generate_agu(("target", ("num", pe), slot), variable["params"], env, state, len(lines), statement[-1]))
    state["routing"][slot][pe] = variable["owners"][slot]
  elif kind == "operation":
    pe = target_pe(statement[1], env)
    if (pe, "operation") in state["set"]:
      raise ValueError(f"pe{pe} has two outputs on the same write, the first one is at line {state['set'][(pe, 'operation')]}")
    claim(state, pe, "operation", statement[-1])
    last, depth = place(state, lines, pe, flatten(fold(statement[2], env), staging_refs(state)), statement[-1])
    state["outputs"].setdefault(pe, statement[-1])
    state["depths"][pe] = depth
    if last == 1:
      state["secondary"].add(pe)
  elif kind == "stageset":
    name = statement[2]
    variable = state["stagings"].get(name)
    if variable is None:
      if name in state["agus"]:
        raise ValueError(f"'{name}' is an Agu variable, only a Staging variable can receive an operation")
      raise ValueError(f"unknown Staging variable '{name}'")
    if "pe" in variable:
      raise ValueError(f"the Staging variable '{name}' is already set at line {variable['line']}")
    pe = target_pe(statement[1], env)
    last, depth = place(state, lines, pe, flatten(fold(statement[3], env), staging_refs(state)), statement[-1])
    variable.update({"pe": pe, "unit": last, "line": statement[-1], "depth": depth})
  elif kind == "peblock":
    for inner in statement[1]:
      emit(inner, env, lines, state)
  elif kind == "for":
    loop = ("for", statement[1], fold(statement[2], env), fold(statement[3], env), statement[4], statement[5])
    for inner in unroll(loop):
      emit(inner, env, lines, state)


def new_state(macros=None, owner=None):
  return {"owner": owner, "macros": set(macros or ()), "secondary": set(), "set": {}, "agus": {}, "stagings": {}, "transfers": {}, "loads": [], "stores": [], "sequence": [], "fus": {}, "routing": {slot: [4, 4, 4, 4] for slot in ("top", "base", "write")}, "warnings": [], "reads": {}, "outputs": {}, "depths": {}, "autos": [], "icn": set()}


def new_env(macros=None):
  env = {"true": ("num", 1), "false": ("num", 0)}
  for name, number in (macros or {}).items():
    env.setdefault(name, ("num", number))
  return env


def resolve_auto(lines, state):
  for pending in state["autos"]:
    pe = pending["pe"]
    if pe not in state["depths"]:
      raise ValueError(f"line {pending['line']}: pe{pe}.write: cyc auto needs an operation in pe{pe}")
    env = dict(pending["env"])
    env["auto"] = ("num", 3 + 3 * state["depths"][pe])
    lines[pending["at"]] = lines[pending["at"]].replace(AUTO, to_c(full_value(pending["expr"], env)))


def run_statements(statements, macros=None, owner=None):
  lines = []
  env = new_env(macros)
  state = new_state(macros, owner)
  for statement in statements:
    emit(statement, env, lines, state)
  resolve_auto(lines, state)
  return lines, state


def block_statement_records(text, blocks):
  found = {}
  per_block = {}
  state = None
  env = None
  owners = block_owners(text, blocks)
  for block in blocks:
    if block[0] == "kernel-block":
      macros = known_macros(text, block[1])
      state = new_state(macros, owners[block[1]])
      env = new_env(macros)
      per_block[block[1]] = state["sequence"]
    elif block[0] == "block-statement":
      _, start, _, end = block
      toks = [(kind, value, s + start, e + start) for kind, value, s, e in tokens(text[start:end])]
      before = len(state["sequence"])
      for statement in parse_body(Parser(text, toks, end)):
        emit(statement, env, [], state)
      found[start] = state["sequence"][before:]
  return found, per_block


def kernel_transfers(statements, macros=None, owner=None):
  state = run_statements(statements, macros, owner)[1]
  return state["loads"], state["stores"]


def generate(text, block, warnings=None):
  kind, start, open_pos, _ = block
  if kind in ("decorator", "emulate", "kernel-block", "block-statement"):
    return ""
  if kind == "kernel-block-end":
    return DISABLE
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
  statements = parse_body(Parser(text, toks, limit))
  if not options:
    raise ValueError(f"line {text.count(chr(10), 0, start) + 1}: kernel '{name}' needs the option direct or memory")
  lines, state = run_statements(statements, known_macros(text, start), name)
  for ref, line in state["reads"].items():
    slot, number = ref.lower().split("_")
    if state["routing"][slot][int(number)] == 4:
      warn(state, line, f"{slot}{number} is read but no .{slot} is bound in pe{number} of this kernel")
  for pe, line in state["outputs"].items():
    if state["routing"]["write"][pe] == 4:
      warn(state, line, f"pe{pe} has an operation but no .write is bound in this kernel")
  for slot, nibbles in state["routing"].items():
    lines.append(f"vme_icn({ROUTING_NAMES[slot]}, 0x{sum(nibble << 4 * i for i, nibble in enumerate(nibbles)):04x});")
  if state["secondary"]:
    lines.append(f"vme_icn(SWEN, fu_on(0b{swen_mask(state['secondary']):04b}));")
  if warnings is not None:
    warnings.extend(state["warnings"])
  if "memory" in options:
    return f"VME_LIB_CONTEXT_BUILDER({name}, param, {{\n" + "".join(f"  {line}\n" for line in lines) + f"}});\nvoid* {name}Context;"
  body = "".join(f"  {line}\n" for line in ["volatile u32 VME_BASE_ADDR = VME_DATAPATH_BASE;"] + lines)
  return f"void {name}() {{\n{body}}}"
