import re
import struct

WORD_BITS = 24


def buffer_format(toks, i):
  if i + 1 >= len(toks) or toks[i + 1][:2] != ("punct", "("):
    return None, i + 1
  shape = [value for _, value, _, _ in toks[i + 2:i + 6]]
  match = re.fullmatch(r"Q(\d+)", shape[0]) if len(shape) == 4 and shape[1] == "." and shape[3] == ")" and shape[2].isdigit() else None
  if match is None:
    raise ValueError("the format of a Buffer is written Qm.n, for example Buffer(Q8.8)")
  integer, fraction = int(match.group(1)), int(shape[2])
  if integer < 1:
    raise ValueError("the integer part of a Q format counts the sign, it is 1 at least")
  if integer + fraction > WORD_BITS:
    raise ValueError(f"the format Q{integer}.{fraction} has {integer + fraction} bits, a Buffer holds {WORD_BITS} bits at most")
  return (integer, fraction), i + 6


NUMBER = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?[fF]?")


def to_q(text, integer, fraction):
  if NUMBER.fullmatch(text) is None:
    return None
  value = float(text.rstrip("fF"))
  if text[-1] in "fF":
    value = struct.unpack("f", struct.pack("f", value))[0]
  word = int(value * 2 ** fraction)
  bits = integer + fraction
  if not -(1 << (bits - 1)) <= word < 1 << (bits - 1):
    raise ValueError(f"the value {text} does not fit the format Q{integer}.{fraction} (from {-2 ** (integer - 1)} to {2 ** (integer - 1) - 2 ** -fraction})")
  return "0x%08x" % (word & 0xffffffff)
