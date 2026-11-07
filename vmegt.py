import argparse
import os
import sys

from vmegt.ids import chosen_ids


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmegt")
  parser.add_argument("input")
  parser.add_argument("ids", nargs="*")
  parser.add_argument("--list", action="store_true")
  args = parser.parse_args(argv)
  if not os.path.exists(args.input):
    print(f"{args.input}: no such file", file=sys.stderr)
    return 2
  try:
    ids = chosen_ids(os.path.abspath(args.input), args.ids)
  except ValueError as e:
    print(f"{args.input}: {e}", file=sys.stderr)
    return 2
  print("\n".join(ids))
  return 0


if __name__ == "__main__":
  sys.exit(main())
