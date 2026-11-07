import argparse
import os
import sys

from vmegt.build import build_all
from vmegt.ids import chosen_ids


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmegt")
  parser.add_argument("input")
  parser.add_argument("ids", nargs="*")
  parser.add_argument("--list", action="store_true")
  parser.add_argument("--pspdev", default=os.environ.get("PSPDEV"))
  parser.add_argument("--work", default=os.path.join(os.getcwd(), "psp-kernels"))
  parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
  parser.add_argument("--buffers-start", type=int, default=0)
  parser.add_argument("--buffers-words", type=int, default=32)
  parser.add_argument("--use", action="append", default=[])
  args = parser.parse_args(argv)
  if not os.path.exists(args.input):
    print(f"{args.input}: no such file", file=sys.stderr)
    return 2
  try:
    ids = chosen_ids(os.path.abspath(args.input), args.ids)
  except ValueError as e:
    print(f"{args.input}: {e}", file=sys.stderr)
    return 2
  if args.list:
    print("\n".join(ids))
    return 0
  if not args.pspdev:
    print("give --pspdev or set PSPDEV", file=sys.stderr)
    return 2
  work = os.path.abspath(args.work)
  builds = build_all(os.path.abspath(args.input), ids, work, args.pspdev, args.jobs, args.buffers_start, args.buffers_words, args.use)
  failed = 0
  for identifier, (program, error) in zip(ids, builds):
    print(f"{identifier}: {'built' if program else 'build failed'}")
    if not program:
      print(error, file=sys.stderr)
      failed += 1
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
