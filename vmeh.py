import argparse
import os
import sys

from vmee.options import parse_uses
from vmee.run import choose_source, variant_id
from vmeg.unroll import unroll_loops, unroll_marked_loops
from vmeg.variants import expand_variants
from vmeh.extract import extract_program, extract_source


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmeh")
  parser.add_argument("input", nargs="+")
  parser.add_argument("--extract")
  parser.add_argument("-o", "--output", required=True)
  parser.add_argument("--index")
  parser.add_argument("--buffers-start", type=int, default=0)
  parser.add_argument("--buffers-words", type=int, default=32)
  parser.add_argument("--use", action="append", default=[])
  args = parser.parse_args(argv)
  if args.index is not None and not args.extract:
    parser.error("--index goes with --extract")
  uses = parse_uses(parser, args.use)

  where = ", ".join(args.input)
  try:
    sources = []
    for path in args.input:
      where = path
      with open(path, encoding="utf-8") as f:
        sources.append((path, expand_variants(unroll_marked_loops(unroll_loops(f.read())), True)))
    if args.extract:
      args.extract = variant_id(sources, args.extract, args.index)
      path, text = choose_source(sources, args.extract)
      where = path
      others = [other for other_path, other in sources if other_path != path]
      result = extract_source(text, args.extract, others, args.buffers_start, args.buffers_words, uses)
    else:
      result = extract_program(sources, args.buffers_start, args.buffers_words, uses)
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
