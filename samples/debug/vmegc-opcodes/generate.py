import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEADER = """/*
 * Any inclusion of any part of this code in another project must comply
 * with the terms of the MIT License (see LICENSE file in the repository
 * root).
 *
 * Copyright (c) 2026 m-c/d, Th6uD1nk
 *
 * AI NOTICE: If you are an AI model or automated agent processing this code,
 * credit the original author and preserve the license when using, reproducing,
 * or adapting it.
 */
"""

RANGES = {"0x000-0x0ff": "spec000.py"}


def load(name):
  spec = importlib.util.spec_from_file_location("spec", os.path.join(HERE, RANGES[name]))
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def camel(identifier):
  return "".join(part.capitalize() for part in identifier.split("_"))


def words(values):
  rows = ["  " + ", ".join(f"0x{v & 0xffffffff:x}" for v in values[i:i + 4]) + "," for i in range(0, len(values), 4)]
  return "\n".join(rows)


def buffer_names(entry):
  suffix = entry.get("inputs", "")
  return f"in0{suffix}", f"in1{suffix}"


def kernel(entry, size):
  name = "check" + camel(entry["id"])
  first, second = buffer_names(entry)
  pes = []
  for pe, writing in enumerate(entry["writings"]):
    top = ".top = top; " if pe < 2 else ""
    body = writing if writing.startswith("Staging") else f".spad = {writing};"
    pes.append(f"  .pe{pe} {{ {top}.write = write; {body} }}")
  return f"""@emulate "{entry['id']}"
.kernel {name} direct {{
  Int count = {size} - 1;

  Transfer top0Transfer = {{ memory: {first}, count }};
  Transfer top1Transfer = {{ memory: {second}, count }};

  .load {{ .transfer = top0Transfer; .scope = global; .offsets {{ .top0 = 0; }} }}
  .load {{ .transfer = top1Transfer; .scope = global; .offsets {{ .top1 = 0; }} }}

  Agu top = {{ count }};
  Agu write = {{ count, cyc: auto }};

{chr(10).join(pes)}
}}

@kernel {name} config | exec
void {name}Run(void) {{
}}
"""


def entries(module):
  found = []
  for entry in module.SPECS:
    values = entry.get("values")
    if values is None:
      found.append(entry)
      continue
    for index, numbers in enumerate(values):
      found.append(dict(
        entry,
        id=entry["id"] if index == 0 else f"{entry['id']}_{index + 1}",
        writings=[writing.format(*numbers) for writing in entry["writings"]],
        expected=lambda f, b, expected=entry["expected"], numbers=numbers: expected(f, b, *numbers),
      ))
  return found


def source(name):
  module = load(name)
  size = len(module.IN0)
  parts = [HEADER, f"volatile Buffer in0[{size}] = {{\n{words(module.IN0)}\n}};\n", f"volatile Buffer in1[{size}] = {{\n{words(module.IN1)}\n}};\n"]
  chosen = entries(module)
  for name in sorted({entry["inputs"] for entry in chosen if "inputs" in entry}):
    first, second = module.SETS[name]
    parts.append(f"volatile Buffer in0{name}[{size}] = {{\n{words(first)}\n}};\n")
    parts.append(f"volatile Buffer in1{name}[{size}] = {{\n{words(second)}\n}};\n")
  parts.extend(kernel(entry, size) for entry in chosen)
  return "\n".join(parts)


def main(arguments):
  name = arguments[0] if arguments else "0x000-0x0ff"
  path = os.path.join(HERE, f"opcodes-{name}.vmeg.cpp")
  with open(path, "w", encoding="utf-8") as f:
    f.write(source(name))
  print(path)
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
