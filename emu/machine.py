from emu.agu import agu_inside_offsets, run_length, stream_at, stream_offsets, write_agu
from emu.dmac import CLEAR_LOCAL_BUFFER, CONTEXT_TRANSFER_BITS, CONTEXT_TRANSFER_MASK, DMAC_BASE, DMAC_CONTROL, DMAC_COUNT, DMAC_MEMORY_ADDRESS, DMAC_REGISTER_COUNT, DMAC_SCRATCHPAD_OFFSET, MEM_FROM_16, MEM_TO_16, PRELOAD_CONTEXT, RING_TO_MEMORY, RING_TO_SCRATCHPAD, TRIGGER
from emu.fu import execute, fu_operands, opcode_entry
from emu.memory import BASE_OFFSET, BUFFER_WORDS, PHYSICAL_MASK, SCRATCHPAD_BASE, STAGING_COUNT, STAGING_LAG, STAGING_WORDS, Scratchpad
from emu.registers import CONTEXT_WORDS, DATAPATH_BASE, FU_KINDS, REGISTER_COUNT, SWEN_REGISTER, decode_fu, fu_register, output_fu


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
      needed[key] = (fu, uses, a, b, {})
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
      for (kind, pe), (fu, uses, a, b, state) in needed.items():
        back = operand(fu["back"], cycle) if "back" in uses else 0
        front = operand(fu["front"], cycle) if "front" in uses else 0
        slot = cycle + STAGING_LAG
        if slot >= STAGING_WORDS:
          raise ValueError(f"the run is longer than the staging, the slot {slot} does not exist")
        staging = pe + FU_KINDS[kind]
        previous = self.staging_read(staging, slot - 1) if cycle else None
        self.staging_write(staging, slot, execute(fu, back, front, a, b, previous, state))

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
        slot = view["cyc"] + j - view["bubbles"] - STAGING_LAG
        writes.append((first + inside, self.staging_read(staging, slot) if j >= view["bubbles"] and slot >= 0 else 0))
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
    return None if offsets is None else [0 if offset is None else self.scratchpad.read(offset) for offset in offsets]

  def load_context(self, words):
    if len(words) != CONTEXT_WORDS:
      raise ValueError(f"a context has {CONTEXT_WORDS} words, not {len(words)}")
    self.registers[:] = [word & 0xffffffff for word in words[:REGISTER_COUNT]]
