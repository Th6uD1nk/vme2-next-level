from emu.extract import chosen_emulation, declared_parts
from vmeg.blocks import find_blocks, kernel_name


def kernel_text(text, identifier):
  name = chosen_emulation(text, identifier)["kernel"]
  for block in find_blocks(text):
    if block[0] == "kernel" and kernel_name(text, block) == name:
      return text[block[1]:block[3]]


def extract_source(text, identifier, others=()):
  arrays, macros = declared_parts(text, identifier, others)
  sections = []
  if macros:
    sections.append("\n".join(macros))
  globals_ = [declaration["text"] for declaration in arrays if declaration["where"] == "global"]
  if globals_:
    sections.append("\n\n".join(globals_))
  sections.append(kernel_text(text, identifier))
  return "\n\n".join(sections) + "\n"
