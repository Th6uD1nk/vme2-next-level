import vmegc

SCRATCHPAD_BASE = 0x44000000
DATAPATH_BASE = 0x440f8000
REGISTER_COUNT = 106
CONTEXT_WORDS = 112
DMAC_BASE = 0x440ff000
DMAC_REGISTER_COUNT = 17
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
  blocks = vmegc.find_blocks(text)
  kernels = {vmegc.kernel_name(text, block): block for block in blocks if block[0] == "kernel"}
  if name is None:
    if len(kernels) != 1:
      known = ", ".join(kernels) if kernels else "there is no kernel in this file"
      raise ValueError(f"give the name of the kernel ({known})")
    name = next(iter(kernels))
  if name not in kernels:
    known = ", ".join(kernels) if kernels else "there is no kernel in this file"
    raise ValueError(f"unknown kernel '{name}' ({known})")
  return vmegc.kernel_statements(text, kernels[name], {})


class Emulator:
  def __init__(self):
    self.scratchpad = Scratchpad()
    self.registers = [0] * REGISTER_COUNT
    self.dmac = [0] * DMAC_REGISTER_COUNT

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
      registers[index] = value & 0xffffffff

  def load_context(self, words):
    if len(words) != CONTEXT_WORDS:
      raise ValueError(f"a context has {CONTEXT_WORDS} words, not {len(words)}")
    self.registers[:] = [word & 0xffffffff for word in words[:REGISTER_COUNT]]
