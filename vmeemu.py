SCRATCHPAD_BASE = 0x44000000
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
