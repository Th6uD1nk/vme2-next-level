SCRATCHPAD_BASE = 0x44000000
PHYSICAL_MASK = 0x1fffffff
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


def check_window(start, words):
  if start < 0:
    raise ValueError("the first word of the buffers cannot be negative")
  if words <= 0:
    raise ValueError("the number of words of the buffers must be 1 or more")
  if start + words > BUFFER_WORDS:
    raise ValueError(f"the window of the buffers goes past the end of a buffer ({BUFFER_WORDS} words)")


def dump_base_buffers(scratchpad, start, words):
  check_window(start, words)
  rows = []
  for n in range(BUFFER_COUNT):
    rows.append(f"Buffer: BASE {n}")
    first = BASE_OFFSET + n * BUFFER_WORDS + start
    for i in range(0, words, 4):
      rows.append(", ".join(f"0x{scratchpad.read(first + i + k):08x}" for k in range(min(4, words - i))) + ",")
    rows.append("")
  return "\n".join(rows) + "\n"
