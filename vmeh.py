import argparse
import os
import sys

from vmee.run import choose_source
from vmeh.extract import extract_program, extract_source


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmeh")
  parser.add_argument("input", nargs="+")
  parser.add_argument("--extract")
  parser.add_argument("-o", "--output", required=True)
  parser.add_argument("--buffers-start", type=int, default=0)
  parser.add_argument("--buffers-words", type=int, default=32)
  args = parser.parse_args(argv)

  where = ", ".join(args.input)
  try:
    sources = []
    for path in args.input:
      where = path
      with open(path, encoding="utf-8") as f:
        sources.append((path, f.read()))
    if args.extract:
      path, text = choose_source(sources, args.extract)
      where = path
      others = [other for other_path, other in sources if other_path != path]
      result = extract_source(text, args.extract, others, args.buffers_start, args.buffers_words)
    else:
      result = extract_program(sources, args.buffers_start, args.buffers_words)
    where = args.output
    if os.path.dirname(args.output):
      os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
      f.write(result)
  except OSError as e:
    print(f"{where}: {e.strerror.lower()}", file=sys.stderr)
    return 1
  except ValueError as e:
    print(f"{where}: {e}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  sys.exit(main())
