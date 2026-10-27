import re

from vmee.listing import defines, emulations
from vmeg.blocks import decorator_names, find_blocks, kernel_name
from vmeg.host import BUFFER_TYPE, function_tokens, kernel_actions, kernel_arguments
from vmeg.kernel import generate
from vmeg.registry import declarations, project_registry
from vmeg.scanner import tokens
from vmeg.vmecalls import finish_calls


def chosen_emulation(text, identifier):
  found = emulations(text)
  chosen = [emulation for emulation in found if emulation["id"] == identifier]
  if not chosen:
    known = ", ".join(emulation["id"] for emulation in found)
    raise ValueError(f"no @emulate with the id '{identifier}' ({known if known else 'there is no @emulate in this file'})")
  return chosen[0]


def kernel_code(text, identifier, compat=None):
  emulation = chosen_emulation(text, identifier)
  blocks = find_blocks(text)
  return "\n\n".join(generate(text, block, None, compat) for name in emulation["kernels"] for block in blocks if block[0] == "kernel" and kernel_name(text, block) == name)


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
      if block[0] == "decorator" and any(name in decorator_names(file, block) for name in emulation["kernels"]):
        available["local"] += [dict(declaration, origin=file) for declaration in declarations(file, function_tokens(file, block), 1)]
  result = []
  seen = set()
  for qualifier in ("global", "local"):
    for source in dict.fromkeys(entry[3] for entry in emulation[qualifier] + emulation["stores"][qualifier]):
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
  return emulation["calls"]


def declared_parts(text, identifier, others=()):
  arrays = array_declarations(text, identifier, others)
  for declaration in arrays:
    if declaration["extern"]:
      raise ValueError(f"the array {', '.join(declaration['names'])} of the @emulate \"{identifier}\" is declared extern and no file defines it")
  emulation = chosen_emulation(text, identifier)
  declared = {name for declaration in arrays for name in declaration["names"]}
  for source in dict.fromkeys(entry[3] for qualifier in ("global", "local") for entry in emulation[qualifier] + emulation["stores"][qualifier]):
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
  return arrays, parts


def host_source(text, identifier, others=(), compat=None):
  arrays, parts = declared_parts(text, identifier, others)
  emulation = chosen_emulation(text, identifier)
  declared = {name for declaration in arrays for name in declaration["names"]}
  parts += [re.sub(r"\bBuffer\b", BUFFER_TYPE, declaration["text"]) for declaration in arrays]
  if declared:
    entries = ", ".join(f"{{(u32){name}, sizeof({name}) / 4}}" for name in sorted(declared))
    parts.append(
      "#undef useg_mem\n"
      "static u32 vmegUsegMem(u32 pointer) {\n"
      f"  static const struct {{ u32 pointer; u32 words; }} arrays[] = {{ {entries} }};\n"
      "  for (unsigned i = 0; i < sizeof(arrays) / sizeof(arrays[0]); i++) {\n"
      "    if (arrays[i].pointer == pointer) {\n"
      "      return emuUsegMem((void*)pointer, arrays[i].words);\n"
      "    }\n"
      "  }\n"
      "  return pointer;\n"
      "}\n"
      "#define useg_mem(v) vmegUsegMem((u32)(v))"
    )
  parts.append(kernel_code(text, identifier, compat))
  if emulation["definitions"]:
    parts.append("\n".join(emulation["definitions"]))
  calls = "".join(f"  {call}\n" for call in upload_calls(text, identifier))
  parts.append(f"static void vmegEmulateUpload(void) {{\n{calls}}}")
  downloads = "".join(f"  {call}\n" for call in emulation["downloads"])
  parts.append(f"static void vmegEmulateDownload(void) {{\n{downloads}}}")
  return finish_calls("\n\n".join(parts) + "\n")


INCLUDES = '#include "hw-trace.h"\n#include "me-core-mapper.h"\n#include <me-core-mapper/vme-lib.h>\n#include <me-core-mapper/vme-fu-opcodes.h>\n'


def host_main(text, identifier):
  emulation = chosen_emulation(text, identifier)
  registry = project_registry([("", text)])
  actions = "".join(f"  {call}\n" for (name, steps), pairs in zip(emulation["steps"], emulation["pairs"]) for call in kernel_actions(name, steps, emulation["modes"][name], False, kernel_arguments(registry, name, pairs)))
  return f"int main() {{\n  vmeLibEnable();\n  vmeLibWipe();\n  vmegEmulateUpload();\n{actions}  vmegEmulateDownload();\n  vmeLibDisable();\n  return 0;\n}}\n"


def host_program(text, identifier, others=(), compat=None):
  return INCLUDES + "\n" + host_source(text, identifier, others, compat) + "\n" + host_main(text, identifier)
