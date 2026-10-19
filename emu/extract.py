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


def other_declaration(others, source):
  for other in others:
    for declaration in declarations(other, list(tokens(other)), 0):
      if source in declaration["names"] and not declaration["extern"] and not declaration["static"]:
        return dict(declaration, origin=other)
  return None


def array_declarations(text, identifier, others=()):
  emulation = chosen_emulation(text, identifier)
  blocks = find_blocks(text)
  available = {"global": declarations(text, list(tokens(text)), 0), "local": []}
  for file in (text, *others):
    for block in (blocks if file is text else find_blocks(file)):
      if block[0] == "decorator" and emulation["kernel"] in decorator_names(file, block):
        available["local"] += [dict(declaration, origin=file) for declaration in declarations(file, function_tokens(file, block), 1)]
  result = []
  seen = set()
  for qualifier in ("global", "local"):
    for source in dict.fromkeys(entry[3] for entry in emulation[qualifier]):
      found = next((declaration for declaration in available[qualifier] if source in declaration["names"]), None)
      if qualifier == "global" and (found is None or found["extern"]):
        found = other_declaration(others, source) or found
      if found is None:
        continue
      key = (qualifier, found["line"], found["text"])
      if key not in seen:
        seen.add(key)
        result.append(dict(found, where=qualifier, origin=found.get("origin", text)))
  return result


def upload_calls(text, identifier):
  emulation = chosen_emulation(text, identifier)
  return [upload_text(target, count, offset, source) for qualifier in ("global", "local") for target, count, offset, source, _ in emulation[qualifier]]


def host_source(text, identifier, others=()):
  arrays = array_declarations(text, identifier, others)
  for declaration in arrays:
    if declaration["extern"]:
      raise ValueError(f"the array {', '.join(declaration['names'])} of the @emulate \"{identifier}\" is declared extern and no file defines it")
  emulation = chosen_emulation(text, identifier)
  declared = {name for declaration in arrays for name in declaration["names"]}
  for source in dict.fromkeys(entry[3] for qualifier in ("global", "local") for entry in emulation[qualifier]):
    if source not in declared:
      raise ValueError(f"the array {source} of the @emulate \"{identifier}\" is defined in no file")
  known = dict(defines(text))
  parts = [f"#define {name} {value}".rstrip() for name, value in defines(text)]
  for origin in dict.fromkeys(declaration["origin"] for declaration in arrays if declaration["origin"] is not text):
    for name, value in defines(origin):
      if name not in known:
        known[name] = value
        parts.append(f"#define {name} {value}".rstrip())
      elif known[name] != value:
        raise ValueError(f"the macro {name} has two different values in the files of the @emulate \"{identifier}\"")
  parts += [re.sub(r"\bBuffer\b", BUFFER_TYPE, declaration["text"]) for declaration in arrays]
  parts.append(kernel_code(text, identifier))
  calls = "".join(f"  {call}\n" for call in upload_calls(text, identifier))
  parts.append(f"static void vmegEmulateUpload(void) {{\n{calls}}}")
  return "\n\n".join(parts) + "\n"


INCLUDES = '#include "hw-trace.h"\n#include <me-core-mapper/vme-lib.h>\n#include <me-core-mapper/vme-fu-opcodes.h>\n'


def host_main(text, identifier):
  kernel = chosen_emulation(text, identifier)["kernel"]
  return f"int main() {{\n  vmeLibEnable();\n  vmeLibWipe();\n  vmegEmulateUpload();\n  {kernel}();\n  vmeLibDisable();\n  return 0;\n}}\n"


def host_program(text, identifier, others=()):
  return INCLUDES + "\n" + host_source(text, identifier, others) + "\n" + host_main(text, identifier)
