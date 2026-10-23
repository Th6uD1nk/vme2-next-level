from emu.extract import declared_parts


def extract_source(text, identifier, others=()):
  arrays, macros = declared_parts(text, identifier, others)
  sections = []
  if macros:
    sections.append("\n".join(macros))
  globals_ = [declaration["text"] for declaration in arrays if declaration["where"] == "global"]
  if globals_:
    sections.append("\n\n".join(globals_))
  return "\n\n".join(sections) + "\n"
