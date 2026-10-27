import argparse
import sys

from vmee.listing import defines, emulations, format_listing
from vmee.machine import Emulator
from vmee.memory import dump_base_buffers
from vmee.run import choose_source, run_emulation
from vmee.trace import replay


def list_emulations(text, kernel, full):
  found = emulations(text)
  if kernel is not None:
    known = [emulation["kernel"] for emulation in found]
    if kernel not in known:
      raise ValueError(f"no @emulate on the kernel '{kernel}' ({', '.join(known) if known else 'there is no @emulate in this file'})")
    found = [emulation for emulation in found if emulation["kernel"] == kernel]
  elif not found:
    print("warning: there is no @emulate in this file", file=sys.stderr)
  for emulation in found:
    if not emulation["global"] and not emulation["local"] and not emulation["stores"]["global"] and not emulation["stores"]["local"]:
      print(f"warning: emulate \"{emulation['id']}\": the kernel {emulation['kernel']} has no buffer", file=sys.stderr)
  sys.stdout.write(format_listing(found, defines(text), full))


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmeemu")
  parser.add_argument("input", nargs="+")
  parser.add_argument("--buffers-start", type=int, default=0)
  parser.add_argument("--buffers-words", type=int, default=32)
  parser.add_argument("--list", action="store_true")
  parser.add_argument("--kernel")
  parser.add_argument("--full", action="store_true")
  parser.add_argument("--run")
  parser.add_argument("--trace")
  parser.add_argument("--compat", choices=["fat"])
  args = parser.parse_args(argv)
  if (args.kernel is not None or args.full) and not args.list:
    parser.error("--kernel and --full go with --list")
  if args.run is not None and args.list:
    parser.error("--run does not go with --list")
  if args.trace is not None and args.run is None:
    parser.error("--trace goes with --run")
  if args.compat is not None and args.run is None:
    parser.error("--compat goes with --run")
  if args.run is None and len(args.input) != 1:
    parser.error("several files go only with --run")

  where = ", ".join(args.input)
  try:
    sources = []
    for path in args.input:
      with open(path, encoding="utf-8") as f:
        sources.append((path, f.read()))
    text = sources[0][1]
    if args.list:
      list_emulations(text, args.kernel, args.full)
      return 0
    if args.run is not None:
      path, text = choose_source(sources, args.run)
      where = path
      others = [other for other_path, other in sources if other_path != path]
      emulator = run_emulation(text, args.run, args.trace, others, args.compat)
    else:
      emulator = Emulator()
      replay(emulator, text)
    sys.stdout.write(dump_base_buffers(emulator.scratchpad, args.buffers_start, args.buffers_words))
  except (ValueError, OSError) as e:
    print(f"{where}: {e}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  sys.exit(main())
