import argparse
import os
import sys

SUFFIX = ".vmeg.c"


def default_output(path):
  name = os.path.basename(path)
  if not name.endswith(SUFFIX):
    raise SystemExit(f"vmegc: input must end with {SUFFIX} (or pass -o)")
  return name[:-len(SUFFIX)] + ".c"


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmegc")
  parser.add_argument("input")
  parser.add_argument("-o", "--output")
  args = parser.parse_args(argv)

  output = args.output or default_output(args.input)

  with open(args.input, encoding="utf-8", newline="") as f:
    text = f.read()
  with open(output, "w", encoding="utf-8", newline="") as f:
    f.write(text)
  return 0


if __name__ == "__main__":
  sys.exit(main())
