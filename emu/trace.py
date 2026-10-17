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
