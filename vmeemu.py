from vmeg.blocks import find_blocks, kernel_name
from vmeg.parser import kernel_statements

SCRATCHPAD_BASE = 0x44000000
DATAPATH_BASE = 0x440f8000
REGISTER_COUNT = 106
CONTEXT_WORDS = 112
DMAC_BASE = 0x440ff000
DMAC_REGISTER_COUNT = 17
PHYSICAL_MASK = 0x1fffffff
DMAC_CONTROL = 2
DMAC_MEMORY_ADDRESS = 4
CONTEXT_TRANSFER_MASK = 0x4c
CONTEXT_TRANSFER_BITS = 0x0c
PRELOAD_CONTEXT = 5
TRIGGER = 0x18
CLEAR_LOCAL_BUFFER = 0x21
MEM_TO_16 = 0x52
MEM_FROM_16 = 0x5a
RING_TO_SCRATCHPAD = 0x40
RING_TO_MEMORY = 0x48
DMAC_COUNT = 5
DMAC_SCRATCHPAD_OFFSET = 6
FU_KINDS = {"primary": 0, "secondary": 4}
FU_OPERAND_REGISTERS = {"primary": 8, "secondary": 16}
MUX_FRONT_SHIFT = 27
MUX_BACK_SHIFT = 22
SWEN_REGISTER = 27
ROUTING_REGISTERS = {"top": 28, "base": 29, "write": 30}
AGU_FIRST_REGISTER = 33
AGU_REGISTERS_PER_PE = 18
AGU_KINDS = {"top": 0, "base": 6, "write": 12}
AGU_FIELDS = {"mode": 0, "count": 1, "inner0": 2, "inner1": 3, "format0": 4, "format1": 5}
STAGING_COUNT = 8
STAGING_WORDS = 2048
STAGING_LAG = 3
BUFFER_WORDS = 0x800
BUFFER_COUNT = 4
BASE_OFFSET = 0
TOP_OFFSET = 0x8000
SPAN = BUFFER_COUNT * BUFFER_WORDS


class Scratchpad:
  def __init__(self):
    self.words = [0] * (2 * SPAN)

  def slot(self, offset):
    if BASE_OFFSET <= offset < BASE_OFFSET + SPAN:
      return offset - BASE_OFFSET
    if TOP_OFFSET <= offset < TOP_OFFSET + SPAN:
      return SPAN + offset - TOP_OFFSET
    raise ValueError(f"scratchpad offset {offset:#x} is outside the base and top buffers")

  def read(self, offset):
    value = self.words[self.slot(offset)]
    return value | 0xff000000 if value & 0x800000 else value

  def write(self, offset, value):
    self.words[self.slot(offset)] = value & 0xffffff

  def offset_of(self, address):
    if address < SCRATCHPAD_BASE or address & 3:
      raise ValueError(f"scratchpad address {address:#x} is not a word address from {SCRATCHPAD_BASE:#x}")
    return (address - SCRATCHPAD_BASE) >> 2

  def read_address(self, address):
    return self.read(self.offset_of(address))

  def write_address(self, address, value):
    self.write(self.offset_of(address), value)

  def transfer(self, offset, values):
    count = len(values)
    if not count:
      return
    first = self.slot(offset)
    if self.slot(offset + count - 1) - first != count - 1:
      raise ValueError(f"a transfer of {count} words at offset {offset:#x} does not fit in the base or top buffers")
    self.words[first:first + count] = [value & 0xffffff for value in values]


def dump_base_buffers(scratchpad, count):
  if count <= 0 or count > BUFFER_WORDS or count % 4:
    raise ValueError(f"the dump needs a number of words that is a multiple of 4, at most {BUFFER_WORDS}, not {count}")
  rows = []
  for n in range(BUFFER_COUNT):
    rows.append(f"Buffer: BASE {n}")
    first = BASE_OFFSET + n * BUFFER_WORDS
    for i in range(0, count, 4):
      rows.append(", ".join(f"0x{scratchpad.read(first + i + k):08x}" for k in range(4)) + ",")
    rows.append("")
  return "\n".join(rows) + "\n"


def load_kernel(text, name=None):
  blocks = find_blocks(text)
  kernels = {kernel_name(text, block): block for block in blocks if block[0] == "kernel"}
  if name is None:
    if len(kernels) != 1:
      known = ", ".join(kernels) if kernels else "there is no kernel in this file"
      raise ValueError(f"give the name of the kernel ({known})")
    name = next(iter(kernels))
  if name not in kernels:
    known = ", ".join(kernels) if kernels else "there is no kernel in this file"
    raise ValueError(f"unknown kernel '{name}' ({known})")
  return kernel_statements(text, kernels[name], {})


class Emulator:
  def __init__(self):
    self.scratchpad = Scratchpad()
    self.registers = [0] * REGISTER_COUNT
    self.dmac = [0] * DMAC_REGISTER_COUNT
    self.active = [0] * REGISTER_COUNT
    self.memory = {}
    self.staging = [[0] * STAGING_WORDS for _ in range(STAGING_COUNT)]
    self.cycles = 0

  def locate(self, address):
    for first, count, registers in ((DATAPATH_BASE, REGISTER_COUNT, self.registers), (DMAC_BASE, DMAC_REGISTER_COUNT, self.dmac)):
      if first <= address < first + 4 * count:
        if address & 3:
          raise ValueError(f"register address {address:#x} is not aligned on 4 bytes")
        return registers, (address - first) >> 2
    if SCRATCHPAD_BASE <= address < DATAPATH_BASE:
      return None
    raise ValueError(f"address {address:#x} is not mapped")

  def read(self, address):
    located = self.locate(address)
    if located is None:
      return self.scratchpad.read_address(address)
    registers, index = located
    return registers[index]

  def write(self, address, value):
    located = self.locate(address)
    if located is None:
      self.scratchpad.write_address(address, value)
    else:
      registers, index = located
      value &= 0xffffffff
      if registers is self.dmac and index == DMAC_CONTROL:
        self.run_control(value)
      registers[index] = value

  def run_control(self, value):
    if value & CONTEXT_TRANSFER_MASK == CONTEXT_TRANSFER_BITS or value == PRELOAD_CONTEXT:
      self.load_context(self.get_memory(self.dmac[DMAC_MEMORY_ADDRESS], CONTEXT_WORDS))
    elif value == CLEAR_LOCAL_BUFFER:
      self.clear_local_buffer()
    elif value == RING_TO_SCRATCHPAD:
      self.ring_to_scratchpad()
    elif value == RING_TO_MEMORY:
      self.ring_to_memory()
    elif value == MEM_TO_16:
      self.mem_to_16()
    elif value == MEM_FROM_16:
      self.mem_from_16()
    elif value == TRIGGER:
      self.trigger()

  def transfer_count(self):
    count = self.dmac[DMAC_COUNT]
    if count >> 16:
      raise ValueError(f"the count register {count:#x} has bits above the 16 low bits, not modeled")
    return count + 1

  def staging_slot(self, index, slot):
    if not 0 <= index < STAGING_COUNT:
      raise ValueError(f"STAGING_{index}: staging out of range (STAGING_0 to STAGING_{STAGING_COUNT - 1})")
    if not 0 <= slot < STAGING_WORDS:
      raise ValueError(f"STAGING_{index}: slot {slot} out of range (0 to {STAGING_WORDS - 1})")
    return self.staging[index]

  def staging_read(self, index, slot):
    value = self.staging_slot(index, slot)[slot]
    return value - 0x1000000 if value & 0x800000 else value

  def staging_write(self, index, slot, value):
    self.staging_slot(index, slot)[slot] = value & 0xffffff

  def simulate_fus(self, cache):
    needed = {}
    pending = [(output_fu(self.active[SWEN_REGISTER], pe), pe) for pe in range(4) if write_agu(self.active, pe) is not None]
    while pending:
      key = pending.pop()
      if key in needed:
        continue
      kind, pe = key
      fu = decode_fu(self.active[fu_register(pe, kind)])
      _, uses = opcode_entry(fu)
      a, b = fu_operands(self.active, pe, kind)
      needed[key] = (fu, uses, a, b)
      for side in uses:
        name, _, number = fu[side].partition("_")
        if name == "STAGING" and number.isdigit() and int(number) < STAGING_COUNT:
          pending.append(("primary", int(number)) if int(number) < 4 else ("secondary", int(number) - 4))

    def operand(source, cycle):
      name, _, number = source.partition("_")
      if name == "STAGING" and number.isdigit() and int(number) < STAGING_COUNT:
        return self.staging_read(int(number), cycle)
      if name in ("TOP", "BASE") and number.isdigit():
        return stream_at(self, name.lower(), int(number), cycle, cache)
      raise ValueError(f"the operand source {source} is not modeled")

    for cycle in range(self.cycles):
      for (kind, pe), (fu, uses, a, b) in needed.items():
        back = operand(fu["back"], cycle) if "back" in uses else 0
        front = operand(fu["front"], cycle) if "front" in uses else 0
        slot = cycle + STAGING_LAG
        if slot >= STAGING_WORDS:
          raise ValueError(f"the run is longer than the staging, the slot {slot} does not exist")
        self.staging_write(pe + FU_KINDS[kind], slot, execute(fu, back, front, a, b))

  def collect_writes(self):
    writes = []
    for pe in range(4):
      found = write_agu(self.active, pe)
      if found is None:
        continue
      driver, view = found
      first = BASE_OFFSET + pe * BUFFER_WORDS
      offsets = agu_inside_offsets(view, f"the write AGU of pe{driver}", f"base{pe}", "writes")
      staging = pe + FU_KINDS[output_fu(self.active[SWEN_REGISTER], pe)]
      for j, inside in enumerate(offsets):
        slot = view["cyc"] + j - STAGING_LAG
        writes.append((first + inside, self.staging_read(staging, slot) if slot >= 0 else 0))
    return writes

  def trigger(self):
    self.active[:] = self.registers
    self.run()

  def run(self):
    self.cycles = run_length(self.active)
    self.simulate_fus({})
    for offset, value in self.collect_writes():
      self.scratchpad.write(offset, value)

  def clear_local_buffer(self):
    self.scratchpad.transfer(self.dmac[DMAC_SCRATCHPAD_OFFSET], [0] * self.transfer_count())

  def ring_to_scratchpad(self):
    words = self.get_memory(self.dmac[DMAC_MEMORY_ADDRESS], self.transfer_count())
    self.scratchpad.transfer(self.dmac[DMAC_SCRATCHPAD_OFFSET], words)

  def ring_to_memory(self):
    offset = self.dmac[DMAC_SCRATCHPAD_OFFSET]
    words = [self.scratchpad.read(offset + i) for i in range(self.transfer_count())]
    self.put_memory(self.dmac[DMAC_MEMORY_ADDRESS], words)

  def mem_to_16(self):
    values = []
    for word in self.get_memory(self.dmac[DMAC_MEMORY_ADDRESS], self.transfer_count()):
      values += [word & 0xffff, word >> 16]
    self.scratchpad.transfer(self.dmac[DMAC_SCRATCHPAD_OFFSET], values)

  def mem_from_16(self):
    offset = self.dmac[DMAC_SCRATCHPAD_OFFSET]
    words = []
    for i in range(self.transfer_count()):
      low = self.scratchpad.read(offset + 2 * i) & 0xffff
      high = self.scratchpad.read(offset + 2 * i + 1) & 0xffff
      words.append(low | high << 16)
    self.put_memory(self.dmac[DMAC_MEMORY_ADDRESS], words)

  def put_memory(self, address, words):
    first = self.memory_address(address)
    for i, word in enumerate(words):
      self.memory[first + 4 * i] = word & 0xffffffff

  def get_memory(self, address, count):
    first = self.memory_address(address)
    words = []
    for i in range(count):
      word = self.memory.get(first + 4 * i)
      if word is None:
        raise ValueError(f"the memory image has no word at {first + 4 * i:#x}")
      words.append(word)
    return words

  def memory_address(self, address):
    if address & 3:
      raise ValueError(f"memory address {address:#x} is not aligned on 4 bytes")
    return address & PHYSICAL_MASK

  def read_stream(self, kind, buffer):
    offsets = stream_offsets(self.active, kind, buffer)
    return None if offsets is None else [self.scratchpad.read(offset) for offset in offsets]

  def load_context(self, words):
    if len(words) != CONTEXT_WORDS:
      raise ValueError(f"a context has {CONTEXT_WORDS} words, not {len(words)}")
    self.registers[:] = [word & 0xffffffff for word in words[:REGISTER_COUNT]]


def hexadecimal(token, line):
  try:
    value = int(token, 16)
  except ValueError:
    raise ValueError(f"line {line}: '{token}' is not a hexadecimal number") from None
  if value < 0:
    raise ValueError(f"line {line}: '{token}' is negative")
  return value


def replay(emulator, text):
  for line, row in enumerate(text.split("\n"), 1):
    row = row.split("#", 1)[0].split()
    if not row:
      continue
    event, args = row[0], [hexadecimal(token, line) for token in row[1:]]
    try:
      if event == "W" and len(args) == 2:
        emulator.write(args[0], args[1])
      elif event == "M" and len(args) >= 1:
        emulator.put_memory(args[0], args[1:])
      elif event in ("W", "M"):
        raise ValueError(f"line {line}: {event} has the wrong number of values")
      else:
        raise ValueError(f"line {line}: unknown event '{event}' (W, M)")
    except ValueError as e:
      if str(e).startswith("line "):
        raise
      raise ValueError(f"line {line}: {e}") from None


def agu_register(pe, agu, field):
  if not 0 <= pe <= 3:
    raise ValueError(f"pe{pe}: processing element out of range (pe0 to pe3)")
  if agu not in AGU_KINDS:
    raise ValueError(f"unknown agu '{agu}' ({', '.join(AGU_KINDS)})")
  if field not in AGU_FIELDS:
    raise ValueError(f"unknown agu register '{field}' ({', '.join(AGU_FIELDS)})")
  return AGU_FIRST_REGISTER + AGU_REGISTERS_PER_PE * pe + AGU_KINDS[agu] + AGU_FIELDS[field]


def decode_count(value):
  return value >> 16, (value & 0xffff) + 1


def decode_mode(value):
  return bool(value >> 31), (value >> 24) & 0xf, value & 0x70ffffff


def decode_offset_cyc(rest):
  offset = rest & 0xffff
  if offset & 0x8000:
    offset -= 0x10000
  return offset, (rest >> 16) & 0xff


def agu_view(registers, pe, agu):
  enabled, mode, rest = decode_mode(registers[agu_register(pe, agu, "mode")])
  step, elements = decode_count(registers[agu_register(pe, agu, "count")])
  offset, cyc = decode_offset_cyc(rest)
  return {"enabled": enabled, "mode": mode, "offset": offset, "cyc": cyc, "step": step, "elements": elements}


def decode_swen(value):
  return [bool(value >> (31 - pe) & 1) for pe in range(4)]


def output_fu(value, pe):
  if not 0 <= pe <= 3:
    raise ValueError(f"pe{pe}: processing element out of range (pe0 to pe3)")
  return "secondary" if decode_swen(value)[pe] else "primary"


def decode_routing(value):
  return [value >> (4 * n) & 0xf for n in range(4)]


def routing_view(registers, kind):
  if kind not in ROUTING_REGISTERS:
    raise ValueError(f"unknown routing '{kind}' ({', '.join(ROUTING_REGISTERS)})")
  nibbles = decode_routing(registers[ROUTING_REGISTERS[kind]])
  if kind == "write":
    return nibbles
  return [nibble if nibble < 4 else "clear" for nibble in nibbles]


def fu_register(pe, kind):
  if not 0 <= pe <= 3:
    raise ValueError(f"pe{pe}: processing element out of range (pe0 to pe3)")
  if kind not in FU_KINDS:
    raise ValueError(f"unknown fu '{kind}' ({', '.join(FU_KINDS)})")
  return FU_KINDS[kind] + pe


def decode_selector(value):
  if 16 <= value <= 23:
    return f"STAGING_{value - 16}"
  if value < 16 and value % 2 == 0:
    return f"{'BASE' if value & 8 else 'TOP'}_{value >> 1 & 3}"
  return f"UNKNOWN_{value}"


def decode_mux(register):
  return decode_selector(register >> MUX_FRONT_SHIFT & 0x1f), decode_selector(register >> MUX_BACK_SHIFT & 0x1f)


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


def decode_fu(register):
  front, back = decode_mux(register)
  return {
    "front": front,
    "back": back,
    "opcode": register >> 12 & 0x3ff,
    "sat": register >> 7 & 0x1f,
    "round": register >> 6 & 1,
    "k": register & 0x3f,
  }


def saturate(value, n):
  if n == 0:
    return value
  return max(-(1 << (n - 1)), min((1 << (n - 1)) - 1, value))


def signed32(value):
  return value - (1 << 32) if value & 0x80000000 else value


def fu_operands(registers, pe, kind):
  if kind not in FU_OPERAND_REGISTERS:
    raise ValueError(f"unknown fu '{kind}' ({', '.join(FU_OPERAND_REGISTERS)})")
  if not 0 <= pe <= 3:
    raise ValueError(f"pe{pe}: processing element out of range (pe0 to pe3)")
  first = FU_OPERAND_REGISTERS[kind] + 2 * pe
  return signed32(registers[first]), signed32(registers[first + 1])


def op_add(back, front, fu, a, b):
  if fu["round"] and fu["k"]:
    raise ValueError("the rounding bit of an ADD with a shift is not modeled")
  return (back + front) >> fu["k"]


def op_clp(back, front, fu, a, b):
  return max(b, min(a, back))


OPCODES = {0x010: (op_add, ("back", "front")), 0x07c: (op_clp, ("back",))}


def opcode_entry(fu):
  entry = OPCODES.get(fu["opcode"])
  if entry is None:
    raise ValueError(f"the opcode {fu['opcode']:#x} is not modeled (modeled: {', '.join(hex(opcode) for opcode in OPCODES)})")
  return entry


def execute(fu, back, front, a=0, b=0):
  handler, _ = opcode_entry(fu)
  return saturate(handler(back, front, fu, a, b), fu["sat"])


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
