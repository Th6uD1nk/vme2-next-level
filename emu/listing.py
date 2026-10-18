import re

from vmeg.blocks import decorator_names, find_blocks, kernel_name
from vmeg.expr import to_c
from vmeg.host import file_buffer_names, function_buffer_names
from vmeg.parser import kernel_statements
from vmeg.scanner import tokens

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


def buffer_entries(statements, qualifier):
  entries = []
  for statement in statements:
    if statement[0] == "buffers" and statement[1] == qualifier:
      entries += [(target, count, "" if offset is None else to_c(offset), source, line) for target, count, offset, source, line in statement[2]]
  return entries


def declared_names(text, blocks, kernel):
  local = set()
  for block in blocks:
    if block[0] == "decorator" and kernel in decorator_names(text, block):
      local |= function_buffer_names(text, block)
  return {"global": file_buffer_names(list(tokens(text))), "local": local}


def emulations(text):
  blocks = find_blocks(text)
  found = []
  for k, block in enumerate(blocks):
    if block[0] != "emulate":
      continue
    kernel = blocks[k + 1]
    statements = kernel_statements(text, kernel, {})
    found.append({
      "id": list(tokens(text[block[1]:block[2]]))[2][1][1:-1],
      "kernel": kernel_name(text, kernel),
      "first": text.count("\n", 0, kernel[1]) + 1,
      "last": text.count("\n", 0, kernel[3] - 1) + 1,
      "global": buffer_entries(statements, "global"),
      "local": buffer_entries(statements, "local"),
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
    for index, (buffer, count, offset, _, _) in enumerate(emulation[qualifier]):
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
  for qualifier in ("global", "local"):
    for index, (_, _, _, source, _) in enumerate(emulation[qualifier]):
      if source not in emulation["declared"][qualifier]:
        notes.setdefault((qualifier, index), []).append(f"'{source}' is not declared with Buffer")
  return notes


def marked(line, notes, key):
  return f"{line}  <-- {'; '.join(notes[key])}" if key in notes else line


def buffer_lines(entries, notes, qualifier):
  lines = []
  for index, (target, count, offset, source, _) in enumerate(entries):
    place = f"at {offset}  " if offset else ""
    line = f"    {target:<8}{count} words  {place}from {source}"
    lines.append(marked(line, notes, (qualifier, index)))
  return lines


BUFFERS = [f"{kind}_{n}" for kind in ("TOP", "BASE") for n in range(4)]


def full_lines(emulation, notes):
  lines = []
  for buffer in BUFFERS:
    links = [(qualifier, index, entry) for qualifier in ("global", "local") for index, entry in enumerate(emulation[qualifier]) if entry[0] == buffer]
    if not links:
      lines.append(f"  {buffer:<8}not linked")
    for qualifier, index, (_, count, offset, source, _) in links:
      line = f"  {buffer:<8}{qualifier:<8}at {offset or 0}  {count} words  from {source}"
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
