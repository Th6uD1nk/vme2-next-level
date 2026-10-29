import re
import struct

from vmeg.scanner import tokens

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


def element_edits(toks, integer, fraction):
  edits = []
  depth = parens = 0
  run = []

  def flush():
    if run:
      word = to_q("".join(value for _, value, _, _ in run), integer, fraction)
      if word is not None:
        edits.append((run[0][2], run[-1][3] - run[0][2], word))
      run.clear()

  for token in toks:
    kind, value = token[0], token[1]
    if kind == "punct" and value == "{":
      flush()
      depth += 1
    elif kind == "punct" and value == "}":
      flush()
      depth -= 1
    elif depth and kind == "punct" and value == "," and not parens:
      flush()
    elif depth:
      if kind == "punct" and value == "(":
        parens += 1
      elif kind == "punct" and value == ")":
        parens -= 1
      run.append(token)
  return edits


def translate_buffer(text, buffer_type):
  toks = list(tokens(text))
  i = next(k for k, (kind, value, _, _) in enumerate(toks) if kind == "ident" and value == "Buffer")
  size, after = buffer_format(toks, i)
  edits = [(toks[i][2], toks[after - 1][3] - toks[i][2], buffer_type)]
  if size is not None:
    edits += element_edits(toks[after:], *size)
  for start, length, new in sorted(edits, reverse=True):
    text = text[:start] + new + text[start + length:]
  return text
