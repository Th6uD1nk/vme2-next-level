import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SOURCE = os.path.join(HERE, "k-checker.vmeg.cpp")
SHIFTS = [">> 1", ">> 24", ">> 32", ">> 56"]


def parse(text):
  found = {}
  for block in text.split("\n\n"):
    match = re.match(r"Buffer: BASE ([0-3])\n", block)
    if match:
      found[int(match.group(1))] = [int(w, 16) for w in re.findall(r"0x[0-9a-f]{8}", block)][:16]
  return found


def emulate(identifier):
  run = subprocess.run([sys.executable, os.path.join(ROOT, "vmeemu.py"), "--run", identifier, SOURCE], capture_output=True, text=True)
  return None if run.returncode else run.stdout, run.stderr.strip()


def compare(identifier, log):
  text, error = emulate(identifier)
  if text is None:
    return [f"{identifier}: {error}"]
  emulated, measured = parse(text), parse(log)
  if len(measured) < 4 or len(emulated) < 4:
    return [f"{identifier}: 4 buffers BASE are needed ({len(measured)} in the log, {len(emulated)} in the emulator)"]
  lines = []
  for pe in range(4):
    different = [index for index, (got, want) in enumerate(zip(measured[pe], emulated[pe])) if got != want]
    if different:
      first = different[0]
      lines.append(f"{identifier} BASE_{pe} ({SHIFTS[pe]}): {len(different)} words differ, the first is word {first}: PSP 0x{measured[pe][first]:08x}, emulator 0x{emulated[pe][first]:08x}")
    else:
      lines.append(f"{identifier} BASE_{pe} ({SHIFTS[pe]}): same as the emulator")
  return lines


def main(arguments):
  if len(arguments) != 3 or arguments[0] != "--log":
    print("usage: check.py --log log.txt kernel-id")
    return 2
  with open(arguments[1], encoding="utf-8") as f:
    log = f.read()
  lines = compare(arguments[2], log)
  print("\n".join(lines))
  return 1 if any("differ" in line for line in lines) else 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
