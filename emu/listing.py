import re

from emu.memory import BUFFER_WORDS
from vmeg.blocks import decorator_names, find_blocks, kernel_name
from vmeg.host import file_buffer_names, function_buffer_names
from vmeg.kernel import kernel_loads
from vmeg.parser import kernel_statements
from vmeg.scanner import tokens

NAME = re.compile(r"(?<!\w)[A-Za-z_]\w*")
DEFINE = re.compile(r"#\s*define\s+([A-Za-z_]\w*(?:\([^)]*\))?)(.*)", re.S)
COMMENTS = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)


def defines(text):
  found = []
  for kind, value, _, _ in tokens(text):
    if kind != "pp":
      continue
    m = DEFINE.match(value)
    if m:
      found.append((m.group(1), " ".join(COMMENTS.sub(" ", m.group(2).replace("\\\n", " ")).split())))
  return found


def declared_names(text, blocks, kernel):
  local = set()
  for block in blocks:
    if block[0] == "decorator" and kernel in decorator_names(text, block):
      local |= function_buffer_names(text, block)
  return {"global": file_buffer_names(list(tokens(text))), "local": local}


def load_links(loads, scope):
  return [(*link[:4], load["line"], link[4]) for load in loads if load["scope"] == scope for link in load["links"]]


def emulations(text):
  blocks = find_blocks(text)
  found = []
  for k, block in enumerate(blocks):
    if block[0] != "emulate":
      continue
    kernel = blocks[k + 1]
    statements = kernel_statements(text, kernel, {})
    loads = kernel_loads(statements)
    found.append({
      "id": list(tokens(text[block[1]:block[2]]))[2][1][1:-1],
      "kernel": kernel_name(text, kernel),
      "first": text.count("\n", 0, kernel[1]) + 1,
      "last": text.count("\n", 0, kernel[3] - 1) + 1,
      "global": load_links(loads, "global"),
      "local": load_links(loads, "local"),
      "calls": [line for load in loads for line in load["lines"]],
      "declared": declared_names(text, blocks, kernel_name(text, kernel)),
    })
  return found


def number(text, definitions):
  value = dict(definitions).get(text, text) if text else "0"
  try:
    return int(value.strip().strip("()").strip(), 0)
  except ValueError:
    return None


def overlap_notes(emulation, definitions):
  notes = {}
  placed = []
  for qualifier in ("global", "local"):
    for index, (buffer, count, offset, _, _, _) in enumerate(emulation[qualifier]):
      start = number(offset, definitions)
      if start is None:
        continue
      end = start + count - 1
      hits = [(other, written, max(start, first), min(end, last)) for other, written, first, last in placed if other == buffer and max(start, first) <= min(end, last)]
      if hits:
        notes.setdefault((qualifier, index), []).append(", ".join(f"overlaps {other} at {written or 0} (words {low}-{high})" for other, written, low, high in hits))
      placed.append((buffer, offset, start, end))
  return notes


def link_notes(emulation, definitions):
  notes = overlap_notes(emulation, definitions)
  known = {name.split("(")[0] for name, _ in definitions}
  for qualifier in ("global", "local"):
    for index, (_, count, offset, source, _, _) in enumerate(emulation[qualifier]):
      if source not in emulation["declared"][qualifier]:
        notes.setdefault((qualifier, index), []).append(f"'{source}' is not declared with Buffer")
      start = number(offset, definitions)
      if start is not None and start + count > BUFFER_WORDS:
        notes.setdefault((qualifier, index), []).append(f"goes past the end of the buffer ({hex(BUFFER_WORDS)} words)")
      for name in dict.fromkeys(NAME.findall(offset)):
        if name not in known:
          notes.setdefault((qualifier, index), []).append(f"'{name}' has no #define in this file")
  return notes


def marked(line, notes, key):
  return f"{line}  <-- {'; '.join(notes[key])}" if key in notes else line


def buffer_lines(entries, notes, qualifier):
  lines = []
  for index, (target, count, offset, source, _, extended) in enumerate(entries):
    place = f"at {offset}  " if offset else ""
    line = f"    {target:<8}{count} words{' extended' if extended else ''}  {place}from {source}"
    lines.append(marked(line, notes, (qualifier, index)))
  return lines


BUFFERS = [f"{kind}_{n}" for kind in ("TOP", "BASE") for n in range(4)]


def full_lines(emulation, notes):
  lines = []
  for buffer in BUFFERS:
    links = [(qualifier, index, entry) for qualifier in ("global", "local") for index, entry in enumerate(emulation[qualifier]) if entry[0] == buffer]
    if not links:
      lines.append(f"  {buffer:<8}not linked")
    for qualifier, index, (_, count, offset, source, _, extended) in links:
      line = f"  {buffer:<8}{qualifier:<8}at {offset or 0}  {count} words{' extended' if extended else ''}  from {source}"
      lines.append(marked(line, notes, (qualifier, index)))
  return lines


def format_listing(found, definitions, full=False):
  lines = []
  for emulation in found:
    notes = link_notes(emulation, definitions)
    lines.append(f"emulate \"{emulation['id']}\": kernel {emulation['kernel']} (lines {emulation['first']}-{emulation['last']})")
    if full:
      lines += full_lines(emulation, notes)
      continue
    for qualifier in ("global", "local"):
      entries = emulation[qualifier]
      lines.append(f"  {qualifier} buffers:" if entries else f"  {qualifier} buffers: none")
      lines += buffer_lines(entries, notes, qualifier)
  lines += ["", "defines of the file:"]
  lines += [f"  {name}  {value}" if value else f"  {name}" for name, value in definitions]
  return "\n".join(lines) + "\n"
