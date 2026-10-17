DATAPATH_BASE = 0x440f8000
REGISTER_COUNT = 106
CONTEXT_WORDS = 112
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
