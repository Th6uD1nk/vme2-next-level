import re

from emu.listing import defines, emulations
from vmeg.blocks import decorator_names, find_blocks, kernel_name
from vmeg.host import BUFFER_TYPE, function_tokens
from vmeg.kernel import generate
from vmeg.parser import upload_text
from vmeg.registry import declarations
from vmeg.scanner import tokens


def chosen_emulation(text, identifier):
  found = emulations(text)
  chosen = [emulation for emulation in found if emulation["id"] == identifier]
  if not chosen:
    known = ", ".join(emulation["id"] for emulation in found)
    raise ValueError(f"no @emulate with the id '{identifier}' ({known if known else 'there is no @emulate in this file'})")
  return chosen[0]


def kernel_code(text, identifier):
  emulation = chosen_emulation(text, identifier)
  for block in find_blocks(text):
    if block[0] == "kernel" and kernel_name(text, block) == emulation["kernel"]:
      code = generate(text, block)
      if not code:
        raise ValueError(f"the kernel {emulation['kernel']} of the @emulate \"{identifier}\" has no code to run, it needs the option direct")
      return code


def array_declarations(text, identifier):
  emulation = chosen_emulation(text, identifier)
  blocks = find_blocks(text)
  available = {"global": declarations(text, list(tokens(text)), 0), "local": []}
  for block in blocks:
    if block[0] == "decorator" and emulation["kernel"] in decorator_names(text, block):
      available["local"] += declarations(text, function_tokens(text, block), 1)
  result = []
  seen = set()
  for qualifier in ("global", "local"):
    for source in dict.fromkeys(entry[3] for entry in emulation[qualifier]):
      for declaration in available[qualifier]:
        key = (qualifier, declaration["line"], declaration["text"])
        if source in declaration["names"] and key not in seen:
          seen.add(key)
          result.append(dict(declaration, where=qualifier))
          break
  return result


def upload_calls(text, identifier):
  emulation = chosen_emulation(text, identifier)
  return [upload_text(target, count, offset, source) for qualifier in ("global", "local") for target, count, offset, source, _ in emulation[qualifier]]


def host_source(text, identifier):
  for declaration in array_declarations(text, identifier):
    if declaration["extern"]:
      raise ValueError(f"the array {', '.join(declaration['names'])} of the @emulate \"{identifier}\" is declared extern, its contents are in another file")
  parts = [f"#define {name} {value}".rstrip() for name, value in defines(text)]
  parts += [re.sub(r"\bBuffer\b", BUFFER_TYPE, declaration["text"]) for declaration in array_declarations(text, identifier)]
  parts.append(kernel_code(text, identifier))
  calls = "".join(f"  {call}\n" for call in upload_calls(text, identifier))
  parts.append(f"static void vmegEmulateUpload(void) {{\n{calls}}}")
  return "\n\n".join(parts) + "\n"


INCLUDES = '#include "hw-trace.h"\n#include <me-core-mapper/vme-lib.h>\n#include <me-core-mapper/vme-fu-opcodes.h>\n'


def host_main(text, identifier):
  kernel = chosen_emulation(text, identifier)["kernel"]
  return f"int main() {{\n  vmeLibEnable();\n  vmeLibWipe();\n  vmegEmulateUpload();\n  {kernel}();\n  vmeLibDisable();\n  return 0;\n}}\n"


def host_program(text, identifier):
  return INCLUDES + "\n" + host_source(text, identifier) + "\n" + host_main(text, identifier)
