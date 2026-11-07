import argparse
import os
import sys

from vmegt.build import build_all
from vmegt.check import check_all, parse_log
from vmegt.ids import ROOT, chosen_ids
from vmegt.run import find_pspsh, reset, run_kernel


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmegt")
  parser.add_argument("input")
  parser.add_argument("ids", nargs="*")
  parser.add_argument("--list", action="store_true")
  parser.add_argument("--check", action="store_true")
  parser.add_argument("--reuse-log", action="store_true")
  parser.add_argument("--pspdev", default=os.environ.get("PSPDEV"))
  parser.add_argument("--pspsh", default=None)
  parser.add_argument("--host", default=os.environ.get("PSP_HOST"))
  parser.add_argument("--work", default=os.path.join(os.getcwd(), "psp-kernels"))
  parser.add_argument("--log", default=None)
  parser.add_argument("--port", type=int, default=int(os.environ.get("PSP_PORT", "10000")))
  parser.add_argument("--reset-wait", type=float, default=14)
  parser.add_argument("--timeout", type=float, default=60)
  parser.add_argument("--retries", type=int, default=1)
  parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
  parser.add_argument("--buffers-start", type=int, default=0)
  parser.add_argument("--buffers-words", type=int, default=32)
  parser.add_argument("--use", action="append", default=[])
  args = parser.parse_args(argv)
  if args.reuse_log and not args.check:
    print("--reuse-log goes with --check", file=sys.stderr)
    return 2
  if not os.path.exists(args.input):
    print(f"{args.input}: no such file", file=sys.stderr)
    return 2
  source = os.path.abspath(args.input)
  try:
    ids = chosen_ids(source, args.ids)
  except ValueError as e:
    print(f"{args.input}: {e}", file=sys.stderr)
    return 2
  if args.list:
    print("\n".join(ids))
    return 0
  work = os.path.abspath(args.work)
  final = args.log or os.path.join(work, "results.log")
  if args.reuse_log:
    if not os.path.exists(final):
      print(f"{final}: no such file", file=sys.stderr)
      return 2
    with open(final, encoding="utf-8") as f:
      raw = f.read()
    sections = parse_log(raw)
    if not sections and len(ids) == 1:
      sections = {ids[0]: raw.strip()}
    checked = check_all(source, ids, sections, args.jobs, args.buffers_start, args.buffers_words, args.use)
    for identifier in ids:
      print(f"{identifier}: {checked[identifier]}")
    return 0 if all(value == "ok" for value in checked.values()) else 1
  if not args.pspdev:
    print("give --pspdev or set PSPDEV", file=sys.stderr)
    return 2
  pspsh = find_pspsh(args.pspdev, args.pspsh)
  if not pspsh:
    print("pspsh was not found, give --pspsh", file=sys.stderr)
    return 2
  host = os.path.abspath(args.host or os.path.join(ROOT, "samples", "vmeh", "build"))
  os.makedirs(work, exist_ok=True)
  os.makedirs(host, exist_ok=True)
  builds = build_all(source, ids, work, args.pspdev, args.jobs, args.buffers_start, args.buffers_words, args.use)
  status = {}
  sections = {}
  reset(pspsh, args.port, work, args.reset_wait)
  with open(final, "w", encoding="utf-8") as out:
    for position, (identifier, (program, error)) in enumerate(zip(ids, builds), 1):
      out.write(f"=== kernel {identifier} ===\n")
      if program is None:
        status[identifier] = "build failed"
        out.write(f"build failed\n{error}\n")
      else:
        text = run_kernel(pspsh, args.port, host, work, program, identifier, args.reset_wait, args.timeout, args.retries)
        status[identifier] = "no log" if text is None else "done"
        if text is not None:
          sections[identifier] = text
        out.write("no log\n" if text is None else text.rstrip("\n") + "\n")
      out.write("\n")
      out.flush()
      print(f"[{position}/{len(ids)}] {identifier}: {status[identifier]}", file=sys.stderr, flush=True)
    if args.check:
      checked = check_all(source, [i for i in ids if i in sections], sections, args.jobs, args.buffers_start, args.buffers_words, args.use)
      for identifier, result in checked.items():
        status[identifier] = result
        print(f"{identifier}: {result}", file=sys.stderr, flush=True)
    out.write("=== summary ===\n")
    for identifier in ids:
      out.write(f"{identifier}: {status[identifier]}\n")
  print(final)
  expected = "ok" if args.check else "done"
  return 0 if all(value == expected for value in status.values()) else 1


if __name__ == "__main__":
  sys.exit(main())
