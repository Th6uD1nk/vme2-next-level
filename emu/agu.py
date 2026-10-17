from emu.fu import signed32
from emu.memory import BASE_OFFSET, BUFFER_WORDS, TOP_OFFSET
from emu.registers import agu_view, routing_view


def mode4_offsets(view):
  return [view["offset"] + i * view["step"] for i in range(view["elements"])]


AGU_MODES = {4: mode4_offsets}


def write_agu(registers, pe):
  driver = routing_view(registers, "write")[pe]
  if driver > 3:
    raise ValueError(f"the write routing {driver} of the output of pe{pe} is not modeled")
  view = agu_view(registers, driver, "write")
  return (driver, view) if view["enabled"] else None


def run_length(registers):
  length = 0
  for pe in range(4):
    found = write_agu(registers, pe)
    if found is not None:
      length = max(length, found[1]["cyc"] + found[1]["elements"])
  return length


def agu_inside_offsets(view, label, buffer, verb):
  if view["mode"] not in AGU_MODES:
    raise ValueError(f"the mode {view['mode']} of {label} is not modeled (modeled: {', '.join(str(mode) for mode in AGU_MODES)})")
  offsets = AGU_MODES[view["mode"]](view)
  for inside in offsets:
    if not 0 <= inside < BUFFER_WORDS:
      raise ValueError(f"{label} {verb} the word {inside} of {buffer}, outside the buffer, the circular mode is not modeled")
  return offsets


def stream_offsets(registers, kind, buffer):
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
  first = (TOP_OFFSET if kind == "top" else BASE_OFFSET) + buffer * BUFFER_WORDS
  return [first + inside for inside in agu_inside_offsets(view, f"the {kind} AGU of pe{driver}", f"{kind}{buffer}", "reads")]


def stream_at(emulator, kind, buffer, cycle, cache):
  if cycle < 0:
    raise ValueError(f"cycle {cycle} is before the start of the run")
  key = (kind, buffer)
  if key not in cache:
    cache[key] = emulator.read_stream(kind, buffer)
  stream = cache[key]
  if stream is None or cycle >= len(stream):
    return 0
  return signed32(stream[cycle])
