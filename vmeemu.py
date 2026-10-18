import argparse
import sys

from emu.listing import defines, emulations, format_listing
from emu.machine import Emulator
from emu.memory import dump_base_buffers
from emu.trace import replay


def list_emulations(text, kernel):
  found = emulations(text)
  if kernel is not None:
    known = [emulation["kernel"] for emulation in found]
    if kernel not in known:
      raise ValueError(f"no @emulate on the kernel '{kernel}' ({', '.join(known) if known else 'there is no @emulate in this file'})")
    found = [emulation for emulation in found if emulation["kernel"] == kernel]
  elif not found:
    print("warning: there is no @emulate in this file", file=sys.stderr)
  sys.stdout.write(format_listing(found, defines(text)))


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmeemu")
  parser.add_argument("input")
  parser.add_argument("--words", type=int, default=32)
  parser.add_argument("--list", action="store_true")
  parser.add_argument("--kernel")
  args = parser.parse_args(argv)
  if args.kernel is not None and not args.list:
    parser.error("--kernel goes with --list")

  try:
    with open(args.input, encoding="utf-8") as f:
      text = f.read()
    if args.list:
      list_emulations(text, args.kernel)
      return 0
    emulator = Emulator()
    replay(emulator, text)
    sys.stdout.write(dump_base_buffers(emulator.scratchpad, args.words))
  except (ValueError, OSError) as e:
    print(f"{args.input}: {e}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  sys.exit(main())
