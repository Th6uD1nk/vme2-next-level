import importlib.util
import os

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


def kernel(entry):
  name = "check" + camel(entry["id"])
  pes = []
  for pe, writing in enumerate(entry["writings"]):
    top = ".top = top; " if pe < 2 else ""
    pes.append(f"  .pe{pe} {{ {top}.write = write; .spad = {writing}; }}")
  return f"""@emulate "{entry['id']}"
.kernel {name} direct {{
  Int count = 16 - 1;

  Transfer top0Transfer = {{ memory: in0, count }};
  Transfer top1Transfer = {{ memory: in1, count }};

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
