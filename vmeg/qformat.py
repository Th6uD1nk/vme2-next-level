import re

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
