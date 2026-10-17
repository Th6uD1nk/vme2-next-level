from vmeg.blocks import find_blocks, kernel_name
from vmeg.parser import kernel_statements
from emu.memory import BASE_OFFSET, BUFFER_WORDS, PHYSICAL_MASK, SCRATCHPAD_BASE, STAGING_COUNT, STAGING_LAG, STAGING_WORDS, Scratchpad
from emu.registers import CONTEXT_WORDS, DATAPATH_BASE, FU_KINDS, REGISTER_COUNT, SWEN_REGISTER, decode_fu, fu_register, output_fu
from emu.fu import execute, fu_operands, opcode_entry
from emu.agu import agu_inside_offsets, run_length, stream_at, stream_offsets, write_agu

DMAC_BASE = 0x440ff000
DMAC_REGISTER_COUNT = 17
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
