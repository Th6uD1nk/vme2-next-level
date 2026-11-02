import re

from vmee.listing import defines, emulations
from vmeg.blocks import decorator_names, find_blocks, kernel_name
from vmeg.host import BUFFER_TYPE, enclosing_function_tokens, function_tokens, kernel_lines, memory_edits
from vmeg.kernel import generate
from vmeg.qformat import translate_buffer
from vmeg.registry import declarations, project_registry, split_declarators
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


def other_declaration(others, source, pointers=False):
  for other in others:
    for declaration in declarations(other, list(tokens(other)), 0, "Buffer", pointers):
      if source in declaration["names"] and not declaration["extern"] and not declaration["static"]:
        return dict(declaration, origin=other)
  return None


def array_declarations(text, identifier, others=(), uses=(), pointers=False, also=()):
  emulation = chosen_emulation(text, identifier)
  blocks = find_blocks(text)
  available = {"global": declarations(text, list(tokens(text)), 0, "Buffer", pointers), "local": []}
  for file in (text, *others):
    for block in (blocks if file is text else find_blocks(file)):
      if block[0] == "decorator" and any(name in decorator_names(file, block) for name in emulation["kernels"]):
        available["local"] += [dict(declaration, origin=file) for declaration in declarations(file, function_tokens(file, block), 1, "Buffer", pointers)]
  if emulation["form"] == "block":
    available["local"] += [dict(declaration, origin=text) for declaration in declarations(text, enclosing_function_tokens(text, emulation["at"]), 1, "Buffer", pointers)]
  result = []
  seen = set()
  for qualifier in ("global", "local"):
    for source in dict.fromkeys([entry[3] for entry in emulation[qualifier] + emulation["stores"][qualifier]] + [used for _, used in uses] + list(also)):
      found = next((declaration for declaration in available[qualifier] if source in declaration["names"]), None)
      if qualifier == "global" and (found is None or found["extern"]):
        found = other_declaration(others, source, pointers) or found
      if found is None:
        continue
      key = (qualifier, found["line"], found["text"])
      if key not in seen:
        seen.add(key)
        result.append(dict(found, where=qualifier, origin=found.get("origin", text)))
  return result


def pointer_target(declaration, name):
  _, declarators = split_declarators(declaration["text"])
  for declarator in declarators:
    names = [value for kind, value, _, _ in declarator if kind == "ident" and value not in ("const", "volatile", "restrict")]
    if declarator and names and names[0] == name:
      for at, (kind, value, _, _) in enumerate(declarator):
        if kind == "punct" and value == "=":
          rest = declarator[at + 1:]
          return rest[0][1] if len(rest) == 1 and rest[0][0] == "ident" else None
  return None


def pointer_bindings(text, identifier, others=(), uses=()):
  found = array_declarations(text, identifier, others, (), True)
  used = dict(uses)
  bindings = {}
  for declaration in found:
    for name in declaration["names"]:
      bindings[name] = used.get(name) or pointer_target(declaration, name)
  return found, bindings


def memory_declarations(text, identifier):
  emulation = chosen_emulation(text, identifier)
  available = [dict(declaration, where="global") for declaration in declarations(text, list(tokens(text)), 0, "Memory")]
  if emulation["form"] == "block":
    available += [dict(declaration, where="local") for declaration in declarations(text, enclosing_function_tokens(text, emulation["at"]), 1, "Memory")]
  found = []
  for value in dict.fromkeys(memory for memory in emulation["memories"] if memory):
    name = re.search(r"[A-Za-z_]\w*", value).group()
    declaration = next((declaration for declaration in available if name in declaration["names"]), None)
    if declaration is None:
      raise ValueError(f"the Memory {name} of the @emulate \"{identifier}\" is defined in no file")
    if declaration not in found:
      found.append(declaration)
  return found


def memory_text(declaration):
  text = declaration["text"]
  edits = sorted(memory_edits(text, list(tokens(text))), reverse=True)
  for start, length, replacement in edits:
    text = text[:start] + replacement + text[start + length:]
  return text


def declared_parts(text, identifier, others=(), uses=()):
  _, bindings = pointer_bindings(text, identifier, others, uses)
  arrays = array_declarations(text, identifier, others, [pair for pair in uses if pair[0] not in bindings], False, [target for target in bindings.values() if target])
  for declaration in arrays:
    if declaration["extern"]:
      raise ValueError(f"the array {', '.join(declaration['names'])} of the @emulate \"{identifier}\" is declared extern and no file defines it")
  emulation = chosen_emulation(text, identifier)
  declared = {name for declaration in arrays for name in declaration["names"]}
  for source in dict.fromkeys(entry[3] for qualifier in ("global", "local") for entry in emulation[qualifier] + emulation["stores"][qualifier]):
    if source not in declared and source not in bindings:
      raise ValueError(f"the array {source} of the @emulate \"{identifier}\" is defined in no file")
  read = {entry[3] for qualifier in ("global", "local") for entry in emulation[qualifier] + emulation["stores"][qualifier]}
  for replaced, used in uses:
    if replaced not in read:
      raise ValueError(f"--use {replaced}={used}: the array {replaced} is not read or written by the @emulate \"{identifier}\"")
    if used not in declared:
      raise ValueError(f"--use {replaced}={used}: the array {used} is defined in no file")
    if replaced in bindings:
      continue
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


def buffer_text(declaration):
  try:
    return translate_buffer(declaration["text"], BUFFER_TYPE)
  except ValueError as e:
    raise ValueError(f"line {declaration['line']}: {e}") from None


def host_source(text, identifier, others=(), compat=None, uses=()):
  arrays, parts = declared_parts(text, identifier, others, uses)
  _, bindings = pointer_bindings(text, identifier, others, uses)
  uses = [pair for pair in uses if pair[0] not in bindings]
  emulation = chosen_emulation(text, identifier)
  declared = {name for declaration in arrays for name in declaration["names"]}
  parts += [buffer_text(declaration) for declaration in arrays]
  parts += [f"volatile u32* {name};" for name in sorted(bindings)]
  parts.append("static void vmegBindPointers(void) {\n" + "".join(f"  {name} = {target};\n" for name, target in sorted(bindings.items()) if target) + "}")
  parts += [f'static_assert(sizeof({replaced}) == sizeof({used}), "--use {replaced}={used}: the two arrays must have the same size");' for replaced, used in uses]
  parts += [memory_text(declaration) for declaration in memory_declarations(text, identifier)]
  entries = ", ".join(f'{{"{name}", (u32*){name}, (u32)(sizeof({name}) / 4)}}' for name in sorted(declared))
  parts.append(
    "static void vmegLoadArrays(const char* path) {\n"
    + (
      f"  static const struct {{ const char* name; u32* data; u32 words; }} arrays[] = {{ {entries} }};\n"
      "  std::ifstream file(path);\n"
      "  std::string line;\n"
      "  while (std::getline(file, line)) {\n"
      "    std::istringstream words(line);\n"
      "    std::string name;\n"
      "    words >> name;\n"
      "    for (unsigned i = 0; i < sizeof(arrays) / sizeof(arrays[0]); i++) {\n"
      "      std::string token;\n"
      "      for (u32 k = 0; name == arrays[i].name && k < arrays[i].words && (words >> token); k++) {\n"
      "        if (token != \"-\") {\n"
      "          arrays[i].data[k] = (u32)strtoul(token.c_str(), 0, 16);\n"
      "        }\n"
      "      }\n"
      "    }\n"
      "  }\n" if declared else ""
    )
    + "}"
  )
  fixed = "".join(f"  fprintf(hwTraceFile(), \"# array {name} 0x%x %u\\n\", emuFixArray((void*){name}, sizeof({name}) / 4), (unsigned)(sizeof({name}) / 4));\n" for name in sorted(declared))
  parts.append(f"static void vmegFixArrays(void) {{\n{fixed}}}")
  if declared:
    redirected = dict(uses)
    entries = ", ".join(f"{{(u32){name}, (u32){redirected.get(name, name)}, sizeof({redirected.get(name, name)}) / 4}}" for name in sorted(declared))
    parts.append(
      "#undef useg_mem\n"
      "static u32 vmegUsegMem(u32 pointer) {\n"
      f"  static const struct {{ u32 pointer; u32 target; u32 words; }} arrays[] = {{ {entries} }};\n"
      "  for (unsigned i = 0; i < sizeof(arrays) / sizeof(arrays[0]); i++) {\n"
      "    if (arrays[i].pointer == pointer) {\n"
      "      return emuUsegMem((void*)arrays[i].target, arrays[i].words);\n"
      "    }\n"
      "  }\n"
      "  return pointer;\n"
      "}\n"
      "#define useg_mem(v) vmegUsegMem((u32)(v))"
    )
  parts.append(kernel_code(text, identifier, compat))
  if emulation["definitions"]:
    parts.append("\n".join(emulation["definitions"]))
  return finish_calls("\n\n".join(parts) + "\n")


INCLUDES = '#include <cstdlib>\n#include <fstream>\n#include <sstream>\n#include <string>\n#include "hw-trace.h"\n#include "me-core-mapper.h"\n#include <me-core-mapper/vme-lib.h>\n#include <me-core-mapper/vme-fu-opcodes.h>\n'


def host_main(text, identifier):
  emulation = chosen_emulation(text, identifier)
  registry = project_registry([("", text)])
  steps = list(zip(emulation["steps"], emulation["pairs"], emulation["memories"], emulation["after"]))
  blocks = "".join(
    f"  if (all || step >= {index}) {{\n    hwTraceMuted() = step > {index};\n" + "".join(f"    {call}\n" for call in kernel_lines(registry, name, actions, pairs, memory) + written) + "  }\n"
    for index, ((name, actions), pairs, memory, written) in enumerate(steps)
  )
  return finish_calls(
    "int main(int argc, char** argv) {\n"
    "  const int step = argc > 1 ? atoi(argv[1]) : -1;\n"
    "  const bool all = step < 0;\n"
    "  vmegFixArrays();\n"
    "  vmegBindPointers();\n"
    "  if (argc > 2) {\n    vmegLoadArrays(argv[2]);\n  }\n"
    "  hwTraceMuted() = step > 0;\n"
    "  vmeLibEnable();\n  vmeLibWipe();\n"
    f"{blocks}"
    f"  if (all || step == {len(steps) - 1}) {{\n    vmeLibDisable();\n  }}\n"
    "  return 0;\n}\n"
  )


def host_program(text, identifier, others=(), compat=None, uses=()):
  return INCLUDES + "\n" + host_source(text, identifier, others, compat, uses) + "\n" + host_main(text, identifier)
