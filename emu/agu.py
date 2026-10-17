from emu.fu import signed32
from emu.memory import BASE_OFFSET, BUFFER_WORDS, TOP_OFFSET
from emu.registers import RING_TOKEN, agu_view, routing_view


def mode4_offsets(view):
  return [view["offset"] + i * view["step"] for i in range(view["elements"])]


AGU_MODES = {4: mode4_offsets}


def write_agu(registers, pe):
  driver = routing_view(registers, "write")[pe]
  if driver > 3:
    raise ValueError(f"the write routing {driver} of the output of pe{pe} is not modeled")
  view = agu_view(registers, driver, "write")
  if not view["enabled"]:
    return None
  if view["format0"] >> 16 or view["format1"]:
    raise ValueError(f"the formats {view['format0']:#x}, {view['format1']:#x} of the write AGU of pe{driver} are not modeled (modeled: only the 16 low bits of the first, the bubbles, and 0 for the second, the sync is not modeled)")
  view["start"] = view["cyc"] + view["format0"]
  return driver, view


def run_length(registers):
  length = 0
  for pe in range(4):
    found = write_agu(registers, pe)
    if found is not None:
      length = max(length, found[1]["start"] + found[1]["elements"])
  return length


def agu_inside_offsets(view, label, buffer, verb):
  if view["mode"] not in AGU_MODES:
    raise ValueError(f"the mode {view['mode']} of {label} is not modeled (modeled: {', '.join(str(mode) for mode in AGU_MODES)})")
  offsets = AGU_MODES[view["mode"]](view)
  for inside in offsets:
    if not 0 <= inside < BUFFER_WORDS:
      raise ValueError(f"{label} {verb} the word {inside} of {buffer}, outside the buffer, the circular mode is not modeled")
  return offsets


def read_view(registers, kind, buffer):
  if kind not in ("top", "base"):
    raise ValueError(f"unknown read agu '{kind}' (top, base)")
  if not 0 <= buffer <= 3:
    raise ValueError(f"{kind}{buffer}: buffer out of range ({kind}0 to {kind}3)")
  driver = routing_view(registers, kind)[buffer]
  if driver == "clear":
    return None
  view = agu_view(registers, driver, kind)
  if not view["enabled"]:
    raise ValueError(f"the {kind} AGU of pe{driver}, that drives {kind}{buffer}, is not enabled")
  label = f"the {kind} AGU of pe{driver}"
  if view["format0"] not in (0, RING_TOKEN) or view["format1"]:
    raise ValueError(f"the formats {view['format0']:#x}, {view['format1']:#x} of {label} are not modeled (modeled: 0 and {RING_TOKEN:#x} for the first, 0 for the second)")
  return label, view


def ring_offsets(view):
  count, step = view["inner0"] >> 16, view["inner0"] & 0xffff
  return [view["offset"] + i * step for i in range(count + 1)]


def stream_ring(registers, kind, buffer):
  found = read_view(registers, kind, buffer)
  return found is not None and found[1]["format0"] == RING_TOKEN


def stream_offsets(registers, kind, buffer):
  found = read_view(registers, kind, buffer)
  if found is None:
    return None
  label, view = found
  group = TOP_OFFSET if kind == "top" else BASE_OFFSET
  first = group + buffer * BUFFER_WORDS
  if view["format0"] == RING_TOKEN:
    offsets = ring_offsets(view)
  elif view["mode"] in AGU_MODES:
    offsets = AGU_MODES[view["mode"]](view)
  else:
    raise ValueError(f"the mode {view['mode']} of {label} is not modeled (modeled: {', '.join(str(mode) for mode in AGU_MODES)})")
  for inside in offsets:
    if inside >= BUFFER_WORDS:
      raise ValueError(f"{label} reads the word {inside} of {kind}{buffer}, outside the buffer, the circular mode is not modeled")
  return [first + inside if first + inside >= group else None for inside in offsets]


def stream_at(emulator, kind, buffer, cycle, cache):
  if cycle < 0:
    raise ValueError(f"cycle {cycle} is before the start of the run")
  key = (kind, buffer)
  if key not in cache:
    cache[key] = (emulator.read_stream(kind, buffer), stream_ring(emulator.active, kind, buffer))
  stream, ring = cache[key]
  if stream is None:
    return 0
  if ring:
    return signed32(stream[cycle % len(stream)])
  if cycle >= len(stream):
    return 0
  return signed32(stream[cycle])
