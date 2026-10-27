import re

from vmee.memory import BUFFER_WORDS
from vmeg.blocks import decorator_names, find_blocks, header_words, kernel_name
from vmeg.host import file_buffer_names, function_buffer_names
from vmeg.kernel import kernel_transfers
from vmeg.macros import evaluate, known_macros, macro_events
from vmeg.parser import kernel_statements
from vmeg.scanner import tokens

NAME = re.compile(r"(?<!\w)[A-Za-z_]\w*")


def defines(text):
  return [(event["name"] + (event["params"] or ""), event["body"]) for event in macro_events(text) if event["kind"] == "define"]


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
    loads, stores = kernel_transfers(statements, known_macros(text, kernel[1]), kernel_name(text, kernel))
    found.append({
      "id": list(tokens(text[block[1]:block[2]]))[2][1][1:-1],
      "kernel": kernel_name(text, kernel),
      "mode": next((word for word in header_words(text, kernel)[2:] if word in ("direct", "memory")), None),
      "first": text.count("\n", 0, kernel[1]) + 1,
      "last": text.count("\n", 0, kernel[3] - 1) + 1,
      "global": load_links(loads, "global"),
      "local": load_links(loads, "local"),
      "definitions": list(dict.fromkeys(record["definition"] for record in loads + stores)),
      "calls": [call for load in loads for call in load["calls"]],
      "stores": {"global": load_links(stores, "global"), "local": load_links(stores, "local")},
      "downloads": [call for store in stores for call in store["calls"]],
      "declared": declared_names(text, blocks, kernel_name(text, kernel)),
    })
  return found


def number(text):
  return evaluate(text or "0", lambda name: None)


def words(count):
  return count if isinstance(count, int) else number(count)


def overlap_notes(emulation):
  notes = {}
  placed = []
  for qualifier in ("global", "local"):
    for index, (buffer, count, offset, _, _, extended) in enumerate(emulation[qualifier]):
      start = number(offset)
      size = words(count)
      if start is None or size is None or extended:
        continue
      end = start + size - 1
      hits = [(other, written, max(start, first), min(end, last)) for other, written, first, last in placed if other == buffer and max(start, first) <= min(end, last)]
      if hits:
        notes.setdefault((qualifier, index), []).append(", ".join(f"overlaps {other} at {written or 0} (words {low}-{high})" for other, written, low, high in hits))
      placed.append((buffer, offset, start, end))
  return notes


def link_notes(emulation, definitions, overlaps=True):
  notes = overlap_notes(emulation) if overlaps else {}
  known = {name.split("(")[0] for name, _ in definitions}
  for qualifier in ("global", "local"):
    for index, (_, count, offset, source, _, extended) in enumerate(emulation[qualifier]):
      if source not in emulation["declared"][qualifier]:
        notes.setdefault((qualifier, index), []).append(f"'{source}' is not declared with Buffer")
      start = number(offset)
      size = words(count)
      if start is not None and size is not None and not extended and start + size > BUFFER_WORDS:
        notes.setdefault((qualifier, index), []).append(f"goes past the end of the buffer ({hex(BUFFER_WORDS)} words)")
      for name in dict.fromkeys(NAME.findall(offset)):
        if name not in known:
          notes.setdefault((qualifier, index), []).append(f"'{name}' has no #define in this file")
  return notes


def marked(line, notes, key):
  return f"{line}  <-- {'; '.join(notes[key])}" if key in notes else line


def buffer_lines(entries, notes, qualifier, way="from"):
  lines = []
  for index, (target, count, offset, source, _, extended) in enumerate(entries):
    place = f"at {offset}  " if offset else ""
    line = f"    {target:<8}{count} words{' extended' if extended else ''}  {place}{way} {source}"
    lines.append(marked(line, notes, (qualifier, index)))
  return lines


BUFFERS = [f"{kind}_{n}" for kind in ("TOP", "BASE") for n in range(4)]


def full_lines(emulation, notes, way="from", empty=True):
  lines = []
  for buffer in BUFFERS:
    links = [(qualifier, index, entry) for qualifier in ("global", "local") for index, entry in enumerate(emulation[qualifier]) if entry[0] == buffer]
    if not links and empty:
      lines.append(f"  {buffer:<8}not linked")
    for qualifier, index, (_, count, offset, source, _, extended) in links:
      line = f"  {buffer:<8}{qualifier:<8}at {offset or 0}  {count} words{' extended' if extended else ''}  {way} {source}"
      lines.append(marked(line, notes, (qualifier, index)))
  return lines


def format_listing(found, definitions, full=False):
  lines = []
  for emulation in found:
    notes = link_notes(emulation, definitions)
    stored = dict(emulation["stores"], declared=emulation["declared"])
    store_notes = link_notes(stored, definitions, overlaps=False)
    has_stores = bool(stored["global"] or stored["local"])
    mode = f"{emulation['mode']}, " if emulation.get("mode") else ""
    lines.append(f"emulate \"{emulation['id']}\": kernel {emulation['kernel']} ({mode}lines {emulation['first']}-{emulation['last']})")
    if full:
      lines += full_lines(emulation, notes)
      if has_stores:
        lines.append("  stores:")
        lines += full_lines(stored, store_notes, "to", False)
      continue
    for qualifier in ("global", "local"):
      entries = emulation[qualifier]
      lines.append(f"  {qualifier} loads:" if entries else f"  {qualifier} loads: none")
      lines += buffer_lines(entries, notes, qualifier)
    for qualifier in ("global", "local"):
      if stored[qualifier]:
        lines.append(f"  {qualifier} stores:")
        lines += buffer_lines(stored[qualifier], store_notes, qualifier, "to")
  lines += ["", "defines of the file:"]
  lines += [f"  {name}  {value}" if value else f"  {name}" for name, value in definitions]
  return "\n".join(lines) + "\n"
