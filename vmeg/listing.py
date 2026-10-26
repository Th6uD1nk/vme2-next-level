from vmeg.operations import OPERATIONS


def reference_text(ref):
  return ref.lower().replace("_", "")


def bound_values(operation):
  specification = OPERATIONS[operation["kind"]]
  if specification["operands"] == ("front", "back"):
    operands = [reference_text(operation["front"]), reference_text(operation["back"])]
  else:
    operands = [reference_text(operation["source"] or f"STAGING_{operation['pe']}")]
  values = []
  for name, role in specification["arguments"]:
    if role == "number":
      values.append(f"{name} = {operation['numbers'].get(name, 0)}")
    else:
      values.append(f"{name} = {operands.pop(0)}")
  return ", ".join(values)


def kernel_operation_lines(state):
  rows = []
  for operation in state["operations"]:
    specification = OPERATIONS[operation["kind"]]
    rows.append((f"pe{operation['pe']}", f"line {operation['line']}", f"0x{specification['opcode']:03x}", specification["pattern"], bound_values(operation)))
  widths = [max(len(row[i]) for row in rows) for i in range(4)] if rows else []
  return ["  " + "  ".join(column.ljust(width) for column, width in zip(row, widths)) + "  " + row[4] for row in rows]
