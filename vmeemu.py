import argparse
import sys

from emu.machine import Emulator
from emu.memory import dump_base_buffers
from emu.trace import replay


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmeemu")
  parser.add_argument("trace")
  parser.add_argument("--words", type=int, default=32)
  args = parser.parse_args(argv)

  try:
    with open(args.trace, encoding="utf-8") as f:
      text = f.read()
    emulator = Emulator()
    replay(emulator, text)
    sys.stdout.write(dump_base_buffers(emulator.scratchpad, args.words))
  except (ValueError, OSError) as e:
    print(f"{args.trace}: {e}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  sys.exit(main())
